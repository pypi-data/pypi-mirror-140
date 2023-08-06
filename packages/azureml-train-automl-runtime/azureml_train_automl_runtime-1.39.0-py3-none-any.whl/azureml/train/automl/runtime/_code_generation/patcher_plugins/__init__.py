# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import ExitStack, contextmanager
from typing import Any, Callable, ContextManager, Dict, Iterable, Iterator, cast

from azureml.automl.core import _codegen_utilities

from .abstract_code_generator import AbstractCodeGenerator
from .base_estimator import BaseEstimatorCodeGenerator
from .enum import EnumCodeGenerator
from .featurization_config import FeaturizationConfigCodeGenerator
from .multi_grain_forecast_base import MultiGrainForecastBaseCodeGenerator
from .rolling_window import RollingWindowCodeGenerator

plugins = [
    RollingWindowCodeGenerator(),
    MultiGrainForecastBaseCodeGenerator(),
    FeaturizationConfigCodeGenerator(),
    BaseEstimatorCodeGenerator(),
    EnumCodeGenerator(),
]


class CompositeCodeGenerator(AbstractCodeGenerator):
    @classmethod
    @contextmanager
    def patch(cls) -> Any:
        with ExitStack() as stack:
            for plugin in plugins:
                stack.enter_context(cast(ContextManager[Callable[..., str]], plugin.patch()))
            yield

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return any(plugin.can_handle(obj) for plugin in plugins)

    @classmethod
    def get_repr(cls, obj: Any) -> str:
        for plugin in plugins:
            if plugin.can_handle(obj):
                return plugin.get_repr(obj)
        raise ValueError()

    @classmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        for plugin in plugins:
            if plugin.can_handle(obj):
                return plugin.get_params(obj)
        raise ValueError()

    @classmethod
    def get_imports(cls, obj: Any) -> Iterable[_codegen_utilities.ImportInfoType]:
        for plugin in plugins:
            if plugin.can_handle(obj):
                return plugin.get_imports(obj)
        raise ValueError()


patcher = CompositeCodeGenerator()
