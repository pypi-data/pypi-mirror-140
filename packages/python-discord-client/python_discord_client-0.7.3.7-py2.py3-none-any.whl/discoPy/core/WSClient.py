
import asyncio
import websockets as ws
import sys, traceback
import json
import time 
import logging 
import numpy as np

import requests

from discoPy.core.base_client import BaseClient

class WSClient(BaseClient):
    '''
        Connect to the Discord websocket-feed.

        @param: token (str): required 
        @param: url (str):  required
    '''
    _heartbeat_interval = 41250 / 1000 # in seconds
    _last_ping = None
    _sequence = None

    _url = 'wss://gateway.discord.gg/?v=9&encording=json'

    def __init__(self, token: str, intents: list, api_version: int=None):

        super().__init__(token=token, api_version=api_version)

        self._log = logging.getLogger(__name__)

        self._token = token
        self._intents = np.sum([self._get_intents(intent) for intent in intents])

        if api_version != None:
            self._url = f'wss://gateway.discord.gg/?v={api_version}&encording=json'
            
    def run(self) -> None:
        self._connect()

    async def _main(self) -> None:
        try:
            keepwaiting = True
            async with ws.connect(self._url) as socket:
                self.ws = socket
                await self._authenticate() 

                try:
                    while keepwaiting:
                        if not self._last_ping or int(time.time()) - self._last_ping > self._get_ws_pingtimeout():
                            await self._send_ping()
                        try:
                            evt = await asyncio.wait_for(self.ws.recv(), timeout=self._get_ws_pingtimeout())
                        except asyncio.TimeoutError:
                            self._log.info(f'No message in {self._get_ws_pingtimeout()} seconds')
                            await self._send_ping()
                        except asyncio.CancelledError:
                            self._log.warn(f'Cancelled error')
                            await self.ws.ping()
                        else:
                            try:
                                evt_obj = json.loads(evt)
                                if evt_obj['op'] != 11 and 's' in evt_obj and evt_obj['s']: # setting the _sequence
                                    self._sequence = evt_obj['s']
                                    if evt_obj['op'] == 10:  
                                        self._heartbeat_interval = int(evt_obj['d']['heartbeat_interval']) / 1000
                            except ValueError:
                                pass
                            else:
                                await self.trigger('on_event', evt_obj)
                    
                except ws.ConnectionClosed:
                    keep_waiting = False
                    self._log.warn(f'Websocket connection closed!  {e} {traceback.format_exc()}')
                    await self._reconnect()
                except Exception as e:
                    self._log.error(f'WS exception: {e} {traceback.format_exc()}')
                    keep_waiting = False
                    await self._reconnect()

        except Exception as e:
            self._log.error(f'Exception!: {e} {traceback.format_exc()}')

    def _connect(self) -> None:
        self._log.info('Connecting...')
        self._conn = asyncio.ensure_future(self._main())

    async def _reconnect(self) -> None:
        self._log.info('Reconnecting Websocket...')
        await self._close_connection()
        self._connect()
    
    async def _close_connection(self) -> None:
        await self.ws.close()

    async def send_message(self, message: dict) -> None:
        await self.ws.send(json.dumps(message))

    async def _send_ping(self):
        self._log.info(f'Sending ping now, _sequence: {self._sequence}')
        await self.send_message({
            'op': 1,
            'd': self._sequence
        })
        self._last_ping = int(time.time())
    
    async def _authenticate(self) -> None:
        await self.send_message(self._get_payload(kind='init'))

    def _get_ws_pingtimeout(self) -> None:
        return self._heartbeat_interval

    def _get_payload(self, kind: str) -> dict:
        '''https://discord.com/developers/docs/topics/gateway#identifying'''
        op = None
        if kind == 'reconnect':
            op = 7
        elif kind == 'resume':
            op = 6
        elif kind == 'init':
            op = 2
        else:
            raise ValueError
        return {
            'op': op,
            'd': {
                'token': self._token,
                'intents': f'{self._intents}',
                'properties': {
                    '$os': sys.platform,
                    '$browser': 'disco',
                    '$device': 'pc'
                },
                'compress': True
            }
        }
        
