
from pyspark.sql import SparkSession, HiveContext
from pyspark.sql.functions import col, explode

spark = SparkSession.\
        builder.\
        appName("Hive_Data_To_HDFS") \
        .config("hive.metastore.uris", "thrift://172.103.0.9:9083") \
        .config("spark.sql.warehouse.dir", "/user/local-datalake/") \
        .config("spark.sql.parquet.writeLegacyFormat", "true") \
        .config("spark.sql.hive.convertMetastoreParquet", "false") \
        .config("spark.sql.parquet.mergeSchema", "true") \
        .enableHiveSupport() \
        .getOrCreate()

spark.sql("USE warehouse;")
df = spark.sql("SELECT id, title, media_type, original_language, `cast` FROM movies;")
df_exploded = df.select("id",
                     "title",
                     "media_type",
                     "original_language",
                     explode(col("cast")).alias("cast_exploded"))
df_exploded = df_exploded.withColumn("actor", col("cast_exploded").getItem("original_name"))
df_exploded = df_exploded.drop(col("cast_exploded")).dropDuplicates(['id', 'title', 'actor'])
df_exploded \
            .repartition(1) \
            .write.format("csv") \
            .mode("overwrite") \
            .option("sep", ",") \
            .option("header", "true") \
            .save("hdfs://172.103.0.17:9000/user/local-datalake/tmdb/movies_neo_graph.csv")
spark.stop()