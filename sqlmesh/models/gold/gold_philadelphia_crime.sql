MODEL (
  name gold.philadelphia_crime,
  kind FULL,
  gateway duckdb
);

WITH phil_pop AS (
    SELECT
        *
    FROM stg.population_estimates
    WHERE geographic_area ILIKE 'philadelphia city, pennsylvania'
),
default_pop AS (
    SELECT
        population as pop
    FROM stg.population_estimates
    WHERE geographic_area ILIKE 'philadelphia city, pennsylvania'
    ORDER BY year DESC
    LIMIT 1
),
phil_crime_agg AS (
    SELECT
        dispatch_date,
        dispatch_year,
        COALESCE(pop.population, def.pop) as population,
        COALESCE(pop.population, def.pop)/100000 as pop_100k,
        COUNT(incident_type) as total_incidents,
        SUM(CASE WHEN incident_type ILIKE '%homicide%'
                    OR incident_type ILIKE '%assault%'
                    OR incident_type ILIKE '%rape%'
                    OR incident_type ILIKE '%robber%'
                    THEN 1
                    ELSE 0 END) AS violent_crime,
        SUM(CASE WHEN incident_type ILIKE '%homicide%' THEN 1 ELSE 0 END) AS homicide,
        SUM(CASE WHEN incident_type ILIKE '%assault%' THEN 1 ELSE 0 END) AS assault,
        SUM(CASE WHEN incident_type ILIKE '%rape%' THEN 1 ELSE 0 END) AS rape,
        SUM(CASE WHEN incident_type ILIKE '%robber%' THEN 1 ELSE 0 END) AS robbery,
        SUM(CASE WHEN incident_type ILIKE '%theft%' THEN 1 ELSE 0 END) AS theft,
        SUM(CASE WHEN incident_type ILIKE '%burglar%' THEN 1 ELSE 0 END) AS burglary,
        SUM(CASE WHEN incident_type ILIKE '%arson%' THEN 1 ELSE 0 END) AS arson
    FROM stg.philadelphia_crime crime
    LEFT JOIN phil_pop pop
    ON crime.dispatch_year = pop.year
    LEFT JOIN default_pop def
    ON TRUE
    GROUP BY dispatch_date, dispatch_year, pop.population, def.pop
    ORDER BY dispatch_date
)
SELECT
    dispatch_date,
    total_incidents,
    ROUND(total_incidents/pop_100k, 3) AS total_incidents_per_100000,
    violent_crime,
    ROUND(violent_crime/pop_100k, 3) AS violent_crime_per_100000,
    homicide,
    ROUND(homicide/pop_100k, 3) AS homicide_per_100000,
    assault,
    ROUND(assault/pop_100k, 3) AS assault_per_100000,
    rape,
    ROUND(rape/pop_100k, 3) AS rape_per_100000,
    robbery,
    ROUND(robbery/pop_100k, 3) AS robbery_per_100000,
    theft,
    ROUND(theft/pop_100k, 3) AS theft_per_100000,
    burglary,
    ROUND(burglary/pop_100k, 3) AS burglary_per_100000,
    arson,
    ROUND(arson/pop_100k, 3) AS arson_per_100000
FROM phil_crime_agg;
