from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Optional,
)

from function_tools.caches import (
    CacheStorage,
)
from function_tools.errors import (
    BaseError,
)
from function_tools.functions import (
    BaseFunction,
    LazyDelegateSavingPredefinedQueueFunction,
    LazySavingPredefinedQueueFunction,
)
from function_tools.helpers import (
    BaseFunctionHelper,
    BaseRunnerHelper,
)
from function_tools.managers import (
    RunnerManager,
)
from function_tools.presenters import (
    ResultPresenter,
)
from function_tools.results import (
    BaseRunnableResult,
)
from function_tools.runners import (
    BaseRunner,
    LazySavingRunner,
)
from function_tools.validators import (
    BaseValidator,
)


class FunctionImplementationStrategy(ABC):
    """
    Базовый класс стратегии реализации функции
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self._manager_class = None
        self._runner_class = None
        self._function_class = None
        self._runner_helper_class = None
        self._function_helper_class = None
        self._runner_validator_class = None
        self._function_validator_class = None
        self._runner_cache_storage_class = None
        self._function_cache_storage_class = None
        self._error_class = None
        self._runner_result_class = None
        self._function_result_class = None
        self._result_presenter_class = None

        self._key = self._prepare_key()
        self._title = self._prepare_title()
        self._function_template_name = self._prepare_function_template_name()

        self._prepare()

    @property
    def key(self) -> Optional[str]:
        """
        Возвращает уникальный идентификатор стратегии создания функции
        """
        return self._key

    @property
    def title(self) -> Optional[str]:
        """
        Возвращает название стратегии создания функции
        """
        return self._title

    @property
    def function_template_name(self) -> Optional[str]:
        """
        Возвращает наименование стратегии реализации функции
        """
        return self._function_template_name

    @property
    def manager_class(self):
        return self._manager_class

    @property
    def manager_class_name(self):
        return self._manager_class.__name__

    @property
    def manager_class_module(self):
        return self._manager_class.__module__

    @property
    def runner_class(self):
        return self._runner_class

    @property
    def runner_class_name(self):
        return self._runner_class.__name__

    @property
    def runner_class_module(self):
        return self._runner_class.__module__

    @property
    def function_class(self):
        return self._function_class

    @property
    def function_class_name(self):
        return self._function_class.__name__

    @property
    def function_class_module(self):
        return self._function_class.__module__

    @property
    def runner_helper_class(self):
        return self._runner_helper_class

    @property
    def runner_helper_class_name(self):
        return self._runner_helper_class.__name__

    @property
    def runner_helper_class_module(self):
        return self._runner_helper_class.__module__

    @property
    def function_helper_class(self):
        return self._function_helper_class

    @property
    def function_helper_class_name(self):
        return self._function_helper_class.__name__

    @property
    def function_helper_class_module(self):
        return self._function_helper_class.__module__

    @property
    def runner_validator_class(self):
        return self._runner_validator_class

    @property
    def runner_validator_class_name(self):
        return self._runner_validator_class.__name__

    @property
    def runner_validator_class_module(self):
        return self._runner_validator_class.__module__

    @property
    def function_validator_class(self):
        return self._function_validator_class

    @property
    def function_validator_class_name(self):
        return self._function_validator_class.__name__

    @property
    def function_validator_class_module(self):
        return self._function_validator_class.__module__

    @property
    def runner_cache_storage_class(self):
        return self._runner_cache_storage_class

    @property
    def runner_cache_storage_class_name(self):
        return self._runner_cache_storage_class.__name__

    @property
    def runner_cache_storage_class_module(self):
        return self._runner_cache_storage_class.__module__

    @property
    def function_cache_storage_class(self):
        return self._function_cache_storage_class

    @property
    def function_cache_storage_class_name(self):
        return self._function_cache_storage_class.__name__

    @property
    def function_cache_storage_class_module(self):
        return self._function_cache_storage_class.__module__

    @property
    def error_class(self):
        return self._error_class

    @property
    def error_class_name(self):
        return self._error_class.__name__

    @property
    def error_class_module(self):
        return self._error_class.__module__

    @property
    def runner_result_class(self):
        return self._runner_result_class

    @property
    def runner_result_class_name(self):
        return self._runner_result_class.__name__

    @property
    def runner_result_class_module(self):
        return self._runner_result_class.__module__

    @property
    def function_result_class(self):
        return self._function_result_class

    @property
    def function_result_class_name(self):
        return self._function_result_class.__name__

    @property
    def function_result_class_module(self):
        return self._function_result_class.__module__

    @property
    def result_presenter_class(self):
        return self._result_presenter_class

    @property
    def result_presenter_class_name(self):
        return self._result_presenter_class.__name__

    @property
    def result_presenter_class_module(self):
        return self._result_presenter_class.__module__

    @abstractmethod
    def _prepare_key(self) -> Optional[str]:
        """
        Формирование уникального ключа стратегии создания функции
        """

    @abstractmethod
    def _prepare_title(self) -> Optional[str]:
        """
        Формирование наименования стратегии создания функции
        """
    @abstractmethod
    def _prepare_function_template_name(self) -> Optional[str]:
        """
        Формирование названия шаблона создания функции
        """

    def _prepare_manager_class(self):
        """
        Устанавливает класс менеджера
        """
        self._manager_class = RunnerManager

    def _prepare_runner_class(self):
        """
        Устанавливает класс пускателя
        """
        self._runner_class = BaseRunner

    def _prepare_function_class(self):
        """
        Устанавливает класс Функции
        """
        self._function_class = BaseFunction

    def _prepare_runner_helper_class(self):
        """
        Устанавливает класс помощника пусковика
        """
        self._runner_helper_class = BaseRunnerHelper

    def _prepare_function_helper_class(self):
        """
        Устанавливает класс помощника функции
        """
        self._function_helper_class = BaseFunctionHelper

    def _prepare_runner_validator_class(self):
        """
        Устанавливает класс валидатора пусковика
        """
        self._runner_validator_class = BaseValidator

    def _prepare_function_validator_class(self):
        """
        Устанавливает класс валидатора Функции
        """
        self._function_validator_class = BaseValidator

    def _prepare_runner_cache_storage_class(self):
        """
        Устанавливает класс хранилища кешей пусковика
        """
        self._runner_cache_storage_class = CacheStorage

    def _prepare_function_cache_storage_class(self):
        """
        Устанавливает класс хранилища кешей Функции
        """
        self._function_cache_storage_class = CacheStorage

    def _prepare_error_class(self):
        """
        Устанавливает класс ошибки
        """
        self._error_class = BaseError

    def _prepare_runner_result_class(self):
        """
        Устанавливает класс результата
        """
        self._runner_result_class = BaseRunnableResult

    def _prepare_function_result_class(self):
        """
        Устанавливает класс результата
        """
        self._function_result_class = BaseRunnableResult

    def _prepare_result_presenter_class(self):
        """
        Устанавливает класс презентера результата
        """
        self._result_presenter_class = ResultPresenter

    def _prepare(self):
        """
        Подготовка компонентов реализации функции
        """
        self._prepare_manager_class()
        self._prepare_runner_class()
        self._prepare_function_class()
        self._prepare_runner_helper_class()
        self._prepare_function_helper_class()
        self._prepare_runner_validator_class()
        self._prepare_function_validator_class()
        self._prepare_function_cache_storage_class()
        self._prepare_runner_cache_storage_class()
        self._prepare_error_class()
        self._prepare_runner_result_class()
        self._prepare_function_result_class()
        self._prepare_result_presenter_class()


class SyncBaseRunnerBaseFunctionImplementationStrategy(FunctionImplementationStrategy):
    """
    Реализация простой функции без отложенного сохранения
    """

    def _prepare_key(self) -> str:
        """
        Возвращает уникальный идентификатор стратегии создания функции
        """
        return 'SYNC_BASE_FUNCTION'

    def _prepare_title(self) -> str:
        """
        Возвращает название стратегии создания функции
        """
        return 'Реализация простой функции без отложенного сохранения'

    def _prepare_function_template_name(self) -> Optional[str]:
        """
        Формирование названия шаблона создания функции
        """
        return 'm3_function_sync_template'


class SyncBaseRunnerLazySavingPredefinedQueueFunctionImplementationStrategy(FunctionImplementationStrategy):
    """
    Реализация функции с отложенным сохранением и предустановленной очередью объектов на сохранение
    """

    def _prepare_key(self) -> str:
        """
        Возвращает уникальный идентификатор стратегии создания функции
        """
        return 'SYNC_LAZY_SAVING_FUNCTION'

    def _prepare_title(self) -> str:
        """
        Возвращает название стратегии создания функции
        """
        return (
            'Реализация функции с отложенным сохранением и предустановленной очередью объектов на сохранение. '
            'Сохранение производится после удачной работы функции'
        )

    def _prepare_function_template_name(self) -> Optional[str]:
        """
        Формирование названия шаблона создания функции
        """
        return 'm3_function_sync_template'

    def _prepare_function_class(self):
        """
        Устанавливает класс Функции
        """
        self._function_class = LazySavingPredefinedQueueFunction


class SyncLazySavingRunnerLazyDelegateSavingPredefinedQueueFunctionImplementationStrategy(FunctionImplementationStrategy):
    """
    Реализация функции с отложенным сохранением его делегированием пускателю. Когда все функции отработают, только
    после этого запускается сохранение объектов из очередей каждой функции
    """

    def _prepare_key(self) -> str:
        """
        Возвращает уникальный идентификатор стратегии создания функции
        """
        return 'SYNC_LAZY_SAVING_RUNNER_FUNCTION'

    def _prepare_title(self) -> str:
        """
        Возвращает название стратегии создания функции
        """
        return (
            'Реализация функции с отложенным сохранением его делегированием пускателю. Когда все функции отработают, '
            'только после этого запускается сохранение объектов из очередей каждой функции'
        )

    def _prepare_function_template_name(self) -> Optional[str]:
        """
        Формирование названия шаблона создания функции
        """
        return 'm3_function_sync_template'

    def _prepare_runner_class(self):
        """
        Устанавливает класс пусковика
        """
        self._runner_class = LazySavingRunner

    def _prepare_function_class(self):
        """
        Устанавливает класс Функции
        """
        self._function_class = LazyDelegateSavingPredefinedQueueFunction
