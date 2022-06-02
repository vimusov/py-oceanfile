#!/usr/bin/python

"""
    oceanfile - Simplified and lightweight alternative to Seafile server.

    Copyright (C) 2022 Vadim Kuznetsov <vimusov@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import logging
from argparse import ArgumentParser

from aiohttp.web import Application, HTTPUnauthorized, Request, Response, middleware, run_app, view
from tomli import load as toml_load

from oceanfile.accounts import UserAccounts
from oceanfile.errors import SessionNotFound, UserNotFound
from oceanfile.handlers.auth import AuthorizationHandler
from oceanfile.handlers.dirs import ManageDirsHandler
from oceanfile.handlers.info import AccountInfoHandler, ServerInfoHandler
from oceanfile.handlers.repos import ReposListHandler
from oceanfile.handlers.stubs import AvatarInfoHandler, StarredHandler, ThumbnailHandler
from oceanfile.handlers.upload import UPLOAD_URI, UploadFileHandler, UploadLinkHandler
from oceanfile.notify import notify_start
from oceanfile.sessions import AuthSessions
from oceanfile.settings import ServerSettings, ShareSettings

log = logging.getLogger(__name__)


@middleware
async def _errors_handling_factory(request: Request, handler) -> Response:
    try:
        return await handler(request)
    except (HTTPUnauthorized, SessionNotFound, UserNotFound) as error:
        # Can be used with fail2ban.
        log.warning('Authorization from %s failed.', request.remote)
        return error


def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', required=True, help='Path to config file.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode.')
    parser.add_argument('-a', '--debug-access', action='store_true', help='Debug all requests.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    logging.getLogger('asyncio').setLevel(logging.ERROR)
    logging.getLogger('aiohttp.access').setLevel(logging.INFO if args.debug_access else logging.ERROR)

    with open(args.config, mode='rb') as config_file:
        settings = toml_load(config_file)

    auth_sessions = AuthSessions(settings)
    user_accounts = UserAccounts(settings)
    share_settings = ShareSettings.load(settings)
    server_settings = ServerSettings.load(settings)

    share_path = share_settings.path
    if share_path.is_dir():
        log.info("Using share directory '%s'.", share_path)
    else:
        msg = f"Share directory '{share_path!s}' is not found"
        log.error('%s.', msg)
        raise RuntimeError(f'{msg}:')

    app = Application(middlewares=[_errors_handling_factory], client_max_size=server_settings.max_upload_size)
    app.router.add_routes([
        view('/api/v2.1/starred-items/', StarredHandler),
        view('/api2/account/info/', AccountInfoHandler),
        view('/api2/auth-token/', AuthorizationHandler),
        view('/api2/repos/', ReposListHandler),
        view('/api2/server-info/', ServerInfoHandler),
        view(UPLOAD_URI, UploadFileHandler),
        view(r'/api2/avatars/user/{email:[^/]+}/resized/{size:\d+}', AvatarInfoHandler),
        view(r'/api2/repos/{repo_id:[^/]+}/dir/', ManageDirsHandler),
        view(r'/api2/repos/{repo_id:[^/]+}/thumbnail/', ThumbnailHandler),
        view(r'/api2/repos/{repo_id:[^/]+}/upload-link/', UploadLinkHandler),
    ])

    app['accounts'] = user_accounts
    app['sessions'] = auth_sessions
    app['share_settings'] = share_settings
    app['server_settings'] = server_settings

    async def notify_start_ctx(unused_app):
        notify_start()
        yield

    app.cleanup_ctx.append(notify_start_ctx)

    run_app(app, host=server_settings.listen, port=server_settings.port, print=None)
    log.info('Shutting down.')
