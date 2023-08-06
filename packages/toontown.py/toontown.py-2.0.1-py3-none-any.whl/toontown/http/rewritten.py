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

from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import ClassVar, Union
import asyncio
import bz2
import hashlib
import logging
import os
import platform
import sys

from ..exceptions import *
from .base import BaseAsyncHTTPClient, BaseSyncHTTPClient


__all__ = ['RewrittenSyncHTTPClient', 'RewrittenAsyncHTTPClient']


logger = logging.getLogger(__name__)

MANIFEST = 'https://cdn.toontownrewritten.com/content/patchmanifest.txt'
PATCHES = 'https://download.toontownrewritten.com/patches'

CHUNK_SIZE = 10 * 10 * 1024


def get_platform():
    if sys.platform == 'win32' and platform.machine().endswith('64'):
        return 'win64' # for handling 64 bit files in the patch manifest
    return sys.platform


class RewrittenSyncHTTPClient(BaseSyncHTTPClient):
    BASE: ClassVar[str] = 'https://toontownrewritten.com/api'

    def update(self, path: Union[str, Path]) -> None:
        if isinstance(path, str):
            path = Path(path)

        if not path.is_dir():
            raise Exception('Path does not exist or is not a directory')

        manifest = self._session.get(
            MANIFEST,
            headers=self.HEADERS,
        ).json()

        pf = get_platform()

        def try_update(args):
            file, props = args
            if pf not in props['only']:
                return

            file_path = path.joinpath(file)

            if file_path.exists():
                hash = hashlib.sha1(file_path.open('rb').read()).hexdigest()
                if props['hash'] == hash:
                    return

            url = '{0}/{1}'.format(PATCHES, props['dl'])

            with self._session.get(url, stream=True) as resp:
                logger.info(f'Downloading {url} to {file_path}')
                resp.raise_for_status()
                decompressor = bz2.BZ2Decompressor()

                with open(file_path, 'wb') as file:
                    for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                        file.write(decompressor.decompress(chunk))

        with ThreadPool(os.cpu_count()) as pool:
            pool.map(try_update, manifest.items())


class RewrittenAsyncHTTPClient(BaseAsyncHTTPClient):
    BASE: ClassVar[str] = 'https://toontownrewritten.com/api'

    async def update(self, path: Union[str, Path]) -> None:
        if isinstance(path, str):
            path = Path(path)

        if not path.is_dir():
            raise Exception('Path does not exist or is not a directory')

        manifest = await (await self._session.get(
            MANIFEST,
            headers=self.HEADERS,
        )).json()

        pf = get_platform()

        async def try_update(args):
            file, props = args
            if pf not in props['only']:
                return

            file_path = path.joinpath(file)

            if file_path.exists():
                hash = hashlib.sha1(file_path.open('rb').read()).hexdigest()
                if props['hash'] == hash:
                    return

            url = '{0}/{1}'.format(PATCHES, props['dl'])

            async with self._session.get(url) as resp:
                logger.info(f'Downloading {url} to {file_path}')

                resp.raise_for_status()
                decompressor = bz2.BZ2Decompressor()

                with open(file_path, 'wb') as file:
                    async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                        file.write(decompressor.decompress(chunk))

        await asyncio.gather(*map(try_update, manifest.items()))
