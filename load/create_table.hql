CREATE DATABASE IF NOT EXISTS warehouse;
USE warehouse;
CREATE TABLE IF NOT EXISTS movies(
    
)
COMMENT 'Tabla que contiene peliculas'
STORED AS PARQUET
LOCATION '/user/local-datalake/tmdb/movies.parquet'