# Weather x Crime x Baseball: Trend Analysis Data Pipeline
### Data Sources
#### Weather
##### NCEI
 - [Detroit, MI (Detroit City Airport)](https://www.ncei.noaa.gov/access/past-weather/USW00014822/data.csv)
 - [St. Louis, MO (KCPS)](https://www.ncei.noaa.gov/access/past-weather/USW00003960/data.csv)
 - [Atlanta, GA]
 - [Philadelphia, PA (Philadelphia International Airport)](https://www.ncei.noaa.gov/access/past-weather/USW00013739/data.csv)
 #### Crime
 - [Detroit, MI]
 - [St. Louis, MO]
 - [Atlanta, GA]
 - [Philadelphia, PA](https://opendataphilly.org/datasets/crime-incidents/)
 #### Baseball
 - [Historical](https://www.retrosheet.org/gamelogs/index.html)
 - [Current](https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2025&gameType=R)
### Required .env Fields
In order to run properly, a .env file must be created with the following fields defined:
 - MINIO_URL
 - MINIO_ACCESS_KEY
 - MINIO_SECRET_KEY
 - MINIO_BUCKET_NAME
### Developer
Alex Berka
### Last Updated
Sept 3, 2025
