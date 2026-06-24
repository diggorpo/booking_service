from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings
from sqlalchemy import event


class DatabaseHelper:
    def __init__(
        self, url: str = settings.db_url, echo: bool = settings.db_echo
    ) -> None:
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )

        if "sqlite" in url:

            @event.listens_for(self.engine.sync_engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )


db_helper = DatabaseHelper()
