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
from pathlib import Path
from typing import Any, Dict

from aiohttp.web import HTTPBadRequest, HTTPNotFound, Response, json_response

from oceanfile.handlers.base import BaseHandler, check_authorization
from oceanfile.oid import create_oid
from oceanfile.settings import ShareSettings

log = logging.getLogger(__name__)


class ManageDirsHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__settings: ShareSettings = self.request.app['share_settings']

    @staticmethod
    def __get_info(obj_path: Path) -> Dict[str, Any] | None:
        name = obj_path.name
        if name.startswith('.'):
            # Skip hidden files.
            return None

        if obj_path.is_dir():
            obj_info = dict(type='dir', size=None)
        elif obj_path.is_file():
            obj_info = dict(type='file', size=obj_path.stat().st_size)
        else:
            log.warning("Unsupported FS object '%s'.", obj_path)
            return None

        return dict(
            id=create_oid(),
            mtime=int(obj_path.stat().st_mtime),
            name=name,
            permission='rw',
            **obj_info,
        )

    @check_authorization
    async def get(self) -> Response:
        path: str = self.request.query['p']
        dir_path = self.__settings.path / path.removeprefix('/')
        if '..' in path:
            log.error("Path '%s' contains trash.", path)
            return HTTPBadRequest()

        if not dir_path.is_dir():
            log.error("Directory '%s' is not found.", dir_path)
            return HTTPNotFound()

        dir_entries = [
            entry for path in dir_path.glob('*')
            if (entry := self.__get_info(path)) is not None
        ]
        log.debug("Listing directory '%s', entries: %r", dir_path, dir_entries[:8])

        return json_response(dir_entries, headers={'oid': create_oid()})

    @check_authorization
    async def post(self) -> Response:
        dir_ops: Dict[str, str] = dict(await self.request.post())
        action = dir_ops.get('operation', '?').lower()
        if action != 'mkdir':
            log.error('Unknown directory operation %r.', action)
            return HTTPBadRequest()

        path: str = self.request.query['p']
        dir_path = self.__settings.path / path.removeprefix('/')

        if '..' in path:
            log.error("Path '%s' contains trash", path)
            return HTTPBadRequest()

        if dir_path.is_dir():
            log.debug("Directory '%s' already exist.", dir_path)
        else:
            dir_path.mkdir(mode=0o755)
            log.info("New directory '%s' created.", dir_path)

        dir_info = self.__get_info(dir_path)
        return json_response(dir_info, headers={'oid': dir_info['id']})
