import asyncio

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient
from sigit.services.email.email_recon.models import EmailPlatformRule
from sigit.services.email.email_recon.platforms import EMAIL_PLATFORMS


class MailFinderInput(BaseModel):
    target: str | None = Field(
        default=None,
        description="Target email address OR full name (e.g. user@gmail.com or Linus Torvalds)",
    )
    email: str | None = Field(
        default=None,
        description="Known target email address",
        json_schema_extra={"skip_prompt": True},
    )
    full_name: str | None = Field(
        default=None,
        description="Full name of target (e.g. Linus Torvalds)",
        json_schema_extra={"skip_prompt": True},
    )
    target_domain: str | None = Field(
        default=None,
        description="Target corporate domain (optional for name search, e.g. company.com)",
    )


class MailFinder(BaseService):
    name = "MailFinder"
    description = (
        "Audit known email registrations across services or generate corporate name permutations"
    )
    category = Category.EMAIL
    input_schema = MailFinderInput

    DEFAULT_DOMAINS: list[str] = [
        "gmail.com",
        "yahoo.com",
        "outlook.com",
        "proton.me",
        "icloud.com",
    ]

    async def _audit_domain(self, domain: str) -> dict[str, str]:
        mx_url = f"https://dns.google/resolve?name={domain}&type=MX"
        dmarc_url = f"https://dns.google/resolve?name=_dmarc.{domain}&type=TXT"
        mx_status = "No MX"
        spoof_risk = "Unknown"

        try:
            mx_resp = await HttpClient.get(mx_url)
            if mx_resp.status_code == 200 and mx_resp.json().get("Answer"):
                mx_status = "MX Active"

            dmarc_resp = await HttpClient.get(dmarc_url)
            if dmarc_resp.status_code == 200:
                answers = dmarc_resp.json().get("Answer", [])
                dmarc_txt = " ".join(a.get("data", "") for a in answers)
                if "p=reject" in dmarc_txt or "p=quarantine" in dmarc_txt:
                    spoof_risk = "Protected (DMARC Enforced)"
                elif "p=none" in dmarc_txt:
                    spoof_risk = "Vulnerable (p=none)"
                else:
                    spoof_risk = "Vulnerable (No DMARC)"
            else:
                spoof_risk = "Vulnerable (No DMARC)"
        except Exception:
            pass

        return {"mx_status": mx_status, "spoof_risk": spoof_risk}

    async def _check_known_email(self, email: str) -> ServiceResult:
        domain = email.split("@")[-1].strip().lower()
        domain_info = await self._audit_domain(domain)

        async def _probe(rule: EmailPlatformRule) -> str | None:
            try:
                if rule.custom_checker is not None:
                    if await rule.custom_checker(email):
                        return rule.name
                    return None

                (
                    method,
                    check_url,
                    headers,
                    json_data,
                    data_data,
                    params_data,
                ) = rule.build_request(email)
                resp = await HttpClient.request(
                    method,
                    check_url,
                    headers=headers or None,
                    json=json_data,
                    data=data_data,
                    params=params_data,
                    timeout=6.0,
                )
                text = resp.text or ""
                json_obj = None
                try:
                    json_obj = resp.json()
                except Exception:
                    pass
                if rule.evaluate(resp.status_code, text, json_obj):
                    return rule.name
                return None
            except Exception:
                return None

        semaphore = asyncio.Semaphore(10)

        async def _bounded_probe(r: EmailPlatformRule) -> str | None:
            async with semaphore:
                return await _probe(r)

        probe_results = await asyncio.gather(*[_bounded_probe(r) for r in EMAIL_PLATFORMS])
        registered_platforms = [p for p in probe_results if p is not None]

        reg_str = (
            ", ".join(sorted(registered_platforms)) if registered_platforms else "None detected"
        )
        total_categories = len({r.category for r in EMAIL_PLATFORMS})
        checked_str = f"{len(EMAIL_PLATFORMS)} platforms ({total_categories} categories)"

        result_data = {
            "email_address": email,
            "mail_domain": domain,
            "mail_server_status": domain_info["mx_status"],
            "spoof_protection": domain_info["spoof_risk"],
            "registered_services": reg_str,
            "checked_services": checked_str,
        }

        return ServiceResult.ok(result_data, render_type=RenderType.KEY_VALUE)

    async def execute(self, params: MailFinderInput) -> ServiceResult:
        raw_target = (params.email or params.target or params.full_name or "").strip()
        if not raw_target:
            return ServiceResult.fail("Please provide a target email address or full name")

        if "@" in raw_target:
            return await self._check_known_email(raw_target)

        parts = raw_target.lower().split()
        if not parts:
            return ServiceResult.fail("Please provide a valid full name")

        first = parts[0]
        last = parts[-1] if len(parts) > 1 else first

        patterns = list(
            {
                f"{first}.{last}",
                f"{first}{last}",
                f"{first[0]}.{last}",
                f"{first[0]}{last}",
                f"{first}_{last}",
                f"{last}.{first}",
                first,
            }
        )

        target_domains = self.DEFAULT_DOMAINS
        if params.target_domain:
            clean_dom = (
                params.target_domain.strip()
                .lower()
                .replace("https://", "")
                .replace("http://", "")
                .split("/")[0]
            )
            target_domains = [clean_dom]

        domain_info_cache: dict[str, dict[str, str]] = {}

        async def _cache_domain(dom: str) -> None:
            domain_info_cache[dom] = await self._audit_domain(dom)

        await asyncio.gather(*[_cache_domain(d) for d in target_domains])

        candidates: list[dict[str, str]] = []
        for pattern in patterns:
            for domain in target_domains:
                info = domain_info_cache.get(
                    domain, {"mx_status": "Unknown", "spoof_risk": "Unknown"}
                )
                candidates.append(
                    {
                        "candidate_email": f"{pattern}@{domain}",
                        "mail_server": info["mx_status"],
                        "email_security": info["spoof_risk"],
                    }
                )

        candidates.sort(key=lambda item: item["candidate_email"])
        return ServiceResult.ok(candidates, render_type=RenderType.TABLE)
