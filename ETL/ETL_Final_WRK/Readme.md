# Итоговое задание ETL

## Задание 1: Работа с Yandex DataTransfer

Требуется перенести данные из Managed Service for YDB в объектное хранилище Object Storage. 
Выполнить необходимо с использованием сервиса Data Transfer.


**1. Создать БД Yandex DataBase:**


```SQL
CREATE TABLE it_salary_new(
    id UUID NOT NULL,
    job_title Utf8,
    salary_usd Uint32,
    experience_level Utf8,
    company_location Utf8,
    posting_date Date,
    PRIMARY KEY (id)
);
```

**2.	Подготовить данные:**

Для подготовки данных и создание датасета используем создание нескольких таблиц с данными, 
чтобы затем использовать их для подготовки данных в основной таблице.

<details>
<summary>SQL скрипт подготовки данных</summary>

```SQL
CREATE TABLE temp_job_titles(
  id Uint32,
  value Utf8,
  PRIMARY KEY(id)
);


INSERT INTO temp_job_titles(id, value) VALUES
(1, 'Software Engineer'),
(2, 'Data Scientist'),
(3, 'DevOps Engineer'),
(4, 'Product Manager'),
(5, 'QA Engineer'),
(6, 'Frontend Developer'),
(7, 'Backend Developer'),
(8, 'Full Stack Developer'),
(9, 'Data Engineer'),
(10, 'ML Engineer');


CREATE TABLE temp_experience_levels(
  id Uint32,
  value Utf8,
  PRIMARY KEY(id)
);

INSERT INTO temp_experience_levels(id, value) VALUES 
    (1, 'Junior'),
    (2, 'Middle'),
    (3, 'Senior'),
    (4, 'Lead'),
    (5, 'Principal');


CREATE TABLE temp_locations(
  id Uint32,
  value Utf8,
  PRIMARY KEY(id)
);

INSERT INTO temp_locations(id, value) VALUES 
    (1, 'USA'),
    (2, 'Germany'),
    (3, 'UK'),
    (4, 'Canada'),
    (5, 'India'),
    (6, 'Japan'),
    (7, 'Australia'),
    (8, 'France'),
    (9, 'Spain'),
    (10, 'Russia'),
    (11, 'China'),
    (12, 'Brazil'),
    (13, 'Netherlands'),
    (14, 'Sweden'),
    (15, 'Singapore'),
    (16, 'Italy'),
    (17, 'Poland'),
    (18, 'UAR'),
    (19, 'Egypt'),
    (20, 'Switzerland');
```
</details>

Затем приступаем к заполнению основной таблицы, данные в которой будут созданы рандомно в размере 1000 строк,
это поможет нагенерировать необходимый объяем тестовых данных, не копируя и вставляя код, а исполняя его столько раз сколько необходимо. 

<details>
<summary>SQL скрипт Insert Values</summary>
    
```SQL
INSERT INTO it_salary_new (id, job_title, salary_usd, experience_level, company_location)
SELECT 
    RANDOM_UUID(j.id * 10000 + e.id * 1000 + l.id) AS id,  -- Использование комбинации значений как параметра
    j.value AS job_title,
    CAST(50000 + (j.id * 10000) AS Uint32) AS salary_usd,
    e.value AS experience_level,
    l.value AS company_location
FROM 
    temp_job_titles AS j
    CROSS JOIN temp_experience_levels AS e
    CROSS JOIN temp_locations AS l
LIMIT 1000;
```
</details>

**3. Создать трансфер в **Object Storage:****

<details>
<summary>Конфигурация трансфера</summary>
    
![](1st%20task/Screen/info_param_transfer.png)

![](1st%20task/Screen/ydb_transfer%settings.png)

</details>

![](1st%20task/Screen/transfer_go.png)

![](1st%20task/Screen/result_transfer.png)


**Результат задания**:

- Подготовка данных в YDB;
  
- Успешный трансфер данных из YDB в Object Storage.


## Задание 2: Автоматизация работы с Yandex Data Processing при помощи Apache AirFlow

Требуется обрабатывать файлы (parquet или CSV) из внешнего источника. 


**1. Подготовка скрипта PySpark**


<details>
<summary>Pyspark script</summary>

```python
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
```
</details>


Данный скрипт представляет собой инструмент для обработки данных из Object Storage S3 с использованием PySpark. Вот краткое описание его основных функций:

Создание Spark-сессии

    create_spark_session() - настраивает и инициализирует Spark-сессию с конфигурацией для работы с S3, 
    включая поддержку Hive и адаптивное выполнение запросов.

Чтение данных

    read_csv_from_s3() - читает CSV-файлы из S3 с возможностью указать наличие заголовка и автоматическое определение схемы данных.

Обработка данных

    process_data():
        Добавляет колонки с датой и временем обработки
        Создает уникальный идентификатор для каждой записи (record_id)
        Выводит схему обработанного фрейма данных

Запись данных

    write_data_to_s3() - сохраняет обработанные данные обратно в S3:
        Поддерживает форматы Parquet и CSV
        Позволяет указать режим записи (перезапись, добавление и т.д.)
        Поддерживает партиционирование данных по указанным колонкам

Основной процесc

    main():
        Определяет пути к исходным и результирующим данным в S3
        Создает Spark-сессию
        Читает данные из CSV-файла
        Выводит информацию о схеме и образец данных
        Обрабатывает данные
        Записывает результаты с партиционированием по дате обработки
        Обрабатывает возможные ошибки и корректно завершает Spark-сессию



