from operations import *
from tools import decode


def is_sr_admin(user_tgid: int) -> bool:
    system = get_system()
    admins = decode(system.administrators)

    if user_tgid in admins:
        return True
    return False


def is_admin(user_tgid: int) -> bool:
    user = get_user(User.tgid, user_tgid)

    if user.group == "Admin":
        return True
    return False
