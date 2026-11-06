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
of this branch. Today I fixed three bugs:

- ``as_div()`` copied the errors of hidden fields to the top of the
  form without escaping them. Django's error message for an invalid
  choice includes the submitted value, so a visitor could inject HTML
  and JavaScript into the page through a hidden ``ChoiceField``.
- Fields rendered after a hidden field got broken names, so their
  values were lost when the form was submitted. The ``prefix``
  argument of the form had no effect either.
- On Django 1.0 and 1.1, ``as_div()`` crashed whenever a field had an
  error such as "This field is required."

Also note that ``as_div()`` doesn't render errors raised in the
``clean()`` method of the form, so put ``{{ form.non_field_errors }}``
in your template yourself.

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

Moving off WTForm
-----------------

I rebuilt the example forms of WTForm as plain Django 6.0 forms and
templates, and checked that they render like WTForm on Django 1.4. The
code is in `rehearsal/modern`_, and `rehearsal/README.rst`_ describes
the checks. The steps:

1. Make the form a ``forms.Form``, and replace its ``Meta.layout``
   with ``template_name = "myapp/my_form.html"``. ``{{ form }}`` then
   renders that template.
2. Write the layout in that template: ``<fieldset>`` and ``<legend>``
   for a ``Fieldset``, a ``<div class="columns">`` with one ``<div>``
   per column for ``Columns``, plain HTML for ``HTML``, and
   ``{{ form.email.as_field_group }}`` for each field.
3. Give every field WTForm's markup with one field template: set
   ``field_template_name`` on a form renderer class and point
   ``FORM_RENDERER`` at it. WTForm escaped help texts, so don't add
   ``|safe`` the way Django's own field template does.
4. Render the hidden fields, and the errors of hidden fields and
   ``clean()``, from a small template which every layout includes.
5. Replace the YUI grid classes with CSS grid:
   ``grid-template-columns: 1fr 1fr`` for ``yui-g`` and ``2fr 1fr``
   for ``yui-gc``. Class names such as ``CharField TextInput
   Required`` are gone, so update your CSS selectors.
6. Place every field in the template. WTForm added the fields missing
   from the layout to the end of the form, but a template leaves them
   out.

.. _PyPI: https://pypi.org/project/WTForm/
.. _wtform/__init__.py: wtform/__init__.py
.. _Django 5.0 release notes: https://docs.djangoproject.com/en/stable/releases/5.0/
.. _django-crispy-forms: https://django-crispy-forms.readthedocs.io/
.. _WTForms: https://wtforms.readthedocs.io/
.. _rehearsal/modern: rehearsal/modern
.. _rehearsal/README.rst: rehearsal/README.rst
