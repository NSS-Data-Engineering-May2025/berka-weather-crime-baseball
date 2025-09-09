AUDIT (
  name assert_unique_values
);

WITH dupe_count AS (
  SELECT
    @unique_key,
    COUNT(@unique_key) as dupe_count
  FROM @this_model
  GROUP BY @unique_key
)
SELECT
  @unique_key
FROM dupe_count
WHERE dupe_count > 1;
