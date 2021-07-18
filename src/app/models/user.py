import database
from sqlalchemy import Column, Integer, String


class UserModel(database.Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    username = Column(String(255))
    email = Column(String(255))
    password = Column(String)

    # def __init__(self, name: str):
    #     self.name = name