**2. Airflow DAG скрипт:**

<details>
<summary>Airflow script</summary>

```python
import uuid
import datetime
from airflow import DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.providers.yandex.operators.yandexcloud_dataproc import (
    DataprocCreateClusterOperator,
    DataprocCreatePysparkJobOperator,
    DataprocDeleteClusterOperator,
)

YC_DP_AZ = 'ru-central1-d'
YC_DP_SSH_PUBLIC_KEY = 'ssh'
YC_DP_SUBNET_ID = 'fl8hk1i4fk2ch5e952ii'
YC_DP_SA_ID = 'aje2t33o0c2ar3n3af3p'
YC_DP_METASTORE_URI = '10.130.0.23'
YC_BUCKET = 'editeddata'


SOURCE_PATH = "s3a://source-a/ai_job_dataset.csv"
DESTINATION_PATH = "s3a://source-b/"

# DAG settings
with DAG(
    'PROCESS_VARIABLE_SIZE_FILES',
    schedule_interval='@daily',
    tags=['data-processing', 'pyspark', 'variable-size-files'],
    start_date=datetime.datetime.now(),
    max_active_runs=1,
    catchup=False
) as process_files_dag:

    # 1. cluster with HDD not SSD (SSD выходил за лимиты квоты)
    create_spark_cluster = DataprocCreateClusterOperator(
        task_id='create-dataproc-cluster',
        cluster_name=f'data-processing-{uuid.uuid4()}',
        cluster_description='Cluster with HDD storage for processing files',
        ssh_public_keys=YC_DP_SSH_PUBLIC_KEY,
        service_account_id=YC_DP_SA_ID,
        subnet_id=YC_DP_SUBNET_ID,
        s3_bucket=YC_BUCKET,
        zone=YC_DP_AZ,
        cluster_image_version='2.1',
        # Master node with HDD
        masternode_resource_preset='s2.micro',
        masternode_disk_type='network-hdd',
        masternode_disk_size=50,
        # Compute nodes with HDD
        computenode_resource_preset='s2.small',
        computenode_disk_type='network-hdd',
        computenode_disk_size=50,
        computenode_count=1,
        computenode_max_hosts_count=2,
        services=['YARN', 'SPARK'],
        datanode_count=0,
        properties={
            'spark:spark.hive.metastore.uris': f'thrift://{YC_DP_METASTORE_URI}:9083',
            'spark:spark.dynamicAllocation.enabled': 'true',
            'spark:spark.executor.memory': '2g',
            'spark:spark.driver.memory': '1g',
            'spark:spark.sql.adaptive.enabled': 'true',
            'spark:spark.sql.files.maxPartitionBytes': '128m',
        },
    )

    # 2 этап: запуск задания PySpark
    run_pyspark_job = DataprocCreatePysparkJobOperator(
        task_id='process-files-with-pyspark',
        main_python_file_uri=f's3a://{YC_BUCKET}/scripts/spark_task.py',
        python_file_uris=[],
        file_uris=[],
        archive_uris=[],
        jar_file_uris=[],
        properties={
            'spark.executor.memory': '2g',
            'spark.driver.memory': '1g',
            'spark.sql.adaptive.enabled': 'true',
            'spark.sql.files.maxPartitionBytes': '128m',
        },
        args=[
            '--source_path', SOURCE_PATH,
            '--destination_path', DESTINATION_PATH
        ],
    )

    # 3. Удаление
    delete_spark_cluster = DataprocDeleteClusterOperator(
        task_id='delete-dataproc-cluster',
        trigger_rule=TriggerRule.ALL_DONE,
    )


    create_spark_cluster >> run_pyspark_job >> delete_spark_cluster
```
</details>


--Основные компоненты DAG--


1. Создание кластера DataProc

- Создается временный кластер с уникальным именем (используется UUID)
                
- Настроен на использование HDD-дисков вместо SSD для соблюдения квот
                
 - Конфигурация включает:
                
   Мастер-ноду с ресурсами s2.micro и 50 ГБ HDD
   Вычислительные ноды с ресурсами s2.small и 50 ГБ HDD
   Автомасштабирование до 2 вычислительных нод
   Сервисы YARN и SPARK

2. Запуск PySpark-задания

- Запускает Python-скрипт spark_task.py, хранящийся в S3-бакете
        
- Передает параметры источника и назначения данных:
        
  Источник: s3a://source-a/ai_job_dataset.csv
  Назначение: s3a://source-b/
            
  - Настраивает параметры Spark:
        
    Адаптивное выполнение запросов
    Ограничение размера партиций (128 МБ)
    Выделение памяти для драйвера и исполнителей

3. Удаление кластера

После завершения обработки кластер автоматически удаляется
Настроен на выполнение даже при ошибках в предыдущих задачах (TriggerRule.ALL_DONE)



**3. Результат задания**

Поднят кластер Apache Airflow, подготовлены даг и задание PySpark


![](2nd%20task/Screen/airflow_spark.png)

Итог задания обработка внешнего файла S3, его предобработка и сохранение в бакет Yandex Object Storage

![](2nd%20task/Screen/Succes-2.png)

![](2nd%20task/Screen/Succes-3.png)

