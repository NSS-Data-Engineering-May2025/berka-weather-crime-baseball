# Weather x Crime x Baseball (2000-Present): Trend Analysis Data Pipeline
This project combines basic weather, crime, and baseball statistics from the 21st century to examine possible correlations that may exist between the three, such as linking a ballclub’s performance to positive and negative trends in crime (both day-to-day and year-over-year) or how teams accustomed to certain climates may be affected on the road. The included cities (Detroit, Philadelphia) have long-established baseball teams (Tigers – 1901, Phillies – 1883) with open-air stadiums and 21st Century World Series appearances. For at least the last 50 years, they have been single club cities (no New York, Chicago, LA, or San Fran/Oakland) to avoid the effects of split fanbases.
## Tech
- Python
- Docker
- MinIO S3 compatible
- SQLMesh (DuckDB)
## Data Sources
### Weather
#### National Centers for Environmental Information (NCEI)
 - [Detroit, MI (Detroit City Airport - KDET)](https://www.ncei.noaa.gov/access/past-weather/USW00014822/data.csv) (CSV file)
 - [Philadelphia, PA (Philadelphia International Airport - KPHL)](https://www.ncei.noaa.gov/access/past-weather/USW00013739/data.csv) (CSV file)
#### METAR (aviationweather.gov API)
 - Detroit ([KDET](https://aviationweather.gov/api/data/metar?ids=KDET&format=json)) (JSON/daily)
 - Philadelphia ([KPHL](https://aviationweather.gov/api/data/metar?ids=KPHL&format=json)) (JSON/daily)
 ### Crime
 - [Detroit, MI (2017 - Present)](https://data.detroitmi.gov/maps/rms-crime-incidents) (Manual CSV seed file & JSON of daily deltas from API)
 - [Philadelphia, PA (2006 - Present)](https://opendataphilly.org/datasets/crime-incidents/) (JSON/year from API)
 #### Population (For per 100,000 statistics)
 - US Census Bureau Population and Housing Unit Estimates: [2000-2009](https://www.census.gov/data/datasets/time-series/demo/popest/intercensal-2000-2010-cities-and-towns.html), [2010-2019](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-total-cities-and-towns.html), [2020-2024](https://www.census.gov/data/datasets/time-series/demo/popest/2020s-total-cities-and-towns.html) (Manual CSV download)
 ### Baseball
 - [Retrosheet - Historical](https://www.retrosheet.org/gamelogs/index.html) (CSV/year and teams domain table)
 - [MLB API - Current](https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2025&gameType=R) (JSON from API for entire current season)
## Required .env Fields
In order to run properly, a .env file must be created with the following fields defined:
 - MINIO_URL
 - MINIO_ACCESS_KEY
 - MINIO_SECRET_KEY
 - MINIO_BUCKET_NAME
 - DETROIT_CRIME_INGESTION_DELAY
## Developer
Alex Berka
## Last Updated
Sept 8, 2025
