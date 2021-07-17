import database
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class TaskModel(database.Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    is_done = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
