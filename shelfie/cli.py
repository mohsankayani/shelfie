"""shelfie — command line interface.

    shelfie              first run: setup wizard. after that: show status
    shelfie init         re-run the setup wizard
    shelfie sort         preview, confirm, then file everything
    shelfie sort --yes   skip the confirmation (for scripts and schedulers)
    shelfie map          build the Obsidian vault
    shelfie where        print your library layout
    shelfie undo         move the last sort back
"""

import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__, config, sorter, strategies, ui, vault

UNDO_LOG = config.config_dir() / "last-sort.json"


# ---------------------------------------------------------------- wizard ----

def wizard() -> int:
    print(ui.banner())
    ui.head("Setup")
    print("  A few questions, then shelfie remembers your answers.")
    print("  %sNothing is moved during setup.%s" % (ui.DIM, ui.OFF))

    cfg = config.load()

    # 1. inboxes -----------------------------------------------------------
    ui.head("1. Which folders get messy?")
    print("  These are your %sinboxes%s — things pass through, nothing lives there." % (ui.BOLD, ui.OFF))
    found = config.default_inboxes()
    for p in found:
        ui.info(p)
    inboxes = []
    if found and ui.confirm("Use these?", True):
        inboxes = found
    while True:
        extra = ui.ask("Add another folder (blank to finish)")
        if not extra:
            break
        p = Path(os.path.expanduser(extra))
        if p.is_dir():
            inboxes.append(str(p))
            ui.ok("added %s" % p)
        else:
            ui.err("not a folder: %s" % p)
    if not inboxes:
        ui.err("No inbox chosen — nothing to sort.")
        return 1
    cfg["inboxes"] = inboxes

    # 2. library -----------------------------------------------------------
    ui.head("2. Where should the sorted files go?")
    print("  One place for everything worth keeping. It will be created if needed.")
    lib = ui.ask("Library folder", cfg.get("library") or config.default_library())
    cfg["library"] = str(Path(os.path.expanduser(lib)))

    # 3. strategy ----------------------------------------------------------
    ui.head("3. How should it be organised?")
    print("  There is no single right answer — pick what matches how you think.")
    opts = []
    for key in strategies.ORDER:
        s = strategies.STRATEGIES[key]
        sub = "%s\n%sGood for: %s\n%sWatch out: %s" % (
            "  ".join(s.example[:3]), "", s.best_for.split(".")[0] + ".",
            "", s.weakness.split(".")[0] + ".")
        opts.append((("%s — %s" % (s.name, s.tagline)), sub))
    pick = ui.choose("Choose", opts, default=2)
    cfg["strategy"] = strategies.ORDER[pick - 1]

    # 4. age guard ---------------------------------------------------------
    ui.head("4. How long before a file is 'settled'?")
    print("  A file you downloaded an hour ago should not vanish while you use it.")
    print("  %sshelfie leaves anything newer than this alone.%s" % (ui.DIM, ui.OFF))
    raw = ui.ask("Days to wait (0 = sort everything)", str(cfg.get("min_age_days", 0)))
    try:
        cfg["min_age_days"] = max(0, int(raw))
    except ValueError:
        cfg["min_age_days"] = 0

    # 5. vault -------------------------------------------------------------
    ui.head("5. Visual map? (optional)")
    print("  shelfie can generate an Obsidian vault so you can see your whole")
    print("  library as a graph. Needs Obsidian to view — free, obsidian.md.")
    cfg["make_vault"] = ui.confirm("Generate it?", False)
    if cfg["make_vault"]:
        default_vault = str(Path(cfg["library"]).parent / "Library-Map")
        cfg["vault_path"] = ui.ask("Vault folder", cfg.get("vault_path") or default_vault)

    path = config.save(cfg)
    ui.head("Saved")
    ui.ok("settings: %s" % path)
    ui.ok("library : %s" % cfg["library"])
    ui.ok("strategy: %s" % strategies.get(cfg["strategy"]).name)
    print("\n  Next: %sshelfie sort%s — it previews before touching anything.\n"
          % (ui.GREEN + ui.BOLD, ui.OFF))
    return 0


# ------------------------------------------------------------------ sort ----

