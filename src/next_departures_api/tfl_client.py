
import logging
from enum import StrEnum

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

logger =  logging.getLogger(__name__)
TFL_BASE_URL = "https://api.tfl.gov.uk"

class TfLError(Exception):
    pass

class ModeName(StrEnum):
    tube = "tube"
    overground = "overground"

class Departure(BaseModel):
    line: str = Field(validation_alias="lineName") #lineName required
    destination: str = Field(validation_alias="destinationName") #destinationName required
    seconds_to_arrival: int = Field(validation_alias="timeToStation") #int required - lax mode but we should have a test to check whether json is int 
    mode: ModeName = Field(validation_alias="modeName")
    platform: str = Field(validation_alias="platformName", default='')#platformName optional

    model_config = ConfigDict(validate_by_name=True) 

class TflClient:
    def __init__(self, api_key: str, timeout: int) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.base_url: str = TFL_BASE_URL

    async def get_departures(self, station_id: str) -> list[Departure]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            try:
                response = await client.get(f'/StopPoint/{station_id}/Arrivals', params={'app_key': self.api_key}, timeout=self.timeout)
                response.raise_for_status()
            except httpx.HTTPError  as exc:
                raise TfLError(f'Exception happened for station: {station_id}') from exc
        departures: list[Departure] = []

        try:
            json_response: list[dict] = response.json()

        except ValueError as e:
            raise TfLError(f'invalid json for station: {station_id}') from e
        failures = 0
        for train in json_response:
            try:
                departure: Departure = Departure.model_validate(train)
            except ValidationError as e:
                logger.warning('One train skipped for %s due to %s',station_id, e) 
                failures += 1
                continue
            
            departures.append(departure)

        if not departures and failures>0:
            raise TfLError(f'All {failures} trains failed validation for station id {station_id}')

        return departures

