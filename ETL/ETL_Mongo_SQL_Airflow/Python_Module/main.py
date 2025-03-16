from mongo_generator import MongoDataGenerator
from postgres_migrator import PostgresMigrator
from data_warehouse import DataWarehouseManager
import os
from dotenv import load_dotenv, find_dotenv


def main():
    """
    Тест компонентов вне Airflow.
    """
    load_dotenv(find_dotenv())

    mongo_generator = MongoDataGenerator(
        host=os.getenv('MONGO_HOST', '127.0.0.1'),
        port=int(os.getenv('MONGO_PORT', '27017')),
        db_name=os.getenv('MONGO_DB', 'etl_project'),
        user=os.getenv('MONGO_INITDB_ROOT_USERNAME', 'root'),
        password=os.getenv('MONGO_INITDB_ROOT_PASSWORD', 'example')
    )

    # Генерация данных в MongoDB
    collections = [
        'UserSessions', 'SupportTickets', 'ProductPriceHistory'
    ]

    for collection in collections:
        records_count = mongo_generator.generate_data(collection, num_records=1000)
        print(f"Generated {records_count} records in {collection}")

    # Инициализация мигратора PostgreSQL
    postgres_migrator = PostgresMigrator(
        host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
        port=int(os.getenv('POSTGRES_PORT', '5432')),
        dbname=os.getenv('POSTGRES_DB', 'migrate_data'),
        user=os.getenv('POSTGRES_USER', 'admin'),
        password=os.getenv('POSTGRES_PASSWORD', 'admin')
    )

    # Создание таблиц в PostgreSQL
    postgres_migrator.create_tables()

    # Генерация пользователей в PostgreSQL
    postgres_migrator.generate_users(num_users=1000)

    # Миграция данных из MongoDB в PostgreSQL
    for collection in collections:
        records_count = postgres_migrator.migrate_data(mongo_generator, collection)
        print(f"Migrated {records_count} records from {collection}")

    # Создание аналитических витрин
    data_warehouse = DataWarehouseManager(postgres_migrator)
    data_warehouse.create_user_activity_mart()
    data_warehouse.create_support_efficiency_mart()
    print("Data marts created successfully")


if __name__ == "__main__":
    main()
