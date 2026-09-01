"""The move engine.

Two rules it never breaks:

* **Nothing is deleted.** Ever. Files are moved; on a name collision the
  incoming file is renamed rather than overwriting anything.
* **Dry run is the default.** ``plan()`` decides, ``apply()`` acts, and the CLI
  always shows the plan first.

The age threshold matters more than it looks. Without it, automatic sorting is
actively hostile - you download an installer, alt-tab, and it has vanished. With
a few days' delay only genuine backlog moves, and the tool stays trustworthy.
"""

import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from . import rules, strategies


@dataclass
class Move:
    src: Path
    dest_dir: Path
    category: str
    size: int
    is_dir: bool

    @property
    def dest(self) -> Path:
        return self.dest_dir / self.src.name


@dataclass
class Skip:
    src: Path
    reason: str


def _size_of(p: Path) -> int:
    if p.is_file():
        try:
            return p.stat().st_size
        except OSError:
            return 0
    total = 0
    for root, _, files in os.walk(p):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def _age_days(p: Path) -> float:
    try:
        return (time.time() - p.stat().st_mtime) / 86400.0
    except OSError:
        return 0.0


def plan(inbox: str, library: str, strategy_key: str,
         projects: List[str], min_age_days: float = 0
         ) -> Tuple[List[Move], List[Skip]]:
    """Work out what would move. Touches nothing."""
    moves: List[Move] = []
    skips: List[Skip] = []
    inbox_p = Path(inbox)
    lib = Path(library)
    strat = strategies.get(strategy_key)

    if not inbox_p.is_dir():
        return moves, [Skip(inbox_p, "folder does not exist")]

    # never sort a folder into itself
    try:
        if lib.resolve() in inbox_p.resolve().parents or lib.resolve() == inbox_p.resolve():
            return moves, [Skip(inbox_p, "inbox is inside the library")]
    except OSError:
        pass

    for entry in sorted(inbox_p.iterdir(), key=lambda x: x.name.lower()):
        category = rules.categorise(entry.name, entry.is_dir(), projects)
        if category is None:
            skips.append(Skip(entry, "no confident match - left alone"))
            continue
        if min_age_days:
            age = _age_days(entry)
            if age < min_age_days:
                skips.append(Skip(entry, "only %.1f days old" % age))
                continue
        parts = strat.layout(category, str(entry)) if strat.layout else category.split("/")
        moves.append(Move(src=entry, dest_dir=lib.joinpath(*parts),
                          category="/".join(parts), size=_size_of(entry),
                          is_dir=entry.is_dir()))
    return moves, skips


def unique_destination(dest: Path) -> Path:
    """Never overwrite. Add ' (2)', ' (3)' ... until the name is free."""
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    i = 2
    while True:
        candidate = dest.with_name("%s (%d)%s" % (stem, i, suffix))
        if not candidate.exists():
            return candidate
        i += 1


def apply(moves: List[Move], on_progress=None) -> Tuple[int, List[Tuple[Move, str]]]:
    """Perform the moves. Returns (moved_count, failures)."""
    done = 0
    failures: List[Tuple[Move, str]] = []
    for m in moves:
        try:
            m.dest_dir.mkdir(parents=True, exist_ok=True)
            target = unique_destination(m.dest)
            shutil.move(str(m.src), str(target))
            done += 1
            if on_progress:
                on_progress(m, target)
        except Exception as exc:                      # noqa: BLE001
            # A cross-device move is copy-then-delete. If the copy landed but the
            # delete failed - common on Windows when something holds a handle -
            # the data is safe at the destination and only the source husk is
            # left. Report it as such rather than as a loss.
            if m.dest.exists() or unique_destination(m.dest) != m.dest:
                failures.append((m, "copied, but the original could not be removed: %s"
                                 % str(exc)[:80]))
            else:
                failures.append((m, str(exc)[:100]))
    return done, failures
