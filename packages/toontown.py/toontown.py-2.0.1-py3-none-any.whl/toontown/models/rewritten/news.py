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

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..base import BaseAPIModel


__all__ = ['News', 'NewsList']


DATE_FMT = '%B %d, %Y at %I:%M %p'

HTMLELEMENT_CLEANER = re.compile(r'(<.*?>|\r)')
HTMLENCODE_CLEANER = re.compile(r'&nbsp;')
NEWLINE_CLEANER = re.compile(r'\n{2,}')

TITLE_CLEANER = re.compile(r'[^A-Za-z\s]')


def clean(string: Optional[str]):
    """Strips out HTML elements and cleans up new lines from post body"""
    if string is None:
        return string

    string = HTMLELEMENT_CLEANER.sub('', string)
    string = HTMLENCODE_CLEANER.sub(' ', string)
    string = NEWLINE_CLEANER.sub('\n\n', string)

    return string


@dataclass
class News:
    """Wrapper class for the news data
    
    Attributes
    ----------
    post_id : int
        the ID of the post

    title : str
        the title of the post

    author : str
        who wrote the post

    body_raw : str
        the raw body of the post containing HTML elements

    body : str
        a readable version of the body, with HTML elements stripped out

    date : datetime
        when the post was written

    image : str
        a link to the image of the post

    article_url : str
        the link to the full article
    """

    __slots__ = ['post_id', 'title', 'author', 'body_raw', 'body', 'date', 'image']

    def __init__(self, **props) -> None:
        self.post_id: int = props.get('postId')
        self.title: str = props.get('title')
        self.author: str = props.get('author')
        self.date: datetime = datetime.strptime(props.get('date'), DATE_FMT)
        self.image: str = props.get('image')

        body_raw = props.get('body', None)
        self.body_raw: Optional[str] = body_raw
        self.body: Optional[str] = clean(body_raw)

    @property
    def article_url(self):
        title = TITLE_CLEANER.sub('', self.title).lower().replace(' ', '-')
        return f'https://www.toontownrewritten.com/news/item/{self.post_id}/{title}'


class NewsList(BaseAPIModel[News]):
    """Wrapper class for the /news response
    
    A tuple-like class containing `News` objects
    """
    def __init__(self, **payload) -> None:
        iterable = tuple((
            News(**props)
            for props in payload['iterable']
        ))
        
        super().__init__(iterable)
