#!/usr/bin/env python3
"""build-shots — rebuild the Frame-baked WebP screenshot slots under assets/shots/.

Composites the raw app captures shipped by the Fotospots app repo into the
self-contained "device with app on screen" WebP files that this landing page
serves as Frames. Each raw is resized to a fixed 2x inner-screen width, given
rounded inner corners, and pasted onto a dark bezel (#2A2620) that itself
carries rounded outer corners. The CSS keyline outline around each Frame is
supplied by the stylesheet, not baked in here.

Run this whenever the app team refreshes the raw captures under
/Users/michelonwordi/Dev/Fotospots/docs/product/app-store-listing/screenshots/raw/.

Usage:
  python3 scripts/build-shots.py
  scripts/build-shots.py --raws /path/to/raws
  FOTOSPOTS_RAWS=/path/to/raws scripts/build-shots.py
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parent.parent
DEFAULT_RAWS = Path(
    "/Users/michelonwordi/Dev/Fotospots/docs/product/app-store-listing/screenshots/raw"
)

# The bezel color the h2w Frame refactor picked. Kept in sync with CSS token
# --fs-bezel in css/tokens.css.
BEZEL_COLOR = (0x2A, 0x26, 0x20, 0xFF)
WEBP_QUALITY = 85


@dataclass(frozen=True)
class FrameSpec:
    """Bezel geometry for one Frame class, all values at 2x retina pixels.

    padding, wrap_radius, inner_radius are exactly double the 1x CSS values the
    stylesheet's `.fs-shot-*` rules and radius tokens declare. inner_w is the
    target width of the resized raw before it is pasted into the bezel; the
    inner height is derived from the raw's own aspect ratio, and the outer
    frame dimensions come out to inner + 2*padding.
    """

    inner_w: int
    padding: int
    wrap_radius: int
    inner_radius: int


# The three Frame classes rendered by css/style.css. Values match the shipped
# assets/shots/*.webp dimensions at HEAD (i1 660x1396, i3/i6 459x969, p2
# 1720x1303) when applied to the current raws.
IPHONE_LG = FrameSpec(inner_w=628, padding=16, wrap_radius=92, inner_radius=76)
IPHONE_SM = FrameSpec(inner_w=435, padding=12, wrap_radius=72, inner_radius=60)
IPAD = FrameSpec(inner_w=1668, padding=26, wrap_radius=68, inner_radius=44)

# (slot name, Frame class, raw path relative to the raws root).
SLOTS: list[tuple[str, FrameSpec, str]] = [
    ("i1-en", IPHONE_LG, "iphone-6.9/i1-en-light.png"),
    ("i1-de", IPHONE_LG, "iphone-6.9/i1-de-light.png"),
    ("i3-en", IPHONE_SM, "iphone-6.9/i3-en-light.png"),
    ("i3-de", IPHONE_SM, "iphone-6.9/i3-de-light.png"),
    ("i6-en", IPHONE_SM, "iphone-6.9/i6-en-light.png"),
    ("i6-de", IPHONE_SM, "iphone-6.9/i6-de-light.png"),
    ("p2-en", IPAD, "ipad-13/p2-en-light.png"),
    ("p2-de", IPAD, "ipad-13/p2-de-light.png"),
]


def build_frame(raw_path: Path, spec: FrameSpec) -> Image.Image:
    """Resize the raw and composite it onto the bezel per one FrameSpec."""
    raw = Image.open(raw_path).convert("RGBA")

    inner_w = spec.inner_w
    inner_h = round(raw.height * inner_w / raw.width)
    outer_w = inner_w + 2 * spec.padding
    outer_h = inner_h + 2 * spec.padding

    # Downsize the raw capture to the inner-screen dimensions with a
    # high-quality resampler; this is where most visual quality is decided.
    screen = raw.resize((inner_w, inner_h), Image.LANCZOS)

    # Round the inner-screen corners by masking the resized raw's alpha.
    screen_mask = Image.new("L", (inner_w, inner_h), 0)
    ImageDraw.Draw(screen_mask).rounded_rectangle(
        (0, 0, inner_w - 1, inner_h - 1),
        radius=spec.inner_radius,
        fill=255,
    )
    screen.putalpha(screen_mask)

    # Draw the bezel as a rounded rectangle onto a transparent canvas, so the
    # outer corners of the framed image are alpha-shaped rather than square.
    frame = Image.new("RGBA", (outer_w, outer_h), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle(
        (0, 0, outer_w - 1, outer_h - 1),
        radius=spec.wrap_radius,
        fill=BEZEL_COLOR,
    )

    frame.paste(screen, (spec.padding, spec.padding), screen)
    return frame


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild assets/shots/*.webp Frames from the Fotospots raws. "
            "See docs/adapters/stack.md for context."
        )
    )
    parser.add_argument(
        "--raws",
        type=Path,
        default=Path(os.environ.get("FOTOSPOTS_RAWS", str(DEFAULT_RAWS))),
        help=(
            "Directory containing iphone-6.9/ and ipad-13/ raw captures. "
            "Defaults to $FOTOSPOTS_RAWS if set, otherwise the hardcoded "
            "Fotospots repo path."
        ),
    )
    args = parser.parse_args(argv)

    raws: Path = args.raws
    if not raws.is_dir():
        print(f"build-shots: raws directory not found: {raws}", file=sys.stderr)
        return 1

    out_dir = REPO / "assets" / "shots"
    out_dir.mkdir(parents=True, exist_ok=True)

    for slot, spec, rel in SLOTS:
        raw_path = raws / rel
        if not raw_path.is_file():
            print(f"build-shots: missing raw {raw_path}", file=sys.stderr)
            return 1
        framed = build_frame(raw_path, spec)
        out_path = out_dir / f"{slot}.webp"
        framed.save(out_path, "WEBP", quality=WEBP_QUALITY, method=6)
        print(
            f"build-shots: wrote {out_path.relative_to(REPO)} "
            f"{framed.size[0]}x{framed.size[1]}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
