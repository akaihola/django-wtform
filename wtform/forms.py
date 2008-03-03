import copy

from django.newforms.forms import BoundField
from django.utils.html import escape
from django.utils.datastructures import SortedDict
from django.newforms import BaseForm
from django.newforms.fields import Field

__all__ = ('WTForm', 'BaseWTForm', 'Fieldset', 'Columns', 'HTML', 'NoSuchFormField')

class NoSuchFormField(Exception):
    "The form field couldn't be resolved."
    pass

def error_list(errors):
    return '<ul class="errors"><li>' + \
           '</li><li>'.join(errors) + \
           '</li></ul>'

class SortedDictFromList(SortedDict):
    "A dictionary that keeps its keys in the order in which they're inserted."
    # This is different than django.utils.datastructures.SortedDict, because
    # this takes a list/tuple as the argument to __init__().
    def __init__(self, data=None):
        if data is None: data = []
        self.keyOrder = [d[0] for d in data]
        dict.__init__(self, dict(data))

    def copy(self):
        return SortedDictFromList([(k, copy.copy(v)) for k, v in self.items()])

class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, Field)]
        fields.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))

        # If this class is subclassing another Form, add that Form's fields.
        # Note that we loop over the bases in *reverse*. This is necessary in
        # order to preserve the correct order of fields.
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                fields = base.base_fields.items() + fields

        attrs['base_fields'] = SortedDictFromList(fields)
        return type.__new__(cls, name, bases, attrs)

class BaseWTForm(BaseForm):

    def __init__(self, *args, **kwargs):

        super(BaseWTForm, self).__init__(*args, **kwargs)

        # do we have an explicit layout?
        
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'layout'):
            assert hasattr(self.Meta.layout, '__getitem__'), "Meta.layout must be iterable"
            self.layout = self.Meta.layout
        else:
            # Construct a simple layout using the keys from the fields
            self.layout = self.fields.keys()

        self.prefix = []
        self.top_errors = []

    def as_table(self):
        raise NotImplementedError("WTForm does not support <table> output.")

    def as_ul(self):
        raise NotImplementedError("WTForm does not support <ul> output.")
    
    def as_p(self):
        raise NotImplementedError("WTForm does not support <p> output.")

    def as_div(self):

        ''' Render the form as a set of <div>s. '''

        self.rendered_fields = []

        output = self.render_fields(self.layout)

        # render missing fields from layout
        
        output += self.render_fields([field for field in self.fields.keys()
                                      if field not in self.rendered_fields])

        prefix = u''.join(self.prefix)

        if self.top_errors:
            errors = error_list(self.top_errors)
        else:
            errors = u''

        self.prefix = []
        self.top_errors = []

        return prefix + errors + output

    # Default output is now as <div> tags.
    
    __str__ = as_div

    def render_fields(self, fields, separator=u""):

        ''' Render a list of fields and join the fields by
            the value in separator. '''

        output = []
        
        for field in fields:

            if isinstance(field, (Columns, Fieldset, HTML)):
                output.append(field.as_html(self))
            else:
                self.rendered_fields.append(field)
                output.append(self.render_field(field))

        return separator.join(output)

    def render_field(self, field):

        ''' Render a named field to HTML. '''

        try:
            field_instance = self.fields[field]
        except KeyError:
            raise NoSuchFormField("Could not resolve form field '%s'." % field)

        bf = BoundField(self, field_instance, field)

        output = ''

        if bf.errors:

            # If the field contains errors, render the errors to a <ul>
            # using the error_list helper function.
            bf_errors = error_list([escape(error) for error in bf.errors])

        else:
            bf_errors = ''

        if bf.is_hidden:

            # If the field is hidden, add it at the top of the form

            self.prefix.append(unicode(bf))

            # If the hidden field has errors, append them to the top_errors
            # list which will be printed out at the top of form
            
            if bf_errors:
                self.top_errors.extend(bf.errors)

        else:

            # Find field + widget type css classes
            css_class = type(field_instance).__name__ + " " + \
                        type(field_instance.widget).__name__

            # Add an extra class, Required, if applicable
            if field_instance.required:
                css_class += " Required"

            if bf.label:

                # The field has a label, construct <label> tag
                label = escape(bf.label)
                label = bf.label_tag(label) or ''

            else:
                label = ''

            if field_instance.help_text:

                # The field has a help_text, construct <span> tag
                help_text = escape(field_instance.help_text)
                help_text = '<span class="help_text">%s</span>' % help_text

            else:
                help_text = u''

            # Finally render the field
            output = '<div class="field %(class)s">%(label)s%(help_text)s%(errors)s<div class="input">%(field)s</div></div>\n' % \
                     {'class': css_class, 'label': label, 'help_text': help_text, 'errors': bf_errors, 'field': unicode(bf)}

        return output

class WTForm(BaseWTForm):
    __metaclass__ = DeclarativeFieldsMetaclass

class Fieldset(object):

    ''' Fieldset container. Renders to a <fieldset>. '''

    def __init__(self, legend, *fields):
        self.legend_html = legend and ('<legend>%s</legend>' % legend) or ''
        self.fields = fields
    
    def as_html(self, form):
        return u'<fieldset>%s%s</fieldset>' % \
               (self.legend_html, form.render_fields(self.fields))
            
class Columns(object):

    ''' Columns container. Renders to a set og <div>s named
        with classes as used by YUI (Yahoo UI)  '''

    def __init__(self, *columns, **kwargs):
        self.columns = columns
        self.css_class = kwargs.has_key('css_class') and kwargs['css_class'] or 'yui-g'

    def as_html(self, form):
        output = []
        first = " first"

        output.append('<div class="%s">' % self.css_class)

        for fields in self.columns:
            output.append('<div class="yui-u%s">%s</div>' % \
                          (first, form.render_fields(fields)))
            first = ''

        output.append('</div>')

        return u''.join(output)

class HTML(object):

    ''' HTML container '''

    def __init__(self, html):
        self.html = html

    def as_html(self, form):
        return self.html

