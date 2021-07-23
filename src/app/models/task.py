from database.database import Base, engine
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func


class TaskModel(Base):
    __tablename__ = "tasks"
    __table_args__ = {'extend_existing': True}

    # TODO: index=Trueでインデックスを追加
    id = Column(Integer, primary_key=True, autoincrement=True)
    # タスクを作成したユーザー
    task_creator = Column(String, ForeignKey('custom_users.ulid'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False, default='')
    is_done = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
