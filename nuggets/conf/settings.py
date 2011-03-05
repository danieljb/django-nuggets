
from django.conf import settings


CACHE_PREFIX = getattr(settings, 'CACHE_PREFIX', 'nugget_')