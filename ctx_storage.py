from typing import Any, Hashable, Optional

from abc import ABC, abstractmethod
from typing import Any, Hashable

import contextvars


class BaseContext:
    """Parent BaseContext class. Idea taken from aiogram"""

    ctx_instance: Any

    def __init_subclass__(cls, **kwargs):
        if not contextvars:
            raise LookupError(f"To use {cls.__name__} you have to install contextvars")

        cls.ctx_instance = contextvars.ContextVar(kwargs.get("ctx_name") or cls.__name__)
        return cls

    @classmethod
    def get_instance(cls, no_error: bool = True) -> Any:
        if no_error:
            return cls.ctx_instance.get(None)
        return cls.ctx_instance.get()

    @classmethod
    def set_instance(cls, value: Any) -> None:
        cls.ctx_instance.set(value)


class ABCStorage(ABC):

    @abstractmethod
    def get(self, key: Hashable) -> Any:
        pass

    @abstractmethod
    def set(self, key: Hashable, value: Any) -> None:
        pass

    @abstractmethod
    def delete(self, key: Hashable) -> None:
        pass

    @abstractmethod
    def contains(self, key: Hashable) -> bool:
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __contains__(self, item: str) -> bool:
        return self.contains(item)

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self.set(key, value)

    def __getitem__(self, key: Hashable) -> Any:
        return self.get(key)


class CtxStorage(ABCStorage, BaseContext):
    storage: dict = {}

    def __init__(
            self,
            default: Optional[dict] = None,
            force_reset: bool = False,
    ):
        if not self.get_instance() or force_reset:
            default = default or {}
            self.storage = default
            self.set_instance(self)

    def set(self, key: Hashable, value: Any) -> None:
        current_storage = self.get_instance().storage
        current_storage[key] = value
        self.set_instance(CtxStorage(current_storage, True))

    def get(self, key: Hashable) -> Any:
        return self.get_instance().storage.get(key)

    def delete(self, key: Hashable) -> None:
        new_storage = self.get_instance().storage
        new_storage.pop(key)
        self.set_instance(CtxStorage(new_storage, True))

    def contains(self, key: Hashable) -> bool:
        return key in self.get_instance().storage
