# The idea behind the shelves

Most filing systems fail for the same reason: they sort by **what a file is**
instead of **what it is for**.

Sorting by type is easy to automate, which is why every tool defaults to it. It
is also why people abandon the result. A client job produces a contract, a folder
of photos, a website backup and an invoice. Sort by type and those four land in
`Documents/`, `Images/`, `Archive/` and `Documents/Financial/` — four branches,
no thread connecting them. Six months later you know you did work for that
client and you cannot assemble it again.

shelfie starts from the opposite end.

## The shelves

```
Projects/      active work, one folder per client or job
Areas/         ongoing responsibilities with no end date
Resources/     reference material you might want one day
Archive/       finished, kept in case
Inbox/         not yet sorted — should trend towards empty
```

Four of those are [PARA](https://fortelabs.com/blog/para/), Tiago Forte's
scheme. The fifth, `Inbox/`, is the admission that no automatic system gets
everything right.

The distinction that carries the most weight is **Projects vs Areas**:

- A **project** ends. "Rebuild the Acme site" finishes, and the whole folder
  moves to `Archive/` in one drag. That single property is what makes the system
  survive contact with real work.
- An **area** never ends. Finances, health, admin, your own credentials. There is
  no finish line, so there is nothing to archive.

Get that split right and archiving stops being a chore you avoid.

## Why the project rule matters most

shelfie reads the folder names under `Projects/` and treats them as words it
knows. A file mentioning one of them goes there, **whatever its type**.

```
acme-corp-logo.png      → Projects/acme-corp/     (not Media/Images)
acme-invoice-2026.pdf   → Projects/acme-corp/     (not Documents/Financial)
acme-site-backup.wpress → Projects/acme-corp/     (not Archive/Site Backups)
```

That is the whole trick, and it costs nothing to maintain: the project list is
just the folders you already made. Add a client folder and shelfie knows about
them on the next run.

## Inboxes are not storage

`Downloads` and `Desktop` are **inboxes**. Things pass through; nothing lives
there. That is not a rule shelfie enforces so much as one it makes cheap to
follow — emptying them becomes one command instead of an afternoon.

The corollary matters too: **never save into an inbox and leave it**. No tool
fixes a habit. It can only lower the cost of the good one.

## Depth, and why three levels is usually enough

Every level you add is a decision when filing and a guess when looking. Three is
almost always the ceiling:

```
Library/Projects/acme-corp/          ← fine
Library/Projects/acme-corp/2026/q1/  ← you will not remember which quarter
```

If you have a real search tool — [Everything](https://voidtools.com) on Windows,
Spotlight on macOS, `fd` anywhere — deep trees stop paying for themselves
entirely. Search beats hierarchy for *finding*. Hierarchy still wins for
*browsing* and for knowing what you have, which is why shelfie does not simply
dump everything in one folder.

## What shelfie will not do

**It will not guess.** A folder it cannot identify stays where it is and is
listed as skipped. Wrong filing is worse than no filing because it is invisible —
you do not discover it until you are already looking for the thing.

**It will not touch anything new.** The age threshold exists because automatic
sorting without one is hostile: you download an installer, alt-tab, and it is
gone. A few days' delay means only genuine backlog moves.

**It will not delete.** There is no delete path in the code. Duplicates,
corrupt archives and junk are yours to remove deliberately.
