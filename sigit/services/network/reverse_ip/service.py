import asyncio
import socket

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient


class ReverseIpInput(BaseModel):
    target: str = Field(description="Target domain or IP address")


class ReverseIPLookup(BaseService):
    name = "ReverseIP"
    description = "Discover other domains hosted on the same IP"
    category = Category.NETWORK
    input_schema = ReverseIpInput

    async def execute(self, params: ReverseIpInput) -> ServiceResult:
        raw_target = params.target.strip()

        try:
            ip_address = await asyncio.to_thread(socket.gethostbyname, raw_target)
        except OSError:
            ip_address = raw_target

        url = f"https://api.hackertarget.com/reverseiplookup/?q={ip_address}"
        try:
            response = await HttpClient.get(url)
            if response.status_code != 200:
                return ServiceResult.fail("Reverse IP service returned an error")

            lines = [
                line.strip()
                for line in response.text.splitlines()
                if line.strip() and "error" not in line.lower()
            ]

            if not lines:
                return ServiceResult.fail("No neighboring domains discovered")

            domains_data = [{"domain": domain} for domain in lines]
            return ServiceResult.ok(domains_data, render_type=RenderType.TABLE)
        except Exception as error:
            return ServiceResult.fail(f"Lookup error: {error}")
