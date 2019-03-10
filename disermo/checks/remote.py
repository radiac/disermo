"""
Checks which perform remote requests
"""
from dataclasses import dataclass, field
from http.client import HTTPResponse
import socket
from typing import cast, Union
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

from ..constants import Status
from ..utils import Timer
from .base import Check


# Default timeout, in seconds
DEFAULT_TIMEOUT = 10

# Error code for failed connection
# This should be outside the standard HTTP error codes, so it is differentiated
STATUS_FAILED = 0


@dataclass
class Response:
    """
    Wrapper for an urllib Response
    """
    raw: Union[HTTPResponse, HTTPError]
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
        label: str = None,
        timeout: float = DEFAULT_TIMEOUT,
        status_code: int = 200,
        content_contains: str = None,
    ):
        super().__init__(label)
        self.url = url
        self.timeout = timeout
        self.status_code = status_code
        self.content_contains = content_contains

    def update(self) -> None:
        # Clean data, assuming we're going to fail
        self.data = {
            'status': STATUS_FAILED,
        }

        # Make the request
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
            response = Response(raw=e_response)

        except URLError as e:
            # Unable to connect - not expected, raise immediately
            self.status = Status.ERROR
            self.data['error'] = f'Could not reach server: {e.reason}'
            return

        except Exception as e:
            # Most likely here is socket.timeout for HTTPS
            self.status = Status.ERROR
            self.data['error'] = f'Could not reach server: {e}'
            return

        else:
            # Successful request
            response = Response(raw=raw_response)

        finally:
            # All checks log their elapsed time
            self.data['elapsed'] = timer.elapsed()

        # Update status code to that returned by server
        self.data['status'] = response.code

        if response.code != self.status_code:
            self.status = Status.ERROR
            self.data['error'] = (
                f'Expected status {self.status_code}, '
                f'instead found {response.code}.'
            )
            return

        if (
            self.content_contains and
            self.content_contains not in response.content
        ):
            self.status = Status.ERROR
            self.data['error'] = 'Expected content not found'
            return

        self.status = Status.OK
