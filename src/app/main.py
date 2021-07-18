import graphene
from fastapi import FastAPI
from starlette.graphql import GraphQLApp

import database
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
    "/graphql",
    GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutation)))


@app.on_event("startup")
async def startup_event():
    # テーブルのリセット
    # database.Base.metadata.drop_all(bind=database.engine)
    # 起動時にテーブルを作成
    database.Base.metadata.create_all(bind=database.engine)


# APIサーバシャットダウン時にDBセッションを削除
@app.on_event("shutdown")
def shutdown_event():
    database.db_session.remove()
