from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import to_json, col, struct

def main():
    # Kafka configuration
    kafka_host = "rc1d-dataproc-m-8rg5bteqid4r7ufv"
    kafka_port = "9091"
    kafka_topic = "dataproc-kafka-topic"
    kafka_username = "user1"
    kafka_password = "password1"

    #Spark session
    spark = SparkSession.builder \
        .appName("dataproc-kafka-write-app") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.files.maxPartitionBytes", "128m") \
        .config("spark.dynamicAllocation.enabled", "true") \
        .getOrCreate()

    # Log
    print(f"Writing to Kafka topic: {kafka_topic}")
    print(f"Using Kafka bootstrap server: {kafka_host}:{kafka_port}")


    df = spark.createDataFrame([
        Row(msg="Test message #1 from dataproc-cluster"),
        Row(msg="Test message #2 from dataproc-cluster")
    ])

    # Convert JSON
    df = df.select(to_json(struct([col(c).alias(c) for c in df.columns])).alias('value'))

    #JAAS config
    jaas_config = (
        "org.apache.kafka.common.security.scram.ScramLoginModule required "
        f"username={kafka_username} "
        f"password={kafka_password} "
        ";"
    )

    df.write.format("kafka") \
        .option("kafka.bootstrap.servers", f"{kafka_host}:{kafka_port}") \
        .option("topic", kafka_topic) \
        .option("kafka.security.protocol", "SASL_SSL") \
        .option("kafka.sasl.mechanism", "SCRAM-SHA-512") \
        .option("kafka.sasl.jaas.config", jaas_config) \
        .save()

    print("Successfully wrote messages to Kafka")

if __name__ == "__main__":
    main()
