import pytest
from fake_client import FakeTflClient

from next_departures_api.models import Departure, ModeName
from next_departures_api.service import build_board


def departure(seconds: int, mode: ModeName = ModeName.tube) -> Departure:
    """A departure where only the fields the test cares about vary."""
    return Departure(
        line="Test line",
        destination="Somewhere",
        seconds_to_arrival=seconds,
        mode=mode,
    )


@pytest.fixture
def stop_ids() -> dict[ModeName, str]:
    return {ModeName.tube: "TUBE", ModeName.overground: "OG"}


@pytest.mark.asyncio
async def test_departures_are_sorted_across_modes(stop_ids):
    fake = FakeTflClient(
        {
            "TUBE": [departure(300), departure(30)],
            "OG": [departure(60, ModeName.overground)],
        }
    )

    board = await build_board(tfl_client=fake, stop_ids=stop_ids, within_minutes=60)

    assert [d.seconds_to_arrival for d in board.departures] == [30, 60, 300]
