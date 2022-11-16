from enum import IntEnum

from tortoise import connections, fields, models
from tortoise.expressions import F, Q, RawSQL, Subquery
from tortoise.functions import Avg, Sum

# pip install tortoise-orm


class AbstractModel(models.Model):
    # 主键，当表里所有属性都没设置pk时，默认生成一个IntField类型 id 的主键
    id = fields.UUIDField(pk=True)

    class Meta:
        # 抽象模型，不生成表
        abstract = True


class MixinTimeFiled:
    # 添加数据时间 null = True tianjia gengxing buyong fuzhi
    created = fields.DatetimeField(null=True, auto_now_add=True)
    # 修改数据时间
    modified = fields.DatetimeField(null=True, auto_now=True)


class Gender(IntEnum):
    MAN = 0
    WOMAN = 1


class UserModel(AbstractModel, MixinTimeFiled):
    # unique 是否唯一 max—length 数据长度 index 是否索引
    username = fields.CharField(
        max_length=20, description="描述", unique=True, index=True
    )
    # null 是否可以为空
    nickname = fields.CharField(
        max_length=30, description="nickname", null=True, default="777"
    )
    # description 字段备注 ddl展示， 此处入库的为 0 or 1
    gender = fields.IntEnumField(Gender, description="sex", default=Gender.WOMAN)
    # max——digits 小输点左边最大位数，decimal——places 小数点右边最大位数99.99
    balance = fields.DecimalField(max_digits=2, decimal_places=2, description="balance")
    is_admin = fields.BooleanField(default=False)
    job_info = fields.JSONField(default=dict)  # {}

    class Meta:
        # 自定义表名，不配置按照类名小写生成 usermodel
        table = "tableName"
        table_description = "set table ddl desc"

        # 多列设置唯一复合所有
        unique_together = (("gender", "balance"),)
        # 排序
        ordering = ("is_admin",)
        # 索引
        indexes = ("balance",)

    def __str__(self):
        return self.username


async def cud():
    """增删改"""

    # 新增 返回 一个 UserModel null default  ziduan weiyi
    await UserModel.create(username="777", balance=22.135)

    # 更新 - 返回改动行数 filter tiaojian k
    await UserModel.filter(username="777").update(gender=Gender.MAN)  # 0
    await UserModel.filter(username="777").update(gender=0)

    # 删除 - 返回改动行数
    await UserModel.filter(username="777").delete()

    # 批量创建 - [UserModel,]
    await UserModel.bulk_create(
        [UserModel(username=f"{i}", balance=i) for i in range(2)]
    )

    # 批量更新
    users = await UserModel.all()
    for user in users:
        user.gender = 0

    await UserModel.bulk_update(users, fields=["gender"])


async def select_all():
    """
    all 查询
    :return:
    """
    # 全量查询 return [UserModel]  filter 【UserModel】
    await UserModel.all() # select * from user；
    print(UserModel.all().sql())

    # return [dict] - values 可过滤需要的字段[{"id":xx,"usernmae":username}]
    res = await UserModel.all().values("id", "username")
    # select *  from biao;  select id, name form biao
    print(res)

    # 排序 List [UserModel]
    res = await UserModel.all().order_by("-created")  # - 倒序 DESC
    print(res)
    for i in res:
        print(i.username)
        print(i.__dict__)

    # 分页
    res = await UserModel.all().offset(3).limit(2)  # select * from userTable limit 2, 3; 2  3
    print(res)

    # 分组 value_list 可过滤需要字段 return [(id  ， gender  )]
    res = await UserModel.all().group_by("created").values_list("id", "gender")
    print(res)

    # 统计
    res = await UserModel.all().count()
    print(res)

    # 使用聚合函数 + 分组 统计按 男女 各总共有多少 余额 result
    result = (
        await UserModel.all()
        .annotate(result=Sum("balance"))
        .group_by("gender")
        .values_list("gender", "result")
    )
    print(result)


