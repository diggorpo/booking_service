from abc import ABC, abstractmethod


class BaseRepository[T](ABC):
    @abstractmethod
    async def get_by_id(self):
        pass
