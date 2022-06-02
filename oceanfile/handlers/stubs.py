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


class AvatarInfoHandler(BaseHandler):
    @check_authorization
    async def get(self) -> Response:
        # Avatars support is not implemented.
        return json_response(None)


class ThumbnailHandler(BaseHandler):
    @check_authorization
    async def get(self) -> Response:
        # Thumbnails support is not implemented.
        return json_response(None)


class StarredHandler(BaseHandler):
    @check_authorization
    async def get(self) -> Response:
        # Thumbnails support is not implemented.
        return json_response(dict(starred_item_list=[]))
