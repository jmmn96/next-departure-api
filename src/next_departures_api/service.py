from asyncio import gather

from next_departures_api.models import Board, Departure, ModeName
from next_departures_api.tfl_client import TflClient, TfLError


class AllModesFailedError(Exception):
    pass


async def build_board(
    tfl_client: TflClient,
    stop_ids: dict[ModeName, str],
    within_minutes: int,
    mode: ModeName | None = None,
) -> Board:
    selected_departures = {
        mode_name: tfl_client.get_departures(station_id)
        for mode_name, station_id in stop_ids.items()
        if mode_name == mode or mode is None
    }
    if not selected_departures:
        raise KeyError(f"No station is available for selected mode: {mode}")
    results: list[list[Departure] | BaseException] = await gather(
        *selected_departures.values(), return_exceptions=True
    )
    failures: int = 0
    board: Board = Board()

    for mode_name, response in zip(selected_departures.keys(), results):
        if isinstance(response, TfLError):
            failures += 1
            board.warnings.append(f"Failed to gather departures for {mode_name} mode")
        elif isinstance(response, BaseException):
            raise response
        else:
            board.departures.extend(response)

    if failures == len(selected_departures):
        raise AllModesFailedError(f"All {failures} modes failed")

    within_minutes_sec: int = 60 * within_minutes
    board.departures = [
        departure
        for departure in board.departures
        if departure.seconds_to_arrival <= within_minutes_sec
    ]

    board.departures.sort(key=lambda departure: departure.seconds_to_arrival)

    return board
