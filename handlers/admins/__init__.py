from . import set_admin, mstats, pin_message, mstats, distribution

group_handlers = [
    pin_message.dp,
    mstats.dp,
    set_admin.dp,
    distribution.dp
]