from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient


class BreachInput(BaseModel):
    email: str = Field(description="Target email address")


class DataBreachChecker(BaseService):
    name = "BreachChecker"
    description = "Check email in known data breaches"
    category = Category.SECURITY
    input_schema = BreachInput

    async def execute(self, params: BreachInput) -> ServiceResult:
        url = f"https://api.xposedornot.com/v1/check-email/{params.email}"
        try:
            response = await HttpClient.get(url)
            if response.status_code != 200:
                return ServiceResult.ok(
                    {"email": params.email, "status": "No breaches found"},
                    render_type=RenderType.KEY_VALUE,
                )

            data = response.json()
            raw_breaches = data.get("breaches", [])
            breach_names: list[str] = []

            for item in raw_breaches:
                if isinstance(item, list):
                    breach_names.extend(str(sub_item) for sub_item in item)
                else:
                    breach_names.append(str(item))

            if breach_names:
                return ServiceResult.ok(
                    {
                        "email": params.email,
                        "breach_count": len(breach_names),
                        "breaches": breach_names,
                    },
                    render_type=RenderType.KEY_VALUE,
                )

            return ServiceResult.ok(
                {"email": params.email, "status": "No breaches found"},
                render_type=RenderType.KEY_VALUE,
            )
        except Exception as error:
            return ServiceResult.fail(f"Request failed: {error}")
