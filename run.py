import asyncio

from sigit.cli.menu import Menu

if __name__ == "__main__":
    try:
        Menu.show()
        asyncio.run(Menu.run())
    except KeyboardInterrupt:
        print("\nExiting...")