"""Deciding where a file belongs.

Order matters, and it is deliberate:

1. **Project name** beats everything. If a file mentions a folder you already
   have under ``Projects/``, it goes there - a client's logo belongs with that
   client, not in a generic images pile. This is the rule that makes the tool
   feel like it understands your work, and it costs nothing: the project list is
   just the folders you already made.
2. **Name patterns** beat file extension, because an extension often lies. A
   ``.zip`` can be a WordPress plugin, a design template, a site backup or a
   photo dump, and the filename usually says which.
3. **Extension** is the fallback.
4. **Give up honestly.** Anything unmatched goes to ``Inbox/`` rather than being
   guessed at. Ten things in an inbox beats ten things filed wrongly, because
   wrong filing is invisible until you go looking.
"""

import os
import re
from typing import List, Optional

# --- category by extension -------------------------------------------------

BY_EXT = {
    "Media/Video":         ".mp4 .mkv .avi .mov .wmv .m4v .webm .mpg .mpeg .flv",
    "Media/Audio":         ".mp3 .wav .flac .m4a .aac .ogg .opus .aiff",
    "Media/Books":         ".epub .mobi .azw3 .m4b .djvu",
    "Media/Images":        ".jpg .jpeg .png .gif .webp .bmp .heic .tif .tiff .avif",
    "Documents/PDF":       ".pdf",
    "Documents/Office":    ".docx .doc .odt .xlsx .xls .ods .pptx .ppt .odp",
    "Documents/Data":      ".csv .json .xml .yaml .yml .sql .tsv",
    "Documents/Notes":     ".txt .md .rtf .excalidraw .org",
    "Design":              ".psd .ai .fig .xd .indd .eps .sketch .aep .prproj .afdesign",
    "Software/Installers": ".exe .msi .dmg .pkg .deb .rpm .appimage .apk .appx",
    "Software/Disk Images": ".iso .img .vhd .vmdk",
    "Software/Drivers":    ".inf .sys .cat",
    "Code":                ".py .js .ts .tsx .jsx .go .rs .java .c .cpp .h .rb .php .sh .ps1",
    "Fonts":               ".ttf .otf .woff .woff2 .eot",
    "Credentials":         ".pem .ppk .key .kdbx .p12 .keystore",
}

_EXT_MAP = {}
for _cat, _exts in BY_EXT.items():
    for _e in _exts.split():
        _EXT_MAP[_e] = _cat

# --- category by filename pattern -----------------------------------------
# Checked in order; first match wins.

BY_NAME = [
    (r"\.wpress$|wpwp\.\d+_|-wp-\d{8}|wordpress.*backup", "Archive/Site Backups"),
    (r"backup.*\d{4}[-_]?\d{2}[-_]?\d{2}|\d{4}[-_]\d{2}[-_]\d{2}.*backup", "Archive/Backups"),
    (r"elementor|template.?kit|-utc\.(zip|rar)$", "Software/Web Assets"),
    (r"wp-|woocommerce|\bplugin\b|\btheme\b", "Software/Web Assets"),
    (r"invoice|receipt|statement|payslip|tax", "Documents/Financial"),
    (r"\bcv\b|resume|cover.?letter", "Documents/Career"),
    (r"^id_rsa|\.pub$|private.?key|secret", "Credentials"),
    (r"driver|_whql|installtool", "Software/Drivers"),
    (r"screenshot|screen.?shot|capture", "Media/Screenshots"),
    (r"wallpaper", "Media/Wallpapers"),
]

# never move these; they are downloads still in flight
INCOMPLETE = {".crdownload", ".part", ".partial", ".tmp", ".!ut", ".download"}

# archives are ambiguous by nature - hold them rather than guess
ARCHIVE_EXT = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}

# never touch these, on any platform
IGNORE_NAMES = {"desktop.ini", ".ds_store", "thumbs.db", ".localized"}
IGNORE_EXT = {".lnk", ".url", ".alias", ".webloc"}


def _flatten(text: str) -> str:
    return re.sub(r"[\s_\-.]", "", text.lower())


def project_match(name: str, projects: List[str]) -> Optional[str]:
    """Does this filename mention one of the user's existing projects?

    Longest project name first, so 'acme-corp-archive' wins over 'acme'.
    Requires four characters to avoid a project called 'ab' swallowing
    everything.
    """
    flat = _flatten(name)
    for p in sorted(projects, key=len, reverse=True):
        token = _flatten(p)
        if len(token) >= 4 and token in flat:
            return p
    return None


def categorise(name: str, is_dir: bool, projects: List[str]) -> Optional[str]:
    """Return a category path like 'Media/Video', or None to leave it alone."""
    low = name.lower()
    ext = os.path.splitext(low)[1]

    if low in IGNORE_NAMES or ext in IGNORE_EXT:
        return None
    if ext in INCOMPLETE:
        return "Inbox/Incomplete Downloads"

    hit = project_match(name, projects)
    if hit:
        return "Projects/" + hit

    for pattern, category in BY_NAME:
        if re.search(pattern, low):
            return category

    if is_dir:
        # a folder we cannot identify is left where it is - folders usually mean
        # something to their owner, and guessing is worse than asking
        return None

    if ext in _EXT_MAP:
        return _EXT_MAP[ext]
    if ext in ARCHIVE_EXT:
        return "Inbox/Archives"
    return "Inbox/Unsorted"
