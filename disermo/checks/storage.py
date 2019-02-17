"""
Storage checks
"""
from __future__ import annotations
import os

from ..constants import Status
from .base import Check


DEFAULT_WARNING = 0.1
DEFAULT_ERROR = 0.05


class FreeSpace(Check):
    drive: str
    warning: float
    error: float

    def __init__(
        self,
        drive: str,
        label: str = None,
        warning: float = DEFAULT_WARNING,
        error: float = DEFAULT_ERROR,
    ) -> None:
        super().__init__(label)
        self.drive = drive
        self.warning = warning
        self.error = error

    def update(self) -> None:
        data = os.statvfs(self.drive)
        total_bytes = data.f_frsize * data.f_blocks
        # free_bytes = data.f_frsize * data.f_bfree
        allowed_bytes = data.f_frsize * data.f_bavail
        percent_free = allowed_bytes / total_bytes

        self.data = {
            'total': total_bytes,
            'free': allowed_bytes,
        }

        if percent_free < self.error:
            self.status = Status.ERROR
        elif percent_free < self.warning:
            self.status = Status.WARN
        else:
            self.status = Status.OK
