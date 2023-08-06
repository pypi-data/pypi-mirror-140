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

from typing import Optional
import aiohttp
import requests

from ..http import ClashSyncHTTPClient, ClashAsyncHTTPClient
from ..models.clash import *
from .base import BaseAsyncToontownClient, BaseSyncToontownClient


__all__ = ['ClashSyncToontownClient', 'ClashAsyncToontownClient']


class ClashSyncToontownClient(BaseSyncToontownClient):
    """Synchronous client to interact with the Toontown Corporate Clash API"""

    def __init__(self, *, session: Optional[requests.Session] = None) -> None:
        super().__init__(ClashSyncHTTPClient(session=session))

    def districts(self) -> Districts:
        data = self.http.request(
            'GET',
            '/districts.js'
        )

        return Districts(**dict(iterable=data))

    def login(self, username: str, password: str) -> Login:
        data = self.http.request(
            'GET',
            f'/login/{username}',
            password=password
        )

        return Login(**data)

    def news(self, id: Optional[int] = None) -> NewsList:
        if id is not None:
            path = f'/launcher/news/{id}'
        else:
            path = '/launcher/news'

        data = self.http.request(
            'GET',
            path
        )

        return NewsList(**dict(iterable=data))


class ClashAsyncToontownClient(BaseAsyncToontownClient):
    """Asynchronous client to interact with the Toontown Corporate Clash API"""

    def __init__(self, *, session: Optional[aiohttp.ClientSession] = None) -> None:
        super().__init__(ClashAsyncHTTPClient(session=session))

    async def districts(self) -> Districts:
        data = await self.http.request(
            'GET',
            '/districts.js'
        )

        return Districts(**dict(iterable=data))

    async def login(self, username: str, password: str) -> Login:
        data = await self.http.request(
            'GET',
            f'/login/{username}',
            password=password
        )

        return Login(**data)

    async def news(self, id: Optional[int] = None) -> NewsList:
        if id is not None:
            path = f'/launcher/news/{id}'
        else:
            path = '/launcher/news'

        data = await self.http.request(
            'GET',
            path
        )

        return NewsList(**dict(iterable=data))
