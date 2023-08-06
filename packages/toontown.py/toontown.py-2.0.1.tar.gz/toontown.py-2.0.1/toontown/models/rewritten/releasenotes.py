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
import re
from datetime import datetime
from typing import  Optional

from ..base import BaseAPIModel


__all__ = ['ReleaseNotes', 'ReleaseNotesList']


DATE_FMT = '%B %-d, %Y at %-I:%M %p'

HTMLELEMENT_CLEANER = re.compile(r'(<.*?>|\r)')
HTMLENCODE_CLEANER = re.compile(r'&nbsp;')
NEWLINE_CLEANER = re.compile(r'\n{2,}')


def clean(string: Optional[str]):
    """Strips out HTML elements and cleans up new lines from post body"""
    if string is None:
        return string

    string = HTMLELEMENT_CLEANER.sub('', string)
    string = HTMLENCODE_CLEANER.sub(' ', string)
    string = NEWLINE_CLEANER.sub('\n\n', string)

    return string


@dataclass
class ReleaseNotes:
    """Wrapper class for the release note data
    
    Attributes
    ----------
    note_id : int
        the ID of the post
        
    slug : str
        the slug of the post

    date : datetime
        when the post was written

    body_raw : str
        the raw body of the post containing HTML elements

    body : str
        a readable version of the body, with HTML elements stripped out
    """

    __slots__ = ['note_id', 'slug', 'date', 'body_raw', 'body']

    def __init__(self, **props) -> None:
        self.note_id: int = props.get('noteId')
        self.slug: str = props.get('slug')
        self.date: datetime = datetime.strptime(props.get('date'), DATE_FMT)

        body_raw = props.get('body', None)
        self.body_raw: Optional[str] = body_raw
        self.body: Optional[str] = clean(body_raw)


class ReleaseNotesList(BaseAPIModel[ReleaseNotes]):
    """Wrapper class for the /releasenotes response
    
    A tuple-like class containing `ReleaseNote` objects
    """
    
    def __init__(self, **payload) -> None:
        iterable = tuple(payload.get('iterable'))
        super().__init__(iterable)
