from pathlib import Path
from sys import path

from fastapi import Depends, FastAPI, HTTPException
from scripts.initialization import init

import database

# current_dir = Path(__file__).resolve().parent
# path.append(str(current_dir) + '/../')

app = FastAPI()

from typing import List

import graphene
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette.graphql import GraphQLApp

from schemas.schemas import Mutation, Query

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.add_route(
    "/", GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutation)))
