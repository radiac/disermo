"""
Disermo constants
"""
from .utils import OrderedEnum


class Status(OrderedEnum):
    DISABLED = 0
    OK = 1
    WARN = 2
    ERROR = 3
