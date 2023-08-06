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
from typing import Any, Literal, Optional

from ..base import BaseAPIModel


@dataclass
class SillyTeam:
    """Wrapper class for current rewards in the /sillymeter
    
    Attributes
    ----------
    reward : str
        the reward this Silly Team will give

    description : str
        the description of the reward this Silly Team will give

    points : int
        the amount of points this Silly Team earned in the cycle, 
        set to `None` if the Silly Meter state is not set to `Reward`
    """

    __slots__ = ['reward', 'description', 'points']

    reward: str
    description: str
    points: Optional[int]


class SillyMeter(BaseAPIModel[SillyTeam]):
    """Wrapper class for /sillymeter response

    A tuple-like class containing `SillyTeam` objects, sorted by points

    Attributes
    ----------
    state : Literal['Active', 'Reward', 'Inactive']
        the current state of the Silly Meter

    health : int
        the current health of the Silly Meter (0 - 5,000,000)

    winner : Optional[str]
        the winning Silly Team whose reward is currently active, otherwise `None`

    next_update_timestamp : datetime
        when the Silly Meter will next update itself

    as_of : datetime
        when the server generated the Silly Meter data
    """

    __slots__ = ['state', 'health', 'winner', 'next_update_timestamp', 'as_of']

    def __init__(self, **payload: dict[str, Any]) -> None:
        self.state: Literal['Active', 'Reward', 'Inactive'] = payload.get('state')
        self.health: int = payload.get('hp')

        self.winner: Optional[str] = payload.get('winner')
        self.next_update_timestamp: datetime = datetime.fromtimestamp(payload.get('nextUpdateTimestamp'))
        self.as_of: datetime = datetime.fromtimestamp(payload.get('asOf'))

        rewards: list[str] = payload.get('rewards')
        reward_descriptions: list[str] = payload.get('rewardDescriptions')
        reward_points: list[Optional[int]] = payload.get('rewardPoints')
        iterable = map(lambda args: SillyTeam(*args), zip(rewards, reward_descriptions, reward_points))

        if self.state == 'Reward':
            iterable = tuple(sorted(iterable, key=lambda silly_team: silly_team.points))
        else:
            iterable = tuple(iterable)

        super().__init__(iterable)
