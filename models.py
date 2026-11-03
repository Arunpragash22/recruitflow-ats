
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    position: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Applied"
    )
