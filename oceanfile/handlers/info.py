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

from aiohttp.web import Response, json_response

from oceanfile.handlers.base import BaseHandler, check_authorization
from oceanfile.settings import ServerSettings, ShareSettings

_SERVER_VERSION = '9.0.4'


class AccountInfoHandler(BaseHandler):
    @check_authorization
    async def get(self) -> Response:
        name = self._get_user()
        email = self._accounts.get_email(name)
        settings: ShareSettings = self.request.app['share_settings']
        return json_response(dict(
            email=email,
            name=name,
            total=settings.max_size,
            usage=0,
        ))


class ServerInfoHandler(BaseHandler):
    @check_authorization
    async def get(self) -> Response:
        return json_response(dict(version=_SERVER_VERSION, features=''))
