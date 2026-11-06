# /// script
# requires-python = ">=3.12"
# dependencies = ["django~=6.0.0"]
# ///
"""Render the examples with Django 6 and print them as JSON, like ../examples.py.

Usage: render.py [TEMPLATE_DIR...]; the given directories override templates.
"""

import json
import sys
from pathlib import Path

import django
from django.conf import settings

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
settings.configure(
    INSTALLED_APPS=["django.forms"],
    TEMPLATES=[{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [*map(Path, sys.argv[1:]), HERE / "templates"],  # overrides first
        "APP_DIRS": True,
    }],
    FORM_RENDERER="layout_forms.LayoutRenderer",
)
django.setup()

import layout_forms  # noqa: E402

DATA = {  # the same submissions as in ../examples.py
    "example1": {"name": "", "email": "not-an-email"},
    "example2": (people := {"name1": "Ann", "email1": "not-an-email", "name2": "",
                            "email2": "bob@example.org"}),
    "example3": people,
    "example4": {"token": "<script>alert(1)</script>", "subject": "", "message": "Hi",
                 "phone": ""},
}


def main() -> None:
    rendered = {}
    for name, data in DATA.items():
        form_class = getattr(layout_forms, name.title())
        bound = form_class(data)
        bound.is_valid()
        rendered[name] = {"unbound": str(form_class()), "errors": str(bound)}
    print(json.dumps({"django": django.get_version(), "examples": rendered},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
