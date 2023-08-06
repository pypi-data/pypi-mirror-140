from typing import (
    Type,
    Union,
)

from function_tools.helpers import (
    BaseFunctionHelper,
    BaseHelper,
    BaseRunnerHelper,
)
from function_tools.validators import (
    BaseValidator,
)


class HelperMixin:
    """
    Миксин для появления помощника у сущности

    В каждый класс, использующий данный миксин должна быть добавлена

    self._helper: Union[BaseHelper, BaseFunctionHelper] = self._prepare_helper(*args, **kwargs)

    в __init__(*args, **kwargs)
    """

    @property
    def helper(self):
        """
        Возвращает помощника
        """
        return self._helper

    def _prepare_helper_class(self) -> Union[Type[BaseHelper], Type[BaseFunctionHelper]]:
        """
        Возвращает класс помощника
        """
        return BaseHelper

    def _prepare_helper(self, *args, **kwargs):
        """
        Точка расширения для создания помощника.
        """
        helper_class = self._prepare_helper_class()

        if issubclass(helper_class, (BaseHelper, BaseFunctionHelper)):
            helper = helper_class(*args, **kwargs)
        else:
            helper = BaseHelper(*args, **kwargs)

        return helper


class ValidatorMixin:
    """
    Миксин для появления валидатора у сущности

    У класса, использующего миксин необходимо добавить

    self._validator: BaseValidator = self._prepare_validator(*args, **kwargs)

    в __init__(*args, **kwargs)
    """

    def _prepare_validator_class(self) -> Type[BaseValidator]:
        """
        Возвращает класс валидатор
        """
        return BaseValidator

    def _prepare_validator(self, *args, **kwargs):
        """
        Точка расширения для создания валидатора
        """
        validator_class = self._prepare_validator_class()

        if issubclass(validator_class, BaseValidator):
            validator = validator_class(*args, **kwargs)
        else:
            validator = BaseValidator(*args, **kwargs)

        return validator

    def before_validate(self):
        """
        Расширение поведения запускаемого объекта перед запуском проверок
        """

    def validate(self):
        """
        Публичный метод для запуска валидатора сущности
        """
        if self._validator:
            self._validator.validate(self)

    def after_validate(self):
        """
        Возможность расширения запускаемого объекта после валидации
        """


class GlobalHelperMixin:
    """
    Миксин добавляющий возможность установки глобального помощника

    У классов наследников должна быть добавлена

    self._global_helper: BaseRunnerHelper = self._prepare_global_helper(*args, **kwargs)

    в __init__(*args, **kwargs)
    """

    @property
    def global_helper(self):
        """
        Возвращает глобального помощника
        """
        return self._global_helper

    def _prepare_global_helper_class(self) -> Type[BaseRunnerHelper]:
        """
        Возвращает класс помощника
        """
        return BaseRunnerHelper

    def _prepare_global_helper(self, *args, **kwargs):
        """
        Предназначен для определения глобального помощника
        """
        global_helper_class = self._prepare_global_helper_class()

        if issubclass(global_helper_class, BaseRunnerHelper):
            global_helper = global_helper_class(*args, **kwargs)
        else:
            global_helper = BaseRunnerHelper()

        return global_helper

    def set_global_helper(
        self,
        global_helper: BaseRunnerHelper,
    ):
        """
        Публичный метод для установки глобального помощника
        """
        self._global_helper = global_helper
