import argparse
import re
from typing import Any

from sigit.core.base import BaseService
from sigit.core.registry import ServiceRegistry


def _to_snake_case(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def build_parser() -> tuple[argparse.ArgumentParser, dict[str, type[BaseService]]]:
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to save output results",
    )

    parser = argparse.ArgumentParser(
        prog="sigit",
        description="Simple Information Gathering Toolkit",
        parents=[common_parser],
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Launch interactive terminal menu",
    )

    subparsers = parser.add_subparsers(dest="command", help="Service to execute")
    cmd_service_map: dict[str, type[BaseService]] = {}

    for svc_cls in ServiceRegistry.ordered():
        cmd_name = _to_snake_case(svc_cls.name)
        cmd_service_map[cmd_name] = svc_cls
        cmd_service_map[svc_cls.name.lower()] = svc_cls

        subparser = subparsers.add_parser(
            cmd_name,
            aliases=[svc_cls.name.lower()],
            help=svc_cls.description,
            parents=[common_parser],
        )

        for field_name, field_info in svc_cls.input_schema.model_fields.items():
            field_type = field_info.annotation
            default = field_info.default if field_info.default is not ... else None
            is_required = field_info.is_required()
            arg_flag = f"--{field_name.replace('_', '-')}"
            help_msg = field_info.description or field_name

            if field_type is bool:
                subparser.add_argument(
                    arg_flag,
                    action="store_true" if not default else "store_false",
                    help=help_msg,
                )
            elif field_type is int:
                subparser.add_argument(
                    arg_flag,
                    type=int,
                    default=default,
                    required=is_required,
                    help=help_msg,
                )
            elif field_type is float:
                subparser.add_argument(
                    arg_flag,
                    type=float,
                    default=default,
                    required=is_required,
                    help=help_msg,
                )
            else:
                subparser.add_argument(
                    arg_flag,
                    type=str,
                    default=default,
                    required=is_required,
                    help=help_msg,
                )

    return parser, cmd_service_map


def extract_params(svc_cls: type[BaseService], parsed_args: argparse.Namespace) -> dict[str, Any]:
    args_dict = vars(parsed_args)
    params: dict[str, Any] = {}

    for field_name in svc_cls.input_schema.model_fields:
        if field_name in args_dict and args_dict[field_name] is not None:
            params[field_name] = args_dict[field_name]

    return params
