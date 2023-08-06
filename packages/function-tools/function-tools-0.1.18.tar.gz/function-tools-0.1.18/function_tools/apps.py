from django.apps import (
    AppConfig,
)

from function_tools.management.storages import (
    ImplementationStrategyStorage,
)


class FunctionToolsConfig(AppConfig):
    name = 'function_tools'
    label = 'function_tools'

    def ready(self):
        """
        На момент готовности приложения, необходимо добавить зарегистрированные стратегии в модель-перечисление
        ImplementationStrategy
        """
        from function_tools.models import (
            ImplementationStrategy,
        )
        strategy_storage = ImplementationStrategyStorage()

        for strategy in strategy_storage.implementation_strategy_map.values():
            if strategy.key:
                ImplementationStrategy.extend(
                    key=strategy.key.upper(),
                    title=strategy.title,
                )
