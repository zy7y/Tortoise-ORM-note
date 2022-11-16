from tortoise import Tortoise, fields, models, run_async
from tortoise.query_utils import Prefetch

# 1⃣️对1⃣️
class Student(models.Model):
    name = fields.CharField(max_length=20, description="name")
    # 与下面的related_name 字段名一致，仅得到友好提示
    info: fields.ReverseRelation["StudentDetail"]


class StudentDetail(models.Model):
    age = fields.IntField(description="age")
    # Student Object 通过 info拿到 StudentDetail Object, 类型标注友好提示 code联想补充
    students: fields.OneToOneRelation[Student] = fields.OneToOneField(
        "models.Student", related_name="info"
    )


async def run():
    await Tortoise.init(
        db_url="sqlite://one_one.sqlite3", modules={"models": ["__main__"]}
    )
    await Tortoise.generate_schemas()

    # create
    student = await Student.create(name="7y")
    await StudentDetail.create(age=18, students=student)

    # 改 只能改 某一张表的数据
    await Student.filter(info__age=18).update(name="777")
    """
    UPDATE "student" SET "name"=? FROM "student" "student_" LEFT OUTER JOIN "studentdetail" ON "student"."id"="studentdetail"."students_id" WHERE "studentdetail"."age"=18: ['777']
    """
    await Student.filter(name="777").update(name="7y")
    await StudentDetail.filter(students__name="777").update(age=18)

    # 查 学生名 7y 并且 学生 年龄 = 18 的数据 主表查从《关联表》表
    res = await Student.filter(name="7y", info__age=18).first()
    """
    SELECT "studentdetail"."age","studentdetail"."students_id","studentdetail"."id" FROM "studentdetail" LEFT OUTER JOIN "student" "studentdetail__students" ON "studentdetail__students"."id"="studentdetail"."students_id" WHERE "studentdetail__students"."name"='7y' LIMIT 1

    """
    # 通过res.related_name可获得被关联模型 StudentDetail
    student_detail = await res.info.first()
    print(student_detail.age)  # 18

    res = (
        await StudentDetail.all()
        .prefetch_related(Prefetch("students", queryset=Student.filter(name="7y")))
        .first()
    )
    print(await res.students.all().values())  # [{'id': 68, 'name': '7y'},]
    """
    SELECT "students_id","age","id" FROM "studentdetail" LIMIT 1
    SELECT "name","id" FROM "student" WHERE "name"='7y' AND "id" IN (68)
"""

    # 关联表查主表
    res = await StudentDetail.filter(students__name="7y").first()
    """
    SELECT "studentdetail"."age","studentdetail"."students_id","studentdetail"."id" FROM "studentdetail" LEFT OUTER JOIN "student" "studentdetail__students" ON "studentdetail__students"."id"="studentdetail"."students_id" WHERE "studentdetail__students"."name"='7y' LIMIT 1
    """
    # 通过 res.students 获得 Student模型
    student = await res.students.first()
    print(student.name)  # 7y

    res = await Student.filter(info__age=18).first().prefetch_related("info")
    """
    SELECT "student"."name","student"."id" FROM "student" LEFT OUTER JOIN "studentdetail" ON "student"."id"="studentdetail"."students_id" WHERE "studentdetail"."age"=18 LIMIT 1
    """
    print(res.info.age)  # 18
    """
    SELECT "students_id","age","id" FROM "studentdetail" WHERE "students_id" IN (68)
    """

    await StudentDetail.all().values("students__name", "students__id", "age")
    """
    SELECT "studentdetail__students"."name" "students__name","studentdetail__students"."id" "students__id","studentdetail"."age" "age" FROM "studentdetail" LEFT OUTER JOIN "student" "studentdetail__students" ON "studentdetail__students"."id"="studentdetail"."students_id": None

    """

    # 删 取决于 on_delete 策略
    await Student.filter(name="7y").delete()


if __name__ == "__main__":
    import logging
    import sys
    from logger import logger_db_client
    run_async(run())
