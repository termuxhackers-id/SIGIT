from typing import List

import socket

from ..core.client import AsyncClient

class ReverseIPLookup:
    
    @staticmethod
    async def lookup(domain: str) -> List[str]:
        try:
            ip = socket.gethostbyname(domain)
            async with AsyncClient() as client:
                status, data = await client.get(f"https://api.hackertarget.com/reverseiplookup/?q={ip}")
                if status == 200:
                    return [d for d in data.strip().split('\n') if d and 'error' not in d.lower()]
        except:
            pass
        return []