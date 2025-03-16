from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
from mongo_generator import MongoDataGenerator
from postgres_migrator import PostgresMigrator
from data_warehouse import DataWarehouseManager


class AirflowETLManager:
    def __init__(self, mongo_host='127.0.0.1', mongo_port=27017, mongo_db='etl_project',
                 mongo_user='root', mongo_password='example',
                 postgres_host='db', postgres_port=5432, postgres_db='migrate_data',
                 postgres_user='admin', postgres_password='admin'):

        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        self.mongo_user = mongo_user
        self.mongo_password = mongo_password

        self.postgres_host = postgres_host
        self.postgres_port = postgres_port
        self.postgres_db = postgres_db
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password

        self.mongo_generator = None
        self.postgres_migrator = None

        self.dag = self._create_dag()

    def _create_mongo_generator(self):
        """Creates MongoDB connection if it doesn't exist"""
        if not self.mongo_generator:
            self.mongo_generator = MongoDataGenerator(
                host=self.mongo_host,
                port=self.mongo_port,
                db_name=self.mongo_db,
                user=self.mongo_user,
                password=self.mongo_password
            )
        return self.mongo_generator

    def _create_postgres_migrator(self):
        """Creates PostgreSQL connection if it doesn't exist"""
        if not self.postgres_migrator:
            self.postgres_migrator = PostgresMigrator(
                host=self.postgres_host,
                port=self.postgres_port,
                dbname=self.postgres_db,
                user=self.postgres_user,
                password=self.postgres_password
            )
        return self.postgres_migrator

    def _create_dag(self):
        """Создает DAG для ETL-процесса"""
        default_args = {
            'owner': 'airflow',
            'depends_on_past': False,
            'start_date': datetime(2023, 1, 1),
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        }

        dag = DAG(
            'mongo_to_postgres_etl',
            default_args=default_args,
            description='ETL pipeline from MongoDB to PostgreSQL',
            schedule_interval=timedelta(days=1),
            catchup=False
        )

        # Создаем задачи для DAG
        self._create_tasks(dag)

        return dag

    def _create_tasks(self, dag):
        """Создает задачи для DAG"""
        # Начальная и конечная задачи
        start = DummyOperator(
            task_id='start_pipeline',
            dag=dag
        )

        end = DummyOperator(
            task_id='end_pipeline',
            dag=dag
        )

        # Задача для генерации данных в MongoDB
        generate_mongo_data = PythonOperator(
            task_id='generate_mongo_data',
            python_callable=self.generate_mongo_data,
            dag=dag,
        )

        # Задача для создания таблиц в PostgreSQL
        create_postgres_tables = PythonOperator(
            task_id='create_postgres_tables',
            python_callable=self.create_postgres_tables,
            dag=dag,
        )

        # Задача для генерации пользователей в PostgreSQL
        generate_users = PythonOperator(
            task_id='generate_users',
            python_callable=self.generate_users,
            dag=dag,
        )

        # Задачи для миграции данных из MongoDB в PostgreSQL
        collections = ['UserSessions', 'SupportTickets', 'ProductPriceHistory']

        migration_tasks = []
        for collection in collections:
            task = PythonOperator(
                task_id=f'migrate_{collection.lower()}',
                python_callable=self.migrate_collection,
                op_kwargs={'collection_name': collection},
                dag=dag,
            )
            migration_tasks.append(task)

        # Задачи для создания аналитических витрин
        create_user_activity_mart = PythonOperator(
            task_id='create_user_activity_mart',
            python_callable=self.create_user_activity_mart,
            dag=dag,
        )

        create_support_efficiency_mart = PythonOperator(
            task_id='create_support_efficiency_mart',
            python_callable=self.create_support_efficiency_mart,
            dag=dag,
        )

        create_product_price_analytics_mart = PythonOperator(
            task_id='create_product_price_analytics_mart',
            python_callable=self.create_product_price_analytics_mart,
            dag=dag,
        )

        # Определение зависимостей между задачами
        start >> generate_mongo_data >> create_postgres_tables >> generate_users

        for task in migration_tasks:
            generate_users >> task

        for task in migration_tasks:
            task >> create_user_activity_mart
            task >> create_support_efficiency_mart
            task >> create_product_price_analytics_mart

        [create_user_activity_mart, create_support_efficiency_mart, create_product_price_analytics_mart] >> end

    def generate_mongo_data(self, **kwargs):
        """Генерирует данные в MongoDB"""
        try:
            mongo_generator = self._create_mongo_generator()
            collections = ['UserSessions', 'SupportTickets', 'ProductPriceHistory']

            for collection in collections:
                records_count = mongo_generator.generate_data(collection, num_records=1000)
                print(f"Generated {records_count} records in {collection}")

            return "MongoDB data generation completed successfully"
        except Exception as e:
            print(f"Error generating MongoDB data: {e}")
            raise

    def create_postgres_tables(self, **kwargs):
        """Создает таблицы в PostgreSQL"""
        try:
            postgres_migrator = self._create_postgres_migrator()
            postgres_migrator.create_tables()
            print("PostgreSQL tables created successfully")

            return "PostgreSQL tables creation completed successfully"
        except Exception as e:
            print(f"Error creating PostgreSQL tables: {e}")
            raise

    def generate_users(self, **kwargs):
        """Генерирует пользователей в PostgreSQL"""
        try:
            postgres_migrator = self._create_postgres_migrator()
            num_users = postgres_migrator.generate_users(num_users=1000)
            print(f"Generated {num_users} users in PostgreSQL")

            return f"Generated {num_users} users in PostgreSQL"
        except Exception as e:
            print(f"Error generating users: {e}")
            raise

    def migrate_collection(self, collection_name, **kwargs):
        """Мигрирует данные из MongoDB в PostgreSQL"""
        try:
            mongo_generator = self._create_mongo_generator()
            postgres_migrator = self._create_postgres_migrator()

            records_count = postgres_migrator.migrate_data(mongo_generator, collection_name)
            print(f"Migrated {records_count} records from {collection_name}")

            return f"Migrated {records_count} records from {collection_name}"
        except Exception as e:
            print(f"Error migrating {collection_name}: {e}")
            raise

    def create_user_activity_mart(self, **kwargs):
        """Создает витрину активности пользователей"""
        try:
            postgres_migrator = self._create_postgres_migrator()
            data_warehouse = DataWarehouseManager(postgres_migrator)
            data_warehouse.create_user_activity_mart()
            print("User activity mart created successfully")

            return "User activity mart created successfully"
        except Exception as e:
            print(f"Error creating user activity mart: {e}")
            raise

    def create_support_efficiency_mart(self, **kwargs):
        """Создает витрину эффективности поддержки"""
        try:
            postgres_migrator = self._create_postgres_migrator()
            data_warehouse = DataWarehouseManager(postgres_migrator)
            data_warehouse.create_support_efficiency_mart()
            print("Support efficiency mart created successfully")

            return "Support efficiency mart created successfully"
        except Exception as e:
            print(f"Error creating support efficiency mart: {e}")
            raise

    def create_product_price_analytics_mart(self, **kwargs):
        """Создает витрину аналитики цен на продукты"""
        try:
            postgres_migrator = self._create_postgres_migrator()
            data_warehouse = DataWarehouseManager(postgres_migrator)
            data_warehouse.create_product_price_analytics_mart()
            print("Product price analytics mart created successfully")

            return "Product price analytics mart created successfully"
        except Exception as e:
            print(f"Error creating product price analytics mart: {e}")
            raise

    def get_dag(self):
        """Возвращает созданный DAG"""
        return self.dag
