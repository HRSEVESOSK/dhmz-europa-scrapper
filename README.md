# dhmz-europa-scrapper
## Create DB
- sudo -u postgres createuser meteoeuuser
- sudo -u postgres createdb meteoeudb
- psql=# alter user meteoeuuser with encrypted password 'meteoeupwd';

## Add postgis extension
- sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" meteoeudb

## Create table
- from db/createDB.sql

## Test
- python scrapper.py > logs/$(date +%Y-%m-%dT%H-%M-%S).log

## Setup cronjob
- run_scrapper.sh