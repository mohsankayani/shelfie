<div align="center">

<img src="assets/banner.svg" alt="shelfie" width="640">

### Shelve your Downloads folder. One command.

A file organiser that asks how you *work* before it moves anything —
then shows you the plan, waits for a yes, and never deletes.

[![License: MIT](https://img.shields.io/badge/License-MIT-9d6bf5.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-2ecc71.svg?style=flat-square)](https://python.org)
[![Windows | macOS | Linux](https://img.shields.io/badge/Windows%20%7C%20macOS%20%7C%20Linux-9d6bf5.svg?style=flat-square)](#install)
[![Zero dependencies](https://img.shields.io/badge/dependencies-none-2ecc71.svg?style=flat-square)](pyproject.toml)

</div>

---

```console
$ shelfie sort

  · library  C:\Library
  · strategy PARA (by how you use it)
  · projects acme-corp, blue-lagoon, northwind

Plan — 14 items, 2.4 GB
──────────────────────────────────────────────
  acme-corp-logo.png            → Projects/acme-corp
  invoice-2026.pdf              → Areas/Finances
  id_rsa                        → Areas/Credentials
  holiday.jpg                   → Resources/Media/Images
  ubuntu-24.04.iso              → Resources/Software/Disk Images
  site-20260101.wpress          → Archive/Site Backups
  random.zip                    → Inbox/Archives

  Left alone (1):
    some-project-folder          no confident match - left alone

  ? Move these now? (y/N)
```

## Why another file organiser

Most of them sort by file extension into `Images`, `Documents`, `Videos`. That is
easy to automate and it is why they get abandoned: it **splits things that belong
together**. The contract, the photos and the site backup from one job end up in
three different branches, and you stop trusting the folder you can no longer
find anything in.

shelfie starts somewhere else — **how you use a thing, not what type it is.**

- **It learns your projects.** Make a folder under `Projects/` for a client and
  anything mentioning them routes there, whatever the file type. That one rule
  is most of the value.
- **It refuses to guess.** No confident match means it stays put and says so. Ten
  things in an inbox beats ten things filed wrongly, because wrong filing is
  invisible until you go looking.
- **It waits.** Files newer than your threshold are left alone, so nothing
  vanishes while you are still using it.
- **It never deletes.** Only moves, and never over an existing file.
- **`shelfie undo`** puts the last sort back.

## Install

```bash
pip install shelfie-cli
```

The command is still `shelfie` — the package is `shelfie-cli` on PyPI because
the shorter name was already taken by an unrelated project.

<details>
<summary>From source</summary>

```bash
git clone https://github.com/mohsankayani/shelfie
cd shelfie
pip install -e .
```
</details>

No dependencies beyond the Python standard library — nothing to break later.

## Use

```bash
shelfie              # status, or the setup wizard on first run
shelfie init         # re-run the wizard
shelfie sort         # preview → confirm → file
shelfie sort -n      # preview only, never moves
shelfie sort -y      # no confirmation (for schedulers)
shelfie undo         # put the last sort back
shelfie where        # your library at a glance
shelfie map          # build an Obsidian graph of it
```

### `shelfie where`

```console
  Projects           ████████████████████··   81.2 GB    258095 files
  Archive            ██████████············   54.3 GB        24 files
  Media              ██████················   36.5 GB       201 files
  Software           ████··················   26.1 GB      1357 files
  Learning           █·····················    4.7 GB        29 files
```

## Pick how you think

The wizard explains each one and shows an example. There is no correct answer —
only the one that matches how you look for things.

| Strategy | Shape | Good for | Watch out |
|---|---|---|---|
| **PARA** | `Projects/` `Areas/` `Resources/` `Archive/` | Work that arrives as jobs. Everything for a client together. | Needs a decision: is this still active? |
| **By type** | `Media/Video/` `Documents/PDF/` | Emptying a downloads folder. Zero decisions. | Splits things that belong together. |
| **Type, then year** | `Media/Images/2026/` | The pragmatic middle. Browsable, and folders stay small. | One more level to click through. |
| **By date** | `2026/03 March/` | Photos, screenshots, scans — things you place in time. | Hopeless for finding by subject. |
| **Flat** | `Media/` `Documents/` | People who genuinely search instead of browsing. | Folders get very large. |

PARA is [Tiago Forte's](https://fortelabs.com/blog/para/) idea; the numbered
variant is [Johnny.Decimal](https://johnnydecimal.com/). shelfie did not invent
either — it just applies one consistently so you do not have to.

## See it as a graph

```bash
shelfie map
```

Writes an [Obsidian](https://obsidian.md) vault: one note per folder, each
linking to its parent and children. Obsidian's graph view then draws your file
system as a network. Install the community **3D Graph** plugin and it becomes
three-dimensional.

The mechanism is deliberately unmagical — Obsidian's graph is built from
`[[links]]` between notes, so writing one note per folder with links to its
children *is* the whole implementation. [How it works →](docs/obsidian.md)

## Safety

Worth being specific, because this category of tool has a bad reputation:

| | |
|---|---|
| **Never deletes** | Only `shutil.move`. No delete path exists in the code. |
| **Never overwrites** | Collisions become `name (2).ext`. |
| **Dry run by default** | `sort` shows a plan and waits. `-n` never moves at all. |
| **Reversible** | `shelfie undo` reads a log of the last sort and puts it back. |
| **Leaves the ambiguous alone** | Unmatched folders stay where they are. |
| **Age threshold** | Files newer than *N* days are not touched. |

Cross-device moves are copy-then-delete. If the copy lands but the delete fails
— common on Windows when something holds a handle — shelfie reports that
precisely rather than as a loss, because your data is safe at the destination.

## Docs

- [The idea behind the shelves](docs/concepts.md)
- [Organising strategies compared](docs/strategies.md)
- [The Obsidian vault](docs/obsidian.md)
- [Writing your own rules](docs/rules.md)

## Contributing

Genuinely welcome, especially:

- **Routing rules for file types I have missed.** `shelfie/rules.py` is a plain
  list — add a pattern, open a PR.
- **macOS and Linux testing.** Written cross-platform and exercised on Windows;
  real use on the others will find things.
- **Localised category names.**

Open an issue first for anything large, so nobody wastes an evening.

## Licence

MIT. Do what you like with it.
