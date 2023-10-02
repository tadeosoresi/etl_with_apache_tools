CREATE DATABASE IF NOT EXISTS warehouse;
USE warehouse;
CREATE TABLE IF NOT EXISTS movies(
    adult BOOLEAN,
    backdrop_path STRING,
    `cast` STRUCT< 
                    `cast`: ARRAY<STRUCT< 
                                            know_for_department: STRING,
                                            name: STRING,
                                            original_name: STRING,
                                            popularity: DOUBLE
                                        >
                        >
                    
                >,
    crew ARRAY<
                STRUCT<
                        adult: BOOLEAN,
                        credit_id: STRING,
                        department: STRING,
                        gender: DOUBLE,
                        id: DOUBLE,
                        job: STRING,
                        know_for_department: STRING,
                        name: STRING,
                        original_name: STRING,
                        popularity: DOUBLE,
                        profile_path: STRING
                    >
            >,
    created_at STRING,
    genre_ids ARRAY<DOUBLE>,
    id DOUBLE,
    media_type STRING,
    original_language STRING,
    original_title STRING,
    overview STRING,
    popularity DOUBLE,
    poster_path STRING,
    release_date STRING,
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
