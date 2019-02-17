"""
Checks which perform Remote requests
"""
import requests
from typing import Union

from ..constants import Status
from .base import Check


class Web(Check):
    url: str
    timeout: float
    status_code: int = 200
    content_contains: Union[str, None]

    def __init__(
        self,
        url: str,
        timeout: float,
        label: str = None,
        status_code: int = 200,
        content_contains: str = None,
    ):
        super().__init__(label)
        self.url = url
        self.status_code = status_code
        self.content_contains = content_contains

    def update(self) -> None:
        response = requests.get(
            self.url,
            timeout=self.timeout,
        )

        if response.status_code != self.status_code:
            self.status = Status.ERROR
            self.data = {
                'error': (
                    f'Expected status {self.status_code}, '
                    f'instead found {response.status_code}.'
                ),
            }
            return

        if (
            self.content_contains and
            self.content_contains not in response.text
        ):
            self.status = Status.ERROR
            self.data = {
                'error': 'Expected content not found',
            }
            return

        self.status = Status.OK
        self.data = {
            'time': response.elapsed.total_seconds(),
        }
