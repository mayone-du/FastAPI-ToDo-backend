from fastapi import FastAPI

import database

app = FastAPI()

import graphene
from starlette.graphql import GraphQLApp

from schemas.schemas import Mutation, Query

app = FastAPI()


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.add_route(
    "/", GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutation)))


@app.on_event("startup")
async def startup_event():
    # 起動時にテーブルを作成
    database.Base.metadata.create_all(bind=database.engine)
