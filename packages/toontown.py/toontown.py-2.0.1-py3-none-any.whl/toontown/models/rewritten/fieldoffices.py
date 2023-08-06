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
from typing import Optional

from ..base import BaseAPIModel


__all__ = ['FieldOffice', 'FieldOffices']


ZONE_LOOKUP = {
    '3100': 'Walrus Way',
    '3200': 'Sleet Street',
    '3300': 'Polar Place',
    '4100': 'Alto Avenue',
    '4200': 'Baritone Boulevard',
    '4300': 'Tenor Terrace',
    '5100': 'Elm Street',
    '5200': 'Maple Street',
    '5300': 'Oak Street',
    '9100': 'Lullaby Lane',
    '9200': 'Pajama Place',
}

DEPARTMENT_LOOKUP = {
    's': 'Sellbot'
}


@dataclass
class FieldOffice:
    """Wrapper class for field office data
    
    Attributes
    ----------
    last_updated : datetime
        when the field office's data was last updated

    street : str
        the street that the field office is on

    department : str
        the department of the field office (currently only `Sellbot`)

    difficulty : int
        how many stars the field office is

    annexes : int
        how many annexes are left in the field office

    open : bool
        whether or not the elevator to the field office is open

    expiring : Optional[datetime]
        shows how long left the field office will stand after the last annex is defeated, otherwise `None`
    """

    __slots__ = ['last_updated', 'street', 'department', 'difficulty',
                 'annexes', 'open', 'expiring']
    
    def __init__(self, last_updated, zone, *, department, difficulty, annexes, open, expiring) -> None:
        self.last_updated: datetime = last_updated
        self.street: str = ZONE_LOOKUP[zone]
        self.department: str = DEPARTMENT_LOOKUP[department]
        self.difficulty: int = difficulty + 1
        self.annexes: int = annexes
        self.open: bool = open
        self.expiring: Optional[datetime] = datetime.fromtimestamp(expiring) if expiring else None


class FieldOffices(BaseAPIModel[FieldOffice]):
    """"Wrapper class for /fieldoffices response

    A tuple-like class containing `FieldOffice` objects, sorted by difficulty

    Attributes
    ----------
    last_updated : datetime
        the time when the field offices data was last updated
    """

    __slots__ = ['last_updated']
    
    def __init__(self, **payload) -> None:
        self.last_updated = last_updated = datetime.fromtimestamp(payload.pop('lastUpdated'))
        iterable = tuple(
            sorted([
                FieldOffice(last_updated, zone, **props)
                for zone, props in payload.pop('fieldOffices').items()
            ],
            key=lambda field_office: field_office.difficulty,
            reverse=True)
        )

        super().__init__(iterable)
