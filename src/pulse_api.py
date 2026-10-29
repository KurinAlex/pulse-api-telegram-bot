from typing import Self

import aiohttp


class PulseApiError(Exception):
    def __init__(self, status: int, body: str):
        super().__init__(f"Pulse API returned {status}")
        self.status = status
        self.body = body


class PulseApi:
    def __init__(self, host: str, token: str):
        self._host = host
        # Change this if your API expects a different auth scheme,
        # e.g. {"X-API-Key": token}.
        self._headers = {"Authorization": f"Bearer {token}"}
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Self:
        self._session = aiohttp.ClientSession(
            headers=self._headers,
            timeout=aiohttp.ClientTimeout(total=30),
        )
        return self

    async def __aexit__(self, *exc) -> None:
        if self._session:
            await self._session.close()

    async def _post(self, path: str, data: aiohttp.FormData | None = None) -> str:
        assert self._session is not None
        async with self._session.post(f"{self._host}{path}", data=data) as resp:
            body = await resp.text()
            if resp.status >= 400:
                raise PulseApiError(resp.status, body)
            return body

    async def sleep_on(self) -> str:
        return await self._post("/sleep_on")

    async def sleep_off(self) -> str:
        return await self._post("/sleep_off")

    async def picture(self, content: bytes, filename: str, content_type: str) -> str:
        form = aiohttp.FormData()
        form.add_field("file", content, filename=filename, content_type=content_type)
        return await self._post("/picture", data=form)
