from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from datetime import datetime


def create_spark_session(app_name="s3-data-processor"):
    """
    Конфигурация для доступа к S3
    """
    spark = SparkSession.builder \
        .appName(app_name) \
        .enableHiveSupport() \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

    return spark


def read_csv_from_s3(spark, file_path, header=True, infer_schema=True):
    """
    Чтение из S3

    - file_path: S3 путь к файлу

    Returns:
    - Фрейм с данными
    """

    if infer_schema:
        return spark.read.option("header", header).option("inferSchema", infer_schema).csv(file_path)
    else:
        return spark.read.option("header", header).csv(file_path)


def process_data(df):
    """
    Обработка фрейма

    Parameters:
    - df: Фрейм предзагруженный

    Returns:
    - Обработанный файл
    """

    processing_date = datetime.now()

    df_processed = df.withColumn("processing_date", lit(processing_date.strftime("%Y-%m-%d")))
    df_processed = df_processed.withColumn("processing_timestamp", lit(processing_date.strftime("%Y-%m-%d %H:%M:%S")))

    df_processed = df_processed.withColumn("record_id", monotonically_increasing_id())

    print("Processed DataFrame Schema:")
    df_processed.printSchema()

    return df_processed


def write_data_to_s3(df, output_path, output_format="parquet", partition_cols=None, mode="overwrite"):
    """
    Write the processed DataFrame to S3

    Parameters:
    - output_path: пункт сохранения S3
    - output_format: формат файла итогового ('parquet' or 'csv')
    """

    writer = df.write.mode(mode)

    if partition_cols:
        writer = writer.partitionBy(partition_cols)

    if output_format.lower() == 'parquet':
        writer.parquet(output_path)
    elif output_format.lower() == 'csv':
        writer.option("header", "true").csv(output_path)
    else:
        raise ValueError(f"Unsupported output format: {output_format}. Use 'parquet' or 'csv'.")


def main():
    input_path = "s3a://source-a/ai_job_dataset.csv"
    output_path = "s3a://source-b/ai_job_processed"

    spark = create_spark_session()

    try:

        print(f"Reading CSV data from {input_path}")
        df = read_csv_from_s3(spark, input_path)

        print("Input Schema:")
        df.printSchema()

        print("Sample Data:")
        df.show(5, truncate=False)

        print("Processing data...")
        processed_df = process_data(df)

        print(f"Writing processed data to {output_path}")
        write_data_to_s3(processed_df, output_path, partition_cols=["processing_date"])

        print("Data processing completed successfully!")

    except Exception as e:
        print(f"Error processing data: {str(e)}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
