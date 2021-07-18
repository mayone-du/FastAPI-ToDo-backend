import database
from sqlalchemy import Column, Integer, Text


class UserModel(database.Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    username = Column(Text)
    email = Column(Text)
    password = Column(Text)

    # def __init__(self, name: str):
    #     self.name = name
