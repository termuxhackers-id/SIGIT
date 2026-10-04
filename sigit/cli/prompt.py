from typing import Any, get_args, get_origin

from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from rich.prompt import Prompt


def prompt_schema(schema: type[BaseModel]) -> BaseModel:
    data: dict[str, Any] = {}

    for name, field_info in schema.model_fields.items():
        if field_info.json_schema_extra and isinstance(field_info.json_schema_extra, dict):
            if field_info.json_schema_extra.get("skip_prompt"):
                continue

        label = field_info.description or name.replace("_", " ").title()

        if field_info.is_required() or field_info.default in (..., PydanticUndefined):
            default = None
            default_str = None
        else:
            default = field_info.default
            default_str = str(default) if default is not None else None

        if default_str is not None:
            raw_val = str(Prompt.ask(f"[bold cyan]{label}[/]", default=default_str) or "")
        else:
            raw_val = str(Prompt.ask(f"[bold cyan]{label}[/]") or "")

        field_type = field_info.annotation
        origin = get_origin(field_type)

        if raw_val == "" and default is None:
            data[name] = None
        elif field_type is int:
            data[name] = int(raw_val)
        elif field_type is float:
            data[name] = float(raw_val)
        elif field_type is bool:
            data[name] = raw_val.lower() in ("true", "1", "yes", "y")
        elif origin is list:
            item_type = get_args(field_type)[0] if get_args(field_type) else str
            items = [item.strip() for item in raw_val.split(",") if item.strip()]
            data[name] = [item_type(item) for item in items]
        else:
            data[name] = raw_val

    return schema.model_validate(data)
