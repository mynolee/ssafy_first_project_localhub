from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    region: Mapped[str] = mapped_column(String(30), index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    category: Mapped[str] = mapped_column(String(30), index=True)
    address: Mapped[str | None] = mapped_column(String(300))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(200))
    license: Mapped[str | None] = mapped_column(String(200))
    collected_at: Mapped[str | None] = mapped_column(String(20))


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(String(30), index=True, default="SEOUL")
    category: Mapped[str] = mapped_column(String(20), index=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(20), default="익명")
    password: Mapped[str] = mapped_column(String(20))
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    image_url: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
