"""
SamsungTVWS - Samsung Smart TV WS API wrapper

Copyright (C) 2019 Xchwarze

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor,
    Boston, MA  02110-1335  USA

"""
from __future__ import annotations

import asyncio
import json
import logging
import ssl

from websockets.client import connect

from . import connection, exceptions, helper
from .command import SamsungTVCommand

_LOGGING = logging.getLogger(__name__)


class SamsungTVWSAsyncConnection(connection.SamsungTVWSBaseConnection):
    async def __aenter__(self):
        return self

    async def __aexit__(self, type, value, traceback):
        await self.close()

    async def open(self):
        ssl_context = ssl.SSLContext(cert_reqs=ssl.CERT_NONE)
        url = self._format_websocket_url(self.endpoint)

        _LOGGING.debug("WS url %s", url)
        connection = await connect(url, open_timeout=self.timeout, ssl=ssl_context)

        response = helper.process_api_response(await connection.recv())
        self._check_for_token(response)

        if response["event"] != "ms.channel.connect":
            await self.close()
            raise exceptions.ConnectionFailure(response)

        return connection

    async def close(self):
        if self.connection:
            await self.connection.close()

        self.connection = None
        _LOGGING.debug("Connection closed.")

    async def send_command(self, command, key_press_delay=None):
        if self.connection is None:
            self.connection = await self.open()

        if isinstance(command, SamsungTVCommand):
            payload = command.get_payload()
        else:
            payload = json.dumps(command)
        await self.connection.send(payload)

        delay = self.key_press_delay if key_press_delay is None else key_press_delay
        await asyncio.sleep(delay)
