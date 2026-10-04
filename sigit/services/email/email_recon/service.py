import asyncio
import json

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient
from sigit.services.email.email_recon.models import EmailPlatformRule
from sigit.services.email.email_recon.platforms import EMAIL_PLATFORMS


class EmailReconInput(BaseModel):
    email: str = Field(description="Target email address to inspect across platforms")


class EmailRecon(BaseService):
    name = "EmailRecon"
    description = (
        "Check email registration status across 100+ platforms with multi-factor validation"
    )
    category = Category.EMAIL
    input_schema = EmailReconInput

    async def _check_platform(self, rule: EmailPlatformRule, email: str) -> dict[str, str] | None:
        try:
            if rule.custom_checker is not None:
                is_taken = await rule.custom_checker(email)
                if is_taken:
                    return {
                        "platform": rule.name,
                        "category": rule.category,
                        "url": rule.url,
                        "status": "Registered",
                    }
                return None

            (
                method,
                check_url,
                headers,
                json_data,
                data_data,
                params_data,
            ) = rule.build_request(email)

            response = await HttpClient.request(
                method,
                check_url,
                headers=headers or None,
                json=json_data,
                data=data_data,
                params=params_data,
                timeout=7.0,
            )

            text = response.text or ""
            json_obj = None
            try:
                json_obj = response.json()
            except (json.JSONDecodeError, ValueError):
                pass

            is_taken = rule.evaluate(response.status_code, text, json_obj)
            if is_taken:
                return {
                    "platform": rule.name,
                    "category": rule.category,
                    "url": rule.url,
                    "status": "Registered",
                }
            return None
        except Exception:
            return None

    async def execute(self, params: EmailReconInput) -> ServiceResult:
        email = params.email.strip().lower()
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            return ServiceResult.fail("Invalid email address format")

        semaphore = asyncio.Semaphore(10)

        async def _bounded_check(rule: EmailPlatformRule) -> dict[str, str] | None:
            async with semaphore:
                return await self._check_platform(rule, email)

        tasks = [_bounded_check(rule) for rule in EMAIL_PLATFORMS]
        results = await asyncio.gather(*tasks)

        hits: list[dict[str, str]] = [r for r in results if r is not None]
        if not hits:
            return ServiceResult.fail(f"No registered accounts identified for '{email}'")

        hits.sort(key=lambda item: (item["category"], item["platform"]))
        return ServiceResult.ok(hits, render_type=RenderType.TABLE)
