from sys import path

import graphene
from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema
from starlette.background import BackgroundTasks
from starlette.graphql import GraphQLApp

from database.database import Base, db_session, engine
# from libs.auth import send_email_background
from schemas.all_schemas import Mutation, Query

path.append('../')
from settings.envs import MAIL_CONFIGS

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
