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


__all__ = ['News', 'NewsList']


DATE_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'


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

    __slots__ = ['id', 'author', 'posted', 'title', 'summary', 'category']

    def __init__(self, **props) -> None:
        self.id: int = props.get('id')
        self.author: str = props.get('author')
        self.title: str = props.get('title')
        self.summary: str = props.get('summary')
        self.category: str = props.get('category')

        posted = props.get('posted')
        self.posted: Optional[datetime] = datetime.strptime(posted, DATE_FMT) if posted else None


    @property
    def article_url(self):
        return f'https://corporateclash.net/news/article/{self.id}'


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
