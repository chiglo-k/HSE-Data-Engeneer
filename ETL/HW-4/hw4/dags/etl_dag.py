from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
import random

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 5),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def generate_data():
    from airflow.hooks.postgres_hook import PostgresHook
    hook = PostgresHook(postgres_conn_id='postgres_default')
    hook.run("""
        INSERT INTO source_table (id, name, value, updated_at)
        VALUES (generate_series(1, 100), 
                md5(random()::text), 
                random() * 100, 
                NOW() - INTERVAL '1 day' * floor(random() * 10));
    """)

with DAG(
    'etl_data_pipeline',
    default_args=default_args,
    description='ETL pipeline for incremental data loading',
    schedule_interval='@daily',
    catchup=False,
    template_searchpath='/include/sql',
    tags=['etl', 'data_pipeline'],
) as dag:
    
    generate_data_task = PythonOperator(
        task_id='generate_data',
        python_callable=generate_data
    )
    
    incremental_load = PostgresOperator(
        task_id='incremental_load',
        postgres_conn_id='postgres_default',
        sql="""
            INSERT INTO target_table (id, name, value, updated_at)
            SELECT id, name, value, updated_at FROM source_table
            WHERE updated_at >= '{{ ds }}' - INTERVAL '3 days'
            ON CONFLICT (id) DO UPDATE 
            SET name = EXCLUDED.name, 
                value = EXCLUDED.value, 
                updated_at = EXCLUDED.updated_at;
        """,
    )

    generate_data_task >> incremental_load

