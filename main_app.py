import argparse
import signal
import sys
import json
import logging
import warnings
import os
import asyncio
import aiohttp
import aiohttp.server
from aiohttp import MultiDict
from urllib.parse import urlparse, parse_qsl

from storage import Storage
from limiter import FuzzyLimiter

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
)

class Handler(aiohttp.server.ServerHttpProtocol):
    def __init__(self, debug, log, keep_alive, limiter):
        super().__init__(debug=debug, log=log, keep_alive=keep_alive)
        self._limiter = limiter
    
    async def handle_request(self, message, payload):
        path = urlparse(message.path).path.lower()
        if path.startswith(u'/api/v1/limit/'):
            get_params = MultiDict(parse_qsl(urlparse(message.path).query))
            domain = get_params.get('d', None)
            gen_time = get_params.get('g', None)
            if domain is None or gen_time is None:
                await super().handle_error(message, payload, reason='domain or gen_time not provided')
            else:
                await self.handle_limit(message, domain, gen_time)
        else:
            await super().handle_request(message, payload)
        
    async def handle_limit(self, message, domain, gen_time):
        dt = await self._limiter.rate_limit(domain, int(gen_time))
        resp_text = '{"delay":%i}'%dt
        resp_body = resp_text.encode('utf-8')
        response = aiohttp.Response(
            self.writer, 200, http_version=message.version
        )
        response.add_header('Content-Type', 'application/json')
        response.add_header('Content-Length', str(len(resp_body)))
        response.send_headers()
        response.write(resp_body)
        await response.write_eof()

class Application:

    def __init__(self, ip='0.0.0.0', port='8080'):
        self._parse_args()
        self._log = logging.getLogger('')
        self._event_loop = asyncio.get_event_loop()
        if self._args.verbose:
            self._log.info('enabling debugging')
            self._event_loop.set_debug(True)
            self._event_loop.slow_callback_duration = 0.1
            warnings.simplefilter('always', ResourceWarning)
            
        self._config = {'rozetka.ua':(10, 15), 'f.ua':(10, 20), 'repka.ua':(20, 12)}
        self._storage = Storage()
        self._limiter = FuzzyLimiter(self._config, self._storage)
        
        self._server = self._event_loop.create_server(
            lambda: Handler(debug=self._args.verbose, log=self._log, keep_alive=3600, limiter=self._limiter),
            ip, port)

    def run(self):
        srv = self._event_loop.run_until_complete(self._server)
        self._log.info('serving on ' + str(srv.sockets[0].getsockname()))
        try:
            self._event_loop.run_forever()
        except KeyboardInterrupt:
            pass
        
    def _parse_args(self):
        parser = argparse.ArgumentParser('debug asyncio')
        parser.add_argument(
            '-v',
            dest='verbose',
            default=False,
            action='store_true',
        )
        self._args = parser.parse_args()
    
if __name__ == '__main__':
    app = Application()
    app.run()

