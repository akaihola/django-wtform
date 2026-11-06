WTForm (What The Form)
======================

WTForm is an extension to the Django forms library which lets you lay
out form fields in ``<fieldset>`` elements and columns. Christian
Joergensen and Oscar Eg Gensmann of GMTA wrote it in 2007 and released
WTForm 1.0 on PyPI_ in 2008.

This is my branch of WTForm 1.0. In 2009 I made it work with Django
1.0, where ``django.newforms`` became ``django.forms``. The
documentation is in the docstring of `wtform/__init__.py`_.

Status
------

Update 2026-11-06: This branch hasn't been developed since 2009.
WTForm needs Python 2 and Django 1.0 to 1.8. Django 1.9 removed the
``SortedDict`` class it is built on.

If you use WTForm from here or from PyPI, update to the latest commit
of this branch. Until today, ``as_div()`` copied the errors of hidden
fields to the top of the form without escaping them. Django's error
message for an invalid choice includes the submitted value, so a
visitor could inject HTML and JavaScript into the page through a hidden
``ChoiceField``. Also note that ``as_div()`` doesn't render errors
raised in the ``clean()`` method of the form, so put
``{{ form.non_field_errors }}`` in your template yourself.

Django and maintained tools do the same job today:

- Django 4.1 added ``Form.as_div()``, and since Django 5.0
  ``{{ form }}`` renders ``<div>`` elements by default. The field group
  templates of Django 5.0 render a field's label, widget, help text
  and errors with ``{{ form.email.as_field_group }}``, so a plain
  template can place fields in fieldsets and columns. See the `Django
  5.0 release notes`_.
- django-crispy-forms_ attaches a ``Layout`` of ``Fieldset``, ``Div``
  and ``HTML`` objects to a form, much like ``Meta.layout`` in WTForm.
- YUI, whose grid CSS the ``Columns`` node was written for, is no
  longer developed. CSS grid layout does the same job.

WTForms_, the form library for Flask and other frameworks, is a
different project.

.. _PyPI: https://pypi.org/project/WTForm/
.. _wtform/__init__.py: wtform/__init__.py
.. _Django 5.0 release notes: https://docs.djangoproject.com/en/stable/releases/5.0/
.. _django-crispy-forms: https://django-crispy-forms.readthedocs.io/
.. _WTForms: https://wtforms.readthedocs.io/
