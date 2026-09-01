"""Ways to organise files, and the reasoning behind each.

There is no single correct filing system. The right one depends on what you do
with your files, and picking the wrong one is why most attempts at "getting
organised" collapse within a month. Each strategy here states plainly what it is
good at and where it falls down, so the choice is informed rather than a coin
toss.

The research, briefly:

* **PARA** (Tiago Forte, *Building a Second Brain*) sorts by how *actionable*
  something is rather than what it is. Its strength is that it matches how work
  actually flows - a project ends, and the whole folder moves to the archive in
  one move.
* **Johnny.Decimal** (Johnny Noble) puts a hard cap on depth and numbers every
  category, so a location can be spoken aloud: "it's in 12.03". Excellent for
  teams and for people who like structure; heavy for a personal downloads folder.
* **By type** is the oldest and most common. Trivially automatable, which is why
  every tool defaults to it - but it separates things that belong together, and
  is the reason people cannot find the invoice that came with the photos.
* **By date** is how cameras and phones do it. Perfect when time is how you
  remember things, useless when it is not.

Nothing here is invented; the value is in applying them consistently and letting
a script do the filing.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List
import datetime
import os


@dataclass
class Strategy:
    key: str
    name: str
    tagline: str
    best_for: str
    weakness: str
    example: List[str]
    # given a routed category and the source file, return the folder path parts
    layout: Callable[[str, str], List[str]] = field(default=None, repr=False)


def _by_type(category: str, path: str) -> List[str]:
    return category.split("/")


def _by_date(category: str, path: str) -> List[str]:
    try:
        ts = os.path.getmtime(path)
    except OSError:
        ts = 0
    d = datetime.datetime.fromtimestamp(ts) if ts else datetime.datetime.now()
    return [d.strftime("%Y"), d.strftime("%m %B")]


def _type_then_date(category: str, path: str) -> List[str]:
    return category.split("/") + _by_date(category, path)[:1]


# Which of the four PARA buckets each category belongs in.
#   Projects  - has an end date; you are working on it now
#   Areas     - ongoing responsibility with no end date (finances, health, admin)
#   Resources - reference material you might want one day
#   Archive   - finished, kept only in case
_PARA_BUCKET = {
    "Projects":  "Projects",
    "Archive":   "Archive",
    "Inbox":     "Inbox",         # stays outside PARA until you triage it
    "Documents/Financial": "Areas/Finances",
    "Documents/Career":    "Areas/Career",
    "Credentials":         "Areas/Credentials",
}


def _para(category: str, path: str) -> List[str]:
    parts = category.split("/")
    top = parts[0]

    # exact category match first (Documents/Financial -> Areas/Finances)
    if category in _PARA_BUCKET:
        return _PARA_BUCKET[category].split("/")

    # then the top-level bucket (Projects/acme -> Projects/acme)
    if top in _PARA_BUCKET:
        return [_PARA_BUCKET[top]] + parts[1:]

    # everything else is reference material
    return ["Resources"] + parts


def _flat(category: str, path: str) -> List[str]:
    return [category.split("/")[0]]


STRATEGIES: Dict[str, Strategy] = {
    "para": Strategy(
        key="para",
        name="PARA (by how you use it)",
        tagline="Projects, Areas, Resources, Archive",
        best_for=(
            "Freelancers, consultants and anyone whose work arrives in jobs. A "
            "client's photos, invoices and site backup live together because "
            "they belong to the same job, not to the same file type."
        ),
        weakness=(
            "Needs a decision per item: is this still active? Automation can "
            "route by client name, but you keep the archive tidy yourself."
        ),
        example=[
            "Projects/acme-corp/",
            "Projects/blue-lagoon/",
            "Areas/finances/",
            "Resources/fonts/",
            "Archive/2025/old-client/",
        ],
        layout=_para,
    ),
    "type": Strategy(
        key="type",
        name="By file type",
        tagline="Documents, Images, Video, Software",
        best_for=(
            "A downloads folder you just want emptied. Fully automatable, no "
            "decisions, and obvious to anyone who opens it."
        ),
        weakness=(
            "Splits things that belong together. The contract and the photos "
            "from the same job end up in different branches."
        ),
        example=[
            "Documents/pdf/",
            "Images/",
            "Video/",
            "Software/Installers/",
        ],
        layout=_by_type,
    ),
    "date": Strategy(
        key="date",
        name="By date",
        tagline="2026/03 March/",
        best_for=(
            "Photos, screenshots, scans, receipts - anything you remember by "
            "roughly when it happened rather than what it was called."
        ),
        weakness=(
            "Hopeless for finding a thing by subject. Pair it with good search "
            "or you will never see these files again."
        ),
        example=["2026/01 January/", "2026/02 February/", "2025/12 December/"],
        layout=_by_date,
    ),
    "hybrid": Strategy(
        key="hybrid",
        name="Type, then year",
        tagline="Images/2026/, Documents/pdf/2026/",
        best_for=(
            "The pragmatic middle. Type at the top so it is browsable, year "
            "underneath so busy folders do not grow to ten thousand items."
        ),
        weakness="Two levels before you reach a file. Mildly more clicking.",
        example=["Images/2026/", "Video/2025/", "Documents/pdf/2026/"],
        layout=_type_then_date,
    ),
    "flat": Strategy(
        key="flat",
        name="Flat shelves",
        tagline="One level, nothing nested",
        best_for=(
            "People who genuinely search rather than browse. With a good search "
            "tool, deep trees stop earning their keep."
        ),
        weakness="Folders get very large. Only workable with real search.",
        example=["Documents/", "Media/", "Software/", "Projects/"],
        layout=_flat,
    ),
}

ORDER = ["para", "type", "hybrid", "date", "flat"]


def get(key: str) -> Strategy:
    return STRATEGIES.get(key, STRATEGIES["type"])
