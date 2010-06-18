from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


MEDIA_URL = getattr(settings, 'COMPRESS_URL', settings.MEDIA_URL)
MEDIA_ROOT = getattr(settings, 'COMPRESS_ROOT', settings.MEDIA_ROOT)
OUTPUT_DIR = getattr(settings, 'COMPRESS_OUTPUT_DIR', 'CACHE')

COMPRESS = getattr(settings, 'COMPRESS', not settings.DEBUG)
ABSOLUTE_CSS_URLS = getattr(settings, 'COMPRESS_ABSOLUTE_CSS_URLS', True)
COMPRESS_CSS_FILTERS = list(getattr(settings, 'COMPRESS_CSS_FILTERS', []))
COMPRESS_JS_FILTERS = list(getattr(settings, 'COMPRESS_JS_FILTERS', ['compressor.filters.jsmin.JSMinFilter']))
COMPILER_FORMATS = getattr(settings, 'COMPILER_FORMATS', {})

if ABSOLUTE_CSS_URLS and 'compressor.filters.css_default.CssAbsoluteFilter' not in COMPRESS_CSS_FILTERS:
    COMPRESS_CSS_FILTERS.insert(0, 'compressor.filters.css_default.CssAbsoluteFilter')
