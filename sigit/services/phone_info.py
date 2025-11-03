from typing import Dict

from ..core.client import AsyncClient

class PhoneInfo:
    
    API_KEY = "5F2D6300E445DEA88684053144996C"

    @staticmethod
    async def lookup(phone: str) -> Dict:
        url = f"https://api.veriphone.io/v2/verify?phone={phone}&key={PhoneInfo.API_KEY}"
        async with AsyncClient() as client:
            _, data = await client.get_json(url)
            return data if isinstance(data, dict) else {}