import logging

import httpx
from pydantic import ValidationError

from next_departures_api.models import Departure

logger = logging.getLogger(__name__)
TFL_BASE_URL = "https://api.tfl.gov.uk"


class TfLError(Exception):
    pass


class TflClient:
    def __init__(self, api_key: str, timeout: int) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.base_url: str = TFL_BASE_URL

    # async def get_station_ids(self, station_name: str) -> list[Station]:
    # '''
    # Stations on the TfL network have the suffix Underground Station if they are on the tube network
    # and a Rail Station if they are on the Overground or National Rail network
    # '''
    # station_names = [f"{station_name} Underground Station", f"{station_name} Rail Station"]
    # station_ids = []
    # async with httpx.AsyncClient(base_url=self.base_url) as client:
    #     for name in station_names:
    #         try:
    #             response = await client.get(f"/StopPoint/Search", params={'query':name, 'app_key': self.api_key}, timeout=self.timeout)
    #             response.raise_for_status()
    #         except httpx.HTTPError  as exc:
    #             raise TfLError(f'Exception happened for station: {name}') from exc

    #         try:
    #             json_response: dict = response.json()
    #             print(json_response['matches'][0])

    #         except ValueError as e:
    #             raise TfLError(f'invalid json for station: {name}') from e
    #         failures = 0

    #         try:
    #             station: Station = Station.model_validate(json_response["matches"][0])
    #         except ValidationError as e:
    #             logger.warning('One station skipped for %s due to %s',name, e)
    #             failures += 1
    #             continue

    #         station_ids.append(station)

    #     return station_ids

    async def get_departures(self, station_id: str) -> list[Departure]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            try:
                response = await client.get(
                    f"/StopPoint/{station_id}/Arrivals",
                    params={"app_key": self.api_key},
                    timeout=self.timeout,
                )
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise TfLError(f"Exception happened for station: {station_id}") from exc

        departures: list[Departure] = []

        try:
            json_response: list[dict] = response.json()

        except ValueError as e:
            raise TfLError(f"invalid json for station: {station_id}") from e
        failures = 0
        for train in json_response:
            try:
                departure: Departure = Departure.model_validate(train)
            except ValidationError as e:
                logger.warning("One train skipped for %s due to %s", station_id, e)
                failures += 1
                continue

            departures.append(departure)

        if not departures and failures > 0:
            raise TfLError(
                f"All {failures} trains failed validation for station id {station_id}"
            )

        return departures
