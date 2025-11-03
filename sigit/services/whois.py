from ..core.client import AsyncClient

class WHOISLookup:
    
    @staticmethod
    async def lookup(domain: str) -> str:
        async with AsyncClient() as client:
            status, data = await client.get(f"https://api.hackertarget.com/whois/?q={domain}")
            return data if status == 200 else ""