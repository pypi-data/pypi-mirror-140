from __future__ import annotations
from typing import Callable, Any, TypeVar
from ..decorators import Command, Event

import inspect

ExtT  = TypeVar('ExtT', bound='Extension')
FuncT = TypeVar('FuncT', bound=Callable[..., Any])

class Extension:
    def __init__(self):
        self.commands = []
        self.__listeners__ = []
    
    @classmethod
    def listener(self, name: str):
        def decorator(func):
            actual = func
            if isinstance(actual, staticmethod):
                actual = actual.__func__
            if not inspect.iscoroutinefunction(actual):
                raise TypeError("Listener functions must be coroutine")
            
            actual.__ext_command__ = False
            actual.__ext_listener__ = True
            actual.__listener_name__ = name
            return actual
        return decorator

    @classmethod
    def command(self, name: str, _type: int):
        def decorator(func):
            actual = func
            if isinstance(actual, staticmethod):
                actual = actual.__func__

            if not inspect.iscoroutinefunction(actual):
                raise TypeError('Command functions must be coroutine')

            actual.__ext_command__ = True
            actual.__ext_listener__ = False
            actual.__command_data__ = (name, _type)
            return actual 
        return decorator

    def _insert(self):
        objects = []
        for attribute in [attr[1] for attr in inspect.getmembers(self, inspect.iscoroutinefunction) if not attr[0].startswith('__') and not attr[0].endswith('__')]:
            try:
                if attribute.__ext_command__:
                    obj = Command(attribute.__command_data__[0], attribute, attribute.__command_data__[1])
                elif attribute.__ext_listener__:
                    obj = Event(attribute.__listener_name__, attribute)
                objects.append(obj)
            except AttributeError:
                pass
        return objects