async def select_get():
    """get"""
    # 根据条件查询符合的对象，条件需唯一 return UserModel
    # await UserModel.get(nickname='777')
    res = await UserModel.get(username="1")
    print(res.username)
    await res.delete()

    # 查询不到返回None，避免 出现对象不存在的异常 return UserModel | None
    res = await UserModel.get_or_none(username=100)
    print(res)

    # 如果有就返回查询数据，没有就创建 return UserModel
    res = await UserModel.get_or_create(username=19, balance=22.9)
    print(res[0].created)


async def select_filter():
    """filter all  [UserModel, UserModel]"""
    # return [UserModel] 条件查询 gender=1
    await UserModel.filter(gender=1).count()
    # 性别为1 的平均余额
    await UserModel.filter(gender=1).annotate(price=Avg("balance")).values("price")
    """
    SELECT AVG("CAST("balance" AS NUMERIC)") "price" FROM "tableName" WHERE "gender"=1
    """

    # 各性别平均余额
    await UserModel.annotate(price=Avg("balance")).group_by("gender").values(
        "gender", "price"
    )
    """
    SELECT "gender" "gender",AVG(CAST("balance" AS NUMERIC)) "price" FROM "tableName" GROUP BY "gender"
    """

    # 获取第一个符合条件的 nickname wei 777 diyige
    await UserModel.filter(nickname=777).first()
    """
    SELECT "nickname","gender","is_admin","created","balance","job_info","id","username","modified" FROM "tableName" WHERE "nickname"='777' ORDER BY "is_admin" ASC LIMIT 1
    """

    # get sql
    UserModel.filter(nickname=777).sql()
    """
    SELECT "nickname","gender","is_admin","created","balance","job_info","id","username","modified" FROM "tableName" WHERE "nickname"='777' ORDER BY "is_admin" ASC

    """

    # 查询 gender 不为 1
    await UserModel.exclude(gender=1)
    """
    SELECT "balance","modified","nickname","is_admin","id","created","job_info","username","gender" FROM "tableName" WHERE NOT "gender"=1 ORDER BY "is_admin" ASC

    """

    # 查询 gender 不为 1 __not in
    await UserModel.filter(gender__not=1)
    """
    SELECT "nickname","job_info","is_admin","created","gender","balance","modified","username","id" FROM "tableName" WHERE "gender"<>1 OR "gender" IS NULL ORDER BY "is_admin" ASC

    """

    # https://tortoise.github.io/query.html?h=__conta#filtering
    # 包含 7 忽略大小写 -》 like
    await UserModel.filter(nickname__icontains="7")
    """
    SELECT "nickname","created","id","balance","is_admin","job_info","modified","gender","username" FROM "tableName" WHERE UPPER(CAST("nickname" AS VARCHAR)) LIKE UPPER('%7%') ESCAPE '\' ORDER BY "is_admin" ASC
    """

    # between 0 and 2
    await UserModel.filter(balance__range=[0, 10])
    """
    SELECT "gender","balance","is_admin","modified","nickname","id","job_info","created","username" FROM "tableName" WHERE "balance" BETWEEN 0 AND 10 ORDER BY "is_admin" ASC
    """

    # 大于等于1
    await UserModel.filter(gender__gte=1)
    """
    SELECT "username","modified","gender","job_info","id","balance","is_admin","nickname","created" FROM "tableName" WHERE "gender">=1 ORDER BY "is_admin" ASC
    """

    # is null
    await UserModel.filter(gender__isnull=True)
    """
    SELECT "username","modified","gender","job_info","id","balance","is_admin","nickname","created" FROM "tableName" WHERE "gender" IS NULL ORDER BY "is_admin" ASC
    """

    await UserModel.get_or_create(
        username=7809,
        balance=99.22,
        job_info={
            "breed": "labrador",
            "owner": {
                "name": "Boby",
                "last": None,
                "other_pets": [
                    {
                        "name": "Fishy",
                    }
                ],
            },
        },
    )
    # json 字段 owner 下other pets第一个 name 不为Fishy
    await UserModel.filter(
        job_info__filter={"owner__other_pets__0__name__not": "Fishy"}
    )
    """
    SELECT "is_admin","id","username","balance","modified","created","nickname","job_info","gender" FROM "tableName" ORDER BY "is_admin" ASC
    """

    # 子查询
    await UserModel.filter(
        pk=Subquery(UserModel.filter(username=777).values("id"))
    ).first()
    """
    SELECT "job_info","created","username","is_admin","gender","balance","modified","nickname","id" FROM "tableName" WHERE "id"=(SELECT "id" "id" FROM "tableName" WHERE "username"='777' ORDER BY "is_admin" ASC) ORDER BY "is_admin" ASC LIMIT 1
    """


