from typing import Any

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient


class HeaderInput(BaseModel):
    url: str = Field(description="Target website URL")


class HeaderAnalyzer(BaseService):
    name = "HeaderAnalyzer"
    description = "Audit HTTP security headers and score posture"
    category = Category.SECURITY
    input_schema = HeaderInput

    SECURITY_HEADERS: dict[str, str] = {
        "Strict-Transport-Security": "HSTS - Enforces secure HTTPS",
        "Content-Security-Policy": "CSP - Prevents XSS and injection",
        "X-Frame-Options": "Clickjacking defense",
        "X-Content-Type-Options": "MIME-sniffing prevention",
        "X-XSS-Protection": "Legacy browser XSS filter",
        "Referrer-Policy": "Controls referrer privacy",
        "Permissions-Policy": "Controls browser feature APIs",
    }

    async def execute(self, params: HeaderInput) -> ServiceResult:
        target_url = params.url.strip()
        if not target_url.startswith(("http://", "https://")):
            target_url = f"https://{target_url}"

        try:
            response = await HttpClient.get(target_url, allow_redirects=True)
            response_headers = {k.lower(): v for k, v in response.headers.items()}

            present_headers: list[str] = []
            missing_headers: list[str] = []

            for header_name, description in self.SECURITY_HEADERS.items():
                if header_name.lower() in response_headers:
                    present_headers.append(f"[+] {header_name}: {description}")
                else:
                    missing_headers.append(f"[-] {header_name}: {description}")

            total = len(self.SECURITY_HEADERS)
            score = len(present_headers)
            percentage = int((score / total) * 100)

            result_data: dict[str, Any] = {
                "target_url": target_url,
                "status_code": response.status_code,
                "security_score": f"{score}/{total} ({percentage}%)",
                "present_headers": present_headers if present_headers else "None",
                "missing_headers": missing_headers if missing_headers else "None",
            }

            server_header = response_headers.get("server")
            if server_header:
                result_data["server"] = server_header

            return ServiceResult.ok(result_data, render_type=RenderType.KEY_VALUE)
        except Exception as error:
            return ServiceResult.fail(f"Failed to inspect headers: {error}")
