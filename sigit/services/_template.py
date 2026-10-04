from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult


class TemplateInput(BaseModel):
    target: str = Field(description="Target domain or IP")


class TemplateService(BaseService):
    name = "TemplateTool"
    description = "Service template example"
    category = Category.RECON
    input_schema = TemplateInput

    async def execute(self, params: TemplateInput) -> ServiceResult:
        result_data = {"target": params.target, "status": "active"}
        return ServiceResult.ok(result_data, render_type=RenderType.KEY_VALUE)
