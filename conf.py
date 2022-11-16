TORTOISE_ORM = {
    # 连接信息
    "connections": {"default": "mysql://root:123456@127.0.0.1:3306/test"},
    "apps": {
        "models": {
            # model 信息
            # "models": ["more_more", "aerich.models", "table", "one_more"],
            "models": ["models", "aerich.models"], # 把需要的模型导进一个module 直接使用module
            "default_connection": "default",
        },
    },
}
