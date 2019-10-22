from .base import *
from .local import *
import os
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = True
TEMPLATES[0]['OPTIONS']['loaders'] = [
  ['django.template.loaders.cached.Loader', [
     'django.template.loaders.filesystem.Loader',
     'django.template.loaders.app_directories.Loader', ]
  , ]
, ]


CACHES = {
  'default': {
     'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
     'LOCATION': ''
  }
}
