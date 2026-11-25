import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query

from next_departures_api.config import Settings
from next_departures_api.models import ModeName
from next_departures_api.service import AllModesFailedError, Board, build_board
from next_departures_api.tfl_client import TflClient

logging.basicConfig(
    format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M"
)

app = FastAPI()


class HealthCheck:
    def __init__(self, pass_) -> None:
        self.pass_: bool = pass_

    def get_health(self):
        return {"status": "ok"}


health_check = HealthCheck(pass_=True)


@app.get("/health")
async def get_health():

    return health_check.get_health()


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]


def make_tfl_client(settings: Annotated[Settings, Depends(get_settings)]) -> TflClient:
    return TflClient(settings.api_key, settings.timeout)


def get_station_mapping(
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[ModeName, str]:
    return {
        ModeName(var_name.split("_")[0]): station_id
        for var_name, station_id in settings.model_dump().items()
        if "station_id" in var_name
    }


@app.get("/departures")
async def get_board(
    tfl_client: Annotated[TflClient, Depends(make_tfl_client)],
    station_mapping: Annotated[dict[ModeName, str], Depends(get_station_mapping)],
    mode: ModeName | None = None,
    within_minutes: Annotated[int, Query(ge=1, le=60)] = 15,
) -> Board:
    try:
        return await build_board(
            tfl_client=tfl_client,
            stop_ids=station_mapping,
            mode=mode,
            within_minutes=within_minutes,
        )
    except AllModesFailedError as exc:
        raise HTTPException(
            status_code=502,
            detail="TfL arrivals are unavailable for every requested mode",
        ) from exc
