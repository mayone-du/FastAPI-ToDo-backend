import database
from sqlalchemy import Column, Integer
from sqlalchemy.sql.sqltypes import Text


class UserModel(database.Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text)
    email = Column(Text, unique=True)
