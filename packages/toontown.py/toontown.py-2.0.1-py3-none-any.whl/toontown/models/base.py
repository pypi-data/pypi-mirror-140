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

from typing import Generic, Iterator, Tuple, TypeVar

from ..exceptions import FailedResponse


__all__ = ['BaseAPIModel']


T = TypeVar('T')


class BaseAPIModel(Generic[T]):
    """Base model for all API wrapper objects

    Supports some tuple methods
    """

    __slots__ = ['_iterable']

    def __new__(cls, **payload):
        instance = super().__new__(cls)

        if payload.get('error', None):
            # Sometimes the server will send an error field when there is no cached response
            raise FailedResponse(payload['error'])
            
        return instance

    def __init__(self, iterable: Tuple[T]) -> None:
        self._iterable = iterable

    def __getitem__(self, index: int) -> T:
        return self._iterable.__getitem__(index)

    def __iter__(self) -> Iterator[T]:
        return self._iterable.__iter__()

    def __next__(self) -> T:
        return next(self._iterable)

    def __len__(self) -> int:
        return self._iterable.__len__()

    def __str__(self) -> str:
        return self._iterable.__str__()

    def __repr__(self) -> str:
        return self._iterable.__str__()
