from sys import path

from sqlalchemy import Column, String

path.append('../')

from database import Base, engine


class UserModel(Base):
    __tablename__ = "app_users"
    __table_args__ = {'extend_existing': True}
    ulid = Column(String, primary_key=True, unique=True)
    username = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String)
    full_name = Column(String(255))

    # Base.metadata.create_all(bind=engine)
