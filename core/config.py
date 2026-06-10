import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    db_url: str = os.getenv("DB_URL")  # type: ignore


settings = Config()
