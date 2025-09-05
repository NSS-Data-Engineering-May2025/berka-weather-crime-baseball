{% set today = execution_time.strftime('%Y-%m-%d') %}

MODEL(
  name raw.detroit_weather,
  kind FULL,
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
FROM read_csv('s3://wcb/weather/detroit/{{ today }}/detroit_weather_report_ncei.csv', skip=1, header=True);
