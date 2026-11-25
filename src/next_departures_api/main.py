from fastapi import FastAPI, Depends
from enum import StrEnum
from pydantic import BaseModel, Field
import httpx
from typing import Annotated
from .config import settings
from .tfl_client import *
import logging
logging.basicConfig(
     format="{asctime} - {levelname} - {message}",
     style="{",
     datefmt="%Y-%m-%d %H:%M"
)

app = FastAPI()
env_settings = settings

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return health_check()

def health_check():
    return 'ok'

async def tfl_url(url: str | None = None):
    return url

@app.get("/departures")
async def get_departures():
    tfl_client = TflClient(env_settings.api_key, 10)
    return await tfl_client.get_departures('910GBLCHSRD')



