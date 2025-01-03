from playhouse.migrate import *
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'vlb_tg.db')
db = SqliteDatabase(db_path)


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
    statistic_date_production = IntegerField(default=0)
    statistic_faq = IntegerField(default=0)
    statistic_start = IntegerField(default=0)

    statistic_time = TextField(default='{}')

    price_pdf = TextField(default='')
    price_text = TextField(default='')

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

    punishment = TextField(default="free")

    class Meta(BaseModel):
        db_table = "user"
        order_by = ('id',)


if __name__ == "__main__":

    migrator = SqliteMigrator(db)
    migrate(migrator.add_column("system", "price_text", TextField(default=''))
    )

