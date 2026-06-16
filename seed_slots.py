import asyncio
from datetime import datetime, timedelta, timezone
from core.infrastructure.db.repositories import SlotRepository
from core.infrastructure.db.db_helper import db_helper


async def seed_slot():

    base_time = datetime(2026, 6, 20, 9, 0, tzinfo=timezone.utc)
    repo = SlotRepository()
    async with db_helper.session_factory() as session:
        for i in range(10):  # Создадим 10 слотов подряд
            start = base_time + timedelta(hours=i)
            end = start + timedelta(hours=1)
            await repo.create(
                session=session,
                data={"start_time": start, "end_time": end, "room_id": 1},
            )
            await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_slot())
