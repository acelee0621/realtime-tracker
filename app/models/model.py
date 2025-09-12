# app/models/model.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String

from app.models.base import Base
from app.models.mixin import DateTimeMixin


class Inventory(Base, DateTimeMixin):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
