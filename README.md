# Weather x Crime x Baseball: Trend Analysis Data Pipeline
This project combines basic weather, crime, and baseball statistics from the 21st century to examine possible correlations that may exist between the three, such as linking a ballclub’s performance to positive and negative trends in crime (both day-to-day and year-over-year) or how teams accustomed to certain climates may be affected on the road. The included cities (Detroit, Philadelphia) have long-established baseball teams (Tigers – 1901, Phillies – 1883) with 21st Century World Series appearances. For at least the last 50 years, they have been single club cities (no New York, Chicago, LA, or San Fran/Oakland) to avoid the effects of split fanbases.
## Data Sources
### Weather
#### NCEI
 - [Detroit, MI (Detroit City Airport)](https://www.ncei.noaa.gov/access/past-weather/USW00014822/data.csv)
 - [Philadelphia, PA (Philadelphia International Airport)](https://www.ncei.noaa.gov/access/past-weather/USW00013739/data.csv)
#### METAR (aviationweather.gov)
 - Detroit ([KDET](https://aviationweather.gov/api/data/metar?ids=KDET&format=json))
 - Philadelphia ([KPHL](https://aviationweather.gov/api/data/metar?ids=KPHL&format=json))
 ### Crime
 - [Detroit, MI](https://data.detroitmi.gov/maps/rms-crime-incidents)
 - [Philadelphia, PA](https://opendataphilly.org/datasets/crime-incidents/)
 ### Baseball
 - [Historical](https://www.retrosheet.org/gamelogs/index.html)
 - [Current](https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2025&gameType=R)
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
