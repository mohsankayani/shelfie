"""Terminal styling. Green and violet, and it degrades gracefully.

Colour is switched off automatically when output is piped, when NO_COLOR is set,
or on a terminal that cannot handle it - so the tool stays usable in a log file
or a CI run.
"""

import os
import sys

_FORCE = os.environ.get("SHELFIE_COLOR")
_NO = os.environ.get("NO_COLOR") is not None


def _supported() -> bool:
    if _FORCE:
        return _FORCE not in ("0", "no", "false")
    if _NO or not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        # modern Windows terminals handle ANSI; enable it explicitly for conhost
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
            return True
        except Exception:                                     # noqa: BLE001
            return os.environ.get("WT_SESSION") is not None
    return True


ON = _supported()


def _c(code: str) -> str:
    return code if ON else ""


GREEN   = _c("\033[38;5;41m")
GREEN_D = _c("\033[38;5;29m")
VIOLET  = _c("\033[38;5;141m")
VIOLET_D = _c("\033[38;5;97m")
GREY    = _c("\033[38;5;245m")
WHITE   = _c("\033[97m")
YELLOW  = _c("\033[38;5;179m")
RED     = _c("\033[38;5;167m")
BOLD    = _c("\033[1m")
DIM     = _c("\033[2m")
OFF     = _c("\033[0m")


def banner() -> str:
    g, v, o, d = GREEN, VIOLET, OFF, DIM
    return "\n".join([
        "",
        "  %s███████%s╗%s██%s╗  %s██%s╗%s███████%s╗%s██%s╗     %s███████%s╗%s██%s╗%s███████%s╗" % (
            g, o, g, o, g, o, g, o, g, o, g, o, g, o, g, o),
        "  %s██%s╔════╝%s██%s║  %s██%s║%s██%s╔════╝%s██%s║     %s██%s╔════╝%s██%s║%s██%s╔════╝" % (
            g, o, g, o, g, o, g, o, g, o, g, o, g, o, g, o),
        "  %s███████%s╗%s███████%s║%s█████%s╗  %s██%s║     %s█████%s╗  %s██%s║%s█████%s╗" % (
            v, o, v, o, v, o, v, o, v, o, v, o, v, o),
        "  %s╚════██%s║%s██%s╔══%s██%s║%s██%s╔══╝  %s██%s║     %s██%s╔══╝  %s██%s║%s██%s╔══╝" % (
            v, o, v, o, v, o, v, o, v, o, v, o, v, o, v, o),
        "  %s███████%s║%s██%s║  %s██%s║%s███████%s╗%s███████%s╗%s██%s║     %s██%s║%s███████%s╗" % (
            v, o, v, o, v, o, v, o, v, o, v, o, v, o, v, o),
        "  %s╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝╚══════╝%s" % (d, o),
        "",
        "  %sShelve your Downloads folder. One command.%s" % (GREY, o),
        "",
    ])


def head(text: str) -> None:
    print("\n%s%s%s%s" % (BOLD, VIOLET, text, OFF))
    print("%s%s%s" % (DIM, "─" * min(len(text), 62), OFF))


def ok(text: str) -> None:
    print("  %s✓%s %s" % (GREEN, OFF, text))


def info(text: str) -> None:
    print("  %s·%s %s" % (GREY, OFF, text))


def warn(text: str) -> None:
    print("  %s!%s %s" % (YELLOW, OFF, text))


def err(text: str) -> None:
    print("  %s✗%s %s" % (RED, OFF, text))


def arrow(left: str, right: str, width: int = 46) -> None:
    print("  %s%-*s%s %s→%s %s%s%s" % (WHITE, width, left[:width], OFF,
                                       VIOLET, OFF, GREEN, right, OFF))


def ask(prompt: str, default: str = "") -> str:
    suffix = " %s[%s]%s" % (DIM, default, OFF) if default else ""
    try:
        val = input("  %s?%s %s%s: " % (VIOLET, OFF, prompt, suffix)).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(1)
    return val or default


def confirm(prompt: str, default: bool = False) -> bool:
    d = "Y/n" if default else "y/N"
    val = ask("%s (%s)" % (prompt, d)).lower()
    if not val:
        return default
    return val.startswith("y")


def choose(prompt: str, options, default: int = 1) -> int:
    """options: list of (title, subtitle). Returns a 1-based index."""
    print()
    for i, (title, sub) in enumerate(options, 1):
        mark = "%s●%s" % (GREEN, OFF) if i == default else "%s○%s" % (DIM, OFF)
        print("   %s %s%d%s  %s%s%s" % (mark, VIOLET, i, OFF, BOLD, title, OFF))
        if sub:
            for line in sub.split("\n"):
                print("        %s%s%s" % (GREY, line, OFF))
    print()
    while True:
        raw = ask(prompt, str(default))
        try:
            n = int(raw)
            if 1 <= n <= len(options):
                return n
        except ValueError:
            pass
        warn("Enter a number between 1 and %d." % len(options))


def size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return "%.1f %s" % (n, unit)
        n /= 1024.0
    return "%.1f PB" % n
