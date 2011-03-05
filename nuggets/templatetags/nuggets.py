from __future__ import absolute_import

from django.core.cache import cache
from django.db.models.loading import get_model
from django.template import Library, Node, TemplateSyntaxError, \
    TemplateDoesNotExist, Variable, VariableDoesNotExist
from django.template.loader import select_template

from nuggets.conf import settings as nugget_settings
from nuggets.models import Nugget


register = Library()


# Usage:
# {% get_nugget "key" for "applabel.modellabel" with cache_time="3600"
#    as "context_variable" %}
#
# or
#
# {% render_nugget "key" for "applabel.modellabel" with
#    template="nuggets/model_nugget.html" and
#    template_context_variable="nugget" and cache_time="3600" as
#    "context_variable" %}

def parse_arguments(token, accepted_keys):
    tokens = token.split_contents()
    tag_def = {'context_variable': None,}

    if len(tokens) > 3 and tokens[2] == 'for':
        tag_def.update({
            'tag_name': tokens[0],
            'nugget_key': tokens[1],
            'app_model': tokens[3],
        })
        tokens = tokens[4:]
    else:
        raise TemplateSyntaxError(
            "{0} requires at least one argument defining"
            " which app and model to use as nugget".format(tag_name))

    if len(tokens) > 1 and tokens[-2] == 'as':
        tag_def['context_variable'] = tokens[-1]
        tokens = tokens[:-2]

    args = {}
    if len(tokens) > 1:
        for i, argument in enumerate(tokens):
            if i == 0:
                if argument != 'with':
                    raise TemplateSyntaxError(
                        "{0} tag requires parameters specified using"
                        " the \"with\" keyword".format(tokens['tag_name']))
            elif not i % 2:
                if argument != 'and':
                    raise TemplateSyntaxError(
                        "{0} tag parameters have to be concatenated"
                        " with \"and\" keyword".format(tokens['tag_name']))
            else:
                key, value = argument.split('=')
                if key not in accepted_keys:
                    raise TemplateSyntaxError(
                        "{0} tag does not accept the {1} keyword".format(
                            tag_def['tag_name'],
                            key))
                args.update({key.encode('ascii'): value})

    tag_def.update({'arguments': args})
    return tag_def


def get_nugget(parser, token):
    ACCEPTED_KEYS = ('cache_time',)
    tokens = parse_arguments(token, ACCEPTED_KEYS)
    tokens.pop('tag_name')

    return NuggetNode(**tokens)


def render_nugget(parser, token):
    ACCEPTED_KEYS = ('cache_time',
                     'template_path',
                     'template_context_variable')

    tokens = parse_arguments(token, ACCEPTED_KEYS)
    tokens.pop('tag_name')

    return NuggetNode(render_nugget=True, **tokens)


class NuggetNode(Node):

    def __init__(self, app_model=None, nugget_key=None,
        context_variable=None, arguments=None, render_nugget=False):

        self.app_model = app_model
        self.nugget_key = nugget_key
        self.context_variable = context_variable
        self.arguments = arguments
        self.render_nugget = render_nugget

    def resolve(self, var, context):
        if isinstance(var, int):
            return var
        if var[0] in ('"', "'") and var[-1] == var[0]:
            return var[1:-1]
        try:
            return Variable(var).resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError(
                "Variable {0} does not exist".format(var))

    def get_model(self, modelname, context):
        applabel, modellabel = self.resolve(modelname, context).split(".")
        related_model = get_model(applabel, modellabel)
        return related_model

    def get_content_object(self, related_model, nugget_key):
        if not issubclass(related_model, Nugget):
            raise TemplateSyntaxError(
                "Model {0} must be subclass of Nugget".format(related_model))
        try:
            return related_model._default_manager.get(key=nugget_key)
        except related_model.DoesNotExist:
            raise TemplateSyntaxError(
                "Could not resolve instance for model {0} with key {1}".format(
                    related_model, nugget_key))

    def render_to_template(self, content, context):
        template_context_variable = self.arguments.get(
                                        'template_context_variable')
        template_path = self.arguments.get('template_path')
        template_paths = []

        if template_path:
            template_paths.append(self.resolve(template_path, context))
        app, model = self.resolve(self.app_model, context).lower().split(".")
        template_paths.extend(['{0}/{1}_{2}.html'.format(app,
                                                         model,
                                                         self.nugget_key),
                               '{0}/{1}_nugget.html'.format(app, model)])

        try:
            t = select_template(template_paths)
        except TemplateDoesNotExist:
            raise TemplateSyntaxError(
                "Could not find template in {0}".format(template_paths))

        if template_context_variable:
            context[self.resolve(template_context_variable, context)] = content
        else:
            context['nugget'] = content
        return t.render(context)

    def render(self, context):
        self.nugget_key = self.resolve(self.nugget_key, context)
        cache_time = 0

        if 'cache_time' in self.arguments:
            cache_time = self.resolve(self.arguments.get('cache_time'),
                                      context)

        related_model = self.get_model(self.app_model, context)

        cache_key = '{prefix}{key}'.format(prefix=nugget_settings.CACHE_PREFIX,
                                           key=self.nugget_key)
        content = cache.get(cache_key)
        if content is None:
            content = self.get_content_object(related_model, self.nugget_key)
            cache.set(cache_key, content, int(cache_time))

        if self.render_nugget:
            content = self.render_to_template(content, context)
        if self.render_nugget and not self.context_variable:
            return content
        if self.context_variable:
            context[self.resolve(self.context_variable, context)] = content
        else:
            context['nugget_{0}'.format(self.nugget_key)] = content
        return ''


register.tag('get_nugget', get_nugget)
register.tag('render_nugget', render_nugget)
