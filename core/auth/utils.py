import jwt
from core.config import settings
import bcrypt


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> str:

    return jwt.encode(payload, private_key, algorithm=algorithm)


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:

    return jwt.decode(token, public_key, algorithms=[algorithm])


def hash_password(password: str) -> bytes:

    salt = bcrypt.gensalt()
    pwd_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed


def validate_password(password: str, hashed: bytes) -> bool:

    pwd_bytes = password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hashed)
