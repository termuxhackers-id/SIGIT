import asyncio
import socket

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient


class SubdomainInput(BaseModel):
    domain: str = Field(description="Target apex domain")
    use_ct_logs: bool = Field(default=True, description="Query Certificate Transparency logs")


class SubdomainScanner(BaseService):
    name = "SubdomainScan"
    description = "Enumerate subdomains via CT logs and DNS enumeration"
    category = Category.DOMAIN
    input_schema = SubdomainInput

    COMMON_PREFIXES: list[str] = [
        "www",
        "mail",
        "ftp",
        "admin",
        "blog",
        "dev",
        "test",
        "api",
        "staging",
        "portal",
        "m",
        "mobile",
        "app",
        "vpn",
        "beta",
        "dashboard",
        "secure",
        "support",
        "help",
        "shop",
        "store",
        "auth",
        "login",
        "status",
        "docs",
    ]

    async def execute(self, params: SubdomainInput) -> ServiceResult:
        clean = params.domain.strip().lower()
        apex_domain = clean.replace("https://", "").replace("http://", "").split("/")[0]
        discovered_subs: set[str] = set()

        if params.use_ct_logs:
            ct_subdomains = await self._query_ct_logs(apex_domain)
            discovered_subs.update(ct_subdomains)

        for prefix in self.COMMON_PREFIXES:
            discovered_subs.add(f"{prefix}.{apex_domain}")

        results: list[dict[str, str]] = []

        async def _resolve_sub(sub: str) -> None:
            try:
                ip = await asyncio.to_thread(socket.gethostbyname, sub)
                results.append({"subdomain": sub, "ip_address": ip, "status": "RESOLVED"})
            except OSError:
                pass

        await asyncio.gather(*[_resolve_sub(sub) for sub in list(discovered_subs)[:100]])

        if not results:
            return ServiceResult.fail(f"No active subdomains resolved for {apex_domain}")

        results.sort(key=lambda item: item["subdomain"])
        return ServiceResult.ok(results, render_type=RenderType.TABLE)

    @staticmethod
    async def _query_ct_logs(domain: str) -> set[str]:
        names: set[str] = set()
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        try:
            response = await HttpClient.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    for item in data[:150]:
                        name_val = item.get("name_value", "")
                        for line in name_val.splitlines():
                            clean = line.strip().lower().lstrip("*.")
                            if clean.endswith(f".{domain}") and clean != domain:
                                names.add(clean)
        except Exception:
            pass
        return names