async def select_QF():
    """Q"""
    # or
    # username 为 '777' 或者 gender 不为1
    await UserModel.filter(Q(username=777) | Q(gender__not=1))
    """
    SELECT "created","id","job_info","username","gender","modified","balance","is_admin","nickname" FROM "tableName" WHERE "username"='777' OR "gender"<>1 OR "gender" IS NULL ORDER BY "is_admin" ASC
    """
    await UserModel.filter(Q(username=777), Q(gender__not=1), join_type="OR")
    """
    SELECT "created","id","job_info","username","gender","modified","balance","is_admin","nickname" FROM "tableName" WHERE "username"='777' AND ("gender"<>1 OR "gender" IS NULL) ORDER BY "is_admin" ASC
"""
    # ~Q 否定 gender 不为1
    await UserModel.filter(Q(username=777), ~Q(gender=1), join_type="OR")
    """
    SELECT "created","id","job_info","username","gender","modified","balance","is_admin","nickname" FROM "tableName" WHERE "username"='777' AND NOT "gender"=1 ORDER BY "is_admin" ASC
"""
    # Q and 查询username 为 777 并且gender不为1
    await UserModel.filter(Q(username=777), Q(gender__not=1))
    """
    SELECT "username","gender","is_admin","job_info","balance","id","created","nickname","modified" FROM "tableName" WHERE "username"='777' AND ("gender"<>1 OR "gender" IS NULL) ORDER BY "is_admin" ASC
"""

    await UserModel.filter(Q(username=777), Q(gender__not=1), join_type="AND")
    """
    SELECT "username","gender","is_admin","job_info","balance","id","created","nickname","modified" FROM "tableName" WHERE "username"='777' AND ("gender"<>1 OR "gender" IS NULL) ORDER BY "is_admin" ASC
"""

    await UserModel.filter(username=777, gender__not=1)
    """
    SELECT "username","gender","is_admin","job_info","balance","id","created","nickname","modified" FROM "tableName" WHERE "username"='777' AND ("gender"<>1 OR "gender" IS NULL) ORDER BY "is_admin" ASC
"""
    # F 可查到结果时直接给结果计算
    # F 将结果的 余额 + 999
    await UserModel.annotate(idp=F("balance") + 999).values("balance", "idp")
    """
    SELECT "balance" "balance","balance"+999 "idp" FROM "tableName"
    """

    # RawSQL 余额 + 999
    await UserModel.annotate(idp=RawSQL("balance + 999")).values("balance", "idp")
    """
    SELECT "balance" "balance",balance + 999 "idp" FROM "tableName"
    """

    # RawSQL 统计
    await UserModel.annotate(idp=RawSQL("count(id)")).values("idp")
    """
    SELECT count(id) "idp" FROM "tableName"
    """

    # 执行原生SQL，返回字典
    conn = connections.get("default")
    await conn.execute_query_dict(
        "SELECT COUNT(*) FROM tableName WHERE username=(?)", ["777"]
    )
    """
    SELECT COUNT(*) FROM tableName WHERE username='777'
    """


async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        # 数据库连接
        db_url="sqlite://basic.sqlite3",
        # 连接mysql pip install aiomysql
        # db_url='mysql://root:123456@127.0.0.1:3306/tortoise',
        # 指定管理的models，__main__ 🈯️当前文件的models.Model
        modules={"models": ["__main__"]},
    )
    # Generate the schema
    await Tortoise.generate_schemas()
    await cud()


if __name__ == "__main__":
    from tortoise import Tortoise, run_async

    from logger import logger_db_client

    run_async(init())
