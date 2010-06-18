from django import template
from django.core.cache import cache

try:
    from django.contrib.sites.models import Site
    DOMAIN = Site.objects.get_current().domain
except:
    DOMAIN = ''
    
from compressor import CssCompressor, JsCompressor
from compressor.conf import settings
from time import sleep

register = template.Library()

class CompressorNode(template.Node):
    def __init__(self, nodelist, kind=None, xhtml=False):
        self.nodelist = nodelist
        self.kind = kind
        self.xhtml = xhtml

    def render(self, context):
        content = self.nodelist.render(context)
        if 'MEDIA_URL' in context:
            media_url = context['MEDIA_URL']
        else:
            media_url = settings.MEDIA_URL
        if self.kind == 'css':
            compressor = CssCompressor(content, xhtml=self.xhtml, media_url=media_url)
        if self.kind == 'js':
            compressor = JsCompressor(content, xhtml=self.xhtml, media_url=media_url)
        in_cache = cache.get(compressor.cachekey)
        if in_cache:
            return in_cache
        else:
            # do this to prevent dog piling
            in_progress_key = '%s.django_css.in_progress.%s' % (DOMAIN, compressor.cachekey)
            added_to_cache = cache.add(in_progress_key, True, 300)
            if added_to_cache:
                output = compressor.output()
                cache.set(compressor.cachekey, output, 2591000) # rebuilds the cache every 30 days if nothing has changed.
                cache.set(in_progress_key, False, 300)
            else:
                while cache.get(in_progress_key):
                    sleep(0.1)
                output = cache.get(compressor.cachekey)
            return output

@register.tag
def compress(parser, token):
    """
    Compresses linked and inline javascript or CSS into a single cached file.

    Syntax::

        {% compress <js/css> %}
        <html of inline or linked JS/CSS>
        {% endcompress %}

    Examples::

        {% compress css %}
        <link rel="stylesheet" href="/media/css/one.css" type="text/css">
        <style type="text/css">p { border:5px solid green;}</style>
        <link rel="stylesheet" href="/media/css/two.css" type="text/css">
        {% endcompress %}

    Which would be rendered something like::

        <link rel="stylesheet" href="/media/CACHE/css/f7c661b7a124.css" type="text/css">

    or::

        {% compress js %}
        <script src="/media/js/one.js" type="text/javascript"></script>
        <script type="text/javascript">obj.value = "value";</script>
        {% endcompress %}

    Which would be rendered something like::

        <script type="text/javascript" src="/media/CACHE/js/3f33b9146e12.js"></script>

    Linked files must be on your COMPRESS_URL (which defaults to MEDIA_URL).
    If DEBUG is true off-site files will throw exceptions. If DEBUG is false
    they will be silently stripped.
    """

    nodelist = parser.parse(('endcompress',))
    parser.delete_first_token()

    args = token.split_contents()

    if not (len(args) == 2 or len(args) == 3):
        raise template.TemplateSyntaxError("%r tag requires either 1, 3 or 5 arguments." % args[0])

    kind = args[1]
    if kind not in ('css', 'js'):
        raise template.TemplateSyntaxError("%r's argument must be 'js' or 'css'." % args[0])
    
    try:
        xhtml = args[2] == "xhtml"
    except:
        xhtml = False
    return CompressorNode(nodelist, kind, xhtml)
