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


__all__ = ['Population', 'District']


@dataclass
class District:
    """Wrapper class for district data
    
    Attributes
    ----------
    name : str
        the name of the district
        
    population : int
        the population of the district
        
    last_updated : datetime
        when the district's population was last updated by the server
    """
    
    name: str
    population: int
    last_updated: datetime


class Population(BaseAPIModel[District]):
    """"Wrapper class for /population response

    A tuple-like class containing `District` objects, sorted by population

    Attributes
    ----------
    total : int
        the total population of Toontown Rewritten

    last_updated : datetime
        the time of the last population update
    """

    __slots__ = ['total', 'last_updated']

    def __init__(self, **payload) -> None:
        self.total: int = payload.get('totalPopulation')
        self.last_updated = last_updated = datetime.fromtimestamp(payload.get('lastUpdated'))

        iterable = tuple(sorted([
            District(name, population, last_updated)
            for name, population in payload.get('populationByDistrict').items()
        ], key=lambda district: district.population))
        
        super().__init__(iterable)
