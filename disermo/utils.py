"""
Generic utility functions
"""
from enum import Enum
import re


_re_camel_to_sentence = re.compile(r'([A-Z]+(?=[A-Z][a-z]|$)|[A-Z][a-z])')


class OrderedEnum(Enum):  # pragma: no cover - comes from python docs
    """
    Ordered enum to allow value comparison, from python docs
    """
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


def camel_to_sentence(val: str) -> str:
    """
    Given a camelCase, convert it into Sentence case

    It is acroynm-aware
    """
    if not val:
        return ''

    words = [
        word if all([char.isupper() for char in word]) else word.lower()
        for word in _re_camel_to_sentence.sub(r' \1', val).split(' ')
        if word
    ]

    sentence = ' '.join(words)
    return f'{sentence[0].upper()}{sentence[1:]}'
