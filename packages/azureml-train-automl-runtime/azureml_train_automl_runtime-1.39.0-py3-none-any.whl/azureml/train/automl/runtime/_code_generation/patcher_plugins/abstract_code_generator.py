# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Type

from azureml.automl.core import _codegen_utilities


class AbstractCodeGenerator(ABC):
    @classmethod
    @abstractmethod
    def can_handle(cls, obj: Any) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    @contextmanager
    def patch(cls) -> Any:
        raise NotImplementedError

    @classmethod
    def _patch_class(cls, clazz: Type[Any], func: Optional[Callable[..., str]] = None) -> Iterator[Callable[..., str]]:
        old_repr = clazz.__repr__

        def generic_repr(obj: Any) -> str:
            return cls.get_repr(obj)

        if func is None:
            func = generic_repr

        try:
            clazz.__repr__ = func
            yield old_repr
        finally:
            clazz.__repr__ = old_repr

    @classmethod
    def get_repr(cls, obj: Any) -> str:
        return _codegen_utilities.generate_repr_str(obj.__class__, cls.get_params(obj))

    @classmethod
    @abstractmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def get_imports(cls, obj: Any) -> Iterable[_codegen_utilities.ImportInfoType]:
        params = cls.get_params(obj)
        return _codegen_utilities.get_recursive_imports(params)
