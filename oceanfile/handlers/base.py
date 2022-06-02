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

from aiohttp.web import HTTPUnauthorized, View

from oceanfile.accounts import UserAccounts
from oceanfile.sessions import AuthSessions


class BaseHandler(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._accounts: UserAccounts = self.request.app['accounts']
        self._sessions: AuthSessions = self.request.app['sessions']

    def get_token(self) -> str:
        header: str = self.request.headers.get('Authorization', '')
        if ' ' not in header:
            raise HTTPUnauthorized()

        method, token = header.split(None, maxsplit=1)
        if method.lower() != 'token':
            raise HTTPUnauthorized()

        return token

    def _get_user(self) -> str:
        return self._sessions.get_user(self.get_token())


def check_authorization(handler_method):
    async def wrapper(self: BaseHandler, *args, **kwargs):
        token = self.get_token()
        sessions: AuthSessions = self.request.app['sessions']
        if not sessions.check(token):
            raise HTTPUnauthorized()
        sessions.update(token)
        return await handler_method(self, *args, **kwargs)
    return wrapper
