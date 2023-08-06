from typing import Callable
from datetime import datetime

class Event:
    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func

class Command:
    def __init__(self, name: str, func: Callable, _type: int):
        self.name = name
        self.func = func
        self.type = _type

class Component:
    def __init__(self, parent, custom_id, func: Callable, timeout: float = 0.0, is_single_use: bool = False):
        self.custom_id = custom_id
        self.parent = parent
        self.func = func
        self.timeout = timeout
        self.created_at = datetime.utcnow()
        self.is_single_use = is_single_use

