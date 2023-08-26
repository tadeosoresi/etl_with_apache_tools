import org.apache.spark.sql.SparkSession

val s3MinioAccessKey: Option[String] = sys.env.get("MINIO_ROOT_USER")
val s3MinioSecretKey: Option[String] = sys.env.get("MINIO_ROOT_PASSWORD")
print(s3MinioAccessKey, s3MinioSecretKey)
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
System.exit(0)