from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
import os
from Docker_Files.Python_Module.mongo_generator import MongoDataGenerator
from Docker_Files.Python_Module.postgres_migrator import PostgresMigrator
from Docker_Files.Python_Module.data_warehouse import DataWarehouseManager


# Функции для создания соединений
def get_mongo_connection():
    """Создает и возвращает соединение с MongoDB"""
    return MongoDataGenerator(
        host=os.getenv('MONGO_HOST', '127.0.0.1'),
        port=int(os.getenv('MONGO_PORT', '27017')),
        db_name=os.getenv('MONGO_DB', 'etl_project'),
        user=os.getenv('MONGO_INITDB_ROOT_USERNAME', 'root'),
        password=os.getenv('MONGO_INITDB_ROOT_PASSWORD', 'example')
    )

def get_postgres_connection():
    """Создает и возвращает соединение с PostgreSQL"""
    return PostgresMigrator(
        host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
        port=int(os.getenv('POSTGRES_PORT', '5432')),
        dbname=os.getenv('POSTGRES_DB', 'migrate_data'),
        user=os.getenv('POSTGRES_USER', 'admin'),
        password=os.getenv('POSTGRES_PASSWORD', 'admin')
    )


# Определяем функции для задач Airflow
def generate_mongo_data(**kwargs):
    """Генерирует данные в MongoDB"""
    mongo_generator = get_mongo_connection()
    collections = ['UserSessions', 'SupportTickets', 'ProductPriceHistory']

    for collection in collections:
        records_count = mongo_generator.generate_data(collection, num_records=1000)
        print(f"Generated {records_count} records in {collection}")


def create_postgres_tables(**kwargs):
    """Создает таблицы в PostgreSQL"""
    postgres_migrator = get_postgres_connection()
    postgres_migrator.create_tables()
    print("PostgreSQL tables created successfully")


def generate_users(**kwargs):
    """Генерирует пользователей в PostgreSQL"""
    postgres_migrator = get_postgres_connection()
    num_users = postgres_migrator.generate_users(num_users=1000)
    print(f"Generated {num_users} users in PostgreSQL")


def migrate_collection(collection_name, **kwargs):
    """Мигрирует данные из MongoDB в PostgreSQL"""
    mongo_generator = get_mongo_connection()
    postgres_migrator = get_postgres_connection()
    records_count = postgres_migrator.migrate_data(mongo_generator, collection_name)
    print(f"Migrated {records_count} records from {collection_name}")


def create_user_activity_mart(**kwargs):
    """Создает витрину активности пользователей"""
    postgres_migrator = get_postgres_connection()
    data_warehouse = DataWarehouseManager(postgres_migrator)
    data_warehouse.create_user_activity_mart()
    print("User activity mart created successfully")


def create_support_efficiency_mart(**kwargs):
    """Создает витрину эффективности поддержки"""
    postgres_migrator = get_postgres_connection()
    data_warehouse = DataWarehouseManager(postgres_migrator)
    data_warehouse.create_support_efficiency_mart()
    print("Support efficiency mart created successfully")


def create_product_price_analytics_mart(**kwargs):
    """Создает витрину аналитики цен на продукты"""
    postgres_migrator = get_postgres_connection()
    data_warehouse = DataWarehouseManager(postgres_migrator)
    data_warehouse.create_product_price_analytics_mart()
    print("Product price analytics mart created successfully")


# Определяем аргументы по умолчанию
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Создаем DAG
dag = DAG(
    'etl_mongo_to_postgres',
    default_args=default_args,
    description='ETL pipeline from MongoDB to PostgreSQL',
    schedule_interval=timedelta(days=1),
    catchup=False
)

# Создаем задачи для ETL-процесса
start = DummyOperator(task_id='start_pipeline', dag=dag)
end = DummyOperator(task_id='end_pipeline', dag=dag)

generate_mongo_data_task = PythonOperator(
    task_id='generate_mongo_data',
    python_callable=generate_mongo_data,
    dag=dag,
)

create_postgres_tables_task = PythonOperator(
    task_id='create_postgres_tables',
    python_callable=create_postgres_tables,
    dag=dag,
)

generate_users_task = PythonOperator(
    task_id='generate_users',
    python_callable=generate_users,
    dag=dag,
)

# Создаем задачи для миграции данных
collections = ['UserSessions', 'SupportTickets', 'ProductPriceHistory']
migration_tasks = []

for collection in collections:
    task = PythonOperator(
        task_id=f'migrate_{collection.lower()}',
        python_callable=migrate_collection,
        op_kwargs={'collection_name': collection},
        dag=dag,
    )
    migration_tasks.append(task)

# Создаем задачи для создания аналитических витрин
create_user_activity_mart_task = PythonOperator(
    task_id='create_user_activity_mart',
    python_callable=create_user_activity_mart,
    dag=dag,
)

create_support_efficiency_mart_task = PythonOperator(
    task_id='create_support_efficiency_mart',
    python_callable=create_support_efficiency_mart,
    dag=dag,
)

create_product_price_analytics_mart_task = PythonOperator(
    task_id='create_product_price_analytics_mart',
    python_callable=create_product_price_analytics_mart,
    dag=dag,
)

# Определяем зависимости между задачами
start >> generate_mongo_data_task >> create_postgres_tables_task >> generate_users_task

for task in migration_tasks:
    generate_users_task >> task

for task in migration_tasks:
    task >> create_user_activity_mart_task
    task >> create_support_efficiency_mart_task
    task >> create_product_price_analytics_mart_task

[create_user_activity_mart_task, create_support_efficiency_mart_task, create_product_price_analytics_mart_task] >> end
