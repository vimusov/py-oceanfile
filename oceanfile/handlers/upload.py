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
from shutil import copyfileobj

from aiohttp.web import FileField, HTTPBadRequest, HTTPNotFound, Response
from yarl import URL

from oceanfile.atomic import atomic_save
from oceanfile.handlers.base import BaseHandler, check_authorization
from oceanfile.oid import create_oid
from oceanfile.settings import ShareSettings

log = logging.getLogger(__name__)

UPLOAD_URI = '/self/upload'


class UploadLinkHandler(BaseHandler):
    @check_authorization
    async def get(self) -> Response:
        path: str = self.request.query['p']
        url = URL.build(scheme='https', host=self.request.host, path=UPLOAD_URI, query=dict(token=self.get_token(), path=path))
        log.debug("Upload file URL '%s' created.", url)
        return Response(text=f'"{url!s}"', content_type='text/plain')


class UploadFileHandler(BaseHandler):
    @check_authorization
    async def post(self) -> Response:
        if 'multipart/form-data' not in self.request.content_type:
            log.error('Unexpected Content-Type %r.', self.request.content_type)
            return HTTPBadRequest()

        dir_name: str = self.request.query.get('path', '')
        settings: ShareSettings = self.request.app['share_settings']
        field: FileField = (await self.request.post())['file']

        path = settings.path / dir_name.removeprefix('/') / field.filename.removeprefix('/')
        if '..' in str(path):
            log.error("Path '%s' contains trash.", path)
            return HTTPBadRequest()
        if not path.parent.is_dir():
            log.error("Directory '%s' is not found.", path)
            return HTTPNotFound()

        with atomic_save(path, text=False) as photo_file:
            copyfileobj(field.file, photo_file)

        log.info("File '%s' uploaded.", path)
        return Response(text=create_oid())
