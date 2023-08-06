import inspect
import sys
from importlib import (
    import_module,
)
from importlib._bootstrap import (
    module_from_spec,
)
from importlib._bootstrap_external import (
    spec_from_file_location,
)
from pathlib import (
    Path,
)
from typing import (
    Dict,
    List,
    Tuple,
    Type,
)

from django.conf import (
    settings,
)

from function_tools.management.strategies import (
    FunctionImplementationStrategy,
)


class ImplementationStrategyStorage:
    """
    Хранилище реализованных стратегий создания функций
    """

    def __init__(self):
        self._implementation_strategy_map = self._prepare_implementation_strategy_map()

    @property
    def implementation_strategy_map(self) -> Dict[str, Type[FunctionImplementationStrategy]]:
        """
        Возвращает карту соответствия зарегистрированных стратегий реализации функций
        """
        return self._implementation_strategy_map

    def get_strategy_implementation(
        self,
        strategy_key: str,
    ):
        """
        Возвращает стратегию реализации функции по значению перечисления
        """
        return self._implementation_strategy_map[strategy_key]

    def _find_strategies_modules(self) -> List[Tuple[str, str]]:
        """
        Поиск модулей содержащих стратегии создания функций
        """
        strategies_modules = []
        checked_packed_paths = []

        for app_name in settings.INSTALLED_APPS:
            app_module = import_module(app_name)
            app_path = app_module.__path__

            # Если поиск уже осуществлялся по родительской директории,
            # то проверку нужно пропустить
            is_already_checked = False
            for check_packed_path in checked_packed_paths:
                if app_path in check_packed_path:
                    is_already_checked = True

                    break

            if is_already_checked:
                continue

            application_path = Path(app_path[0])
            strategies_file_patterns = [
                '**/**/strategies.py',
            ]

            for strategies_file_pattern in strategies_file_patterns:
                strategies_modules_paths = application_path.glob(
                    strategies_file_pattern
                )
                for strategies_module_path in strategies_modules_paths:
                    strategies_module_path = str(strategies_module_path)

                    module_name = (
                        str(strategies_module_path).split('/')[-1].split('.')[0]
                    )

                    spec = spec_from_file_location(
                        name=module_name,
                        location=strategies_module_path,
                    )
                    strategies_module = module_from_spec(
                        spec=spec,
                    )
                    spec.loader.exec_module(strategies_module)
                    strategies_modules.append(
                        (
                            strategies_module,
                            strategies_module_path,
                        )
                    )

        return strategies_modules

    def _prepare_implementation_strategy_map(self) -> Dict[str, FunctionImplementationStrategy]:
        """
        Поиск фабрик во всех подключенных приложениях
        """
        strategy_map = {}
        strategies_modules = self._find_strategies_modules()

        for strategies_module, module_path in strategies_modules:
            strategy_classes_names = list(filter(
                lambda name: (
                    inspect.isclass(getattr(strategies_module, name))
                    and issubclass(getattr(strategies_module, name), FunctionImplementationStrategy)
                    and getattr(strategies_module, name).__name__ != 'FunctionImplementationStrategy'
                ),
                dir(strategies_module)
            ))

            if strategy_classes_names:
                for strategy_class_name in strategy_classes_names:
                    strategy_class: Type[FunctionImplementationStrategy] = getattr(
                        strategies_module,
                        strategy_class_name
                    )

                    strategy = strategy_class()

                    if strategy.key in strategy_map:
                        if strategy.__class__.__name__ != strategy_map[strategy.key].__class__.__name__:
                            sys.stdout.write(
                                f'Please, check {strategy.__class__.__name__} and '
                                f'{strategy_map[strategy.key].__class__.__name__} implementation. Found duplicates '
                                f'unique strategies implementation key {strategy.key}\n'
                            )
                    else:
                        strategy_map[strategy.key] = strategy

        return strategy_map
