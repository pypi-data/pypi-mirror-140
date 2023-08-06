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

from pathlib import Path
from typing import Optional, Union
import aiohttp
import requests

from ..http import RewrittenSyncHTTPClient, RewrittenAsyncHTTPClient
from ..models.rewritten import *
from .base import BaseAsyncToontownClient, BaseSyncToontownClient


__all__ = ['RewrittenSyncToontownClient', 'RewrittenAsyncToontownClient']


class RewrittenSyncToontownClient(BaseSyncToontownClient):
    """Synchronous client to interact with the Toontown Rewritten API"""

    def __init__(self, *, session: Optional[requests.Session] = None) -> None:
        super().__init__(RewrittenSyncHTTPClient(session=session))

    def status(self) -> Status:
        data = self.http.request(
            'GET',
            '/status'
        )

        return Status(**data)

    def release_notes(self, *, id: Optional[int] = None) -> ReleaseNotesList:
        if id is not None:
            path = f'/releasenotes/{id}'
        else:
            path = '/releasenotes'

        data = self.http.request(
            'GET',
            path
        )

        if not isinstance(data, list):
            data = dict(iterable=[data])
        else:
            data = dict(iterable=data)

        return ReleaseNotesList(**data)
        
    def news(self, *, id: Optional[int] = None, all: Optional[bool] = False) -> NewsList:
        if id is not None:
            path = f'/news/{id}'
        elif all is True:
            path = '/news/list'
        else:
            path = '/news'

        data = self.http.request(
            'GET',
            path
        )

        if not isinstance(data, list):
            data = dict(iterable=[data])
        else:
            data = dict(iterable=data)

        return NewsList(**data)

    def doodles(self) -> Doodles:
        data = self.http.request(
            'GET',
            '/doodles'
        )

        return Doodles(**data)

    def field_offices(self) -> FieldOffices:
        data = self.http.request(
            'GET',
            '/fieldoffices'
        )

        return FieldOffices(**data)

    def invasions(self) -> Invasions:
        data = self.http.request(
            'GET',
            '/invasions'
        )

        return Invasions(**data)

    def login(
        self, 
        *, 
        username: Optional[str] = None, 
        password: Optional[str] = None,
        app_token: Optional[str] = None,
        auth_token: Optional[str] = None,
        queue_token: Optional[str] = None,
    ) -> Login:
        params = {'format': 'json'}

        if app_token is not None and auth_token is not None:
            params['appToken'] = app_token
            params['authToken'] = auth_token
        elif queue_token is not None:
            params['queueToken'] = queue_token
        elif username is not None and password is not None:
            params['username'] = username
            params['password'] = password
        else:
            raise Exception('Please provide either a username and password, a queue token, or a auth token and app token to log in')

        headers = self.http.HEADERS | {'Content-Type': 'application/x-www-form-urlencoded'}

        data = self.http.request(
            'POST',
            '/login',
            headers=headers,
            **params
        )
        
        return Login(**data)

    def population(self) -> Population:
        data = self.http.request(
            'GET',
            '/population'
        )

        return Population(**data)

    def silly_meter(self) -> None:
        data = self.http.request(
            'GET',
            '/sillymeter'
        )

        return SillyMeter(**data)

    def update(self, path: Union[str, Path]) -> None:
        self.http.update(path)


class RewrittenAsyncToontownClient(BaseAsyncToontownClient):
    """Asynchronous client to interact with the Toontown Rewritten API"""

    def __init__(self, *, session: Optional[aiohttp.ClientSession] = None) -> None:
        super().__init__(RewrittenAsyncHTTPClient(session=session))

    async def connect(self) -> None:
        await self.http.connect()

    async def close(self) -> None:
        await self.http.close()

    async def status(self) -> Status:
        data = await self.http.request(
            'GET',
            '/status'
        )

        return Status(**data)

    async def release_notes(self, *, id: Optional[int] = None) -> ReleaseNotesList:
        if id is not None:
            path = f'/releasenotes/{id}'
        else:
            path = '/releasenotes'

        data = await self.http.request(
            'GET',
            path
        )

        if not isinstance(data, list):
            data = dict(iterable=[data])
        else:
            data = dict(iterable=data)

        return ReleaseNotesList(**data)
        
    async def news(self, *, id: Optional[int] = None, all: Optional[bool] = False) -> NewsList:
        if id is not None:
            path = f'/news/{id}'
        elif all is True:
            path = '/news/list'
        else:
            path = '/news'

        data = await self.http.request(
            'GET',
            path
        )

        if not isinstance(data, list):
            data = dict(iterable=[data])
        else:
            data = dict(iterable=data)

        return NewsList(**data)

    async def doodles(self) -> Doodles:
        data = await self.http.request(
            'GET',
            '/doodles'
        )

        return Doodles(**data)

    async def field_offices(self) -> FieldOffices:
        data = await self.http.request(
            'GET',
            '/fieldoffices'
        )

        return FieldOffices(**data)

    async def invasions(self) -> Invasions:
        data = await self.http.request(
            'GET',
            '/invasions'
        )

        return Invasions(**data)

    async def login(
        self, 
        *, 
        username: Optional[str] = None, 
        password: Optional[str] = None,
        app_token: Optional[str] = None,
        auth_token: Optional[str] = None,
        queue_token: Optional[str] = None,
    ) -> Login:
        params = {'format': 'json'}

        if app_token is not None and auth_token is not None:
            params['appToken'] = app_token
            params['authToken'] = auth_token
        elif queue_token is not None:
            params['queueToken'] = queue_token
        elif username is not None and password is not None:
            params['username'] = username
            params['password'] = password
        else:
            raise Exception('Please provide either a username and password, a queue token, or a auth token and app token to log in')

        headers = self.http.HEADERS | {'Content-Type': 'application/x-www-form-urlencoded'}

        data = await self.http.request(
            'POST',
            '/login',
            headers=headers,
            **params
        )
        
        return Login(**data)

    async def population(self) -> Population:
        data = await self.http.request(
            'GET',
            '/population'
        )

        return Population(**data)

    async def silly_meter(self) -> SillyMeter:
        data = await self.http.request(
            'GET',
            '/sillymeter'
        )

        return SillyMeter(**data)

    async def update(self, path: Union[str, Path]) -> None:
        await self.http.update(path)
