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

from ..base import BaseAPIModel


__all__ = ['Doodle', 'Doodles']


@dataclass
class Doodle:
    """Wrapper class for doodle data

    Attributes
    ----------
    district : str
        the district the doodle is in

    playground : str
        the playground the doodle is in

    dna : str
        the doodle's DNA string

    rendition : str
        a link to a 256x256 png of the doodle's rendition

    traits : list[str]
        the list of the doodle's traits

    cost : int
        how much the doodle costs to purchase
    """

    __slots__ = ['district', 'playground', 'dna', 'traits', 'cost']

    district: str
    playground: str
    dna: str
    traits: list[str]
    cost: int

    @property
    def rendition(self) -> str:
        """A link to a 256x256 png of the doodle's rendition"""
        return f'https://rendition.toontownrewritten.com/render/{self.dna}/doodle/256x256.png'


class Doodles(BaseAPIModel[Doodle]):
    """Wrapper class for the /doodles response
    
    A tuple-like class containing `Doodle` objects, sorted by district and playground
    """
    
    def __init__(self, **payload) -> None:
        iterable = tuple(
            sorted([
                Doodle(district, playground, **doodle)
                for district, playgrounds in payload.items()
                for playground, doodles in playgrounds.items()
                for doodle in doodles
            ], key = lambda doodle: (doodle.district, doodle.playground))
        )

        super().__init__(iterable)
