# JARS (wget)
https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar
https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.537/aws-java-sdk-bundle-1.12.537.jar
https://repo1.maven.org/maven2/net/java/dev/jets3t/jets3t/0.9.4/jets3t-0.9.4.jar
rm httplient-4.5.6.jar
https://repo1.maven.org/maven2/org/apache/httpcomponents/httpclient/4.5.14/httpclient-4.5.14.jar


# Instalación de apache hdfs provider
sudo apt-get update && apt-get install krb5-config gcc gssapi libkrb5-dev 
pip install hdfs[avro,dataframe]
pip install protobuf==3.20.1
pip install apache-airflow-providers-apache-hdfs==3.2.1