# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from enum import Enum
from typing import Any, Callable, Dict, Iterator

from .abstract_code_generator import AbstractCodeGenerator


class EnumCodeGenerator(AbstractCodeGenerator):
    @classmethod
    @contextmanager
    def patch(cls) -> Any:
        return cls._patch_class(Enum, lambda obj: cls.get_repr(obj))

    @classmethod
    def get_repr(cls, obj: Any) -> str:
        return f"{obj.__class__.__name__}.{obj.name}"

    @classmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return "Enum" in [mro.__name__ for mro in obj.__class__.__mro__]
