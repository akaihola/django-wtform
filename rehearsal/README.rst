Moving the WTForm examples to plain Django 6
============================================

This directory checks whether forms laid out with WTForm can move to
plain Django 6.0 forms and templates without changing how they look
or behave. The 2009 code provides the reference: it still runs on
Python 2.7 and old Django releases in a container, and its output is
compared with the rebuild in two ways. The steps of the move are in
the `main README`_.

Files
-----

examples.py
    The three example forms of the WTForm documentation, and a fourth
    which uses the rest of its features: a hidden field, help text, an
    ``HTML`` node, the ``yui-gc`` column class, a field left out of the
    layout and an error from ``clean()``. Prints the HTML of each form,
    empty and with errors, as JSON. Runs on Python 2.7.
golden/
    That output on Django 1.0.4, 1.1.4, 1.4.22 and 1.8.19.
modern/
    The same forms in Django 6.0: ``layout_forms.py``, a template for
    each layout, one field template, ``layout.css``, and ``render.py``,
    which prints the same JSON as ``examples.py``.
compare.py
    Compares the old and the new HTML field by field: each field's
    place in the layout (fieldset, column grid and column), label, help
    text, errors and input. Known, intended differences are listed with
    their reasons. Any other difference, or an ``aria-describedby``
    that points at a missing element, makes it exit with status 1.
screens.py
    Takes a screenshot of each old form with YUI 2 grids and each new
    form with CSS grid, using ``shared.css`` for both, and asks a Gemini
    vision model whether the pair matches the layout drawing of that
    example. The drawings for examples 1 to 3 are read from the WTForm
    documentation; the one for example 4 is in the script.
negative/
    Two deliberately broken versions, to check that the checks can
    fail: a template with Person 2's fields in the wrong columns, and
    CSS which stacks the columns instead of placing them side by side.
py2run.sh
    Runs a script with Python 2.7.18 and a chosen Django release in an
    offline podman container.

Running it
----------

The old side needs podman and the ``python:2.7-alpine`` image. Django
1.0.4 comes from djangoproject.com, because PyPI has no files for it;
later releases come from PyPI::

    for v in 1.0.4 1.1.4 1.4.22 1.8.19; do
        ./py2run.sh $v .. rehearsal/examples.py > golden/django-$v.json
    done
    uv run modern/render.py > modern/django-6.json
    uv run compare.py golden/django-1.4.22.json modern/django-6.json
    uv run screens.py golden/django-1.4.22.json modern/django-6.json screenshots

``py2run.sh`` mounts a directory at ``/code`` in the container and runs
a script there with the given Django release on ``PYTHONPATH``.
``screens.py`` needs Chromium and a ``GEMINI_API_KEY``.

Results on 2026-11-06
---------------------

The old output was the same on Django 1.0.4, 1.1.4 and 1.4.22. On
1.8.19 the labels end with a colon, ``EmailField`` renders
``<input type="email">``, and the error message says "email" instead
of "e-mail". The rebuild ran on Django 6.0.10 and was compared with
the output of Django 1.4.22.

``compare.py`` found no unexplained differences. The intended ones:

- ``<input type="email">`` for ``EmailField``;
- "email" instead of "e-mail" in Django's message;
- the class ``required`` instead of WTForm's ``CharField TextInput
  Required`` and the like;
- the error from ``clean()`` in example 4, which WTForm never showed.

Django 6 also adds the ``required``, ``maxlength``, ``aria-invalid`` and
``aria-describedby`` attributes to inputs. ``compare.py`` caught a
mistake of mine in the field template: its error list had no ``id``,
so ``aria-describedby`` pointed at nothing.

``screens.py``, with gemini-3.1-pro-preview, found that all eight
pairs of screenshots match the layout drawings and each other. The only
difference it reported is the error from ``clean()``.

The broken versions show what each check can see:

=================  ==============  ==============
Broken version     ``compare.py``  ``screens.py``
=================  ==============  ==============
Swapped columns    fails           fails
Stacked columns    passes          fails
=================  ==============  ==============

The stacked columns differ only in CSS, so only the screenshots show
them. The verdicts are in ``verdicts.json`` beside the screenshots.

Before the 2009 code could serve as the reference, it needed three
fixes, listed in the Status section of the main README.

.. _main README: ../README.rst
