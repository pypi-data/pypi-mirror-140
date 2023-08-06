from typing import Callable
from .task import Task

def use_task(func_name: str):
    return type(func_name, (FunctionalTask,))

class FunctionalTask(Task):
    

    @property
    def func_run(self) -> Callable:
        return getattr(self, '_func_run', lambda: None)
    @func_run.setter
    def func_run(self, func: Callable) -> None:
        self._func_run = func
    def register_run(self, func: Callable) -> None:
        self.func_run = func
    def run(self) -> None:
        self.func_run()
    
    @property
    def func_on_create(self) -> Callable:
        return getattr(self, '_func_on_create', lambda: None)
    @func_on_create.setter
    def func_on_create(self, func: Callable) -> None:
        self._func_on_create = func
    def register_on_create(self, func: Callable) -> None:
        self.func_on_create = func
    def on_create(self) -> None:
        self.func_on_create()