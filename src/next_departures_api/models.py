from pydantic import BaseModel, Field, ConfigDict
from enum import StrEnum

class Board(BaseModel):
    departures: list[Departure] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

class ModeName(StrEnum):
    tube = "tube"
    overground = "overground"


class Station(BaseModel):
    mode: list[ModeName]= Field(validation_alias="modes")
    name: str
    id: str
    zone: int
    model_config = ConfigDict(validate_by_name=True) 

class Departure(BaseModel):
    line: str = Field(validation_alias="lineName") #lineName required
    destination: str = Field(validation_alias="destinationName") #destinationName required
    seconds_to_arrival: int = Field(validation_alias="timeToStation") #int required - lax mode but we should have a test to check whether json is int 
    mode: ModeName = Field(validation_alias="modeName")
    platform: str = Field(validation_alias="platformName", default='')#platformName optional

    model_config = ConfigDict(validate_by_name=True) 