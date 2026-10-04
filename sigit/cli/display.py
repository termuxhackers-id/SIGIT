import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from sigit.core.base import RenderType, ServiceResult

console = Console()

LOGO = """[bold blue]
                    _cyqyc_
                :>3qKKKKKKKq3>:
            ';CpKKKKKKKKKKKKKKKKKpC;'
        -"iPKKKKKKKKKKKKKKKKKKKKKKKPi"-
    `~v]KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK]v~`
,rwKKKKKKKKKKKKKPv;,:'-':,;vPKKKKKKKKKKKKKwr,
!KKKKKKKKKKKKKKK/             !KKKKKKKKKKKKKKK!
!KKKKKKKKKKKKKKf               CKKKKKKKKKKKKKK!
!KKKKKKKKKKKKKp-               -qKKKKKKKKKKKKK!
!KKKKKKKKKKKKK>"               "\\KKKKKKKKKKKKK!
!KKKKKKKw;,_'-                   .-:,"wKKKKKKK!
!KKKKKKKKhi*;"                   ";*ihKKKKKKKK!
!KKKKKKKKKKKKK;                 ;KKKKKKKKKKKKK!
!KKKKKKKKKKKKK2>'             '>2KKKKKKKKKKKKK!
!KKKKKKKKKKKKKKKZ             ZKKKKKKKKKKKKKKK!
!KKKKKKKKKKKKKKK5             eKKKKKKKKKKKKKKK!
!KKKKKKKKKKKqC;-               -;CqKKKKKKKKKKK!
<KKKKKKKKkr,                       ,rSKKKKKKKK<
-"v]qj;-                             -;jq]v"-
[/][bold white]                [ S.I.G.I.T ][/bold white]
[dim blue]    Simple Information Gathering Toolkit[/dim blue]
[dim]        Author by [/dim][bold red]@termuxhackers.id[/bold red]
"""


def clear() -> None:
    console.clear()


def print_logo() -> None:
    console.print(LOGO)


def print_header(title: str) -> None:
    console.print(f"\n[bold blue]───[/] [bold white]{title.upper()}[/] [bold blue]───[/]\n")


def render_result(result: ServiceResult) -> None:
    if not result.success:
        console.print(f"\n[bold red]Error:[/] {result.error}\n")
        return

    data = result.data
    if data is None:
        console.print("[yellow]No data returned.[/yellow]")
        return

    if result.render_type == RenderType.TABLE and isinstance(data, list):
        if not data:
            console.print("[yellow]Empty result set.[/yellow]")
            return

        if isinstance(data[0], dict):
            table = Table(show_header=True, header_style="bold blue")
            keys = list(data[0].keys())
            for key in keys:
                table.add_column(key.replace("_", " ").title())

            for row in data:
                table.add_row(*[str(row.get(k, "")) for k in keys])

            console.print(table)
            console.print(f"\n[dim blue]Total:[/] [yellow]{len(data)}[/] items")
        else:
            for item in data:
                console.print(f" [blue]▸[/] {item}")
            console.print(f"\n[dim blue]Total:[/] [yellow]{len(data)}[/] items")

    elif result.render_type == RenderType.KEY_VALUE and isinstance(data, dict):
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold blue", width=25)
        table.add_column("Value", style="white")

        for key, value in data.items():
            label = key.replace("_", " ").title()
            if isinstance(value, list):
                val_str = "\n".join(f"• {item}" for item in value)
            elif isinstance(value, dict):
                val_str = "\n".join(f"{k}: {v}" for k, v in value.items())
            else:
                val_str = str(value)
            table.add_row(label, val_str)

        console.print(table)

    elif result.render_type == RenderType.LIST and isinstance(data, list):
        for item in data:
            console.print(f" [blue]▸[/] {item}")
        console.print(f"\n[dim blue]Total:[/] [yellow]{len(data)}[/] items")

    elif result.render_type == RenderType.TEXT:
        console.print(Panel(str(data), border_style="dim blue"))

    else:
        console.print(data)


def save_result_to_file(data: Any, filename: str) -> None:
    path = Path(filename)
    if isinstance(data, (dict, list)):
        path.write_text(json.dumps(data, indent=2))
    else:
        path.write_text(str(data))
    console.print(f"[green]Results saved to:[/] [yellow]{filename}[/]")


def ask_save_result(result: ServiceResult, default_name: str) -> None:
    if not result.success or result.data is None:
        return

    try:
        should_save = Confirm.ask("\n[bold cyan]Save results to file?[/]", default=False)
        if not should_save:
            return

        filename = result.save_filename or default_name
        save_result_to_file(result.data, filename)
    except (KeyboardInterrupt, EOFError):
        pass
