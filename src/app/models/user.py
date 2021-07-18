import database
from sqlalchemy import Column, Integer, String


class UserModel(database.Base):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    username = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String)
