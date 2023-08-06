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


__all__ = ['Login']


class Login:
    """Wrapper class for the /login response
    
    Attributes
    ----------
    status : bool
        true if the login was successful
        
    reason : int
        unique number associated with the error when `status` is false
        
    friendly_reason : str
        a user-friendly error/success message. if `status is true, you may show
        a custom status message
        
    token : str
        the login token that should be used by the game
    """

    __slots__ = ['status', 'reason', 'friendly_reason', 'token']

    def __init__(self, **payload) -> None:
        self.status: bool = payload.get('status')
        self.reason: int = payload.get('reason')
        self.friendly_reason: str = payload.get('friendlyreason')
        self.token: str = payload.get('token')
