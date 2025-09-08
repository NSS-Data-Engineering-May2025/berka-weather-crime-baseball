MODEL(
  name raw.historical_baseball_ballparks,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key "PARKID",
  ),
  columns (
    parkid VARCHAR,
    "name" VARCHAR,
    aka VARCHAR,
    city VARCHAR,
    "state" VARCHAR,
    "start" DATE,
    "end" DATE,
    league VARCHAR,
    notes VARCHAR
  ),
  allow_partials true,
  gateway duckdb
);

SET s3_region='us-east-1';
SET s3_access_key_id='miniouser';
SET s3_secret_access_key='miniopassword';
SET s3_endpoint='host.docker.internal:9000';
SET s3_url_style='path';
SET s3_use_ssl=false;

SELECT
  *
FROM read_csv('s3://wcb/baseball/historical/domain/ballparks.csv');
