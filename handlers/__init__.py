from . import (
    start,
    currency,
    price,
    application,
    clear,
    useful,
    rules,
    personal_office
)

from . import (
    admins,
    calculator,
    info_svh,
    useful,
    faq,
    date_production
)

single_handlers = [
    currency.dp,
    start.dp,
    price.dp,
    application.dp,
    clear.dp,
    rules.dp,
    personal_office.dp
]

groups_handlers = [
    admins.group_handlers,
    calculator.group_handlers,
    info_svh.group_handlers,
    useful.group_handlers,
    faq.group_handlers,
    date_production.group_handlers,
    single_handlers
]

handlers = []

for group_handlers in groups_handlers:
    handlers.extend(group_handlers)

__all__ = ["handlers"]
