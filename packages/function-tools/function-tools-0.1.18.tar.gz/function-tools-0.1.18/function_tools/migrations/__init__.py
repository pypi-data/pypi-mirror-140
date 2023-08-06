import sys
from importlib import (
    import_module,
)
from inspect import (
    isclass,
)
from typing import (
    Dict,
    List,
    Tuple,
)

from django.apps import (
    apps,
)
from django.core.management import (
    color_style,
)
from django.db.models.signals import (
    post_migrate,
)

from function_tools.consts import (
    FUNCTION_TOOLS_FUNCTIONS_MODULE_PATH,
    FUNCTIONS_MODULE,
)
from function_tools.functions import (
    BaseFunction,
)
from function_tools.models import (
    RegisteredFunction,
)


class FunctionRegistrar:
    """
    Регистратор функций системы

    Отвечает за поиск всех реализованных функций системы и их регистрацию в модели RegisteredFunction. Путь до
    приложения функции является уникальным, т.к. каждая функция реализуется в отдельном приложении и это приложение
    регистрируется в INSTALLED_APPS. Также указывается название класса функции и ее наименование. Имя функции берется
    из конфига Django-приложения из свойства verbose_name
    """

    def __init__(self):
        self._functions: Dict[str, Tuple[str, List[str]]] = {}

        self._registered_functions = RegisteredFunction.objects.all()
        self._registered_functions_map = {
            registered_function.function_path: registered_function
            for registered_function in self._registered_functions
        }

        self._style = color_style()

    def _find_functions(self):
        """
        Поиск реализованных функций системы
        """
        functions_module = import_module(FUNCTION_TOOLS_FUNCTIONS_MODULE_PATH)
        excluded_base_functions = [
            name
            for name, class_ in functions_module.__dict__.items()
            if isclass(class_) and issubclass(class_, BaseFunction)
        ]

        app_configs = apps.get_app_configs()
        function_app_configs = list(filter(lambda config: getattr(config.module, FUNCTIONS_MODULE, None), app_configs))

        for app_config in function_app_configs:
            app_functions = [
                (name, class_)
                for name, class_ in app_config.module.functions.__dict__.items()
                if isclass(class_) and issubclass(class_, BaseFunction) and name not in excluded_base_functions
            ]

            for app_function in app_functions:
                self._functions[f'{app_config.module.__name__}.functions.{app_function[0]}'] = (
                    app_function[1].verbose_name, app_function[1].tags
                )

    def _process_creating_functions(self):
        """
        Обработка создаваемых функций системы
        """
        for_creating = []

        creating_function_paths = filter(lambda f_p: f_p not in self._registered_functions_map, self._functions.keys())

        for creating_function_path in creating_function_paths:
            for_creating.append(
                RegisteredFunction(
                    function_path=creating_function_path,
                    verbose_name=self._functions[creating_function_path][0],
                    tags=self._functions[creating_function_path][1],
                )
            )

        RegisteredFunction.objects.bulk_create(objs=for_creating)

    def _process_updating_functions(self):
        """
        Обработка обновляемых функций системы
        """
        updating_function_paths = filter(lambda f_p: f_p in self._registered_functions_map, self._functions.keys())

        for updating_function_path in updating_function_paths:
            if (
                self._registered_functions_map[updating_function_path].verbose_name != self._functions[updating_function_path][0]  # noqa
                or self._registered_functions_map[updating_function_path].tags != self._functions[updating_function_path][1]  # noqa
            ):
                self._registered_functions_map[updating_function_path].verbose_name = self._functions[updating_function_path][0]  # noqa
                self._registered_functions_map[updating_function_path].tags = self._functions[updating_function_path][1]  # noqa

                # Иду на преступный шаг с генерацией некоторого количества запросов в БД, все только для того, чтобы
                # изменить дату и время обновления записи
                self._registered_functions_map[updating_function_path].save()

    def _process_deleted_functions(self):
        """
        Обработка удаленных, перенесенных или находящихся в отключенных плагинах функций системы
        """
        deleted_functions = set(self._registered_functions_map.keys()).difference(self._functions.keys())
        if deleted_functions:
            for deleted_function in deleted_functions:
                sys.stdout.write(
                    self._style.NOTICE(
                        f'Found registered function in the database, but not found implementation. Function with path "'
                        f'{deleted_function}". Please, check it!\n'
                    )
                )

    def _register(self):
        """
        Регистрация реализованных функций системы
        """
        self._process_creating_functions()
        self._process_updating_functions()
        self._process_deleted_functions()

    def run(self):
        self._find_functions()
        self._register()


def post_migrate_receiver(sender, app_config, **kwargs):
    """
    Выполняет регистрацию реализованных в проекте функций
    """
    if app_config.name == 'function_tools':
        registrar = FunctionRegistrar()
        registrar.run()


post_migrate.connect(post_migrate_receiver)
