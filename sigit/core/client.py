import aiohttp

from typing import Tuple, Dict, Optional
from .config import config

import asyncio

class AsyncClient:
    def __init__(self):
        self.session: aiohttp.ClientSession | None = None
    
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=config.TIMEOUT)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={"User-Agent": config.USER_AGENT}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get(self, url: str, **kwargs) -> Tuple[int, str]:
        try:
            async with self.session.get(url, **kwargs) as response: # type: ignore
                return response.status, await response.text()
        except asyncio.TimeoutError:
            return 0, "Timeout"
        except Exception as e:
            return 0, str(e)
    
    async def get_json(self, url: str, **kwargs) -> Tuple[int, Dict]:
        try:
            async with self.session.get(url, **kwargs) as response: # type: ignore
                return response.status, await response.json()
        except Exception:
            return 0, {}