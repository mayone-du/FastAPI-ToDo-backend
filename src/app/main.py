from sys import path

import graphene
from fastapi import FastAPI
from starlette.graphql import GraphQLApp

from database import Base, db_session, engine
from schemas.schemas import Mutation, Query

path.append('../')

from models.user import UserModel

# Baseの内容を反映させるにはここでUserModelをimportする必要あり？

app = FastAPI()

# # Dependency
# # セッション周りをうまいことやってくれるぽい？
# def get_db():
#     db = database.SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

app.add_route(
    "/graphql",
    GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutation)))


@app.on_event("startup")
async def startup_event():
    # テーブルのリセット
    Base.metadata.drop_all(bind=engine)
    # 起動時にテーブルを作成
    Base.metadata.create_all(bind=engine)


# APIサーバーのシャットダウン時にDBセッションを削除
@app.on_event("shutdown")
def shutdown_event():
    db_session.remove()
