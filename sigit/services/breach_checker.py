from typing import Dict

from ..core.client import AsyncClient

class DataBreachChecker:
    
    @staticmethod
    async def check(email: str) -> Dict:
        async with AsyncClient() as client:
            status, data = await client.get_json(f"https://api.xposedornot.com/v1/check-email/{email}")
            return data if status == 200 and isinstance(data, dict) else {}