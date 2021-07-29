from sys import path

import graphene
from fastapi import FastAPI
from starlette.graphql import GraphQLApp

from database.database import Base, db_session, engine
from schemas.all_schemas import Mutation, Query

app = FastAPI()

# # Dependency
# # セッション周りをうまいことやってくれるぽい？
# def get_db():
#     db = database.SessionLocal()
#     try:
#         yield db
#     finally:
#         db_session.close()

app.add_route(
    "/graphql",
    GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutation)))


# APIサーバーが立ち上がったときの処理
@app.on_event("startup")
async def startup_event():
    # テーブルのリセットをしたいときはコメントを解除
    # Base.metadata.drop_all(bind=engine)
    # 起動時にテーブルを作成
    Base.metadata.create_all(bind=engine)


# APIサーバーのシャットダウン時にDBセッションを削除
@app.on_event("shutdown")
def shutdown_event():
    db_session.remove()
