from tortoise import Tortoise, fields, models, run_async
from tortoise.query_utils import Prefetch

# 1⃣️对多
class Class(models.Model):
    id = fields.IntField(pk=True, description="班级唯一标识")
    name = fields.CharField(max_length=10, description="班级名称")
    # 类型提示，仅用于Code 联想字段 匹配 下方关联的related_name
    students: fields.ReverseRelation["Student"]


class Student(models.Model):
    """学生"""

    id = fields.IntField(pk=True, description="学生唯一标识")
    name = fields.CharField(max_length=20, description="学生名称")
    # Class Object 通过 students 拿到 List[Student Object] , 类型标注友好提示 code联想补充
    # 生成外建； 字段名 + _to_field（默认主表的主键）
    my_class: fields.ForeignKeyRelation[Class] = fields.ForeignKeyField(
        "models.Class", related_name="students", description="所属班级"
    )


async def run():
    await Tortoise.init(
        db_url="sqlite://one_more.sqlite3", modules={"models": ["__main__"]}
    )
    await Tortoise.generate_schemas()

    # create
    class_obj = await Class.create(name="🚀班")
    student_obj = await Student.create(name="7777777", my_class=class_obj)
    # await Student.create(name='7777777', my_class=class_obj.id)
    # await Student.create(name='7777777', my_class=class_obj.pk)
    """
    INSERT INTO "class" ("name") VALUES (?): ['🚀班']
    INSERT INTO "student" ("name","my_class_id") VALUES (?,?): ['7777777', 1]
    """

    # 通过表class（1） 获取 student（多）
    for student in await class_obj.students.all():
        """
        SELECT "id","name","my_class_id" FROM "student" WHERE "my_class_id"=4
        """
        # pk 和 id 都是表示主键的意思
        print(student.name, student.id, student.pk)

    res = await Class.filter(id=3).first().prefetch_related("students")
    print(await res.students.all().values())

    res = await Class.all().prefetch_related(
        Prefetch("students", queryset=Student.filter(my_class__name__not="7y").all())
    )
    print(await res[0].students.all().values())
    """
    SELECT "student"."name","student"."id","student"."my_class_id" FROM "student" LEFT OUTER JOIN "class" "student__my_class" ON "student__my_class"."id"="student"."my_class_id" WHERE ("student__my_class"."name"<>'7y' OR "student__my_class"."name" IS NULL) AND "student"."my_class_id" IN (1,2,3,4,5,6)

    """

    # 通过表 student（多） 获取 class（1）
    print(await student_obj.my_class.all().values())
    """
    SELECT "id" "id","name" "name" FROM "class"
    """

    res = await Student.filter(my_class__id__lt=2).all()
    """
    SELECT "student"."name","student"."id","student"."my_class_id" FROM "student" LEFT OUTER JOIN "class" "student__my_class" ON "student__my_class"."id"="student"."my_class_id" WHERE "student__my_class"."id"<2: None

    """
    for cls in await res[0].my_class.all():
        print(cls)


if __name__ == "__main__":

    from logger import logger_db_client

    run_async(run())
