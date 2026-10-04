import asyncio
import socket
from typing import Any

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient


class DnsInput(BaseModel):
    domain: str = Field(description="Target domain name")


class DNSRecon(BaseService):
    name = "DNSRecon"
    description = "Enumerate A, CNAME, MX, NS, SOA, and security TXT records"
    category = Category.DOMAIN
    input_schema = DnsInput

    async def execute(self, params: DnsInput) -> ServiceResult:
        clean = params.domain.strip().lower()
        domain = clean.replace("https://", "").replace("http://", "").split("/")[0]
        records: dict[str, Any] = {}

        try:
            ip_address = await asyncio.to_thread(socket.gethostbyname, domain)
            records["A_Record"] = ip_address
        except OSError:
            pass

        async def _query_type(t_name: str) -> list[str]:
            url = f"https://dns.google/resolve?name={domain}&type={t_name}"
            try:
                resp = await HttpClient.get(url)
                if resp.status_code == 200:
                    payload = resp.json()
                    answers = payload.get("Answer", [])
                    return [str(a.get("data", "")) for a in answers if a.get("data")]
            except Exception:
                pass
            return []

        cname_data, mx_data, ns_data, soa_data, txt_data = await asyncio.gather(
            _query_type("CNAME"),
            _query_type("MX"),
            _query_type("NS"),
            _query_type("SOA"),
            _query_type("TXT"),
        )

        if cname_data:
            records["CNAME"] = cname_data
        if mx_data:
            records["MX"] = mx_data
        if ns_data:
            records["NS"] = ns_data
        if soa_data:
            records["SOA"] = soa_data

        spf_record = "None"
        dmarc_record = "None"

        for txt in txt_data:
            if "v=spf1" in txt:
                spf_record = txt
                break

        try:
            dmarc_url = f"https://dns.google/resolve?name=_dmarc.{domain}&type=TXT"
            dmarc_resp = await HttpClient.get(dmarc_url)
            if dmarc_resp.status_code == 200:
                for a in dmarc_resp.json().get("Answer", []):
                    data_val = a.get("data", "")
                    if "v=DMARC1" in data_val:
                        dmarc_record = data_val
                        break
        except Exception:
            pass

        records["SPF_Policy"] = spf_record
        records["DMARC_Policy"] = dmarc_record

        if txt_data:
            records["All_TXT_Records"] = txt_data[:10]

        if not records:
            return ServiceResult.fail("No DNS records resolved")

        return ServiceResult.ok(records, render_type=RenderType.KEY_VALUE)
