import logging

from fastapi import FastAPI, Depends
from typing import Annotated

from next_departures_api.config import Settings
from next_departures_api.tfl_client import TflClient
from next_departures_api.models import ModeName
from next_departures_api.service import build_board

from functools import lru_cache


logging.basicConfig(
     format="{asctime} - {levelname} - {message}",
     style="{",
     datefmt="%Y-%m-%d %H:%M"
)

app = FastAPI()

class HealthCheck():
    def __init__(self, pass_) -> None:
        self.pass_: bool = pass_

    def get_health(self):
        return self.pass_

health_check = HealthCheck(pass_=True)

@app.get("/health")
async def get_health():

    return health_check.get_health()


async def tfl_url(url: str | None = None):
    return url

@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]

def make_tfl_client(settings: Annotated[Settings, Depends(get_settings)]) -> TflClient:
    return TflClient(settings.api_key, settings.timeout)

def get_station_mapping(settings: Annotated[Settings, Depends(get_settings)]) -> dict[ModeName, str]:
    return {ModeName(var_name.split('_')[0]): station_id for var_name, station_id in settings.model_dump().items() if 'station_id' in var_name}

@app.get("/departures")
async def get_board(tfl_client: Annotated[TflClient, Depends(make_tfl_client)], station_mapping: Annotated[dict[ModeName, str], Depends(get_station_mapping)], mode: ModeName | None = None, within_minutes: int = 15):
    return await build_board(tfl_client=tfl_client, stop_ids=station_mapping, mode=mode, within_minutes=within_minutes)

