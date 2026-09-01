# Writing your own rules

Routing lives in [`shelfie/rules.py`](../shelfie/rules.py). It is plain data —
two lists and a dictionary — so changing it needs no understanding of the rest.

## The order, and why it is that order

1. **Project name** — beats everything. If the filename mentions a folder under
   `Projects/`, it goes there regardless of type.
2. **Filename pattern** — beats extension, because extensions lie. A `.zip` can
   be a plugin, a template, a site backup or a photo dump; the name usually says.
3. **Extension** — the fallback.
4. **Give up honestly** — unmatched files go to `Inbox/`, unmatched *folders*
   stay put.

## Adding a file type

```python
BY_EXT = {
    "Media/Video": ".mp4 .mkv .avi .mov",
    "3D Models":   ".blend .fbx .obj .stl",   # <- new shelf
}
```

The key is the destination path; subfolders use `/` on every platform and are
translated automatically.

## Adding a name pattern

Patterns are regular expressions, checked in order, first match wins:

```python
BY_NAME = [
    (r"\.wpress$|wpwp\.\d+_",        "Archive/Site Backups"),
    (r"invoice|receipt|statement",   "Documents/Financial"),
    (r"^DSC_|^IMG_\d{4}",            "Media/Photos"),      # camera output
    (r"\bproposal\b|\bquote\b",      "Documents/Proposals"),
]
```

Put specific patterns above general ones. `invoice-acme.zip` should reach the
invoice rule before the generic archive fallback.

## Never-touch lists

```python
INCOMPLETE  = {".crdownload", ".part", ".tmp"}   # downloads in flight
IGNORE_EXT  = {".lnk", ".url", ".webloc"}        # shortcuts, not content
IGNORE_NAMES = {"desktop.ini", ".ds_store"}      # OS bookkeeping
```

Shortcuts are ignored on purpose: moving a `.lnk` breaks it, and a desktop full
of shortcuts is usually deliberate.

## Testing a change

Always dry run:

```bash
shelfie sort -n
```

That prints the full plan and moves nothing. If a file lands somewhere odd, the
category shown tells you which rule caught it.

## Contributing rules back

Rules for file types other people share are the most useful contribution to this
project. Open a PR against `rules.py` with:

- the pattern or extension,
- one line on what produces those files,
- an example filename.
