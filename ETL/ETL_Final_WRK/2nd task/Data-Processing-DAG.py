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
