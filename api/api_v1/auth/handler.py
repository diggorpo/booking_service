import uuid
from datetime import datetime, timedelta, timezone
import jwt
from core.config import settings
import bcrypt

from .named_tuples import CreateTokenTuple


class AuthHandler:
    private_key = settings.auth_jwt.private_key_path.read_text()
    algorithm = settings.auth_jwt.algorithm
    expire_minutes = settings.auth_jwt.access_token_expire_minutes
    public_key = settings.auth_jwt.public_key_path.read_text()

    async def encode_jwt(
        self,
        payload: dict,
        expire_timedelta: timedelta | None = None,
    ) -> CreateTokenTuple:

        to_encode = payload.copy()
        now = datetime.now(timezone.utc)
        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(minutes=self.expire_minutes)
        session_id = str(uuid.uuid4())

        to_encode.update(exp=expire, iat=now, session_id=session_id)
        encoded_jwt = jwt.encode(to_encode, self.private_key, algorithm=self.algorithm)

        return CreateTokenTuple(encoded_jwt, session_id)

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


auth_handler = AuthHandler()
