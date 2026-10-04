from itertools import groupby

from rich.console import Console
from rich.prompt import Prompt

from sigit.cli.display import ask_save_result, clear, print_header, print_logo, render_result
from sigit.cli.prompt import prompt_schema
from sigit.core.base import BaseService
from sigit.core.registry import ServiceRegistry

console = Console()


class Menu:
    @staticmethod
    def services() -> list[type[BaseService]]:
        return ServiceRegistry.ordered()

    @staticmethod
    def show() -> None:
        clear()
        print_logo()
        all_services = Menu.services()
        sorted_services = sorted(all_services, key=lambda s: s.category.value)

        idx = 1
        for category_name, group in groupby(sorted_services, key=lambda s: s.category.value):
            console.print(f"\n[bold blue]● {category_name.upper()}[/]")
            for svc in group:
                console.print(
                    f"  [bold blue]{idx:02d}.[/] [white]{svc.name:<18}[/] [dim]{svc.description}[/]"
                )
                idx += 1

        console.print(
            f"\n  [bold blue]{idx:02d}.[/] [white]{'Exit Tool':<18}[/] [dim]Close application[/]\n"
        )

    @classmethod
    async def run(cls) -> None:
        while True:
            try:
                all_services = cls.services()
                exit_choice = len(all_services) + 1

                choice_str = Prompt.ask("\n[bold blue]sigit[/][dim]>[/]").strip().lower()
                if choice_str in ("exit", "quit", str(exit_choice)):
                    console.print("\n[blue]*[/] Goodbye!")
                    break

                if choice_str in ("clear", "cls"):
                    cls.show()
                    continue

                try:
                    choice = int(choice_str)
                except ValueError:
                    console.print("[red]Invalid selection[/red]")
                    continue

                if 1 <= choice <= len(all_services):
                    sorted_services = sorted(all_services, key=lambda s: s.category.value)
                    selected_service = sorted_services[choice - 1]
                    await cls._execute_service(selected_service)
                else:
                    console.print("[red]Choice out of range[/red]")

            except (KeyboardInterrupt, EOFError):
                console.print("\n[blue]*[/] Exiting SIGIT...")
                break

    @staticmethod
    async def _execute_service(service_cls: type[BaseService]) -> None:
        try:
            print_header(service_cls.name)
            params = prompt_schema(service_cls.input_schema)
            service_instance = service_cls()

            with console.status(f"[bold blue]Running {service_cls.name}...[/]"):
                result = await service_instance.execute(params)

            console.print("")
            render_result(result)
            ask_save_result(result, f"result_{service_cls.name.lower()}.json")

            Prompt.ask("\n[dim]Press Enter to return to menu...[/]")
            Menu.show()
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation aborted by user[/yellow]")
            Menu.show()
