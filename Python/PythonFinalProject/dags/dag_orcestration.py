from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

dag = DAG(
    'data_replication_and_analytics_all_tables',
    default_args=default_args,
    description='Data replication and analytics using Spark and Airflow for all tables',
    schedule_interval='@daily',
)

replication_task = SparkSubmitOperator(
    task_id='replicate_all_tables',
    application='/path/to/replication_script.py',
    conn_id='spark_default',
    dag=dag,
)

analytics_task = SparkSubmitOperator(
    task_id='create_analytics_views',
    application='/path/to/analytics_script.py',
    conn_id='spark_default',
    dag=dag,
)

replication_task >> analytics_task
