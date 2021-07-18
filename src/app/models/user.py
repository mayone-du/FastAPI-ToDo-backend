import database
from sqlalchemy import Column, Integer, Text


class UserModel(database.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(Text)
    email = Column(Text)

    # def __init__(self, name: str):
    #     self.name = name
