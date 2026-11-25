from next_departures_api.models import Departure

class FakeTflClient:
    def __init__(self, responses: dict[str, list[Departure] | Exception]) -> None:
        # stop ID -> what to "return": a list of departures, or an exception to raise
        self.responses = responses
        # every stop ID the service asked for, in order (useful for tests later)
        self.calls: list[str] = []

    async def get_departures(self, station_id: str) -> list[Departure]:
        self.calls.append(station_id)
        result = self.responses[station_id]
        if isinstance(result, Exception):
            raise result
        return result


#     fake = FakeTflClient({
#     "TUBE": [Departure(line="Victoria", destination="Brixton",
#                        seconds_to_arrival=240, mode=ModeName.tube)],
#     "OG": TfLError("timeout"),
# })