def cmd_sort(args) -> int:
    cfg = config.load()
    if not config.exists():
        ui.warn("No settings yet — running setup first.")
        if wizard() != 0:
            return 1
        cfg = config.load()

    lib = cfg["library"]
    projects = config.projects(lib) if cfg.get("keep_project_names", True) else []
    strat = strategies.get(cfg["strategy"])
    min_age = 0 if args.all else cfg.get("min_age_days", 0)

    print(ui.banner())
    ui.info("library  %s" % lib)
    ui.info("strategy %s" % strat.name)
    if projects:
        ui.info("projects %s" % ", ".join(projects[:6]) + (" …" if len(projects) > 6 else ""))
    if min_age:
        ui.info("leaving anything newer than %d day(s)" % min_age)

    all_moves, all_skips = [], []
    for inbox in cfg["inboxes"]:
        m, s = sorter.plan(inbox, lib, cfg["strategy"], projects, min_age)
        all_moves += m
        all_skips += s

    if not all_moves:
        ui.head("Nothing to do")
        ui.ok("Your inboxes are already clear.")
        if all_skips:
            print("\n  %s%d item(s) left alone:%s" % (ui.DIM, len(all_skips), ui.OFF))
            for s in all_skips[:10]:
                print("    %s%-44s %s%s" % (ui.GREY, s.src.name[:44], s.reason, ui.OFF))
        return 0

    ui.head("Plan — %d item(s), %s" % (len(all_moves), ui.size(sum(m.size for m in all_moves))))
    for m in all_moves[:60]:
        ui.arrow(m.src.name, m.category)
    if len(all_moves) > 60:
        print("  %s… and %d more%s" % (ui.DIM, len(all_moves) - 60, ui.OFF))

    if all_skips:
        print("\n  %sLeft alone (%d):%s" % (ui.DIM, len(all_skips), ui.OFF))
        for s in all_skips[:8]:
            print("    %s%-44s %s%s" % (ui.GREY, s.src.name[:44], s.reason, ui.OFF))

    if args.dry_run:
        print("\n  %sDry run — nothing moved.%s\n" % (ui.YELLOW, ui.OFF))
        return 0
    if not args.yes:
        print()
        if not ui.confirm("Move these now?", False):
            ui.info("Cancelled. Nothing moved.")
            return 0

    ui.head("Moving")
    record = []

    def progress(m, target):
        record.append({"from": str(m.src), "to": str(target)})

    done, failures = sorter.apply(all_moves, progress)
    ui.ok("%d moved" % done)
    for m, why in failures:
        ui.err("%s — %s" % (m.src.name[:40], why))

    if record:
        UNDO_LOG.parent.mkdir(parents=True, exist_ok=True)
        UNDO_LOG.write_text(json.dumps(record, indent=1), encoding="utf-8")
        print("\n  %sUndo available: shelfie undo%s" % (ui.DIM, ui.OFF))

    if cfg.get("make_vault") and cfg.get("vault_path"):
        ui.head("Rebuilding the map")
        n = vault.build([("Library", lib)], cfg["vault_path"])
        ui.ok("%d notes → %s" % (n, cfg["vault_path"]))
    print()
    return 0


# ------------------------------------------------------------------ undo ----

def cmd_undo(args) -> int:
    if not UNDO_LOG.exists():
        ui.warn("Nothing to undo.")
        return 0
    record = json.loads(UNDO_LOG.read_text(encoding="utf-8"))
    ui.head("Undo — %d item(s) from the last sort" % len(record))
    for r in record[:40]:
        ui.arrow(Path(r["to"]).name, str(Path(r["from"]).parent))
    if len(record) > 40:
        print("  %s… and %d more%s" % (ui.DIM, len(record) - 40, ui.OFF))
    if not args.yes and not ui.confirm("Move them back?", False):
        ui.info("Cancelled.")
        return 0
    import shutil
    back = 0
    for r in record:
        src, dst = Path(r["to"]), Path(r["from"])
        if not src.exists():
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(sorter.unique_destination(dst)))
            back += 1
        except Exception as exc:                              # noqa: BLE001
            ui.err("%s — %s" % (src.name[:40], str(exc)[:60]))
    ui.ok("%d moved back" % back)
    UNDO_LOG.unlink(missing_ok=True)
    return 0


# ------------------------------------------------------------------- map ----

