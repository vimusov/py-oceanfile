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

from dataclasses import dataclass
from hashlib import md5
from os import statvfs
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class ServerSettings:
    listen: str
    port: int
    max_upload_size: int

    @classmethod
    def load(cls, settings: Dict[str, Any]):
        section = settings['server']
        return cls(
            listen=section['listen'],
            port=section['port'],
            max_upload_size=section['max-upload-size'],
        )


@dataclass(frozen=True)
class ShareSettings:
    id: str
    name: str
    path: Path
    max_size: int

    @classmethod
    def load(cls, settings: Dict[str, Any]):
        section = settings['share']
        name = section['name']
        path = Path(section['path'])
        # In fact it can be any value but I think it's good idea to use MD5 of the name.
        sid = md5(name.encode(encoding='utf-8', errors='replace')).hexdigest()
        info = statvfs(path)
        max_size = info.f_bsize * info.f_bavail
        return cls(
            id=sid,
            name=name,
            path=path,
            max_size=max_size,
        )
