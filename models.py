from playhouse.migrate import *


db = SqliteDatabase('vlb_tg.db')


class BaseModel(Model):
    class Meta:
        database = db


class System(BaseModel):
    id = PrimaryKeyField(null=False)

    start_time = DateTimeField(default=0)
    synchr_time = DateTimeField(default=0)

    messages_processed = IntegerField(default=0)
    commands_processed = IntegerField(default=0)
    messages_processed_all = IntegerField(default=0)
    commands_processed_all = IntegerField(default=0)

    administrators = TextField(default='[933676802]')

    applications = TextField(default='{}')

    statistic_application = IntegerField(default=0)
    statistic_svh = IntegerField(default=0)
    statistic_calculator = IntegerField(default=0)
    statistic_currency = IntegerField(default=0)
    statistic_price = IntegerField(default=0)
    statistic_useful = IntegerField(default=0)
    statistic_personal_office = IntegerField(default=0)
    statistic_start = IntegerField(default=0)

    statistic_time = TextField(default='{}')

    price_pdf = TextField(default='')

    class Meta(BaseModel):
        db_table = "system"
        order_by = ('id',)


class User(BaseModel):
    id = PrimaryKeyField(null=False)

    tgid = IntegerField(unique=True)
    username = TextField()

    group = TextField(default='Default')

    country = TextField(default='Unknown')

    registration_date = DateTimeField(default=0)
    join_chat_date = DateTimeField(default=0)

    last_synch = IntegerField(default=0)
    cooldown_rules = DateTimeField(default=0)

    class Meta(BaseModel):
        db_table = "user"
        order_by = ('id',)


if __name__ == "__main__":

    migrator = SqliteMigrator(db)
    migrate(
        migrator.add_column("system", "statistic_personal_office", IntegerField(default=0))
    )

