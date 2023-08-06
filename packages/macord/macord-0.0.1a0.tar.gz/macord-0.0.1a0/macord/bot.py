import aiohttp
import asyncio
import json
import requests
from typing import Any, Callable

from .message import *

class Bot(object):

    def __init__(self, token: str) -> None:
        self.__token: str = token
        self.__heartbeat_interval: float = 0.0
        self.__gateway_url: str = None
        self.__ws: aiohttp.ClientWebSocketResponse = None

        self.__message_create_callback: Callable[[Bot, Message], Any] = None
        self.__message_update_callback: Callable[[Bot, Message], Any] = None

    def run(self):
        resp = requests.get(
            'https://discord.com/api/v9/gateway/bot',
            headers={
                "Authorization": "Bot " + self.__token
            }
        )
        if resp.status_code != 200:
            raise requests.RequestException('failed to get gateway url')
        resp_json = resp.json()
        if 'url' not in resp_json:
            raise KeyError('invalid response when get gateway url')
        self.__gateway_url = resp_json['url'] + "?v=9&encoding=json"

        try:
            asyncio.run(self.__run())
        except KeyboardInterrupt:
            print("EXIT!!!")

    def on_message_create(self, callback: Callable[['Bot', Message], Any]):
        self.__message_create_callback = callback
    
    def on_message_update(self, callback: Callable[['Bot', Message], Any]):
        self.__message_update_callback = callback
    
    def send_message(self, channel_id: str, message: MessageSend) -> Message:
        resp = requests.post(
            f"https://discord.com/api/v9/channels/{channel_id}/messages",
            data=message.to_json(),
            headers={
                "Authorization": "Bot " + self.__token
            }
        )
        if resp.status_code != 200:
            raise requests.RequestException('failed to send message')
        resp_json = resp.json()
        return Message(resp_json)

    async def __heartbeat(self):
        heartbeat_payload = {"op": 1, "d": None}
        while True:
            await asyncio.sleep(self.__heartbeat_interval / 1000)
            await self.__ws.send_json(heartbeat_payload)

    async def __run(self):
        session = aiohttp.ClientSession()
        self.__ws = await session.ws_connect(self.__gateway_url)
        resp = await self.__ws.receive_json()
        if 'op' not in resp or resp['op'] != 10 or 'd' not in resp or 'heartbeat_interval' not in resp['d']:
            raise KeyError('invalid response when connected to gateway')
        self.__heartbeat_interval = resp['d']['heartbeat_interval']

        heartbeat_task: asyncio.Task = asyncio.create_task(self.__heartbeat())

        await self.__ws.send_json({
            "op": 2,
            "d": {
                "token": self.__token,
                "intents": 513,
                "properties": {
                    "$os": "linux",
                    "$browser": "disco",
                    "$device": "pc"
                }
            }
        })

        try:
            while True:
                resp = await self.__ws.receive()
                if resp.type == aiohttp.WSMsgType.TEXT:
                    respJson = resp.json()
                    if respJson['op'] == 0:
                        if respJson['t'] == 'MESSAGE_CREATE' and self.__message_create_callback != None:
                            self.__message_create_callback(self, Message(respJson['d']))
                        elif respJson['t'] == 'MESSAGE_UPDATE' and self.__message_update_callback != None:
                            self.__message_update_callback(self, Message(respJson['d']))
        except:
            pass
        heartbeat_task.cancel()
        await self.__ws.close()
        await session.close()
