import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(255))
    resources: Mapped[list] = mapped_column(sa.JSON)
    profit: Mapped[float] = mapped_column(sa.Float)
    status: Mapped[str] = mapped_column(sa.String(20))
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime, server_default=sa.func.now()
    )

    def to_dict(self) -> dict:
        return {"name": self.name, "resources": self.resources, "profit": self.profit}
