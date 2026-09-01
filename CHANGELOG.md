# Changelog

## 0.2.0

Documentation and onboarding pass. No behaviour changes to sorting.

**Added**
- Visual guide showing why sorting by file type splits a job apart, and what
  sorting by use looks like instead
- Diagram of the routing order: project name, then name pattern, then extension,
  then giving up honestly
- Setup walkthrough describing what each of the five wizard questions decides
- `CHANGELOG.md`

**Changed**
- README leads with the problem rather than the feature list
- Safety section made explicit about what the tool will and will not do
- Published on PyPI as `shelfie-organizer`; the command is still `shelfie`

## 0.1.0

First release.

- Five layout strategies: PARA, by type, type+year, by date, flat
- Learns project names from the folders under `Projects/`
- Preview and confirm before anything moves; `shelfie undo` reverses it
- Never deletes, never overwrites, leaves ambiguous folders alone
- Age threshold so files still in use are not pulled away
- Generates an Obsidian vault to browse the library as a graph
- Windows, macOS and Linux; no dependencies outside the standard library
