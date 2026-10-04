import asyncio

from curl_cffi.requests import AsyncSession, Response
from curl_cffi.requests.session import HttpMethod

from sigit.core.config import settings


class HttpClient:
    _session: AsyncSession | None = None
    _semaphore: asyncio.Semaphore | None = None

    @classmethod
    def session(cls) -> AsyncSession:
        if cls._session is None:
            cls._session = AsyncSession(
                impersonate=settings.impersonate,
                timeout=settings.timeout,
                proxy=settings.proxy,
            )
        return cls._session

    @classmethod
    def semaphore(cls) -> asyncio.Semaphore:
        if cls._semaphore is None:
            cls._semaphore = asyncio.Semaphore(settings.max_concurrency)
        return cls._semaphore

    @classmethod
    async def get(cls, url: str, **kwargs) -> Response:
        async with cls.semaphore():
            return await cls.session().get(url, **kwargs)

    @classmethod
    async def post(cls, url: str, **kwargs) -> Response:
        async with cls.semaphore():
            return await cls.session().post(url, **kwargs)

    @classmethod
    async def request(cls, method: HttpMethod, url: str, **kwargs) -> Response:
        async with cls.semaphore():
            return await cls.session().request(method, url, **kwargs)

    @classmethod
    async def close(cls) -> None:
        if cls._session is not None:
            await cls._session.close()
            cls._session = None
