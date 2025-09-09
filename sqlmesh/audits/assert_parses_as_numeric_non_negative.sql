AUDIT (
  name assert_parses_as_numeric_non_negative,
  dialect duckdb
);

SELECT *
FROM (
  SELECT
    @EACH(
      @columns,
      c -> TRY_CAST(c AS NUMERIC) as number_@c
    )
  FROM @this_model
)
WHERE @REDUCE(
  @EACH(
    @columns,
    c -> number_@c < 0 OR number_@c IS NULL
  ),
  (l, r) -> l OR r
);
