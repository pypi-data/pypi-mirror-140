import asyncio
from abc import ABC
from http import HTTPStatus
from typing import Any, Dict, Mapping, Optional

import aiohttp
import fast_json
from aiohttp import hdrs
from yarl import URL


TResponse = Dict[str, Any]


class BaseClient(ABC):
    __slots__ = ("_url", "_session")

    def __init__(
        self,
        url: URL,
        auth_token: str,
        connector: Optional[aiohttp.TCPConnector] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        default_timeout: Optional[aiohttp.ClientTimeout] = None,
        **kwargs: Any,
    ):
        loop = loop or asyncio.get_event_loop()
        self._url = url
        self._session = aiohttp.ClientSession(
            connector=connector,
            json_serialize=fast_json.dumps,
            loop=loop,
            timeout=default_timeout or aiohttp.client.DEFAULT_TIMEOUT,
            headers={
                hdrs.ACCEPT: "application/json",
                hdrs.ACCEPT_ENCODING: "gzip, deflate",
                hdrs.CONNECTION: "keepalive",
                hdrs.AUTHORIZATION: auth_token,
            },
            **kwargs,
        )

    @property
    def url(self) -> URL:
        return self._url

    async def close(self) -> None:
        await self._session.close()

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Mapping[str, str]] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> Optional[TResponse]:
        url = self._url / path.strip("/")
        async with self._session.request(
            method,
            url,
            params=params,
            data=data,
            json=json,
            **kwargs,
        ) as response:
            response.raise_for_status()
            content_type = response.headers.get(hdrs.CONTENT_TYPE)
            if (response.status == HTTPStatus.OK) and (
                content_type == "application/json"
            ):
                return await response.json(loads=fast_json.loads)
            return None

    async def _get(
        self,
        path: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> Optional[TResponse]:
        return await self._request(hdrs.METH_GET, path, params=params, **kwargs)

    async def _post(
        self,
        path: str,
        *,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> Optional[TResponse]:
        return await self._request(
            hdrs.METH_POST,
            path,
            data=data,
            json=json,
            **kwargs,
        )
