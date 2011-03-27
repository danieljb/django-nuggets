
from django.core.cache import cache
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from nuggets.conf import settings


# Create your models here.

class Nugget(models.Model):

    key = models.SlugField(
        _('Key'),
        max_length=50,
        null=False,
        unique=True,
        help_text=_('An identifier key as reference to this nugget.'),)

    def save(self, *args, **kwargs):
        self.key = slugify(self.key)
        super(Nugget, self).save(*args, **kwargs)

        cache.delete('{prefix}{key}'.format(prefix=settings.CACHE_PREFIX,
                                            key=self.key,))

    def __unicode__(self):
        return "%s" % self.key

    class Meta:
        abstract = True
