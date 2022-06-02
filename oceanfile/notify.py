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
from os import getenv

log = logging.getLogger(__name__)


def notify_start():
    if not getenv('NOTIFY_SOCKET'):
        log.debug('No running systemd detected.')
        return
    try:
        # This dependency is optional.
        from systemd.daemon import notify as sd_notify
    except ImportError:
        log.debug('systemd module is not installed.')
    else:
        log.debug('Notifying systemd about successful start.')
        sd_notify('READY=1')
