from tortoise import Tortoise, fields, models, run_async

# 多对多
class Course(models.Model):
    """课程表"""

    name = fields.CharField(max_length=20, description="课程名")
    students: fields.ManyToManyRelation["Student"]


class Student(models.Model):

    name = fields.CharField(max_length=20)
    courses: fields.ManyToManyRelation[Course] = fields.ManyToManyField(
        "models.Course", related_name="students"
    )


# 【stduent 【课程】】


async def run():
    await Tortoise.init(
        db_url="sqlite://more_more.sqlite3", modules={"models": ["__main__"]}
    )
    await Tortoise.generate_schemas()

    # Create student object
    student = await Student.create(name="7y")
    """
    INSERT INTO "student" ("name") VALUES (?): ['7y']
    """
    # 2. course object
    course = await Course.create(name="Python")
    """
    INSERT INTO "course" ("name") VALUES (?): ['Python']
    """
    # 3. student_courses object
    await student.courses.add(course)
    """
    INSERT INTO "student_course" ("course_id","student_id") VALUES (3,3)
    """
    await student.courses
    """
    SELECT "course"."id","course"."name" FROM "course" LEFT OUTER JOIN "student_course" ON "course"."id"="student_course"."course_id" WHERE "student_course"."student_id"=5
    """

    # student表 获取course
    for course in await student.courses:
        print(course.id)  # 5

    r = await Student.filter(courses=5).prefetch_related("courses")
    """
    SELECT "sq0"."_backward_relation_key" "_backward_relation_key","course"."name" "name","course"."id" "id" FROM "course" JOIN (SELECT "student_id" "_backward_relation_key","course_id" "_forward_relation_key" FROM "student_course" WHERE "student_id" IN (5)) "sq0" ON "sq0"."_forward_relation_key"="course"."id"

    """
    print(r)

    # course表获取 student
    await course.students
    """
    SELECT "student"."name","student"."id" FROM "student" LEFT OUTER JOIN "student_course" ON "student"."id"="student_course"."student_id" WHERE "student_course"."course_id"=7
    """

    await student.fetch_related("courses")
    await course.fetch_related("students")

    # 去掉重复
    await Student.filter(courses__name="Python").distinct()
    """
    SELECT DISTINCT "student"."id","student"."name" FROM "student" LEFT OUTER JOIN "student_course" ON "student"."id"="student_course"."student_id" LEFT OUTER JOIN "course" ON "student_course"."course_id"="course"."id" WHERE "course"."name"='Python'
    """


if __name__ == "__main__":
    from logger import logger_db_client

    run_async(run())
