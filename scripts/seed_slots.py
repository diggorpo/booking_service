import asyncio
from datetime import time, timezone
from core.infrastructure.db.repositories import SlotRepository
from core.infrastructure.db.db_helper import db_helper


async def seed_slot():
    repo = SlotRepository(db_helper.session_factory())
    async with db_helper.session_factory() as session:
        repo.session = session
        slots = []
        for i in range(10):
            start_hour = 9 + i
            end_hour = start_hour + 1
            slot = await repo.create(
                data={
                    "start_time": time(start_hour, 0, tzinfo=timezone.utc),
                    "end_time": time(end_hour, 0, tzinfo=timezone.utc),
                    "room_id": 1,
                },
            )
            slots.append(slot)
        await session.commit()
        print(f"Created {len(slots)} slots")


if __name__ == "__main__":
    asyncio.run(seed_slot())
