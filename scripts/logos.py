"""ASCII / SVG-text logos for the neofetch-style header.

Each logo is a list of (line, color_role) tuples. color_role refers to
a key in the active theme palette (accent, text, muted, green, ...).
"""
from __future__ import annotations

# Arch Linux — classic compact form
ARCH = [
    ("       /\\       ", "accent"),
    ("      /  \\      ", "accent"),
    ("     /\\   \\     ", "accent"),
    ("    /      \\    ", "accent"),
    ("   /   ,,   \\   ", "accent"),
    ("  /   |  |   \\  ", "accent"),
    (" / _-'    `-_ \\ ", "muted"),
    ("/_-'        `-_\\", "muted"),
]

# Random tiny cat (the one from the mockup)
CAT = [
    ("    /\\_/\\        ", "accent"),
    ("   ( o.o )       ", "accent"),
    ("    > ^ <        ", "accent"),
    ("   /     \\       ", "muted"),
    ("  ( | | | )      ", "muted"),
    ("   ^^   ^^       ", "muted"),
]

LOGOS = {
    "arch": ARCH,
    "cat": CAT,
    "none": [],
}


def get(name: str):
    return LOGOS.get(name, ARCH)


def width(name: str) -> int:
    """Approximate character width of the widest line."""
    lines = LOGOS.get(name, [])
    return max((len(l) for l, _ in lines), default=0)


def height(name: str) -> int:
    return len(LOGOS.get(name, []))
