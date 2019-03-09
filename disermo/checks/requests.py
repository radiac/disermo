"""
Checks which perform Remote requests
"""
from dataclasses import dataclass, field
from http.client import HTTPResponse
from typing import cast, Union
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

from ..constants import Status
from ..utils import Timer
from .base import Check


@dataclass
class Response:
    """
    Wrapper for an urllib Response
    """
    raw: Union[HTTPResponse, HTTPError]
    elapsed: float
    _content: str = field(init=False, repr=False)

    @property
    def code(self):
        return self.raw.code

    @property
    def content(self):
        if self._content is None:
            self._content = self.raw.read().decode('utf-8')
        return self._content


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
        timer = Timer()
        try:
            raw_response: HTTPResponse = cast(
                HTTPResponse,
                urlopen(
                    self.url,
                    timeout=self.timeout,
                ),
            )

        except HTTPError as e_response:
            # HTTP error - should be expected, analyse below
            response = Response(
                raw=e_response,
                elapsed=timer.elapsed(),
            )

        except URLError as e:
            # Unable to connect - not expected, raise immediately
            self.status = Status.ERROR
            self.data = {
                'error': f'Could not reach server: {e.reason}',
            }
            return

        else:
            # Successful request
            response = Response(
                raw=raw_response,
                elapsed=timer.elapsed(),
            )

        if response.code != self.status_code:
            self.status = Status.ERROR
            self.data = {
                'error': (
                    f'Expected status {self.status_code}, '
                    f'instead found {response.code}.'
                ),
            }
            return

        if (
            self.content_contains and
            self.content_contains not in response.content
        ):
            self.status = Status.ERROR
            self.data = {
                'error': 'Expected content not found',
            }
            return

        self.status = Status.OK
        self.data = {
            'time': response.elapsed,
        }
