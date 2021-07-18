from app.database import Base
from sqlalchemy import Column, Integer, Text


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer(unsigned=True),
                primary_key=True,
                unique=True,
                autoincrement=True)
    name = Column(Text)

    def __init__(self, name: str):
        self.name = name
