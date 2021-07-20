from database.database import Base, engine
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func


class TaskModel(Base):
    __tablename__ = "tasks"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # タスクを作成したユーザー
    task_creator = Column(String, ForeignKey('custom_users.ulid'))
    title = Column(String(255))
    content = Column(String(255))
    is_done = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
