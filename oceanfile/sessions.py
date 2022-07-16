"""
    This file is part of oceanfile.

    oceanfile is free software: you can redistribute it and/or modify it under the terms
    of the GNU General Public License as published by the Free Software Foundation, either
    version 3 of the License, or (at your option) any later version.

    oceanfile is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
    without even the implied warranty     of MERCHANTABILITY or FITNESS FOR A PARTICULAR
    PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with oceanfile.
    If not, see <https://www.gnu.org/licenses/>.
"""

import logging
from json import dump as json_dump, load as json_load
from pathlib import Path
from time import ctime, time
from typing import Any, Dict
from uuid import uuid4

from oceanfile.atomic import atomic_save
from oceanfile.errors import SessionNotFound

log = logging.getLogger(__name__)


class AuthSessions:
    def __init__(self, settings: Dict[str, Any]):
        section: Dict[str, Any] = settings['sessions']
        self.__ttl: int = section['ttl']
        self.__path = Path(section['cache'])
        try:
            with self.__path.open(mode='rt') as sessions_file:
                sessions = json_load(sessions_file)
        except FileNotFoundError:
            sessions = dict()
        cur_time = time()
        self.__sessions = {token: session for token, session in sessions.items() if session['deadline'] > cur_time}

    def __sync(self, sessions: Dict[str, float]):
        with atomic_save(self.__path, perms=0o600) as sessions_file:
            json_dump(sessions, sessions_file)
        self.__sessions = sessions

    def add(self, user: str) -> str:
        token = str(uuid4())
        deadline = time() + self.__ttl
        self.__sync({**self.__sessions, token: dict(user=user, deadline=deadline)})
        log.info('New token %r (user=%r) added, deadline=%r.', token, user, ctime(deadline))
        return token

    def get_user(self, token: str) -> str:
        session = self.__sessions.get(token)
        if session is None:
            raise SessionNotFound()
        return session['user']

    def check(self, token: str) -> bool:
        session = self.__sessions.get(token)
        if session is None:
            log.debug('Token %r is not found in sessions.', token)
            return False
        is_valid = time() < session['deadline']
        log.debug('Token %r (user=%r) is valid? %s.', token, session['user'], is_valid)
        return is_valid

    def update(self, token: str):
        session = self.__sessions[token]
        cur_deadline = session['deadline']
        new_deadline = time() + self.__ttl
        if abs(new_deadline - cur_deadline) < 3600:
            # Do not change file if deadline is not near.
            return
        user = session['user']
        self.__sync({**self.__sessions, token: dict(user=user, deadline=new_deadline)})
        log.debug('Token %r (user=%r) updated, new deadline %r.', token, user, ctime(new_deadline))
