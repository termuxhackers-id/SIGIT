from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class Category(StrEnum):
    SOCIAL = "Social"
    NETWORK = "Network"
    DOMAIN = "Domain"
    SECURITY = "Security"
    EMAIL = "Email"
    RECON = "Reconnaissance"


class RenderType(StrEnum):
    TABLE = "table"
    KEY_VALUE = "key_value"
    LIST = "list"
    TEXT = "text"


class ServiceResult(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None
    render_type: RenderType = RenderType.TABLE
    save_filename: str | None = None

    @classmethod
    def ok(
        cls,
        data: Any,
        render_type: RenderType = RenderType.TABLE,
        save_filename: str | None = None,
    ) -> "ServiceResult":
        return cls(
            success=True,
            data=data,
            render_type=render_type,
            save_filename=save_filename,
        )

    @classmethod
    def fail(cls, error: str) -> "ServiceResult":
        return cls(
            success=False,
            error=error,
        )


class BaseService(ABC):
    name: str
    description: str
    category: Category
    input_schema: type[BaseModel]

    @abstractmethod
    async def execute(self, params: Any) -> ServiceResult:
        pass
