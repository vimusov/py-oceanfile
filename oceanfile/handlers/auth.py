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
from typing import Dict

from aiohttp.web import HTTPUnauthorized, Response, json_response

from oceanfile.handlers.base import BaseHandler

log = logging.getLogger(__name__)


class AuthorizationHandler(BaseHandler):
    # WARN: No authorization decorator here!
    async def post(self) -> Response:
        creds: Dict[str, str] = dict(await self.request.post())
        log.debug('User credentials: %r.', creds)

        if not (name := creds.get('username')):
            return HTTPUnauthorized()

        if not (password := creds.get('password')):
            return HTTPUnauthorized()

        if not self._accounts.check(name, password):
            return HTTPUnauthorized()

        token = self._sessions.add(name)
        log.info('User %r successully authorized and got token %r.', name, token)
        return json_response(dict(token=token))
