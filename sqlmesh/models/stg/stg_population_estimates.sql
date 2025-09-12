MODEL (
  name stg.population_estimates,
  kind FULL
);

WITH dedupe AS (
  SELECT
    *,
    ROW_NUMBER() OVER(
      PARTITION BY geographic_area, year
      ORDER BY population DESC
    ) AS dupe_count
  FROM raw.population_estimates
)
SELECT
  geographic_area,
  year,
  population
FROM dedupe
WHERE dupe_count = 1;
