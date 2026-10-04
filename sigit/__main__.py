import asyncio
import sys

from sigit.cli.display import render_result, save_result_to_file
from sigit.cli.menu import Menu
from sigit.cli.parser import build_parser, extract_params
from sigit.core.http import HttpClient


async def run_app() -> None:
    parser, cmd_service_map = build_parser()
    args = parser.parse_args()

    if args.interactive or not args.command:
        Menu.show()
        await Menu.run()
        return

    svc_cls = cmd_service_map.get(args.command)
    if not svc_cls:
        parser.print_help()
        sys.exit(1)

    try:
        raw_params = extract_params(svc_cls, args)
        params = svc_cls.input_schema.model_validate(raw_params)
        service = svc_cls()
        result = await service.execute(params)

        render_result(result)

        if args.output and result.data is not None:
            save_result_to_file(result.data, args.output)

        if not result.success:
            sys.exit(1)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


async def main() -> None:
    try:
        await run_app()
    finally:
        await HttpClient.close()


def entrypoint() -> None:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    entrypoint()
