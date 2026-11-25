import logging

from fastapi import FastAPI

from next_departures_api.config import settings
from next_departures_api.tfl_client import *

logging.basicConfig(
     format="{asctime} - {levelname} - {message}",
     style="{",
     datefmt="%Y-%m-%d %H:%M"
)

app = FastAPI()
env_settings = settings

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return health_check()

def health_check():
    return 'ok'

async def tfl_url(url: str | None = None):
    return url

# @app.get("/departures/{station_name}")
# async def get_departures(station_name):
#     tfl_client = TflClient(env_settings.api_key, 10)
#     station_list = await tfl_client.get_station_ids(station_name)
#     departures = []
#     for station in station_list:
#          departures.append(await tfl_client.get_departures(station.id))

#     return departures



