from datetime import datetime, timedelta
import jwt
from core.config import settings
import bcrypt


class AuthHandler:
    private_key = settings.auth_jwt.private_key_path.read_text()
    algorithm = settings.auth_jwt.algorithm
    expire_minutes = settings.auth_jwt.access_token_expire_minutes
    public_key = settings.auth_jwt.public_key_path.read_text()

    async def encode_jwt(
        self,
        payload: dict,
        expire_timedelta: timedelta | None = None,
    ) -> str:

        to_encode = payload.copy()
        now = datetime.now(datetime.timezone.utc)
        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(minutes=self.expire_minutes)
        to_encode.update(exp=expire, iat=now)
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    async def decode_jwt(
        self,
        token: str | bytes,
    ) -> dict:

        return jwt.decode(token, self.public_key, algorithms=[self.algorithm])

    @staticmethod
    def hash_password(password: str) -> bytes:
        salt = bcrypt.gensalt()
        pwd_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed

    async def validate_password(self, password: str, hashed: bytes) -> bool:

        pwd_bytes = password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed)
