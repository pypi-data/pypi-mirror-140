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

from ..http import BaseHTTPClient


__all__ = ['BaseToontownClient', 'BaseSyncToontownClient', 'BaseAsyncToontownClient']


class BaseToontownClient(ABC):
    """Base Toontown Client to provide functionality for users to interact with the Toontown Rewritten API"""

    @abstractmethod
    def __init__(self, httpclient: BaseHTTPClient) -> None:
        self.http = httpclient

    @abstractmethod
    def connect(self) -> None:
        """Connect to the HTTP client
        
        Must be called before using any other methods in this class
        """

    @abstractmethod
    def close(self) -> None:
        """Closes connection to the HTTP client"""


class BaseSyncToontownClient(BaseToontownClient):
    def connect(self) -> None:
        self.http.connect()

    def close(self) -> None:
        self.http.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()


class BaseAsyncToontownClient(BaseToontownClient):
    async def connect(self) -> None:
        await self.http.connect()

    async def close(self) -> None:
        await self.http.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.close()
