
class Punishment:
    def __init__(self, status):
        self.status = status

    FREE = "free"
    WARN = "warn"
    KICK = "kick"

    def is_free(self) -> bool:
        return self.status == Punishment.FREE

    def is_warn(self) -> bool:
        return self.status == Punishment.WARN

    def is_kick(self) -> bool:
        return self.status == Punishment.KICK


