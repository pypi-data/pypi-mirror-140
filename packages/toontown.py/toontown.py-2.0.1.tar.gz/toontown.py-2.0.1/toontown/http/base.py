"""
The MIT License (MIT)

Copyright (c) 2022-present jaczerob

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Optional, Union
import asyncio
import logging
import time

import aiohttp
import requests

from toontown.exceptions import *


__all__ = ['BaseHTTPClient', 'BaseAsyncHTTPClient', 'BaseSyncHTTPClient']


Session = Union[aiohttp.ClientSession, requests.Session]


logger = logging.getLogger(__name__)


class BaseHTTPClient(ABC):
    BASE: ClassVar[str]
    HEADERS: ClassVar[dict[str, str]] = {
        'Content-Type': 'application/json',
        'User-Agent': 'toontown.py (https://github.com/jaczerob/toontown.py)'
    }

    @abstractmethod
    def __init__(self, *, session: Optional[Session] = None) -> None:
        self._session = session

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def request(self, method: str, path: str, headers: Optional[dict[str, str]] = None, **params: Any) -> Any: ...


class BaseSyncHTTPClient(BaseHTTPClient):
    def __init__(self, *, session: Optional[requests.Session] = None) -> None:
        self._session: requests.Session = session
        self._is_closed = True

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    @is_closed.setter
    def is_closed(self, value: bool) -> None:
        self._is_closed = bool(value)

    def request(self, method: str, path: str, headers: Optional[dict[str, str]] = None, **params: Any) -> Any:
        if self.is_closed:
            raise SessionNotConnected

        url = self.BASE + path
        headers = headers or self.HEADERS

        for tries in range(5):
            try:
                logger.info('Attempting {0} request #{1}: {2}'.format(method, tries+1, url))

                with self._session.request(method, url, params=params, headers=headers) as response:
                    response.raise_for_status()

                    data = response.json()
                    status = response.status_code

                    if 300 > status >= 200:
                        return data

                    if status in {500, 502, 504}:
                        time.sleep(1 + tries * 2)
                        continue

            except requests.exceptions.HTTPError as e:
                message = str(e)
                exc_info = type(e), e, e.__traceback__
                logger.error(message, exc_info=exc_info)

            except OSError as e:
                if tries < 4 and e.errno in {54, 10054}:
                    time.sleep(1 + tries * 2)
                    continue

                logger.info('Exhausted attempts for {0} request: {1}'.format(method, url))
                raise


class BaseAsyncHTTPClient(BaseHTTPClient):
    def __init__(self, *, session: Optional[aiohttp.ClientSession] = None) -> None:
        self._session: aiohttp.ClientSession = session

    async def connect(self) -> None:
        if self._session is None:
            self._session = aiohttp.ClientSession(raise_for_status=True)

    async def close(self) -> None:
        await self._session.close()

    async def request(self, method: str, path: str, headers: Optional[dict[str, str]] = None, **params: Any) -> Any:
        if self._session.closed:
            raise SessionNotConnected

        url = self.BASE + path
        headers = headers or self.HEADERS

        for tries in range(5):
            try:
                logger.info('Attempting {0} request #{1}: {2}'.format(method, tries+1, url))

                async with self._session.request(method, url, params=params, headers=headers) as response:
                    data = await response.json()
                    status = response.status

                    if 300 > status >= 200:
                        return data

                    if status in {500, 502, 504}:
                        await asyncio.sleep(1 + tries * 2)
                        continue

            except aiohttp.ClientResponseError as e:
                message = str(e)
                exc_info = type(e), e, e.__traceback__
                logger.error(message, exc_info=exc_info)
                raise

            except OSError as e:
                if tries < 4 and e.errno in {54, 10054}:
                    time.sleep(1 + tries * 2)
                    continue

                logger.info('Exhausted attempts for {0} request: {1}'.format(method, url))
                raise
