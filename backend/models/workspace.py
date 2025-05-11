from sqlalchemy.orm import mapped_column, Mapped, relationship, validates
from sqlalchemy import ForeignKey, UniqueConstraint, Column
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from utils.pure_funcs import get_now
from services.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    owner_address: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    notification_email: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=get_now)
    updated_at: Mapped[datetime] = mapped_column(default=get_now, onupdate=get_now)

    def __repr__(self):
        return f"<Workspace {self.name}>"
