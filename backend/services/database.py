from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config.settings import get_settings
from sqlalchemy.orm import class_mapper

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


class ToDictMixin:
    def to_dict(self):
        data = {c.key: getattr(self, c.key) for c in class_mapper(self.__class__).columns}
        relationships = {
            r.key: getattr(self, r.key) for r in class_mapper(self.__class__).relationships
        }
        return {**data, **relationships}


class Base(DeclarativeBase, ToDictMixin):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
