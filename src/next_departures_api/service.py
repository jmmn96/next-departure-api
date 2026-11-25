from pydantic import BaseModel, Field
from .tfl_client import Departure


class Board(BaseModel):
    departures: list[Departure] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

def create_
