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

from dataclasses import dataclass
from datetime import datetime

from ..base import BaseAPIModel


__all__ = ['District', 'Districts']


@dataclass
class District:
    """Wrapper class for district data
    
    Attributes
    ----------
    name : str
        district name
    
    online : bool
        generally always true, districts are removed if they don't report their status 
        after a few minutes

    population : int
        district population

    invasion_online : bool
        true if invasion is present in district

    last_update : datetime
        the time at which the district was last updated

    cogs_attacking : str
        the cogs attacking name

    count_defeated : int
        amount of cogs defeated in the district

    remaining_time : int
        amount of time before the invasion automatically ends in seconds
    """

    __slots__ = [
        'name', 'online', 'population', 'invasion_online', 'last_update',
        'cogs_attacking', 'count_defeated', 'count_total', 'remaining_time'
    ]

    def __init__(self, **props) -> None:
        self.name: str = props.get('name')
        self.online: bool = props.get('online')
        self.population: int = props.get('population')
        self.invasion_online: bool = props.get('invasion_online')
        self.last_update: datetime = datetime.fromtimestamp(props.get('last_update'))
        self.cogs_attacking: str = props.get('cogs_attacking')
        self.count_defeated: int = props.get('count_defeated')
        self.count_total: int = props.get('count_total')
        self.remaining_time: int = props.get('remaining_time')


class Districts(BaseAPIModel[District]):
    """Wrapper class for the /districts response
    
    A tuple-like class containing `District` objects, sorted by district and playground
    """

    def __init__(self, **payload) -> None:
        iterable = tuple(
            sorted([
                District(**district)
                for district in payload['iterable']
            ], key=lambda district: district.population)
        )

        super().__init__(iterable)
