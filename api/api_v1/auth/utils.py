from fastapi import Request, status, HTTPException


async def get_token_from_cookie(request: Request) -> str | None:
    token = request.cookies.get("Authorization")

    if token:
        return token

    raise HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail="Token is missing",
    )
