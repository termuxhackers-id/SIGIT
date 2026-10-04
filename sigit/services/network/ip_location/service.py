import asyncio
import socket
from typing import Any

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient


class IpLocationInput(BaseModel):
    ip: str = Field(description="Target IP address")


class IPLocation(BaseService):
    name = "IPLocation"
    description = "Lookup geolocation, reverse DNS, and ISP details for an IP"
    category = Category.NETWORK
    input_schema = IpLocationInput

    FIELDS: dict[str, str] = {
        "ip": "IP Address",
        "city": "City",
        "region": "Region",
        "country": "Country",
        "loc": "Coordinates",
        "org": "Organization / ASN",
        "postal": "Postal Code",
        "timezone": "Timezone",
    }

    async def execute(self, params: IpLocationInput) -> ServiceResult:
        ip_target = params.ip.strip()
        url = f"https://ipinfo.io/{ip_target}/json"

        try:
            response = await HttpClient.get(url)
            if response.status_code != 200:
                return ServiceResult.fail(f"Could not retrieve location for IP: {ip_target}")

            raw_data = response.json()
            if "bogon" in raw_data:
                return ServiceResult.fail(f"IP {ip_target} is a bogon/private address")

            reverse_ptr = "None resolved"
            try:
                host_info = await asyncio.to_thread(socket.gethostbyaddr, ip_target)
                reverse_ptr = host_info[0]
            except Exception:
                if "hostname" in raw_data:
                    reverse_ptr = raw_data["hostname"]

            clean_data: dict[str, Any] = {
                "Reverse_DNS_PTR": reverse_ptr,
            }

            for api_key, label in self.FIELDS.items():
                if api_key in raw_data and raw_data[api_key]:
                    clean_data[label] = raw_data[api_key]

            if not clean_data:
                return ServiceResult.fail("No location data found")

            return ServiceResult.ok(clean_data, render_type=RenderType.KEY_VALUE)
        except Exception as error:
            return ServiceResult.fail(f"Lookup error: {error}")
