"""Каталог заданий, отсортированный по ID."""

from .arrays_collections import TASKS as ARRAYS_COLLECTIONS_TASKS
from .async_concurrency import TASKS as ASYNC_CONCURRENCY_TASKS
from .basics import TASKS as BASICS_TASKS
from .classes_oop import TASKS as CLASSES_OOP_TASKS
from .conditions_loops import TASKS as CONDITIONS_LOOPS_TASKS
from .enums_structs import TASKS as ENUMS_STRUCTS_TASKS
from .files_json import TASKS as FILES_JSON_TASKS
from .interfaces_generics import TASKS as INTERFACES_GENERICS_TASKS
from .linq import TASKS as LINQ_TASKS
from .methods import TASKS as METHODS_TASKS
from .null_exceptions import TASKS as NULL_EXCEPTIONS_TASKS
from .strings_console import TASKS as STRINGS_CONSOLE_TASKS

# Задания сгруппированы по темам; в общем каталоге сохраняем порядок по ID.
TASKS = sorted(
    [
        *BASICS_TASKS,
        *CONDITIONS_LOOPS_TASKS,
        *METHODS_TASKS,
        *ARRAYS_COLLECTIONS_TASKS,
        *CLASSES_OOP_TASKS,
        *NULL_EXCEPTIONS_TASKS,
        *LINQ_TASKS,
        *ASYNC_CONCURRENCY_TASKS,
        *STRINGS_CONSOLE_TASKS,
        *ENUMS_STRUCTS_TASKS,
        *INTERFACES_GENERICS_TASKS,
        *FILES_JSON_TASKS,
    ],
    key=lambda task: task["id"],
)

__all__ = ["TASKS"]
