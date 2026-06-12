from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class AuthJWT(BaseModel):
    private_key_path: str = BASE_DIR / "certs" / "jwt-private_key.pem"
    public_key_path: str = BASE_DIR / "certs" / "jwt-public_key.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15


class Config(BaseSettings):
    db_url: str
    db_echo: bool = True
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    auth_jwt: AuthJWT = AuthJWT()


settings = Config()
