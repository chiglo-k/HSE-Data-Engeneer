import os
import requests
from pyspark.sql import SparkSession

def download_jdbc_driver(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

def replicate_all_tables():

    # Установка драйверов для баз данных

    postgres_jdbc_url = "https://jdbc.postgresql.org/download/postgresql-42.2.5.jar"
    mysql_jdbc_url = "https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-8.0.23.jar"

    # Создание абсолютных путей к файлу
    jdbc_dir = "jdbc_drivers"
    os.makedirs(jdbc_dir, exist_ok=True)
    postgres_jar_path = os.path.join(jdbc_dir, "postgresql.jar")
    mysql_jar_path = os.path.join(jdbc_dir, "mysql.jar")

    # Скачивание драйверов
    download_jdbc_driver(postgres_jdbc_url, postgres_jar_path)
    download_jdbc_driver(mysql_jdbc_url, mysql_jar_path)

    # Инициализация сессии
    spark = SparkSession.builder \
        .appName("Postgres to MySQL Replication") \
        .master("local") \
        .config("spark.jars", f"{postgres_jar_path},{mysql_jar_path}") \
        .getOrCreate()

    tables = ["albums", "artists", "customers",
              "employees", "genres", "invoices",
              "invoice_items", "media_types", "playlists",
              "playlist_track"]

    for table in tables:
        # Считывание из PostgreSQL
        postgres_df = spark.read \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://localhost:5433/postgres") \
            .option("dbtable", table) \
            .option("user", "airflow") \
            .option("password", "airflow") \
            .load()

        # Запись данных в MySQL
        postgres_df.write \
            .format("jdbc") \
            .option("url", "jdbc:mysql://localhost:3306/chinook_mysql") \
            .option("dbtable", table) \
            .option("user", "mysql") \
            .option("password", "admin") \
            .mode("overwrite") \
            .save()

    spark.stop()

if __name__ == "__main__":
    replicate_all_tables()
