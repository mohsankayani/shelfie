"""Turn a folder tree into an Obsidian vault you can explore as a graph.

The trick is small. Obsidian's graph view knows nothing about folders - it only
draws links between notes. So write one note per folder, have each note link
*up* to its parent and *down* to its children, and Obsidian renders your file
system as a navigable network. Install the community "3D Graph" plugin and the
same links become a three-dimensional map.

Nothing here touches your actual files. It reads names and sizes, and writes
markdown into a separate vault folder.
"""

import datetime
import os
from pathlib import Path
from typing import List, Tuple

SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv",
        "$RECYCLE.BIN", "System Volume Information", ".Trash", ".DS_Store"}

# hand-written notes the generator must never clobber
PROTECTED = {"HOW THIS VAULT WORKS", "README"}


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return "%.1f %s" % (n, unit)
        n /= 1024.0
    return "%.1f PB" % n


def safe(name: str) -> str:
    """Note names become filenames, so the reserved characters have to go."""
    out = name
    for ch in '\\/:*?"<>|#^[]':
        out = out.replace(ch, "-")
    return out.strip(" .") or "untitled"


def measure(path: Path) -> Tuple[int, int]:
    size = count = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            try:
                size += os.path.getsize(os.path.join(root, f))
                count += 1
            except OSError:
                pass
    return size, count


def build(roots: List[Tuple[str, str]], vault: str,
          depth: int = 3, max_files: int = 25) -> int:
    """roots: list of (label, path). Returns the number of notes written."""
    vault_p = Path(vault)
    vault_p.mkdir(parents=True, exist_ok=True)
    written = [0]

    def write(title: str, body: str) -> None:
        if title in PROTECTED:
            return
        (vault_p / (safe(title) + ".md")).write_text(body, encoding="utf-8")
        written[0] += 1

    def walk(label: str, real: Path, note: str, parent: str, left: int) -> None:
        try:
            entries = sorted(real.iterdir(), key=lambda x: x.name.lower())
        except OSError:
            return
        subdirs = [e for e in entries if e.is_dir() and e.name not in SKIP]
        files = [e for e in entries if e.is_file()]
        size, count = measure(real)

        lines = [
            "---",
            "location: %s" % str(real).replace("\\", "/"),
            "size: %s" % human(size),
            "files: %d" % count,
            "subfolders: %d" % len(subdirs),
            "tags: [shelfie, %s]" % label.lower().replace(" ", "-"),
            "---",
            "",
            "# %s" % note,
            "",
            "`%s`" % real,
            "",
            "**%s** across **%d** files in **%d** subfolders." % (human(size), count, len(subdirs)),
            "",
        ]
        if parent:
            lines += ["Up: [[%s]]" % safe(parent), ""]

        if subdirs and left > 0:
            lines.append("## Folders")
            for e in subdirs:
                child = "%s / %s" % (note, e.name)
                s, c = measure(e)
                lines.append("- [[%s|%s]] — %s, %d files" % (safe(child), e.name, human(s), c))
            lines.append("")

        if files:
            lines.append("## Files (%d)" % len(files))
            for e in files[:max_files]:
                try:
                    lines.append("- %s — %s" % (e.name, human(e.stat().st_size)))
                except OSError:
                    lines.append("- %s" % e.name)
            if len(files) > max_files:
                lines.append("- *… and %d more*" % (len(files) - max_files))
            lines.append("")

        write(note, "\n".join(lines))

        if left > 0:
            for e in subdirs:
                walk(label, e, "%s / %s" % (note, e.name), note, left - 1)

    hub = [
        "---", "tags: [shelfie, hub]", "---", "",
        "# Library Map", "",
        "Generated %s by [shelfie](https://github.com/mohsankayani/shelfie)."
        % datetime.datetime.now().strftime("%d %B %Y at %H:%M"), "",
        "Press **Ctrl+G** (**Cmd+G** on macOS) for the graph. For the 3D view:",
        "Settings → Community plugins → Browse → **3D Graph** → Install.", "",
        "## Roots", "",
    ]
    for label, root in roots:
        rp = Path(root)
        if not rp.is_dir():
            continue
        s, c = measure(rp)
        hub.append("- [[%s]] — `%s` — %s, %d files" % (safe(label), root, human(s), c))
        walk(label, rp, label, "Library Map", depth)

    hub += [
        "", "## Reading the graph", "",
        "Each dot is a folder; each line is a parent/child link. Dense clusters",
        "are folders with many subfolders. Every note carries its real path in",
        "the properties panel, so you can copy it straight into your file",
        "manager.", "",
        "> These notes are generated. Edits are overwritten on the next run —",
        "> keep your own writing in a different vault.",
    ]
    write("Library Map", "\n".join(hub))
    return written[0]
