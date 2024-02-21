import time

from models import *
from typing import List, Any
from peewee import InternalError, DoesNotExist


def get_system() -> None | System:
    return System.get(System.id == 1)


def get_user(
        column: User,
        value: Any) -> None | User:

    try:
        user = User.get(column == value)
    except DoesNotExist:
        user = None

    return user


def get_users(
        title: str,
        value: Any) -> None | List[User]:
    try:
        attr = getattr(User, str(title))
    except AttributeError:
        return None

    return User.select().where(attr == value)


def get_users_all() -> List[User]:
    return User.select()


def set_users(
        title: str,
        value: Any,
        title_set: str,
        value_set: Any):
    try:
        attr = getattr(User, title)
        attr_set = getattr(User, title_set)
    except AttributeError:
        return None

    User.update({attr_set: value_set}).where(attr == value).execute()


# Добавление строк
def add_system():
    row = System()
    row.save()


def add_user(tgid: int, nick: str, nickname: str):
    User(
        tgid=tgid,
        nick=nick.lower().strip(),
        nickname=nickname,
        registration_date=time.time()
    ).save()

    user = get_user(User.tgid, tgid)
    user.registration_date = time.time()

