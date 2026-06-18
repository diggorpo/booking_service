import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from core.infrastructure.db.models.base import Base
from core.infrastructure.db.models.booking import Booking
from core.infrastructure.db.models.user import User
from main import app
from api.deps.db_session import get_db_session
from core.infrastructure.db.models import Role
import bcrypt
from api.api_v1.auth.handler import AuthHandler
from core.infrastructure.db.models import Room, Slot
from datetime import date, time, timezone


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def seed_bookings(db_session: AsyncSession, seed_users, seed_slots) -> None:
    booking_client = Booking(
        id=1,
        user_id=2,
        slot_id=1,
        date=date(2026, 6, 20),
    )

    booking_admin = Booking(id=2, user_id=1, slot_id=2, date=date(2026, 6, 20))

    db_session.add_all([booking_client, booking_admin])
    await db_session.commit()


@pytest.fixture(scope="function")
async def seed_rooms(db_session: AsyncSession) -> None:
    room1 = Room(id=1)
    room2 = Room(id=2)

    db_session.add_all([room1, room2])
    await db_session.commit()


@pytest.fixture(scope="function")
async def seed_slots(db_session: AsyncSession, seed_rooms) -> None:
    slots = []
    for i in range(4):
        start_hour = 9 + (i * 2)
        end_hour = start_hour + 2

        slot = Slot(
            id=i + 1,
            room_id=1,
            start_time=time(start_hour, 0, tzinfo=timezone.utc),
            end_time=time(end_hour, 0, tzinfo=timezone.utc),
        )
        slots.append(slot)

    db_session.add_all(slots)
    await db_session.commit()


@pytest.fixture(scope="function")
async def seed_roles(db_session: AsyncSession) -> None:
    admin = Role(id=1, name="admin")
    manager = Role(id=2, name="manager")
    client = Role(id=3, name="client")

    db_session.add_all([admin, manager, client])
    await db_session.commit()


@pytest.fixture(scope="function")
async def seed_users(db_session: AsyncSession, seed_roles) -> None:

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(b"password123", salt)

    admin_user = User(
        id=1,
        first_name="Admin",
        last_name="System",
        email="admin@example.com",
        phone_number="+79991110000",
        password_hash=hashed_password,
        role_id=1,
    )

    client_user = User(
        id=2,
        first_name="Yaroslav",
        last_name="Nikolaev",
        email="client@example.com",
        phone_number="+79991112233",
        password_hash=hashed_password,
        role_id=3,
    )

    db_session.add_all([admin_user, client_user])
    await db_session.commit()


@pytest.fixture(scope="function")
async def auth_client(
    client: AsyncClient, seed_users
) -> AsyncGenerator[AsyncClient, None]:

    auth_handler = AuthHandler()

    token, _ = await auth_handler.encode_jwt({"user_id": "2"})

    client.cookies.set("Authorization", token)

    yield client


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
