import asyncio
import json

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient
from sigit.services.social.user_recon.models import PlatformRule
from sigit.services.social.user_recon.platforms import PLATFORMS


class UserReconInput(BaseModel):
    username: str = Field(description="Target username to inspect across platforms")


class UserRecon(BaseService):
    name = "UserRecon"
    description = "Check username across 100+ platforms with multi-factor response validation"
    category = Category.SOCIAL
    input_schema = UserReconInput

    async def _check_platform(self, rule: PlatformRule, username: str) -> dict[str, str] | None:
        if not rule.is_valid_username(username):
            return None

        check_url = rule.get_check_url(username)
        profile_url = rule.get_profile_url(username)

        try:
            if rule.custom_checker is not None:
                is_found = await rule.custom_checker(username)
                if is_found:
                    return {
                        "platform": rule.name,
                        "category": rule.category,
                        "url": profile_url,
                        "status": "Found",
                    }
                return None

            response = await HttpClient.get(
                check_url,
                headers=rule.headers,
                allow_redirects=rule.allow_redirects,
                timeout=6.0,
            )

            status = response.status_code
            if status in rule.available_status_codes:
                return None

            text = response.text or ""

            for neg in rule.negative_markers:
                if neg in text:
                    return None

            if rule.positive_markers:
                if not any(pos in text for pos in rule.positive_markers):
                    return None

            if rule.is_json:
                try:
                    payload = response.json()
                except (json.JSONDecodeError, ValueError):
                    return None

                if rule.json_list_not_empty:
                    if not isinstance(payload, list) or len(payload) == 0:
                        return None

                if rule.json_verify_key:
                    if not isinstance(payload, dict):
                        return None
                    val = payload.get(rule.json_verify_key)
                    if val is None or val == "" or val == []:
                        return None
                    if rule.json_verify_key == "them" and isinstance(val, list):
                        if not val or val[0] is None:
                            return None

            if status not in rule.taken_status_codes:
                return None

            return {
                "platform": rule.name,
                "category": rule.category,
                "url": profile_url,
                "status": "Found",
            }
        except Exception:
            return None

    async def execute(self, params: UserReconInput) -> ServiceResult:
        username = params.username.strip()
        semaphore = asyncio.Semaphore(10)

        async def _bounded_check(rule: PlatformRule) -> dict[str, str] | None:
            async with semaphore:
                return await self._check_platform(rule, username)

        tasks = [_bounded_check(rule) for rule in PLATFORMS]
        results = await asyncio.gather(*tasks)

        hits: list[dict[str, str]] = [r for r in results if r is not None]

        if not hits:
            return ServiceResult.fail(f"No active accounts identified for '{username}'")

        hits.sort(key=lambda item: (item["category"], item["platform"]))
        return ServiceResult.ok(hits, render_type=RenderType.TABLE)
