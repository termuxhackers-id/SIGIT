import os

from pathlib import Path
from ..core.colors import Colors
from ..core.config import config

c = Colors()

# Logo
LOGO = f"""{c.BLUE}
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
                       {c.RESET}[ S.I.G.I.T ]{c.BLUE}
           {c.DIM}Simple Information Gathering Toolkit{c.RESET}
               {c.DIM}Author by {c.RESET}{c.RED}@Termuxhackers.id{c.RESET}"""


def clear():
    os.system('clear' if os.name == 'posix' else 'cls')


def separator():
    print(f"{c.RESET}{config.SPACE}" + "-" * 44)


def print_user_result(result: dict):
    print(f"  {config.SPACE}{c.BLUE}[{result['color']}{result['status']}{c.BLUE}] "
          f"{c.RESET}{result['url']}")


def save_results(data: list | dict, filename: str):
    Path(filename).write_text("\n".join(map(str, data)) if isinstance(data, list) else str(data))
    print(f"{config.SPACE}{c.BLUE}> {c.RESET}Results saved to: {c.YELLOW}{filename}{c.RESET}")


def print_header(title: str):
    separator()
    print(f"{config.SPACE}{c.BG_BLUE} {title} {c.RESET}")
    separator()


def print_found(count: int, item: str = "results"):
    print(f"{config.SPACE}{c.BLUE}> {c.RESET}Found {c.YELLOW}{count}{c.RESET} {item}")


def input_prompt(prompt: str) -> str:
    return input(f"{config.SPACE}{c.BLUE}> {c.RESET}{prompt}{c.BLUE} ").strip()