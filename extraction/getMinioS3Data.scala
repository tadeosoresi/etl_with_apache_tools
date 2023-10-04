import org.apache.spark.sql.SparkSession

val s3MinioAccessKey = System.getenv("MINIO_ROOT_USER")
val s3MinioSecretKey = System.getenv("MINIO_ROOT_PASSWORD")
val s3MinioEndpoint = "http://172.103.0.16:9000"

val spark = SparkSession.builder().appName("S3MinioData").getOrCreate()
spark.sparkContext.hadoopConfiguration.set("fs.s3a.endpoint", s3MinioEndpoint)
spark.sparkContext.hadoopConfiguration.set("fs.s3a.access.key", s3MinioAccessKey)
spark.sparkContext.hadoopConfiguration.set("fs.s3a.secret.key", s3MinioSecretKey)
spark.sparkContext.hadoopConfiguration.set("spark.sql.debug.maxToStringFields", "100")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.path.style.access", "true")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.connection.ssl.enabled", "false")
spark.sparkContext.hadoopConfiguration.set("spark.hadoop.fs.defaultFS", "hdfs://172.103.0.17:9000/user/local-datalake")
spark.sparkContext.hadoopConfiguration.set("spark.sql.warehouse.dir", "hdfs://172.103.0.17:9000/user/local-datalake")

// Loading csv from Minio to DataFrame:
val sqlContext = new org.apache.spark.sql.SQLContext(sc)
val startTimeMillis = System.currentTimeMillis()

val s3MinioBucket: String = "movies-datalake"
val df = sqlContext.read.json("s3a://%s/movies.json".format(s3MinioBucket))
val new_df = df.withColumn("created_at", col("created_at").getItem("$date")) \
                .withColumn("release_date", col("release_date").getItem("$date"))
new_df.write.option("compression", "snappy").mode("overwrite").parquet("hdfs://172.103.0.17:9000/user/local-datalake/tmdb/movies.parquet")

val endTimeMillis = System.currentTimeMillis()
val durationMilliSeconds = (endTimeMillis - startTimeMillis)
print("Tiempo de Ejecucion:", durationMilliSeconds)
     
spark.stop()
System.exit(0)