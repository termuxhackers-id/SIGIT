from typing import Dict

from ..core.client import AsyncClient

class IPLocation:
    
    @staticmethod
    async def lookup(ip: str) -> Dict[str, str]:
        async with AsyncClient() as client:
            _, data = await client.get_json(f"https://ipinfo.io/{ip}/json")
            return data if isinstance(data, dict) else {}