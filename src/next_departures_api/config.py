from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    api_key: str = Field(default="", alias="next_departure_KEY")
    overground_station_id: str
    tube_station_id: str
    timeout: int
