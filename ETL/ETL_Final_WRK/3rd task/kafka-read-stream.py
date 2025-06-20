import argparse
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, schema_of_json, current_timestamp, lit
from pyspark.sql.types import StringType, StructType, StructField

def main():
    parser = argparse.ArgumentParser(description='Process data from Kafka and S3 using PySpark')
    parser.add_argument('--kafka-host', required=True, help='Kafka host FQDN')
    parser.add_argument('--kafka-port', default='9091', help='Kafka port')
    parser.add_argument('--kafka-topic', default='dataproc-kafka-topic', help='Kafka topic')
    parser.add_argument('--kafka-username', default='user1', help='Kafka username')
    parser.add_argument('--kafka-password', default='password1', help='Kafka password')
    parser.add_argument('--input-path', required=True, help='S3 input path for files')
    parser.add_argument('--input-format', default='csv', choices=['csv', 'parquet', 'json'],
                        help='Input file format (default: csv)')
    parser.add_argument('--output-path', required=True, help='S3 output path')
    parser.add_argument('--output-format', default='parquet', choices=['parquet', 'json', 'csv', 'text'],
                        help='Output file format (default: parquet)')


    try:
        args = parser.parse_args()
    except Exception as e:
        print(f"Error parsing arguments: {str(e)}")
        sys.exit(1)

    try:
        #Spark session
        spark = SparkSession.builder \
            .appName("dataproc-data-processing-app") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.files.maxPartitionBytes", "128m") \
            .config("spark.dynamicAllocation.enabled", "true") \
            .getOrCreate()

        print(f"Spark version: {spark.version}")
        print(f"Reading from Kafka topic: {args.kafka_topic}")
        print(f"Using Kafka bootstrap server: {args.kafka_host}:{args.kafka_port}")
        print(f"Input path: {args.input_path}")
        print(f"Input format: {args.input_format}")
        print(f"Output path: {args.output_path}")
        print(f"Output format: {args.output_format}")

        print("Reading data from S3...")
        s3_df = None

        if args.input_format == 'csv':
            s3_df = spark.read.option("header", "true").option("inferSchema", "true").csv(args.input_path)
        elif args.input_format == 'parquet':
            s3_df = spark.read.parquet(args.input_path)
        elif args.input_format == 'json':
            s3_df = spark.read.json(args.input_path)

        if s3_df is not None:
            s3_df = s3_df.withColumn("source", lit("s3"))
            s3_df = s3_df.withColumn("processing_timestamp", current_timestamp())

            print("Sample data from S3:")
            s3_df.show(5, truncate=False)
            print(f"S3 data count: {s3_df.count()}")
        else:
            print("No S3 data found or could not read S3 data")

        print("Reading data from Kafka...")

        # Construct JAAS config with variables
        jaas_config = (
            "org.apache.kafka.common.security.scram.ScramLoginModule required "
            f"username={args.kafka_username} "
            f"password={args.kafka_password} "
            ";"
        )

        # Read from Kafka stream
        kafka_df = spark.readStream.format("kafka") \
            .option("kafka.bootstrap.servers", f"{args.kafka_host}:{args.kafka_port}") \
            .option("subscribe", args.kafka_topic) \
            .option("kafka.security.protocol", "SASL_SSL") \
            .option("kafka.sasl.mechanism", "SCRAM-SHA-512") \
            .option("kafka.sasl.jaas.config", jaas_config) \
            .option("startingOffsets", "earliest") \
            .load()

        # Select and filter value
        value_df = kafka_df.selectExpr("CAST(value AS STRING) as value") \
            .where(col("value").isNotNull())

        query = value_df.writeStream \
            .trigger(once=True) \
            .queryName("received_messages") \
            .format("memory") \
            .start()

        query.awaitTermination()
        print("Kafka stream processing completed")

        kafka_result_df = spark.sql("SELECT value FROM received_messages")

        kafka_count = kafka_result_df.count()
        print(f"Found {kafka_count} messages in Kafka topic")

        kafka_parsed_df = None
        if kafka_count > 0:
            try:

                sample = kafka_result_df.limit(1).collect()[0]["value"]
                json_schema = schema_of_json(sample)
                print("Detected JSON schema from Kafka:")
                print(json_schema.simpleString())

                # Parse JSON
                kafka_parsed_df = kafka_result_df.withColumn("parsed", from_json(col("value"), json_schema)) \
                    .select("parsed.*")

                kafka_parsed_df = kafka_parsed_df.withColumn("source", lit("kafka"))
                kafka_parsed_df = kafka_parsed_df.withColumn("processing_timestamp", current_timestamp())

                print("Sample data from Kafka (parsed):")
                kafka_parsed_df.show(5, truncate=False)
            except Exception as json_error:
                print(f"Could not parse Kafka data as JSON: {str(json_error)}")

        final_df = None

        if s3_df is not None and kafka_parsed_df is not None:

            s3_columns = set(s3_df.columns)
            kafka_columns = set(kafka_parsed_df.columns)
            common_columns = s3_columns.intersection(kafka_columns)

            if common_columns:
                print(f"Common columns found: {common_columns}")
                s3_selected = s3_df.select(*common_columns)
                kafka_selected = kafka_parsed_df.select(*common_columns)

                final_df = s3_selected.union(kafka_selected)
            else:
                print("No common columns found, will write data separately")
                final_df = s3_df
        elif s3_df is not None:
            final_df = s3_df
        elif kafka_parsed_df is not None:
            final_df = kafka_parsed_df

        if final_df is not None:
            print(f"Writing combined data to {args.output_path}")

            if args.output_format == 'parquet':
                final_df.write.mode("overwrite").parquet(args.output_path)
            elif args.output_format == 'json':
                final_df.write.mode("overwrite").json(args.output_path)
            elif args.output_format == 'csv':
                final_df.write.mode("overwrite").option("header", "true").csv(args.output_path)
            else:  # text !
                final_df.select(col("*").cast(StringType())).write.mode("overwrite").text(args.output_path)

            print(f"Successfully wrote {final_df.count()} records to {args.output_path}")
        else:
            print("No data to write")
            empty_df = spark.createDataFrame([("No data found",)], ["message"])
            empty_df.write.mode("overwrite").text(f"{args.output_path}/empty")

    except Exception as e:
        print(f"Error in data processing job: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'spark' in locals():
            spark.stop()
            print("Spark session stopped")


if __name__ == "__main__":
    main()