def cmd_map(args) -> int:
    cfg = config.load()
    lib = cfg["library"]
    dest = args.out or cfg.get("vault_path") or str(Path(lib).parent / "Library-Map")
    if not Path(lib).is_dir():
        ui.err("Library not found: %s" % lib)
        return 1
    print(ui.banner())
    ui.head("Building the vault")
    ui.info("reading %s" % lib)
    n = vault.build([("Library", lib)], dest, depth=args.depth)
    ui.ok("%d notes written to %s" % (n, dest))
    print("\n  Open Obsidian → %sOpen folder as vault%s → %s" % (ui.BOLD, ui.OFF, dest))
    print("  Press %sCtrl+G%s (%sCmd+G%s on macOS) for the graph." % (ui.BOLD, ui.OFF, ui.BOLD, ui.OFF))
    print("  3D: Settings → Community plugins → Browse → %s3D Graph%s\n" % (ui.BOLD, ui.OFF))
    return 0


# ----------------------------------------------------------------- where ----

def cmd_where(args) -> int:
    cfg = config.load()
    lib = Path(cfg["library"])
    print(ui.banner())
    if not lib.is_dir():
        ui.warn("No library yet at %s — run 'shelfie init'." % lib)
        return 0
    ui.head(str(lib))
    rows = []
    for shelf in sorted(lib.iterdir(), key=lambda x: x.name.lower()):
        if not shelf.is_dir():
            continue
        size, count = vault.measure(shelf)
        rows.append((shelf.name, size, count))
    if not rows:
        ui.info("empty")
        return 0
    biggest = max(r[1] for r in rows) or 1
    for name, size, count in sorted(rows, key=lambda r: -r[1]):
        bar_len = int(22 * size / biggest)
        bar = "%s%s%s%s" % (ui.GREEN, "█" * bar_len, ui.DIM + "·" * (22 - bar_len), ui.OFF)
        print("  %s%-18s%s %s  %10s  %s%7d files%s" % (
            ui.WHITE, name[:18], ui.OFF, bar, ui.size(size), ui.GREY, count, ui.OFF))
    total = sum(r[1] for r in rows)
    print("\n  %s%s across %d shelves%s\n" % (ui.BOLD, ui.size(total), len(rows), ui.OFF))
    return 0


# ---------------------------------------------------------------- status ----

def status() -> int:
    print(ui.banner())
    if not config.exists():
        print("  %sFirst time here?%s Run %sshelfie init%s to set up.\n"
              % (ui.BOLD, ui.OFF, ui.GREEN + ui.BOLD, ui.OFF))
        return 0
    cfg = config.load()
    ui.head("Current setup")
    ui.info("library  %s" % cfg["library"])
    ui.info("strategy %s" % strategies.get(cfg["strategy"]).name)
    for i in cfg["inboxes"]:
        pending = 0
        p = Path(i)
        if p.is_dir():
            pending = sum(1 for _ in p.iterdir())
        ui.info("inbox    %-42s %s%d item(s)%s" % (i, ui.GREEN if pending else ui.GREY, pending, ui.OFF))
    print("\n  %sshelfie sort%s   preview and file everything" % (ui.GREEN + ui.BOLD, ui.OFF))
    print("  %sshelfie where%s  see your library at a glance" % (ui.GREEN + ui.BOLD, ui.OFF))
    print("  %sshelfie map%s    build the Obsidian graph\n" % (ui.GREEN + ui.BOLD, ui.OFF))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="shelfie", add_help=True,
                                description="Shelve your Downloads folder. One command.")
    p.add_argument("--version", action="version", version="shelfie %s" % __version__)
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("init", help="run the setup wizard")

    s = sub.add_parser("sort", help="file everything from your inboxes")
    s.add_argument("--yes", "-y", action="store_true", help="skip the confirmation")
    s.add_argument("--dry-run", "-n", action="store_true", help="show the plan and stop")
    s.add_argument("--all", action="store_true", help="ignore the age threshold")

    m = sub.add_parser("map", help="build the Obsidian vault")
    m.add_argument("--out", help="vault folder")
    m.add_argument("--depth", type=int, default=3, help="folder levels to map")

    sub.add_parser("where", help="show the library layout")

    u = sub.add_parser("undo", help="reverse the last sort")
    u.add_argument("--yes", "-y", action="store_true")

    args = p.parse_args(argv)
    try:
        if args.cmd == "init":
            return wizard()
        if args.cmd == "sort":
            return cmd_sort(args)
        if args.cmd == "map":
            return cmd_map(args)
        if args.cmd == "where":
            return cmd_where(args)
        if args.cmd == "undo":
            return cmd_undo(args)
        return status()
    except KeyboardInterrupt:
        print("\n  cancelled\n")
        return 130


if __name__ == "__main__":
    sys.exit(main())
