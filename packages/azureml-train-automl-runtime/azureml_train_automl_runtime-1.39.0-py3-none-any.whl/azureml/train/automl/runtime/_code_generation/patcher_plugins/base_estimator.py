# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import sys
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, cast

from sklearn.base import BaseEstimator

from .abstract_code_generator import AbstractCodeGenerator


class BaseEstimatorCodeGenerator(AbstractCodeGenerator):
    @classmethod
    @contextmanager
    def patch(cls) -> Any:
        # sklearn BaseEstimator uses a different signature from normal, so we add this closure here.
        def _sklearn_repr(self: Any, N_CHAR_MAX: int = sys.maxsize) -> str:
            return cls.get_repr(self)

        return cls._patch_class(BaseEstimator, _sklearn_repr)

    @classmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        return cast(Dict[str, Any], obj.get_params(deep=False))

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return isinstance(obj, BaseEstimator)
