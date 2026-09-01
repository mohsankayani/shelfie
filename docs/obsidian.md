# Seeing your files as a graph

```bash
shelfie map
```

This writes an [Obsidian](https://obsidian.md) vault — a folder of Markdown
files — that mirrors your library. Open it in Obsidian, press **Ctrl+G**
(**Cmd+G** on macOS), and your file system appears as a network you can pan,
zoom and click through.

<div align="center">
  <em>Each dot is a folder. Each line is a parent/child link.</em>
</div>

## The mechanism, which is deliberately unmagical

Obsidian is not a database. **A vault is just a folder full of `.md` text
files.** You could open every one in Notepad, and if you uninstalled Obsidian
tomorrow they would still be readable.

More importantly: **Obsidian's graph has nothing to do with folders.** It knows
exactly one thing — links between notes. You write a link like this:

```markdown
[[Library - Media - Audio]]
```

Every time Obsidian sees that, it draws a line between two dots. That is the
entire mechanism.

So to make the graph show a folder structure, you write **one note per folder**,
and have each note link *up* to its parent and *down* to its children. Obsidian
does the rest.

A generated note looks like this:

```markdown
---
location: C:/Library/Media
size: 24.1 GB
files: 342
subfolders: 5
---

# Library / Media

`C:\Library\Media`

**24.1 GB** across **342** files in **5** subfolders.

Up: [[Library]]

## Folders
- [[Library - Media - Audio|Audio]] — 770.2 MB, 12 files
- [[Library - Media - Books|Books]] — 10.5 GB, 175 files
- [[Library - Media - Video|Video]] — 12.7 GB, 63 files
```

Three parts:

1. **Frontmatter** (between the `---` lines) — metadata Obsidian shows in a
   Properties panel. The real path lives here so you can copy it into your file
   manager.
2. **The body** — ordinary Markdown.
3. **The links** — the only part the graph actually uses.

## Build one by hand in thirty seconds

If you want to prove there is nothing else going on:

1. Make an empty folder anywhere.
2. Obsidian → **Open folder as vault** → pick it.
3. Create a note called `Home`. Type `[[Photos]]` and `[[Work]]`.
4. Obsidian offers to create those notes — accept.
5. Press **Ctrl+G**.

Three dots, two lines. shelfie does the same thing, with a few hundred notes.

## The 3D view

The built-in graph is two-dimensional. For 3D:

**Settings → Community plugins → turn off Restricted Mode → Browse →
search "3D Graph" → Install → Enable.**

A new icon appears in the sidebar. It reads exactly the same links and lays them
out in three dimensions.

## Options

```bash
shelfie map --depth 4      # map more levels (the graph gets busy fast)
shelfie map --out ~/my-map # somewhere else
```

Default depth is 3. Depth 5 on a large library produces a hairball that is
impressive and useless.

`.git`, `node_modules`, `__pycache__` and `.venv` are skipped. They contain tens
of thousands of files that are not really *yours*, and including them buries the
signal.

## One thing to know

**These notes are generated.** Editing one by hand works fine until the next
`shelfie map`, which overwrites it. Notes named `HOW THIS VAULT WORKS` and
`README` are left alone, so you have somewhere to write — but for real notes,
use a separate vault. Obsidian switches between vaults from the icon at the
bottom-left.
