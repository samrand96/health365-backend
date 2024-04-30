from fastapi import FastAPI
from passlib.handlers.bcrypt import bcrypt
from tortoise.contrib.fastapi import register_tortoise
from app.database.models.user import User
from app.database.models.patient import Patient
from app.helpers.constant import DB_URL

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["app.database.models.user","app.database.models.patient", "aerich.models"],
            "default_connection": "default",
        },
    },
}


def init_db(app: FastAPI) -> None:

    register_tortoise(
        app,
        db_url=DB_URL,
        modules={"models": ["app.database.models.user", "app.database.models.patient"]},
        generate_schemas=True,
        add_exception_handlers=False
    )

    # users_exist = await User.exists()
    #
    # if users_exist is False:
    #     password = bcrypt.hash("admin123")
    #     await User.create(
    #         email='samrand96@gmail.com',
    #         password_hash=password,
    #         role='admin',
    #         first_name='Samrand',
    #         last_name='Hassan',
    #         is_active=True,
    #         mobile_number='1234567890',
    #         status='Active'
    #     )
