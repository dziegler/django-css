import os, re
from textwrap import dedent

from django.template import Template, Context
from django.test import TestCase
from compressor import CssCompressor, JsCompressor, UncompressableFileError
from compressor.conf import settings
from django.conf import settings as django_settings

from BeautifulSoup import BeautifulSoup

class CompressorTestCase(TestCase):

    def setUp(self):
        settings.COMPRESS = True
        settings.COMPILER_FORMATS = {
            '.ccss': {
                'binary_path': 'python ' + os.path.join(django_settings.TEST_DIR,'clevercss.py'),
                'arguments': '*.ccss'
            },
            '.xcss': {
                'python':'clevercss.convert',
            },            
        }
        self.ccssFile = os.path.join(settings.MEDIA_ROOT, u'css/three.css')
        self.xcssFile = os.path.join(settings.MEDIA_ROOT, u'css/four.xcss')        
        self.css = dedent("""
        <link rel="stylesheet" href="/media/css/one.css" type="text/css">
        <style type="text/css">p { border:5px solid green;}</style>
        <link rel="stylesheet" href="/media/css/two.css" type="text/css">
        <link rel="stylesheet" href="/media/css/three.ccss" type="text/css">
        <link rel="stylesheet" href="/media/css/four.xcss" type="text/css">
        <style type="text/xcss">
        """)+ \
        '\n'.join((
        "small:\n  font-size:10px",
        '</style>\n<style type="xcss">',
        "h1:\n  font-weight:bold",
        "</style>"))

        self.cssNode = CssCompressor(self.css)

        self.js = """
        <script src="/media/js/one.js" type="text/javascript"></script>
        <script type="text/javascript">obj.value = "value";</script>
        """
        self.jsNode = JsCompressor(self.js)
    
    def test_get_filename(self):
        settings.COMPRESS_URL = '/static_test/'
        settings.COMPRESS_ROOT = os.path.join(os.path.dirname(__file__),'static_test_dir')
        path = os.path.join(settings.MEDIA_URL,'something.css')
        filename = self.cssNode.get_filename(path)
        self.assertEqual(filename,os.path.join(settings.MEDIA_ROOT,'something.css'))
        path = "http://something.com/static/something.css"
        self.assertRaises(UncompressableFileError, self.cssNode.get_filename,path)
        self.assertRaises(UncompressableFileError, self.jsNode.get_filename,path)
    
    def test_css_compiler_exists(self):
        settings.COMPILER_FORMATS = {
            '.ccss': {
                'binary_path': 'python ' + os.path.join(django_settings.TEST_DIR,'clevrcss.py'),
                'arguments': '*.ccss'
            },
        }            
        self.assertRaises(Exception, self.cssNode.output)

    def test_css_split(self):
        out = [
            {'filename': os.path.join(settings.MEDIA_ROOT, u'css/one.css'), 
                'elem': '<link rel="stylesheet" href="/media/css/one.css" type="text/css" />'},
            {'data': u'p { border:5px solid green;}', 
                'elem': '<style type="text/css">p { border:5px solid green;}</style>'},
            {'filename': os.path.join(settings.MEDIA_ROOT, u'css/two.css'), 
                'elem': '<link rel="stylesheet" href="/media/css/two.css" type="text/css" />'},
            {'filename': self.ccssFile, 
                'elem': '<link rel="stylesheet" href="/media/css/three.css" type="text/css" />'},
            {'filename': self.xcssFile, 
                'elem': '<link rel="stylesheet" href="/media/css/four.xcss" type="text/css" />',
                'data': u'p {\n  color: black;\n}'},
            {'data': u'small {\n  font-size: 10px;\n}',
                'elem': '<style type="text/xcss">\nsmall:\n  font-size:10px\n</style>'},
            {'data': u'h1 {\n  font-weight: bold;\n}',
                'elem': '<style type="xcss">\nh1:\n  font-weight:bold\n</style>'}
        ]
        split = self.cssNode.split_contents()
        for item in split:
            item['elem'] = str(item['elem'])        
        self.assertEqual(out, split)
        if os.path.exists(self.ccssFile):
            os.remove(self.ccssFile)

    def test_css_hunks(self):
        out = ['body { background:#990; }',
               'p { border:5px solid green;}', 
               'body { color:#fff; }', 
               'a {\n  color: #5c4032;\n}',
               'p {\n  color: black;\n}',
               'small {\n  font-size: 10px;\n}', 
               'h1 {\n  font-weight: bold;\n}'               
               ]
        self.assertEqual(out, self.cssNode.hunks)
        if os.path.exists(self.ccssFile):
            os.remove(self.ccssFile)

    def test_css_output(self):
        out = '\n'.join((
            'body { background:#990; }',
            'p { border:5px solid green;}',
            'body { color:#fff; }',
            'a {\n  color: #5c4032;\n}',
            'p {\n  color: black;\n}',
            'small {\n  font-size: 10px;\n}',
            'h1 {\n  font-weight: bold;\n}',
            ))
        self.assertEqual(out, self.cssNode.combined)
        if os.path.exists(self.ccssFile):
            os.remove(self.ccssFile)

    def test_css_mtimes(self):
        is_date = re.compile(r'^\d{10}\.\d$')
        for date in self.cssNode.mtimes:
            self.assert_(is_date.match(str(date)), "mtimes is returning something that doesn't look like a date")
        if os.path.exists(self.ccssFile):
            os.remove(self.ccssFile)
            
    def test_css_return_if_off(self):
        settings.COMPRESS = False
        # TODO: The processor when off replaces all compileable formats with css files
        # Not sure if that is what one would expect from turned off thing
        css_expected = self.css.strip().replace('three.ccss', 'three.css')
        self.assertEqual(css_expected, self.cssNode.output().strip())
        if os.path.exists(self.ccssFile):
            os.remove(self.ccssFile)
            
    def test_cachekey(self):
        is_cachekey = re.compile(r'django_compressor\.\w{12}')
        self.assert_(is_cachekey.match(self.cssNode.cachekey), "cachekey is returning something that doesn't look like r'django_compressor\.\w{12}'")
        if os.path.exists(self.ccssFile):
            os.remove(self.ccssFile)
            
    def test_css_hash(self):
        self.assertEqual('82250ce4120c', self.cssNode.hash)
        if os.path.exists(self.ccssFile):
            os.remove(self.ccssFile)
            
    def test_css_return_if_on(self):
        output = u'<link rel="stylesheet" href="/media/CACHE/css/82250ce4120c.css" type="text/css">'
        self.assertEqual(output.strip(), self.cssNode.output().strip())
        if os.path.exists(self.ccssFile):
            os.remove(self.ccssFile)

    def test_js_split(self):
        out = [
            {'filename': os.path.join(settings.MEDIA_ROOT, u'js/one.js'), 
             'elem':'<script src="/media/js/one.js" type="text/javascript"></script>'},
            {'data': u'obj.value = "value";', 
             'elem': '<script type="text/javascript">obj.value = "value";</script>'},
         ]
        split = self.jsNode.split_contents()
        for item in split:
            item['elem'] = str(item['elem'])
        self.assertEqual(out, split)
        
    def test_js_hunks(self):
        out = ['obj = {};', u'obj.value = "value";']
        self.assertEqual(out, self.jsNode.hunks)

    def test_js_concat(self):
        out = u'obj = {};\nobj.value = "value";'
        self.assertEqual(out, self.jsNode.concat())

    def test_js_output(self):
        out = u'obj={};obj.value="value";'
        self.assertEqual(out, self.jsNode.combined)

    def test_js_return_if_off(self):
        settings.COMPRESS = False
        self.assertEqual(self.js, self.jsNode.output())

    def test_js_return_if_on(self):
        output = u'<script type="text/javascript" src="/media/CACHE/js/3f33b9146e12.js"></script>\n'
        self.assertEqual(output, self.jsNode.output())


