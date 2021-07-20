from database.database import Base, engine
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class TaskModel(Base):
    __tablename__ = "task"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255))
    content = Column(String(255))
    is_done = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
