from typing import List, Optional

import socket
import asyncio

from ..core.client import AsyncClient

class SubdomainScanner:
    
    COMMON_SUBS = [
        "www", "mail", "ftp", "admin", "blog", "dev", "test", "api",
        "staging", "portal", "m", "mobile", "app", "vpn", "beta",
        "dashboard", "secure", "support", "help", "shop", "store"
    ]

    @staticmethod
    async def scan(domain: str) -> List[str]:
        found = set()
        async with AsyncClient() as client:
            tasks = [SubdomainScanner._check(client, f"{sub}.{domain}") for sub in SubdomainScanner.COMMON_SUBS]
            for coro in asyncio.as_completed(tasks):
                result = await coro
                if result:
                    found.add(result)
        return list(found)

    @staticmethod
    async def _check(client: AsyncClient, sub: str) -> Optional[str]:
        try:
            status, _ = await client.get(f"http://{sub}", allow_redirects=False)
            if status > 0 and status != 404:
                return sub
        except:
            pass
        try:
            await asyncio.get_event_loop().run_in_executor(None, socket.gethostbyname, sub)
            return sub
        except:
            return None