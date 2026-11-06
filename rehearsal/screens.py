# /// script
# requires-python = ">=3.12"
# dependencies = ["google-genai"]
# ///
"""Screenshot old and new renderings and ask a vision model to compare them.

Usage: screens.py OLD.json NEW.json OUT_DIR [--css EXTRA.css] [--only EXAMPLE]

The old page uses YUI 2 grids; the new page uses layout.css. Both use
shared.css for field styling. The model compares each pair of
screenshots with the layout drawing for that example: the three
drawings in the WTForm documentation, and one in this file for example
4. Needs GEMINI_API_KEY and Chromium.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path

from google import genai
from google.genai import types
from pydantic import BaseModel

HERE = Path(__file__).resolve().parent
MODEL = "gemini-3.1-pro-preview"
YUI_GRIDS = ("https://raw.githubusercontent.com/yui/yui2/"
             "067c9f82ecc90e4b392b7cb06a4a4f7fe3f6136e/build/grids/grids.css")
YUI_SHA256 = "42c892a038773ff4712a98566e02d56153cda6189ea4ed3ea9ae75637a43fffc"
EXAMPLE4_DRAWING = """\
  (hidden input, then a list of errors from hidden fields and clean())
  All fields except the newsletter are required.        <- italic note
  +-----------------------------------+-----------------+
  | Subject                           | Send me the     |
  | A few words, <b>please</b>        | newsletter      |
  | [_______________________________] | [ ] (checkbox)  |
  | Message                           |                 |
  | [                               ] |                 |
  | [_______________________________] |                 |
  +-----------------------------------+-----------------+
  Phone
  [___________________________________________________]
  (columns: the left one is 2/3 and the right one 1/3 of the width)"""
PROMPT = """\
Image 1 is an HTML form rendered by old code, image 2 the same form rendered by
its replacement. The intended layout, from the documentation, is this drawing:

{drawing}

Boxes drawn with +-[ Legend ]-+ are fieldsets with that legend, vertical bars
separate columns, and [___] is a text input. The drawing shows the empty form;
the screenshots may also show error messages in red. Ignore fonts, colours,
border styles, exact widths and the spelling of "e-mail" or "email".

Answer in JSON:
- old_matches_drawing, new_matches_drawing: does each image have the drawing's
  fieldsets, columns, and fields in the same columns and order?
- same_layout: do the two images place the same fields in the same fieldsets,
  columns and order?
- same_content: do they show the same labels, help texts, values and errors?
- differences: a list of the differences you see, each a short sentence.
"""


class Verdict(BaseModel):
    old_matches_drawing: bool
    new_matches_drawing: bool
    same_layout: bool
    same_content: bool
    differences: list[str]


def drawings():
    """The layout drawings of the WTForm documentation, plus example 4."""
    doc = (HERE.parent / "wtform" / "__init__.py").read_text()
    found = []
    for chunk in doc.split("This will result in the form layout of:")[1:]:
        lines = []
        for line in chunk.splitlines()[1:]:
            if line.strip() and not line.startswith(("  +", "  |")):
                break
            lines.append(line)
        found.append("\n".join(lines).strip("\n"))
    return dict(zip(["example1", "example2", "example3"], found)) | {"example4": EXAMPLE4_DRAWING}


def yui_grids():
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "yui2-grids.css"
    if not cache.exists():
        cache.write_bytes(urllib.request.urlopen(YUI_GRIDS).read())
    data = cache.read_bytes()
    if hashlib.sha256(data).hexdigest() != YUI_SHA256:
        raise SystemExit(f"Unexpected content in {cache}")
    return data.decode()


def screenshot(html, css, png):
    page = png.with_suffix(".html")
    page.write_text(f"<!doctype html><meta charset=utf-8><style>{css}</style><form>{html}</form>")
    subprocess.run([os.environ.get("CHROMIUM", "chromium"), "--headless=new", "--disable-gpu",
                    "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=712,700", f"--screenshot={png.resolve()}", page.resolve().as_uri()],
                   check=True, capture_output=True, timeout=120)
    page.unlink()


def judge(client, drawing, old_png, new_png):
    response = client.models.generate_content(
        model=MODEL,
        contents=[types.Part.from_bytes(data=old_png.read_bytes(), mime_type="image/png"),
                  types.Part.from_bytes(data=new_png.read_bytes(), mime_type="image/png"),
                  PROMPT.format(drawing=drawing)],
        config=types.GenerateContentConfig(response_mime_type="application/json",
                                           response_schema=Verdict))
    return response.parsed.model_dump()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("old")
    parser.add_argument("new")
    parser.add_argument("out", type=Path)
    parser.add_argument("--css", type=Path, help="extra CSS for the new page")
    parser.add_argument("--only", help="compare only this example")
    args = parser.parse_args()
    old, new = (json.loads(Path(p).read_text())["examples"] for p in (args.old, args.new))
    shared = (HERE / "shared.css").read_text()
    old_css = yui_grids() + shared
    new_css = shared + (HERE / "modern" / "layout.css").read_text()
    if args.css:
        new_css += args.css.read_text()
    args.out.mkdir(parents=True, exist_ok=True)
    client = genai.Client(http_options=types.HttpOptions(api_version="v1beta"))
    verdicts = {}
    for example, drawing in drawings().items():
        if args.only and example != args.only:
            continue
        for state in ("unbound", "errors"):
            old_png = args.out / f"{example}-{state}-old.png"
            new_png = args.out / f"{example}-{state}-new.png"
            screenshot(old[example][state], old_css, old_png)
            screenshot(new[example][state], new_css, new_png)
            verdict = judge(client, drawing, old_png, new_png)
            verdicts[f"{example} {state}"] = verdict
            keys = ("old_matches_drawing", "new_matches_drawing", "same_layout", "same_content")
            print(f"{example} {state}: " + ", ".join(f"{k}={verdict.get(k)}" for k in keys))
            for difference in verdict.get("differences", []):
                print(f"  - {difference}")
    (args.out / "verdicts.json").write_text(json.dumps({"model": MODEL, "verdicts": verdicts},
                                                      indent=1) + "\n")


if __name__ == "__main__":
    main()
