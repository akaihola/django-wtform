"""The WTForm examples as plain Django 6 forms: each layout is a template."""

from django import forms
from django.forms.renderers import TemplatesSetting


class LayoutRenderer(TemplatesSetting):
    """Render every field group with WTForm's field markup."""

    field_template_name = "layout/field.html"


class LayoutForm(forms.Form):
    required_css_class = "required"

    def get_context(self):
        """Show errors of hidden fields and of clean() at the top, like WTForm."""
        context = super().get_context()
        hidden_errors = [e for field in self.hidden_fields() for e in field.errors]
        context["top_errors"] = [*hidden_errors, *self.non_field_errors()]
        return context


class Example1(LayoutForm):
    template_name = "layout/example1.html"
    name = forms.CharField(label="Name")
    email = forms.EmailField(label="E-mail address")


class TwoPeople(LayoutForm):
    name1 = forms.CharField(label="Name (1)")
    email1 = forms.EmailField(label="E-mail address (1)")
    name2 = forms.CharField(label="Name (2)")
    email2 = forms.EmailField(label="E-mail address (2)")


class Example2(TwoPeople):
    template_name = "layout/example2.html"


class Example3(TwoPeople):
    template_name = "layout/example3.html"


class Example4(LayoutForm):
    template_name = "layout/example4.html"
    token = forms.ChoiceField(choices=[("a", "A")], widget=forms.HiddenInput)
    subject = forms.CharField(label="Subject", help_text="A few words, <b>please</b>")
    message = forms.CharField(label="Message", widget=forms.Textarea)
    newsletter = forms.BooleanField(label="Send me the newsletter", required=False)
    phone = forms.CharField(label="Phone")

    def clean(self):
        if self.data.get("message") == "Hi":
            raise forms.ValidationError('Please write more than "Hi".')
        return self.cleaned_data
