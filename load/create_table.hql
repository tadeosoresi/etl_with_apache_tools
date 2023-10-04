CREATE DATABASE IF NOT EXISTS warehouse;
USE warehouse;
CREATE TABLE IF NOT EXISTS movies(
    adult BOOLEAN,
    backdrop_path STRING,
    `cast`  ARRAY< 
                STRUCT  < 
                            know_for_department: STRING,
                            original_name: STRING
                        >
            >,
    crew    ARRAY<
                STRUCT  <
                            job: STRING,
                            original_name: STRING
                        >
            >,
    created_at DATE,
    genre_ids ARRAY<DOUBLE>,
    id DOUBLE,
    media_type STRING,
    original_language STRING,
    original_title STRING,
    overview STRING,
    popularity DOUBLE,
    poster_path STRING,
    release_date DATE,
    title STRING,
    video BOOLEAN,
    vote_average DOUBLE,
    vote_count DOUBLE

)
COMMENT 'Tabla de Hive que contiene peliculas de distintas fuentes'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS PARQUET
LOCATION '/user/local-datalake/tmdb/movies.parquet'
TBLPROPERTIES ("parquet.compression"="SNAPPY");

CREATE INDEX movies_general_index ON TABLE movies(created_at, media_type)
AS 'org.apache.hadoop.hive.ql.index.compact.CompactIndexHandler' WITH DEFERRED REBUILD;
