# Django Nuggets #

A Django app similar to django-flatblocks or django-chunks to add dynamic snippets of content to a django website. 

# Installation #

Install using pip:

    pip install -e git+https://https://github.com/danieljb/django-nuggets

# Usage #

Django Nuggets comes with two template tags:

 - get_nugget
 - render_nugget

While `get_nugget` just writes the nugget model into the context `render_nugget` renders the nugget model into a template.

### `get_nugget` ###

    {% get_nugget "key" for "applabel.modellabel" with cache_time="3600" as "context_variable" %}

### `render_nugget` ###

    {% render_nugget "key" for "applabel.modellabel" with template_path="nuggets/model_nugget.html" and template_context_variable="nugget" and cache_time="3600" as "context_variable" %}

# Example Usage #

Install django-nuggets and create a nugget model:

    # example_app/models.py

    from django.db import models
    from nuggets.models import Nugget

    class Text(Nugget):
        content = models.TextField()

Register model for use in django’s admin interface:

    # example_app/admin.py

    from django.contrib import admin
    from example_app.models import Text

    admin.site.register(Text)

If you want the model rendered as template instead of requesting a context variable create:

    # templates/example_app/text_nugget.html

    <p>{{ nugget.content }}</p>

*Note: you can overwrite both, the template_context_variable as well as the template_path*

Create a Nugget in your admin interface (e.g. "about"). Now we can load and use the nuggets in our templates like this:

    {% load nuggets %}
    <h1>My Site</h1>
    <h4>About</h4>
    <p>{% render_nugget "about" for "example_app.text" %}</p>

If you only want to retrieve a context variable use it like this:

    {% load nuggets %}
    {% get_nugget "about" for "example_app.text" as "about_text" %}
    <h1>My Site</h1>
    <h4>About</h4>
    <p>{{ about_text }}</p>


# Copyright #

Django Nuggets is distributed under GNU General Public License. 
You should have received a copy of the GNU General Public License along 
with Django Nuggets. 
If not, see <http://www.gnu.org/licenses/>.

Copyright (c) 2011, Daniel J. Becker
