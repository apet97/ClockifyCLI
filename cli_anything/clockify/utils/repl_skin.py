"""cli-anything REPL Skin — Clockify edition.

Adapted from the shared repl_skin.py pattern used across all CLI harnesses.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


# ── ANSI color codes ──────────────────────────────────────────────────

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"

_CYAN = "\033[38;5;80m"
_WHITE = "\033[97m"
_GRAY = "\033[38;5;245m"
_DARK_GRAY = "\033[38;5;240m"
_LIGHT_GRAY = "\033[38;5;250m"

# Clockify brand color — blue-green
_CLOCKIFY_ACCENT = "\033[38;5;43m"   # teal / Clockify green-blue

_GREEN = "\033[38;5;78m"
_YELLOW = "\033[38;5;220m"
_RED = "\033[38;5;196m"
_BLUE = "\033[38;5;75m"

_ICON = f"{_CYAN}{_BOLD}◆{_RESET}"
_ICON_SMALL = f"{_CYAN}▸{_RESET}"

_H_LINE = "─"
_V_LINE = "│"
_TL = "╭"
_TR = "╮"
_BL = "╰"
_BR = "╯"

HISTORY_FILE = Path.home() / ".local" / "share" / "clockify-cli" / "history"


def _strip_ansi(text: str) -> str:
    import re
    return re.sub(r"\033\[[^m]*m", "", text)


def _visible_len(text: str) -> int:
    return len(_strip_ansi(text))


def _detect_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if not hasattr(sys.stdout, "isatty"):
        return False
    return sys.stdout.isatty()


_COLOR = _detect_color()


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}" if _COLOR else text


def print_banner(workspace: str = "") -> None:
    inner = 54

    def box_line(content: str) -> str:
        pad = inner - _visible_len(content)
        vl = _c(_DARK_GRAY, _V_LINE)
        return f"{vl}{content}{' ' * max(0, pad)}{vl}"

    top = _c(_DARK_GRAY, f"{_TL}{_H_LINE * inner}{_TR}")
    bot = _c(_DARK_GRAY, f"{_BL}{_H_LINE * inner}{_BR}")

    icon = _c(_CYAN + _BOLD, "◆")
    brand = _c(_CYAN + _BOLD, "cli-anything")
    dot = _c(_DARK_GRAY, "·")
    name = _c(_CLOCKIFY_ACCENT + _BOLD, "Clockify")
    title = f" {icon}  {brand} {dot} {name}"
    ver = f" {_c(_DARK_GRAY, '   v0.1.0')}"
    tip = f" {_c(_DARK_GRAY, '   Type help for commands, quit to exit')}"
    ws_line = f" {_c(_DARK_GRAY, f'   Workspace: {workspace}')}" if workspace else ""

    print(top)
    print(box_line(title))
    print(box_line(ver))
    if ws_line:
        print(box_line(ws_line))
    print(box_line(""))
    print(box_line(tip))
    print(bot)
    print()


def print_goodbye() -> None:
    print(f"\n  {_ICON_SMALL} {_c(_GRAY, 'Goodbye!')}\n")


def success(msg: str) -> None:
    print(f"  {_c(_GREEN + _BOLD, '✓')} {_c(_GREEN, msg)}")


def error(msg: str) -> None:
    print(f"  {_c(_RED + _BOLD, '✗')} {_c(_RED, msg)}", file=sys.stderr)


def warning(msg: str) -> None:
    print(f"  {_c(_YELLOW + _BOLD, '⚠')} {_c(_YELLOW, msg)}")


def info(msg: str) -> None:
    print(f"  {_c(_BLUE, '●')} {_c(_LIGHT_GRAY, msg)}")


def get_prompt_style():
    try:
        from prompt_toolkit.styles import Style
    except ImportError:
        return None
    return Style.from_dict({
        "icon": "#5fdfdf bold",
        "software": "#2ab7a9 bold",
        "bracket": "#585858",
        "context": "#bcbcbc",
        "arrow": "#808080",
        "completion-menu.completion": "bg:#303030 #bcbcbc",
        "completion-menu.completion.current": "bg:#2ab7a9 #000000",
        "auto-suggest": "#585858",
        "bottom-toolbar": "bg:#1c1c1c #808080",
    })


def prompt_tokens(context: str = "") -> list:
    tokens = [("class:icon", "◆ "), ("class:software", "clockify")]
    if context:
        tokens += [
            ("class:bracket", " ["),
            ("class:context", context),
            ("class:bracket", "]"),
        ]
    tokens.append(("class:arrow", " ❯ "))
    return tokens


def create_prompt_session(completions: list[str] | None = None):
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        from prompt_toolkit.completion import WordCompleter

        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        kwargs: dict = {
            "history": FileHistory(str(HISTORY_FILE)),
            "auto_suggest": AutoSuggestFromHistory(),
            "style": get_prompt_style(),
            "enable_history_search": True,
        }
        if completions:
            kwargs["completer"] = WordCompleter(completions, ignore_case=True)

        return PromptSession(**kwargs)
    except ImportError:
        return None


def get_input(pt_session, context: str = "") -> str:
    if pt_session is not None:
        from prompt_toolkit.formatted_text import FormattedText
        tokens = prompt_tokens(context)
        return pt_session.prompt(FormattedText(tokens)).strip()
    raw = "clockify"
    if context:
        raw += f" [{context}]"
    raw += " ❯ "
    return input(raw).strip()


REPL_COMPLETIONS = [
    # groups
    "timer", "entries", "projects", "clients", "tags", "tasks",
    "workspaces", "users", "reports",
    "webhooks", "approval", "groups", "expenses", "holidays",
    "invoices", "time-off", "custom-fields", "shared-reports", "entities",
    "scheduling",
    # timer
    "timer start", "timer stop", "timer status", "timer restart",
    # entries
    "entries list", "entries get", "entries add", "entries update",
    "entries delete", "entries today",
    "entries bulk-delete", "entries duplicate", "entries mark-invoiced",
    # projects
    "projects list", "projects get", "projects create",
    "projects update", "projects delete",
    "projects estimate", "projects members",
    # clients
    "clients list", "clients create", "clients update", "clients delete",
    # tags
    "tags list", "tags create", "tags update", "tags delete",
    # tasks
    "tasks list", "tasks create", "tasks update", "tasks delete",
    "tasks cost-rate", "tasks hourly-rate",
    # workspaces
    "workspaces list", "workspaces use", "workspaces create", "workspaces invite",
    # users
    "users list", "users me", "users profile", "users update-status", "users managers",
    # reports
    "reports detailed", "reports summary", "reports weekly",
    "reports attendance", "reports expense",
    # webhooks
    "webhooks list", "webhooks get", "webhooks create",
    "webhooks update", "webhooks delete", "webhooks logs",
    # approval
    "approval list", "approval submit", "approval update",
    # groups
    "groups list", "groups create", "groups update", "groups delete",
    "groups add-user", "groups remove-user",
    # expenses
    "expenses list", "expenses get", "expenses create", "expenses delete",
    "expenses categories list", "expenses categories create", "expenses categories delete",
    # holidays
    "holidays list", "holidays in-period", "holidays create", "holidays delete",
    # invoices
    "invoices list", "invoices get", "invoices delete", "invoices status",
    "invoices duplicate",
    "invoices payments list", "invoices payments add", "invoices payments delete",
    # time-off
    "time-off policies list", "time-off policies get", "time-off policies delete",
    "time-off request create",
    "time-off balance get",
    # custom-fields
    "custom-fields list", "custom-fields create", "custom-fields delete",
    "custom-fields project list", "custom-fields project delete",
    # shared-reports
    "shared-reports list", "shared-reports create", "shared-reports delete",
    # entities
    "entities created", "entities deleted", "entities updated",
    # scheduling
    "scheduling assignments list", "scheduling assignments create-recurring",
    "scheduling assignments update-recurring", "scheduling assignments delete-recurring",
    "scheduling assignments update-series", "scheduling assignments copy",
    "scheduling assignments publish", "scheduling assignments project-totals",
    "scheduling assignments user-capacity",
    # meta
    "help", "quit", "exit",
]
