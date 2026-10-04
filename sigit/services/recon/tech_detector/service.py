import re
from typing import Any

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient


class TechDetectorInput(BaseModel):
    url: str = Field(description="Target website URL")


class TechStackDetector(BaseService):
    name = "TechDetector"
    description = "Detect CMS, frameworks, meta generators, web servers, and CDNs"
    category = Category.RECON
    input_schema = TechDetectorInput

    FRAMEWORK_PATTERNS: dict[str, list[str]] = {
        "WordPress": ["wp-content", "wp-includes"],
        "Joomla": ["joomla"],
        "Drupal": ["drupal"],
        "Shopify": ["shopify", "cdn.shopify.com"],
        "Ghost": ["ghost-root", "ghost.org"],
        "React": ["react", "_reactroot"],
        "Vue.js": ["vue", "__vue__"],
        "Angular": ["ng-version", "angular"],
        "Bootstrap": ["bootstrap"],
        "Tailwind CSS": ["tailwindcss", "tailwind"],
        "jQuery": ["jquery"],
        "Next.js": ["__next", "_next/static"],
        "Nuxt.js": ["__nuxt"],
        "Laravel": ["laravel"],
        "Django": ["csrfmiddlewaretoken"],
    }

    CDN_HEADERS: dict[str, str] = {
        "cf-ray": "Cloudflare",
        "x-amz-cf-id": "AWS CloudFront",
        "server-timing": "Akamai / CDN",
        "x-fastly-request-id": "Fastly",
        "x-vercel-id": "Vercel",
    }

    async def execute(self, params: TechDetectorInput) -> ServiceResult:
        target_url = params.url.strip()
        if not target_url.startswith(("http://", "https://")):
            target_url = f"https://{target_url}"

        try:
            response = await HttpClient.get(target_url, allow_redirects=True)
            if response.status_code >= 400:
                return ServiceResult.fail(f"HTTP {response.status_code} returned by target")

            detected: dict[str, list[str]] = {
                "servers": [],
                "frameworks": [],
                "cms_generator": [],
                "cdn": [],
                "analytics": [],
            }

            headers_lower = {k.lower(): v for k, v in response.headers.items()}
            server_val = headers_lower.get("server")
            if server_val:
                detected["servers"].append(server_val)

            for cdn_header, cdn_name in self.CDN_HEADERS.items():
                if cdn_header in headers_lower:
                    detected["cdn"].append(cdn_name)

            body = response.text
            body_lower = body.lower()

            generator_match = re.search(
                r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']',
                body,
                re.IGNORECASE,
            )
            if generator_match:
                detected["cms_generator"].append(generator_match.group(1))

            for framework, keywords in self.FRAMEWORK_PATTERNS.items():
                if any(kw in body_lower for kw in keywords):
                    detected["frameworks"].append(framework)

            if "google-analytics" in body_lower or "gtag" in body_lower:
                detected["analytics"].append("Google Analytics")
            if "googletagmanager" in body_lower:
                detected["analytics"].append("Google Tag Manager")

            summary: dict[str, Any] = {
                "target_url": target_url,
                "status_code": response.status_code,
                "servers": detected["servers"] or ["Unknown"],
                "generator_tag": detected["cms_generator"] or ["None declared"],
                "frameworks": detected["frameworks"] or ["None detected"],
                "cdn": detected["cdn"] or ["None detected"],
                "analytics": detected["analytics"] or ["None detected"],
            }

            return ServiceResult.ok(summary, render_type=RenderType.KEY_VALUE)
        except Exception as error:
            return ServiceResult.fail(f"Tech detection error: {error}")
