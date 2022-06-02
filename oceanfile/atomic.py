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

from contextlib import contextmanager
from os import O_CLOEXEC, O_DIRECTORY, O_RDONLY, close as os_close, fchmod, fdatasync, open as os_open
from pathlib import Path
from tempfile import mkstemp


@contextmanager
def atomic_save(path: Path, *, text: bool = True, perms: int = 0o644):
    file_path = path.resolve()
    work_dir = file_path.parent
    # http://bugs.python.org/issue21579
    tmp_fd, tmp_name = mkstemp(dir=work_dir, text=text, prefix=f'{file_path.name}.')
    tmp_path = Path(tmp_name)
    try:
        fchmod(tmp_fd, perms)
        with open(tmp_fd, mode='wt' if text else 'wb', closefd=False) as tmp_file:
            yield tmp_file
            tmp_file.flush()
            fdatasync(tmp_fd)
        tmp_path.replace(file_path)
    except BaseException:
        tmp_path.unlink()
        raise
    finally:
        os_close(tmp_fd)
    dir_fd = os_open(work_dir, O_RDONLY | O_CLOEXEC | O_DIRECTORY)
    try:
        fdatasync(dir_fd)
    finally:
        os_close(dir_fd)
