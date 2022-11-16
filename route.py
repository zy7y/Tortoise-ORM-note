"""
This example to use router to implement read/write separation
"""
import asyncio
from typing import Type

from tortoise import Tortoise, fields, run_async
from tortoise.models import Model


class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    datetime = fields.DatetimeField(null=True)

    class Meta:
        table = "event"

    def __str__(self):
        return self.name

class Router:
    def db_for_read(self, model: Type[Model]):
        print("slave runing")
        return "slave"

    def db_for_write(self, model: Type[Model]):
        print("master runing")
        return "master"


async def run():
    config = {
        "connections": {"master": "mysql://root:123456@127.0.0.1:3306/test",
                        "slave": "mysql://root:123456@127.0.0.1:3307/test"},
        "apps": {
            "models": {
                "models": ["__main__"],
                "default_connection": "master",
            }
        },
        "routers": ["__main__.Router"],
        "use_tz": False,
        "timezone": "UTC",
    }
    await Tortoise.init(config=config)
    await Tortoise.generate_schemas()
    # this will use connection master
    event = await Event.create(name="Test1")
    print(event)
    # await asyncio.sleep(1)
    # this will use connection slave
    result = await Event.get(pk=event.pk)
    print(result)


if __name__ == "__main__":
    from logger import logger_db_client
    run_async(run())
