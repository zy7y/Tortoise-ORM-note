"""
信号 & 事务
"""
from typing import List

from tortoise import models, fields
from tortoise.exceptions import OperationalError
from tortoise.signals import pre_save, post_save, pre_delete, post_delete
from tortoise.transactions import in_transaction, atomic


class Role(models.Model):
    name = fields.CharField(max_length=30, description='desc')
    desc = fields.TextField(description='text')


class User(models.Model):
    name = fields.CharField(max_length=30)
    age = fields.IntField()

    def __str__(self):
        return f"User {self.name} |age: {self.age}"


@pre_save(User)
async def signal_pre_save(
        sender: "Type[User]", instance: User, using_db, update_fields
) -> None:
    """save 前执行"""
    print("pre save...", sender, instance, using_db, update_fields)


@post_save(User)
async def signal_post_save(
        sender: "Type[User]",
        instance: User,
        created: bool,
        using_db: "Optional[BaseDBAsyncClient]",
        update_fields: List[str],
) -> None:
    """save 后执行"""
    print("post.save...", sender, instance, using_db, created, update_fields)


@pre_delete(User)
async def signal_pre_delete(
        sender: "Type[User]", instance: User, using_db: "Optional[BaseDBAsyncClient]"
) -> None:
    print("pre delete ...", sender, instance, using_db)


@post_delete(User)
async def signal_post_delete(
        sender: "Type[User]", instance: User, using_db: "Optional[BaseDBAsyncClient]"
) -> None:
    print("post delete.", sender, instance, using_db)


async def signal_demo():
    user = await User.create(name="23", age=18)
    print("1\n")
    user.name = "7y"
    print("2\n")
    await user.save(update_fields=["name"])
    # UPDATE "user" SET "name"=? WHERE "id"=?: ['7y', 20]
    # await user.save() # update 表里所有字段
    # UPDATE "user" SET "name"=?,"age"=? WHERE "id"=?: ['7y', 18, 22]
    print("3\n")
    await user.delete()
    print("4\n")

    await User.create(name="231", age=19)

    # 下面 不触发
    await User.filter(age=19).update(name="78")
    await User.filter(age=19).delete()


async def cd():
    """操作"""
    # 1. 创建
    await User.create(name="Test", age=19)
    # 2. 创建是否成功
    print(await User.filter(name="Test", age=19).first())
    # 3. 报个错
    await User.get(age=30)  # 数据不存在 rasie Object does not exist


async def tran_with():
    """事务 上下文管理器实现"""
    try:
        async with in_transaction() as connection:
            await cd()
    except OperationalError as e:
        print(e)


async def tran_decto():
    """事务 装饰器 实现"""
    # @atomic()
    # async def bound_to_fall():
    #     await cd()

    try:
        # await bound_to_fall()
        atomic(await cd())()
    except OperationalError as e:
        print(e)


async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        # 数据库连接
        db_url="sqlite://signal_transaction.sqlite3",
        # 连接mysql pip install aiomysql
        # db_url='mysql://root:123456@127.0.0.1:3306/tortoise',
        # 指定管理的models，__main__ 🈯️当前文件的models.Model
        modules={"models": ["__main__"]},
    )
    # Generate the schema
    await Tortoise.generate_schemas()
    # await signal_demo()

    # print(await User.filter(name="Test", age=19).delete())

    # await cd()

    # await tran_with()
    await tran_decto()

    # 4. 确认是否回滚, 如果查到了 说明回滚失败 还是新增了数据
    print(await User.filter(name="Test", age=19).first())


if __name__ == "__main__":
    from tortoise import Tortoise, run_async

    from logger import logger_db_client

    run_async(init())
