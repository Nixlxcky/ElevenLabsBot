from typing import List, Dict
import logging


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Boolean, select, delete
from sqlalchemy.dialects.mysql import insert

Base = declarative_base()


class Voice(Base):
    __tablename__ = 'voices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    voice_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    language = Column(String(50), nullable=False)
    gender = Column(String(20))
    is_cloned = Column(Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'voice_id': self.voice_id,
            'name': self.name,
            'language': self.language,
            'gender': self.gender,
            'is_cloned': self.is_cloned
        }


class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.async_session = None


    async def create_pool(self):

        try:
            self.engine = create_async_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )

            self.async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logging.info("Successfully connected to database")
        except Exception as e:
            logging.error(f"Failed to connect to database: {e}")
            raise

    async def get_voices_by_language(self, language: str) -> List[Dict]:
        async with self.async_session() as session:
            query = select(Voice).where(Voice.language == language)
            result = await session.execute(query)
            voices = result.scalars().all()
            return [voice.to_dict() for voice in voices]

    async def get_all_voices(self) -> List[Dict]:

        async with self.async_session() as session:
            query = select(Voice)
            result = await session.execute(query)
            voices = result.scalars().all()
            return [voice.to_dict() for voice in voices]

    async def add_voice(self, voice_data: Dict):
        async with self.async_session() as session:
            stmt = insert(Voice).values(
                voice_id=voice_data['voice_id'],
                name=voice_data['name'],
                language=voice_data['language'],
                gender=voice_data.get('gender'),
                is_cloned=voice_data.get('is_cloned', False)
            )


            stmt = stmt.on_duplicate_key_update(
                name=stmt.inserted.name,
                language=stmt.inserted.language,
                gender=stmt.inserted.gender,
                is_cloned=stmt.inserted.is_cloned
            )

            await session.execute(stmt)
            await session.commit()

    async def clear_voices(self):
        async with self.async_session() as session:
            await session.execute(delete(Voice))
            await session.commit()

    async def close(self):

        if self.engine:
            await self.engine.dispose()

    async def create_tables(self):
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logging.info("Tables created successfully.")
        except Exception as e:
            logging.error(f"Failed to create tables: {e}")
            raise