import org.apache.spark.sql.SparkSession
System.setProperty(SDKGlobalConfiguration.DISABLE_CERT_CHECKING_SYSTEM_PROPERTY, "true")

val s3MinioAccessKey = sys.env.get("MINIO_ROOT_USER")
val s3MinioSecretKey = sys.env.get("MINIO_ROOT_PASSWORD")
val s3MinioEndpoint: String = "172.103.0.16:9000"

val spark = SparkSession.builder().appName("S3MinioData").getOrCreate()
spark.sparkContext.hadoopConfiguration.set("fs.s3a.endpoint", s3MinioEndpoint)
spark.sparkContext.hadoopConfiguration.set("fs.s3a.access.key", s3MinioAccessKey)
spark.sparkContext.hadoopConfiguration.set("fs.s3a.secret.key", s3MinioSecretKey)
spark.sparkContext.hadoopConfiguration.set("spark.sql.debug.maxToStringFields", "100")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.path.style.access", "true")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.connection.ssl.enabled", "true")

// Loading csv from Minio to DataFrame:
val sqlContext = new org.apache.spark.sql.SQLContext(sc)
val startTimeMillis = System.currentTimeMillis()

val s3MinioBucket: String = "movies-datalake"
val df = sqlContext.read.json("s3a://%s/movies.json".format(s3MinioBucket))
df.show()

val endTimeMillis = System.currentTimeMillis()
val durationMilliSeconds = (endTimeMillis - startTimeMillis)
print("Tiempo de Ejecucion:", durationMilliSeconds)
     
spark.stop()
"""
df.write.option("compression", "snappy").mode("overwrite").parquet(
                "hdfs://172.100.0.5:8020/user/bbdataengineer/bbdata/%s/latest.parquet".format(lower_dir))
"""
System.exit(0)