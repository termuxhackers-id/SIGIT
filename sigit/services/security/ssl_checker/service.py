import asyncio
import socket
import ssl
from datetime import datetime
from typing import Any

import certifi
from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult


class SslInput(BaseModel):
    domain: str = Field(description="Target domain name")


class SSLChecker(BaseService):
    name = "SSLChecker"
    description = "Inspect SSL/TLS certificate, SANs, validity, and cipher"
    category = Category.SECURITY
    input_schema = SslInput

    async def execute(self, params: SslInput) -> ServiceResult:
        clean_domain = (
            params.domain.strip().replace("https://", "").replace("http://", "").split("/")[0]
        )

        try:
            cert_data = await asyncio.to_thread(self._fetch_certificate, clean_domain)
            if not cert_data:
                return ServiceResult.fail(f"Could not retrieve SSL certificate for {clean_domain}")

            return ServiceResult.ok(cert_data, render_type=RenderType.KEY_VALUE)
        except Exception as error:
            return ServiceResult.fail(f"SSL handshake error: {error}")

    def _fetch_certificate(self, domain: str) -> dict[str, Any] | None:
        context = ssl.create_default_context(cafile=certifi.where())
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                cert_dict: dict[str, Any] = cert if isinstance(cert, dict) else {}
                if not cert_dict:
                    return None

                tls_version = ssock.version() or "Unknown"
                cipher_info = ssock.cipher()
                cipher_name = cipher_info[0] if cipher_info else "Unknown"

                subject_items: dict[str, str] = {}
                for rdn in cert_dict.get("subject", ()):
                    for key, val in rdn:
                        subject_items[key] = val

                issuer_items: dict[str, str] = {}
                for rdn in cert_dict.get("issuer", ()):
                    for key, val in rdn:
                        issuer_items[key] = val

                san_list: list[str] = []
                for san_type, san_val in cert_dict.get("subjectAltName", ()):
                    if san_type == "DNS":
                        san_list.append(san_val)

                not_after_str = str(cert_dict.get("notAfter", ""))
                not_before_str = str(cert_dict.get("notBefore", ""))

                days_remaining = 0
                expired = False
                if not_after_str:
                    try:
                        expiry_date = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                        now = datetime.now()
                        expired = expiry_date < now
                        days_remaining = max(0, (expiry_date - now).days)
                    except ValueError:
                        pass

                issuer_name = issuer_items.get(
                    "organizationName", issuer_items.get("commonName", "N/A")
                )

                return {
                    "common_name": str(subject_items.get("commonName", "N/A")),
                    "issuer": str(issuer_name),
                    "tls_version": tls_version,
                    "cipher_suite": cipher_name,
                    "valid_from": not_before_str,
                    "valid_until": not_after_str,
                    "days_remaining": f"{days_remaining} days",
                    "is_expired": "Yes" if expired else "No",
                    "sans_count": len(san_list),
                    "subject_alt_names": san_list[:20] if san_list else ["None"],
                }
