"""Render WTForm example forms with Python 2 and print them as JSON.

Examples 1-3 are the ones in the WTForm documentation. Example 4 covers
the other features: a hidden field, help text, an HTML node, a column
class, a field left out of the layout and an error from clean().
"""
from __future__ import print_function

import json

from django.conf import settings

settings.configure()
import django

if hasattr(django, 'setup'):
    django.setup()
from django import forms

from wtform import HTML, Columns, Fieldset, WTForm


class Example1(WTForm):
    name = forms.CharField(label="Name")
    email = forms.EmailField(label="E-mail address")

    class Meta:
        layout = (Columns(("name",), ("email",)),)


class TwoPeople(WTForm):
    name1 = forms.CharField(label="Name (1)")
    email1 = forms.EmailField(label="E-mail address (1)")
    name2 = forms.CharField(label="Name (2)")
    email2 = forms.EmailField(label="E-mail address (2)")


class Example2(TwoPeople):
    class Meta:
        layout = (Fieldset("Person 1", Columns(("name1",), ("email1",))),
                  Fieldset("Person 2", Columns(("name2",), ("email2",))))


class Example3(TwoPeople):
    class Meta:
        layout = (Fieldset("Person details",
                           Columns(("name1", "name2"), ("email1", "email2"))),)


class Example4(WTForm):
    token = forms.ChoiceField(choices=[('a', 'A')], widget=forms.HiddenInput)
    subject = forms.CharField(label="Subject", help_text="A few words, <b>please</b>")
    message = forms.CharField(label="Message", widget=forms.Textarea)
    newsletter = forms.BooleanField(label="Send me the newsletter", required=False)
    phone = forms.CharField(label="Phone")

    class Meta:
        layout = (HTML('<p class="note">All fields except the newsletter are required.</p>'),
                  Columns(("subject", "message"), ("newsletter",), css_class="yui-gc"))

    def clean(self):
        if self.data.get('message') == 'Hi':
            raise forms.ValidationError('Please write more than "Hi".')
        return self.cleaned_data


TWO_PEOPLE = {'name1': 'Ann', 'email1': 'not-an-email', 'name2': '', 'email2': 'bob@example.org'}
EXAMPLES = {
    'example1': (Example1, {'name': '', 'email': 'not-an-email'}),
    'example2': (Example2, TWO_PEOPLE),
    'example3': (Example3, TWO_PEOPLE),
    'example4': (Example4, {'token': '<script>alert(1)</script>', 'subject': '',
                            'message': 'Hi', 'phone': ''}),
}


def main():
    rendered = {}
    for name, (form_class, data) in sorted(EXAMPLES.items()):
        bound = form_class(data)
        bound.is_valid()
        rendered[name] = {'unbound': form_class().as_div(), 'errors': bound.as_div()}
    print(json.dumps({'django': django.get_version(), 'examples': rendered},
                     indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
