from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15


class Config(BaseSettings):
    db_url: str = Field(...)
    db_echo: bool = True
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    auth_jwt: AuthJWT = AuthJWT()


settings = Config()
