from typing import Any, Dict

import aiohttp

from lunar.config import Config


class LunarError(Exception):
    """
    Exception class for Lunar Client.
    """

    def __init__(self, code: int, msg: str, error_code: str = ""):
        super().__init__(msg)
        self.code = code
        self.msg = msg
        self.error_code = error_code


class LunarClient:
    """
    Super class for clients.
    """

    def __init__(self, config: Config):
        self.config = config
        self.url = config.URL
        self.env = config.ENV
        self.apikey_header = {"x-api-key": config.APIKEY}

    async def _request(
        self, method: str, url: str, headers: Dict[str, Any] = None, data: Any = None, params=None
    ) -> Any:
        api_path = url if self.config.ENV == "LOCAL" or self.config.RUNTIME_ENV == "BAP" else f"/api{url}"

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=f"{self.url}{'' if api_path.startswith('/') else '/'}{api_path}",
                headers={**self.apikey_header, **headers} if headers else self.apikey_header,
                json=data,
                params=params,
            ) as response:
                try:
                    body = await response.json()
                    if not response.ok:
                        raise LunarError(code=response.status, msg=body.get("message"), error_code=body.get("code"))
                    return body
                except aiohttp.client_exceptions.ContentTypeError:
                    return await response.text() or None
