import database
from sqlalchemy import Column, String


class UserModel(database.Base):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}
    ulid = Column(String, primary_key=True, unique=True)
    username = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String)
