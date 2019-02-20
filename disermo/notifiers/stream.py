"""
Stream notifier
"""
from typing import TYPE_CHECKING, List, TextIO

from .base import Notifier

if TYPE_CHECKING:  # pragma: no cover
    from ..checks import Check
    from ..node import Node


class Stream(Notifier):
    stream: TextIO

    def __init__(self, stream: TextIO):
        self.stream = stream

    def send(self, node: 'Node', checks: 'List[Check]') -> None:
        check: Check
        depth: int
        for check, depth in node.iter_flat_depth_checks():
            self.stream.write(
                f'{"  " * depth}{check.label}: {check.status.name.title()}\n'
            )
