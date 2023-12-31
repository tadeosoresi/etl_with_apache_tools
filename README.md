# Complete ETL with apache tools

## Descripción
Proyecto donde se simula un ETL con diversas tecnologias, con las cuales podemos extraer datos de diversas fuentes y llevar a diversos destinos.
La idea es "simular" a menor escala y sin un fin especifico, procesos y pipelines orquestados con Apache Airflow. 
El flujo del ETL es el siguiente:<br><br>
    - **Obtención de datos via API de TMDB (scrapper en Python)**<br>
    - **Almacenamiento en MongoDB**<br>
    - **Upload de los datos a AWS S3 (Minio)**<br>
    - **Extracción de dichos datos desde el S3 a HDFS local via Spark**<br>
    - **Creación y carga de los datos en el Data Warehouse (Hive)**<br>
    - **Creación de grafos via Neo4J**
    
Todo este proceso esta apoyado con multiples Sensors de Airflow, para crear los directorios en HDFS, Minio y también detectar cuando
los datos estan disponibles en cierta fuente

## Fuentes de Datos
Este proyecto utiliza varias fuentes de datos para extraer información sobre peliculas:

- **TMDB API**
- **MongoDB**
- **Minio S3**
- **HDFS**
- **Hive**

## Lenguajes de Programación utilizados
- **Python**
- **Scala**

## Tecnologias para el despliegue
- **Docker**
- **Shell scripting**

## Orquestadores
- **Airflow**


## Despliegue del repositorio ##
1. Crear una cuenta en TMDB la cual proveera el token para la API
2. Obtener dicho token y agregarlo a la variable TMDB_API_TOKEN en el archivo environment_variables.sh
    modificar aquellos variables con valores a elección del desarrollador (esto no es obligatorio)
3. Cargar dichas variables en la sesion de Ubuntu (puede ser WSL2) -> source environment_variables.sh
4. Modificar archivo .env con valores a elección del dev (opcional)
5. Instalar paquetes necesarios para Airflow HDFS Provider -> sudo apt-get update && apt-get install krb5-config gcc libkrb5-dev
6. Ejecutar en super user mood airflow_and_docker_setup.sh -> sudo sh airflow_and_docker_setup.sh
7. Esperar que el ambiente se despliegue, se levanten los contenedores y se instale Airflow en el environment
8. Activar environment: source airflow_env/bin/activate y desplegar Airflow:

       8.1. Primero, hacer un "echo $AIRFLOW_HOME", la salida por consola debe ser el directorio del repo.

       8.2. airflow db init

       8.3. airflow users create --firstname xxxx --lastname xxx --role Admin --username xxx --password xxx --email xxx@xxx.com

       8.4 airflow standalone (esto levantara el webserver en localhost puerto 8877, tambien el scheduler) 

9.  Ir al Airflow Webserver (UI): ingresar al navegador -> locahost:8877
10. Setear conexiones y descargar JAR's (al final del README), ejecutar DAG (Play) y validar que las tasks corran sin excepciones:
    
    10.1 Entrando al contenedor de MongoDB, validando la coleccion movies

    10.2 Visitando Minio en el navegador: localhost:9000 -> Ingresar usuario y clave contenidas en el archivo .env -> Validar JSON file subido
    
    10.3 Validar datos en HIVE:

            10.3.1 docker exec -it hive-server bash

            10.3.2 hive

            10.3.3 SHOW DATABASES; (validar la db warehouse)

            10.3.4 USE warehouse;

            10.3.5 SHOW TABLES; (validar la tabla movies)

            10.3.6 SELECT * FROM movies;


## JARS ###
Es necesario descargar ciertos JAR's para que Spark funcione correctamente, los siguientes jars se descargan en la carpeta
/spark/jars/ del contenedor spark-master:

    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.537/aws-java-sdk-bundle-1.12.537.jar
    wget https://repo1.maven.org/maven2/net/java/dev/jets3t/jets3t/0.9.4/jets3t-0.9.4.jar
    rm httpclient-4.5.6.jar
    wget https://repo1.maven.org/maven2/org/apache/httpcomponents/httpclient/4.5.14/httpclient-4.5.14.jar

## Conexiones de Airflow ###
Para la ejecucion de distintos Operators/Sensors/Hooks en Airflow, es necesario que seteemos las siguientes conexiones
desde la pestaña Admin -> Connections -> + (add connection):

1. **MongoDB del contenedor:**<br>
        ConnectionId: mongo_etl_id<br>
        Type: MongoDB<br>
        Host: 127.0.0.1<br>
        Port: 27018

2. **AWS S3 (Minio):**<br>
        ConnectionId: aws_etl_id<br>
        Type: Amazon Web Services<br>
        AWS Access Key ID: variable MINIO_ROOT_USER del .env<br>
        AWS Secret Access Key ID: variable MINIO_ROOT_PASSWORD del .env<br>
        Extra: {"host": "http://127.0.0.1:9000"}

3. **HDFS:**<br>
        ConnectionId: hdfs_conn_id<br>
        Type: HDFS<br>
        Host: 127.0.0.1<br>
        Login: root<br>
        Port: 9890

4. **Hive Metastore:**<br>
        ConnectionId: hive_etl_id<br>
        Type: Hive Metastore Thrift<br>
        Host: 127.0.0.1<br>
        Login: hive<br>
        Password: hive<br>
        Port: 9083

### Una vez que seteemos esto, podremos ejecutar el DAG. ###
Al finalizarlo deberemos ver una carpeta llamada ./data en la raiz del repositorio, en caso de no verla:
    
    sudo chmod 777 ./data/ para poder visualizarla ya que se comparte desde el contenedor de spark a host.

En caso de que no este disponible, crear la carpeta manualmente:

    mkdir data
    sudo docker cp spark-master:/data/movies_neo_graph/ ./data/
    docker-compose up -d

Nuestro csv ya estara disponible en la carpeta import del contenedor de Neo4j, ya podremos realizar grafos:<br>
    1. Ir a localhost:7474<br>
    2. Conectar al servidor con el username neo4j y password zeppelin<br>
    3. Ejecutar el codigo del archivo isualization/neo4j/movies_query.cypher<br>
    4. Experimentar nuevas queries
