# /// script
# requires-python = ">=3.12"
# dependencies = ["beautifulsoup4"]
# ///
"""Compare old WTForm output with the Django 6 rebuild, field by field.

Usage: compare.py OLD.json NEW.json

Each rendering becomes a list of items (hidden input, error list, HTML
note, field) with its place in the layout: fieldset legend, column grid
and column number. Differences that are known and intended are listed
with their reason; any other difference, or an aria-describedby that
points at a missing element, makes the script exit with status 1.
"""

import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

GRIDS = {  # old YUI grid class / new class -> column widths
    "yui-g": "1/2 + 1/2",
    "yui-gc": "2/3 + 1/3",
    "columns": "1/2 + 1/2",
    "columns wide-narrow": "2/3 + 1/3",
}
CONTROL_KEYS = ("tag", "type", "name", "id", "value", "checked")
INTENDED = [  # (field key, old value pattern, new value pattern, reason)
    ("control.type", r"text", r"email",
     "Django 1.6+ renders EmailField as <input type=\"email\">"),
    ("errors", r".*e-mail address.*", r".*email address.*",
     "Django changed its wording from \"e-mail\" to \"email\""),
    ("classes", r"(CharField|EmailField|BooleanField) \w+( Required)?", r"(required)?",
     "Django's required_css_class replaces WTForm's field and widget class names;"
     " CSS selectors need updating"),
    ("top errors", r".*", r".*Please write more than .*",
     "WTForm never rendered errors from clean(); the rebuild does"),
]


def text(tag):
    return " ".join(tag.get_text(" ", strip=True).split())


def grid_of(tag):
    return GRIDS.get(" ".join(tag.get("class", [])))


def control(tag):
    attrs = dict(tag.attrs)
    value = tag.get_text().removeprefix("\n") if tag.name == "textarea" else attrs.get("value")
    info = {"tag": tag.name, "type": attrs.get("type"), "name": attrs.get("name"),
            "id": attrs.get("id"), "value": value, "checked": "checked" in attrs}
    extra = sorted(k for k in attrs if k not in CONTROL_KEYS + ("rows", "cols"))
    return info, extra


def items(html):
    found = []

    def walk(node, place):
        for child in node.children:
            if not isinstance(child, Tag):
                continue
            classes = child.get("class", [])
            if child.name == "fieldset":
                legend = child.find("legend", recursive=False)
                walk(child, place + [f"fieldset {text(legend)!r}"])
            elif child.name == "legend":
                continue
            elif grid_of(child):
                columns = [c for c in child.children if isinstance(c, Tag)]
                for number, column in enumerate(columns, 1):
                    walk(column, place + [f"columns {grid_of(child)} #{number}"])
            elif "field" in classes:
                label = child.find("label")
                help_text = child.find(class_="help_text")
                errors = child.find("ul", class_="errors")
                info, extra = control(child.find(["input", "textarea", "select"]))
                found.append({
                    "kind": "field", "place": place, "label": label and text(label),
                    "label for": label and label.get("for"),
                    "help": help_text and text(help_text),
                    "errors": errors and [text(li) for li in errors.find_all("li")],
                    "classes": " ".join(c for c in classes if c != "field"),
                    "control": info, "extra attributes": extra})
            elif child.name == "input" and child.get("type") == "hidden":
                found.append({"kind": "hidden", "place": place,
                              "control": control(child)[0]})
            elif child.name == "ul" and "errors" in classes:
                found.append({"kind": "top errors", "place": place,
                              "top errors": [text(li) for li in child.find_all("li")]})
            elif child.name == "div":
                walk(child, place)
            else:
                found.append({"kind": "html", "place": place, "html": str(child)})

    walk(BeautifulSoup(html, "html.parser"), [])
    return found


def flat(item):
    out = {}
    for key, value in item.items():
        if key == "control":
            out.update({f"control.{k}": v for k, v in value.items()})
        elif key != "extra attributes":
            out[key] = value
    return out


def intended(key, old, new):
    for k, old_pattern, new_pattern, reason in INTENDED:
        if k == key and re.fullmatch(old_pattern, str(old or "")) \
                and re.fullmatch(new_pattern, str(new or "")):
            return reason
    return None


def dangling_aria(html):
    soup = BeautifulSoup(html, "html.parser")
    ids = {tag["id"] for tag in soup.find_all(id=True)}
    return [ref for tag in soup.find_all(attrs={"aria-describedby": True})
            for ref in tag["aria-describedby"].split() if ref not in ids]


def compare(old_html, new_html):
    """Return (intended differences, unexplained differences, new extra attributes)."""
    reasons, problems, extras = [], [], set()
    old_items, new_items = items(old_html), items(new_html)
    if len(old_items) != len(new_items):
        problems.append(f"{len(old_items)} items before, {len(new_items)} after")
    for old, new in zip(old_items, new_items):
        extras.update(new.get("extra attributes", []))
        old_flat, new_flat = flat(old), flat(new)
        for key in sorted(set(old_flat) | set(new_flat)):
            a, b = old_flat.get(key), new_flat.get(key)
            if a == b:
                continue
            where = old_flat.get("control.name") or old["kind"]
            reason = intended(key, a, b)
            if reason:
                reasons.append(reason)
            else:
                problems.append(f"{where}: {key} {a!r} -> {b!r}")
    problems += [f"aria-describedby points at missing #{ref}" for ref in dangling_aria(new_html)]
    return reasons, problems, extras


def main():
    old, new = (json.loads(Path(p).read_text()) for p in sys.argv[1:3])
    print(f"Django {old['django']} (WTForm) vs Django {new['django']} (templates)\n")
    failed = False
    for example, states in sorted(old["examples"].items()):
        for state, old_html in sorted(states.items()):
            reasons, problems, extras = compare(old_html, new["examples"][example][state])
            failed |= bool(problems)
            print(f"{example} {state}: {'FAIL' if problems else 'ok'}")
            for reason in sorted(set(reasons)):
                print(f"  intended ({reasons.count(reason)}x): {reason}")
            if extras:
                print(f"  new attributes on controls: {', '.join(sorted(extras))}")
            for problem in problems:
                print(f"  UNEXPLAINED: {problem}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