class CssAbsolutizingTestCase(TestCase):
    def setUp(self):
        settings.COMPRESS = True
        settings.MEDIA_URL = '/media/'
        self.css = """
        <link rel="stylesheet" href="/media/css/url/url1.css" type="text/css">
        <link rel="stylesheet" href="/media/css/url/2/url2.css" type="text/css">
        """
        self.cssNode = CssCompressor(self.css)

    def test_css_absolute_filter(self):
        from compressor.filters.css_default import CssAbsoluteFilter
        filename = os.path.join(settings.MEDIA_ROOT, 'css/url/test.css')
        content = "p { background: url('../../images/image.gif') }"
        output = "p { background: url('%simages/image.gif') }" % settings.MEDIA_URL
        filter = CssAbsoluteFilter(content)
        self.assertEqual(output, filter.input(filename=filename))
        settings.MEDIA_URL = 'http://media.example.com/'
        filename = os.path.join(settings.MEDIA_ROOT, 'css/url/test.css')
        output = "p { background: url('%simages/image.gif') }" % settings.MEDIA_URL
        self.assertEqual(output, filter.input(filename=filename))

    def test_css_hunks(self):
        out = [u"p { background: url('/media/images/test.png'); }\np { background: url('/media/images/test.png'); }\np { background: url('/media/images/test.png'); }\np { background: url('/media/images/test.png'); }\n",
               u"p { background: url('/media/images/test.png'); }\np { background: url('/media/images/test.png'); }\np { background: url('/media/images/test.png'); }\np { background: url('/media/images/test.png'); }\n",
               ]
        self.assertEqual(out, self.cssNode.hunks)


class CssMediaTestCase(TestCase):
    def setUp(self):
        self.css = """
        <link rel="stylesheet" href="/media/css/one.css" type="text/css" media="screen">
        <style type="text/css" media="print">p { border:5px solid green;}</style>
        <link rel="stylesheet" href="/media/css/two.css" type="text/css" media="all">
        """
        self.cssNode = CssCompressor(self.css)

    def test_css_output(self):
        out = u'@media screen {body { background:#990; }}\n@media print {p { border:5px solid green;}}\n@media all {body { color:#fff; }}'
        self.assertEqual(out, self.cssNode.combined)


class TemplatetagTestCase(TestCase):
    def render(self, template_string, context_dict=None):
        """A shortcut for testing template output."""
        if context_dict is None:
            context_dict = {}

        c = Context(context_dict)
        t = Template(template_string)
        return t.render(c).strip()

    def test_css_tag(self):
        template = u"""{% load compress %}{% compress css %}
        <link rel="stylesheet" href="{{ MEDIA_URL }}css/one.css" type="text/css">
        <style type="text/css">p { border:5px solid green;}</style>
        <link rel="stylesheet" href="{{ MEDIA_URL }}css/two.css" type="text/css">
        {% endcompress %}
        """
        context = { 'MEDIA_URL': settings.MEDIA_URL }
        out = u'<link rel="stylesheet" href="/media/CACHE/css/f7c661b7a124.css" type="text/css">'
        self.assertEqual(out, self.render(template, context))

    def test_js_tag(self):
        template = u"""{% load compress %}{% compress js %}
        <script src="{{ MEDIA_URL }}js/one.js" type="text/javascript"></script>
        <script type="text/javascript">obj.value = "value";</script>
        {% endcompress %}
        """
        context = { 'MEDIA_URL': settings.MEDIA_URL }
        out = u'<script type="text/javascript" src="/media/CACHE/js/3f33b9146e12.js"></script>'
        self.assertEqual(out, self.render(template, context))

