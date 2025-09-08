MODEL(
  name raw.historical_baseball_teams,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key "TEAM",
  ),
  columns (
    team VARCHAR,
    league VARCHAR,
    city VARCHAR,
    nickname VARCHAR,
    "first" INT,
    "last" INT
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
FROM read_csv('s3://wcb/baseball/historical/domain/teams.csv');
