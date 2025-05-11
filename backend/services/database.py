from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config.settings import get_settings

settings = get_settings()


def build_db_url():
    if settings.use_mock_db:
        return f"postgresql://u0:password@shilling-postgres:5432/db10"
    else:
        return settings.db_url


SQLALCHEMY_DATABASE_URL = build_db_url()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=True, bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
