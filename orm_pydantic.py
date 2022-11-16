"""
This example demonstrates pydantic serialisation
已知问题：表中的关联字段 序列化 pydantic模型会被忽略，出现这种问题，可继承生成出来的schema 再把关系字段 写进去
"""
from typing import Optional, List

from tortoise import Tortoise, fields
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from tortoise.models import Model


async def connect():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()


class User(Model):
    name = fields.CharField(max_length=20)
    loves = fields.JSONField(default=list)
    age = fields.IntField()
    password = fields.CharField(max_length=120)
    parent = fields.ForeignKeyField("models.User", related_name="pid", null=True, default=True)

    # 关系表序列化

    def length(self) -> int:
        """计算属性 pydantic"""
        return len(self.name)

    # https://tortoise.github.io/contrib/pydantic.html?h=pydanticmeta#inheritance
    class PydanticMeta:
        allow_cycles: bool = False # 关系递归引用
        backward_relations: bool = True # 递归关系
        config_class = None # 自定义配置类
        exclude_raw_fields: bool = True # 排除原始的关系字段 字段包含_id

        max_recursion: int = 3 # 最大递归级别
        sort_alphabetically: bool = False # 按字母排序

        # 生成模型排除字段
        exclude = ("created_at",)
        # Let's include two callables as computed columns 计算属性列
        computed = () # 计算属性，计算属性 必须带返回值类型


Tortoise.init_models(["__main__"], "models")

# model（ORM） to  schema（Pydantic） 序列化   ｜｜｜ schema（Pydantic） to  model（ORM） 反序列化

# exclude 排除 include 包含

Default = pydantic_model_creator(User, name="default")  # 所有字段
UserSchema = pydantic_model_creator(User, name="UserInput", exclude_readonly=True) # 只读 主键、
IncludeName = pydantic_model_creator(User, name="UserName", include=("name", ))
Computed = pydantic_model_creator(User, name="computed", computed=("length",))
UserSchemaOut = pydantic_model_creator(User, exclude=("password",))
UserSchemaList = pydantic_queryset_creator(User)



from fastapi import FastAPI, APIRouter

app = FastAPI(title="Tortoise ORM Pydantic 序列化", on_startup=[connect], on_shutdown=[Tortoise.close_connections])

serialization = APIRouter(tags=['model 序列化 pydantic - 需要model作为参数'])

@serialization.post("/Default", summary="Default - 根据model全量")
def defa(data: Default):
    pass

@serialization.post("/int", summary="UserSchema - 排除只读")
def inp(data: UserSchema):
    pass

@serialization.post("/demo", summary="IncludeName - 仅包含name")
def ipn(data: IncludeName):
    pass

@serialization.post("/Computed", summary="Computed - 添加计算属性")
def Comp(data: Computed):
    pass

@serialization.post("/out", summary="UserSchemaOut - 排除password")
def out(data: UserSchemaOut):
    pass


@serialization.post("/list", summary="UserSchemaList - 列表")
def li(data: UserSchemaList):
    pass


deserialization = APIRouter(tags=["pydantic 反序列化 model - 需要model作为参数"])


class Input(UserSchema):
    parent: Optional[int]


@deserialization.post("/user", summary="from_tortoise_orm - 单个model")
async def add(data: Input):
    print(data)
    obj = await User.create(**data.dict())
    # 反序列化 需要一个Model 对象
    return await UserSchemaOut.from_tortoise_orm(obj)


@deserialization.get("/user", summary="用户列表", response_model=UserSchemaList)
async def arr():
    # 反序列化 需要一个QuerySet 对象
    return await UserSchemaList.from_queryset(User.all())


@deserialization.get("/user/{id}", summary="用户详细")
async def info(id: int):
    return await UserSchemaOut.from_queryset_single(User.filter(id=id).first())


@deserialization.get("/user/q/{id}", summary="用户查询", response_model=List[UserSchemaOut])
async def query():
    return await UserSchemaOut.from_queryset(User.all())
    # return await UserSchemaList.from_queryset(User.all())
    # return await UserSchemaOut.from_queryset_single(User.all())


app.include_router(serialization)
app.include_router(deserialization)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("__main__:app", reload=True)
