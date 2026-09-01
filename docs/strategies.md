# Strategies compared

Five ways to lay out a library. The wizard asks once and remembers.

## PARA — by how you use it

```
Projects/acme-corp/     Areas/Finances/
Projects/blue-lagoon/   Areas/Credentials/
Resources/Media/        Archive/2025/old-client/
```

Sorts by **actionability**, not type. From Tiago Forte's *Building a Second
Brain*.

**Good for** work that arrives as jobs — freelancing, consulting, agency work.
Everything for one client lives together whatever the file type.

**Weak** where nothing is a project. If your files are mostly personal media,
this adds a layer that earns nothing.

**The key split:** a *project* ends and can be archived whole; an *area* never
ends. Getting that right is what makes archiving painless instead of a chore.

## By file type

```
Media/Video/   Documents/PDF/   Software/Installers/
```

**Good for** emptying a downloads folder with zero decisions. Obvious to anyone.

**Weak** in exactly the way described in [concepts](concepts.md): it splits
things that belong together.

The honest default. Start here if unsure; `shelfie init` can change it later.

## Type, then year

```
Media/Images/2026/   Documents/PDF/2025/
```

**Good for** the pragmatic middle. Browsable by type, and folders do not grow to
ten thousand items.

**Weak** only in adding one more level to click through.

## By date

```
2026/01 January/   2026/02 February/
```

**Good for** photos, screenshots, scans, receipts — anything you place in time
rather than by subject.

**Weak** for everything else. An installer and a holiday photo from the same week
end up side by side.

## Flat shelves

```
Documents/   Media/   Software/   Projects/
```

**Good for** people who genuinely search rather than browse. With
[Everything](https://voidtools.com) or Spotlight, deep trees stop paying off.

**Weak** if you browse. Folders get very large.

---

## Changing your mind

```bash
shelfie init
```

Re-runs the wizard. **It does not re-file anything already sorted** — the new
strategy applies from the next `shelfie sort` onward. Moving an existing library
between layouts is not something to do automatically, because the mapping is
rarely one-to-one.
