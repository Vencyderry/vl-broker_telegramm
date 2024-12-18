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
    date_production,
    promotions
)

single_handlers = [
    start.dp,
    currency.dp,
    price.dp,
    application.dp,
    clear.dp,
    rules.dp,
    personal_office.dp
]

groups_handlers = [
    single_handlers,
    admins.group_handlers,
    calculator.group_handlers,
    info_svh.group_handlers,
    useful.group_handlers,
    faq.group_handlers,
    date_production.group_handlers,
    promotions.group_handlers
]

handlers = []

for group_handlers in groups_handlers:
    handlers.extend(group_handlers)

__all__ = ["handlers"]
