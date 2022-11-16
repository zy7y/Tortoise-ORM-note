"""
Tortoise ORM & SQLAlchemy
"""
# SQlAlchemy
from sqlalchemy import Column, Integer, String, DateTime, func, select
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SqlAlchemyTable(Base):
    __tablename__ = "a"

    id = Column(Integer, primary_key=True)
    data = Column(String)
    create_date = Column(DateTime, server_default=func.now())


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///basic.sqlite3")
async_session = sessionmaker(
    engine, expire_on_commit=True, class_=AsyncSession
)
# 异步session 类， 实例类 去操作表


def get_db():
    session = async_session()
    try:
        yield session
    finally:
        session.close()


from fastapi import FastAPI, Depends
from pydantic import BaseModel

class Response(BaseModel):
    id: int
    data: str

app = FastAPI(title="SQLAlchemy & TortoiseORM")


@app.get("/", response_model=Response)
async def index():
    # 视图里面实例db对象
    async with async_session() as session:
        result = await session.execute(select(SqlAlchemyTable).order_by(SqlAlchemyTable.id))
        return result.scalars().first().__dict__ # 第一条


@app.get("/index")
async def index1(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SqlAlchemyTable).order_by(SqlAlchemyTable.id))
    return result.scalars().all() # 所有


# from tortoise.contrib.fastapi import register_tortoise
# from tortoise.contrib.pydantic import pydantic_model_creator
# from tortoise import models, fields
# class TortoiseOrm(models.Model):
#     data = fields.CharField(max_length=30)
#     create_date = fields.DatetimeField(auto_now_add=True, null=True)
#
#     class Meta:
#         table = 'a'
#
# # biao 转成pydantic模型 output openapi 模型名称，
# Response = pydantic_model_creator(TortoiseOrm, name="OutPut", exclude=("create_date",))
#
# print({"id":1,"data":"22"})
#
#
# from fastapi import FastAPI
# app = FastAPI(title="SQLAlchemy & TortoiseORM")
#
# register_tortoise(
#     app,
#     db_url="sqlite://basic.sqlite3",
#     modules={"models": ["__main__"]},
#     add_exception_handlers=True,
# )
#
#
# @app.get("/", response_model=Response)
# async def index():
#     return await TortoiseOrm.all().order_by("id").first().values('id', 'data')
#     # select * from a;
#
#
# @app.get("/index")
# async def index1():
#     return await TortoiseOrm.all().order_by("id")
#

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("__main__:app", reload=True)
