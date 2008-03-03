'''
WTForm (What The Form)
======================

WTForm is an extension to the django newforms library allowing
the developer, in a very flexible way, to layout the form
fields using <fieldset>s and columns

WTForm was built with the well-documented YUI Grid CSS[1] in
mind when rendering the columns and fields. This should make
it easy to implement WTForm in your own applications.

Specifying the form layout
--------------------------

WTForm will look for a subclass of your form called "Meta". This
class should have a tuple variable called layout . The layout
variable will hold a tree structure of fields, field sets and
columns.

Here is a simple example:

  class MyForm(WTForm):

      name = forms.CharField(label="Name")
      email = forms.EmailField(label="E-mail address")

      class Meta:

          layout = (Columns(("name",), ("email",)),)

This will result in the form layout of:

  +--------------------------+--------------------------+
  | Name                     | E-mail address           |
  | [______________________] | [______________________] |
  +--------------------------+--------------------------+

WTForm currently uses four types of nodes (fields):

  - Fieldset(legend, field[, field])

    Represents a HTML <fieldset> with the fields specified
    by the arguments as contents. The first argument will
    be the content of the <legend> HTML node. If the legend
    argument is the empty string, the <legend> HTML node
    will not be rendered.
  
  - Columns(column[, column] [, css_class="foobar"])

    Represents a column grid. The columns are specified as
    tuples of fields. In order to obtain different grid
    sizes, the Columns function takes an optional keyword
    argument called css_class which will be rendered as the
    class of the outer-most <div> of the grid layout.

    See the YUI Grid CSS specification[1] for details on
    possible values for css_class. Also, see the
    "Columns CSS styling" part of this documentation.

    Even if you only have one field per column, remember
    to pass a tuple to the Columns function:

      Columns(("field1",), ("field2",))
  
  - HTML(content)

    Represents HTML content. This is useful for embedding
    HTML pieces in between fields for documentation. This
    type of node has no children.

  - "name"

    A string represents a single field. The field must be
    defined in your form. If the field could not be
    resolved, the NoSuchFormField exception will be raised.

Columns and Fieldset nodes can be nested as deep as you
want (just as long as you dont get in a fight with your web
designer).

More examples:
--------------

If you need to add two individuals in your form, you could put
them in field sets:

  class MyForm(WTForm):

      name1 = forms.CharField(label="Name (1)")
      email1 = forms.EmailField(label="E-mail address (1)")

      name2 = forms.CharField(label="Name (2)")
      email2 = forms.EmailField(label="E-mail address (2)")

      class Meta:

          layout = (Fieldset("Person 1",
                             Columns(("name1",), ("email1",))),
                    Fieldset("Person 2",
                             Columns(("name2",), ("email2",))))

This will result in the form layout of:

  +-[ Person 1 ]----------------------------------------+
  |+-------------------------+-------------------------+|
  || Name (1)                | E-mail address (1)      ||
  || [_____________________] | [_____________________] ||
  |+-------------------------+-------------------------+|
  +-----------------------------------------------------+

  +-[ Person 2 ]----------------------------------------+
  |+-------------------------+-------------------------+|
  || Name (2)                | E-mail address (2)      ||
  || [_____________________] | [_____________________] ||
  |+-------------------------+-------------------------+|
  +-----------------------------------------------------+

Say you would like one big field set with the charfields in
two columns:

  class MyForm(WTForm):

      name1 = forms.CharField(label="Name (1)")
      email1 = forms.EmailField(label="E-mail address (1)")

      name2 = forms.CharField(label="Name (2)")
      email2 = forms.EmailField(label="E-mail address (2)")

      class Meta:

          layout = (Fieldset("Person details",
                             Columns(("name1", "name2"),
                                     ("email1", "email2"))),)

This will result in the form layout of:

  +-[ Person details ]----------------------------------+
  |+-------------------------+-------------------------+|
  || Name (1)                | E-mail address (1)      ||
  || [_____________________] | [_____________________] ||
  ||                         |                         ||
  || Name (2)                | E-mail address (2)      ||
  || [_____________________] | [_____________________] ||
  |+-------------------------+-------------------------+|
  +-----------------------------------------------------+

Columns CSS styling:
--------------------

The Column HTML is written with the intent of working with
the YUI CSS for grids. When using Columns you can specify
the CSS class of the outer <div> by supplying the keyword
argument css_class:

  Columns(field1, field2, field3, css_class="yui-gc")

This will create a 2/3 - 1/3 grid with two columns. Read
more about YUI Grids CSS:

  http://developer.yahoo.com/yui/grids/

Differences from newforms / HTML structure of fields:
-----------------------------------------------------

In order to make CSS styling a lot easier, WTForm til raise
NotImplemented on as_table, as_p and as_ul. When rendering
WTForm forms you must use as_div, as we believe that this
is the way to structure your forms.

A field will be rendered as:

  <div class="CharField TextInput">
    <label for="id_name">Name</label>
    <span class="help_text">Very helpful text</span>
    <ul class="errors">
      <li>Error 1</li>
      <li>Error 2</li>
    </ul>
    <div class="field">
      <input type="text" name="name" value="" id="id_name" />
    </div>
  </div>    
    
The CSS classes in the outer <div> is fetched from the field
type as well as the widget type. If the field is marked as
required - it will also get a Required.

Data handling / newforms compability:
-------------------------------------

WTForm descends from newforms.Form, thus data handling is
done the same way: is_valid(), clean_data...

Refer to the newforms documentation[2] for details.

Credits:
--------

Christian Joergensen <christian.joergensen [at] gmta.info>
Oscar Eg Gensmann <oscar.gensmann [at] gmta.info>

Founded in 2003, GMTA ApS is the partnership between three
danish computer enthusiasts with a strong interest in the
web-phenomenon.

Visit our website: http://www.gmta.info

License:
--------

Creative Commons Attribution-Share Alike 3.0 License
http://creativecommons.org/licenses/by-sa/3.0/

When attributing this work, you must maintain the Credits
paragraph above.

References:
-----------

 [1] http://developer.yahoo.com/yui/grids/
 [2] http://www.djangoproject.com/documentation/newforms/

'''

__version__ = "1.0"
__author__ = "Christian Joergensen <christian.joergensen@gmta.info>"

from wtform.forms import *
