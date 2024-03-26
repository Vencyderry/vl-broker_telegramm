from . import (
    start,
    currency,
    price,
    application,
    clear,
    useful,
    rules
)

from . import (
    admins,
    calculator,
    info_svh,
    useful
)

single_handlers = [
    currency.dp,
    start.dp,
    price.dp,
    application.dp,
    clear.dp,
    rules.dp
]

groups_handlers = [
    admins.group_handlers,
    calculator.group_handlers,
    info_svh.group_handlers,
    useful.group_handlers,
    single_handlers
]

handlers = []

for group_handlers in groups_handlers:
    handlers.extend(group_handlers)

__all__ = ["handlers"]
