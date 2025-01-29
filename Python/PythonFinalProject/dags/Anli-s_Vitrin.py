from pyspark.sql import SparkSession
from pyspark.sql.functions import count

def create_analytics_views():
    spark = SparkSession.builder \
        .appName("Analytics Views Creation") \
        .getOrCreate()

    # Cчитывание данных из MySQL
    albums_df = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:mysql://localhost:5433/chinook_mysql") \
        .option("dbtable", "albums") \
        .option("user", "mysql") \
        .option("password", "admin") \
        .load()

    # Первая витрина
    analytics_view = albums_df.groupBy("title").agg(count("*").alias("album_count"))

    # Сохранение витрины
    analytics_view.write \
        .format("jdbc") \
        .option("url", "jdbc:mysql://localhost:3306/chinook_mysql") \
        .option("dbtable", "popular_albums") \
        .option("user", "mysql") \
        .option("password", "admin") \
        .mode("overwrite") \
        .save()

    tracks_df = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:mysql://localhost:5433/chinook_mysql") \
        .option("dbtable", "tracks") \
        .option("user", "mysql") \
        .option("password", "admin") \
        .load()

    # Вторая витрина
    tracks_analytics_view = tracks_df.groupBy("album_id").agg(count("*").alias("track_count"))

    # Сохранение витрины
    tracks_analytics_view.write \
        .format("jdbc") \
        .option("url", "jdbc:mysql://localhost:3306/chinook_mysql") \
        .option("dbtable", "album_track_counts") \
        .option("user", "mysql") \
        .option("password", "admin") \
        .mode("overwrite") \
        .save()

    spark.stop()

if __name__ == "__main__":
    create_analytics_views()
