import os
import re
import subprocess
from BeautifulSoup import BeautifulSoup

from django import template
from django.conf import settings as django_settings
from django.template.loader import render_to_string

from compressor.conf import settings
from compressor import filters


register = template.Library()


class UncompressableFileError(Exception):
    pass

class PythonicParserNotFound(Exception):
    pass

def pythonic_parse(fancy_css, ext):
    """ Parses the css data with 'ext' handler
        It is supposed to be stated in form:
        COMPILER_FORMATS = {
            '.ccss': {
                'python':'clevercss.convert',
            },
        }"""
    pythoncmd = settings.COMPILER_FORMATS[ext].get('python')
    if not pythoncmd:
        raise PythonicParserNotFound
    module,func = pythoncmd.split('.')
    return getattr(__import__(module),func)(fancy_css)     


def get_hexdigest(plaintext):
    try:
        import hashlib
        return hashlib.sha1(plaintext).hexdigest()
    except ImportError:
        import sha
        return sha.new(plaintext).hexdigest()

def exe_exists(program):

    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True
    return False

class Compressor(object):

    def __init__(self, content, ouput_prefix="compressed", xhtml=False):
        self.content = content
        self.ouput_prefix = ouput_prefix
        self.split_content = []
        self.soup = BeautifulSoup(self.content)
        self.xhtml = xhtml

    def content_hash(self):
        """docstring for content_hash"""
        pass

    def split_contents(self):
        raise NotImplementedError('split_contents must be defined in a subclass')

    def get_filename(self, url):
        if not url.startswith(settings.MEDIA_URL):
            raise UncompressableFileError('"%s" is not in COMPRESS_URL ("%s") and can not be compressed' % (url, settings.MEDIA_URL))
        basename = url[len(settings.MEDIA_URL):]
        filename = os.path.join(settings.MEDIA_ROOT, basename)
        return filename

    @property
    def mtimes(self):
        return [os.path.getmtime(h['filename']) for h in self.split_contents() if h.has_key('filename')]

    @property
    def cachekey(self):
        cachebits = [self.content]
        cachebits.extend([str(m) for m in self.mtimes])
        cachestr = "".join(cachebits)
        return "django_compressor.%s" % get_hexdigest(cachestr)[:12]

    @property
    def hunks(self):
        """ Returns a list of processed data
        """
        if getattr(self, '_hunks', ''):
            return self._hunks
            
        self._hunks = []
        for item in self.split_contents():
            filename = item.get('filename')
            data     = item.get('data')
            if not data:
                data = open(filename, 'rb').read()
            if self.filters:                    
                data = self.filter(data, 'input', **item)
            self._hunks.append(data)
                    
        return self._hunks

    def concat(self):
        return "\n".join(self.hunks)

    def filter(self, content, method, **kwargs):
        content = content
        for f in self.filters:
            filter = getattr(filters.get_class(f)(content, filter_type=self.type), method)
            try:
                if callable(filter):
                    content = filter(**kwargs)
            except NotImplementedError:
                pass
        return str(content)

    @property
    def combined(self):
        if getattr(self, '_output', ''):
            return self._output
        output = self.concat()
        filter_method = getattr(self, 'filter_method', None)
        if self.filters:
            output = self.filter(output, 'output')
        self._output = output
        return self._output

    @property
    def hash(self):
        return get_hexdigest(self.combined)[:12]

    @property
    def new_filepath(self):
        filename = "".join([self.hash, self.extension])
        filepath = "%s/%s/%s" % (settings.OUTPUT_DIR.strip('/'), self.ouput_prefix, filename)
        return filepath

    def save_file(self):
        filename = "%s/%s" % (settings.MEDIA_ROOT.rstrip('/'), self.new_filepath)
        if os.path.exists(filename):
            return False
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        fd = open(filename, 'wb+')
        fd.write(self.combined)
        fd.close()
        return True

    def return_compiled_content(self, content):
        if self.type != 'css':
            return content
        if not self.split_content:
            self.split_contents()
        
        if self.xhtml:
            return os.linesep.join([unicode(i['elem']) for i in self.split_content])
        else:
            return os.linesep.join([re.sub("\s?/>",">",unicode(i['elem'])) for i in self.split_content]) 
        
    def output(self):
        if not settings.COMPRESS:
            return self.return_compiled_content(self.content)
        url = "%s/%s" % (settings.MEDIA_URL.rstrip('/'), self.new_filepath)
        self.save_file()
        context = getattr(self, 'extra_context', {})
        context['url'] = url
        context['xhtml'] = self.xhtml
        return render_to_string(self.template_name, context)


class CssCompressor(Compressor):

    def __init__(self, content, ouput_prefix="css", xhtml=False):
        self.extension = ".css"
        self.template_name = "compressor/css.html"
        self.filters = ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.css_default.CssMediaFilter']
        self.filters.extend(settings.COMPRESS_CSS_FILTERS)
        self.type = 'css'
        super(CssCompressor, self).__init__(content, ouput_prefix, xhtml)
        
    def compile(self,filename,compiler):
        """ Runs compiler on given file. 
            Results are expected to appear nearby, same name, .css extension """
        try:
            bin = compiler['binary_path']
        except:
            raise Exception("Path to CSS compiler must be included in COMPILER_FORMATS")
        arguments = compiler.get('arguments','').replace("*",filename)
        command = '%s %s' % (bin, arguments)
        p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if p.wait() != 0:
            err = p.stderr.read()
            p.stderr.close()
            if not err:
                err = 'Invalid command to CSS compiler: %s' % command
            raise Exception(err)
    
    
    def split_contents(self):
        """ Iterates over the elements in the block """
        if self.split_content:
            return self.split_content
        split = self.soup.findAll({'link' : True, 'style' : True})
        for elem in split:
            if elem.name == 'link' and elem['rel'] == 'stylesheet':
                filename = self.get_filename(elem['href'])
                path, ext = os.path.splitext(filename)
                if ext in settings.COMPILER_FORMATS.keys():
                    # that thing can be compiled
                
                    try:
                        css = pythonic_parse(open(filename).read(), ext)
                        self.split_content.append({'data': css, 'elem': elem, 'filename': filename})
                        continue
                    except PythonicParserNotFound:
                        pass
                        
                    # let's run binary    
                    if self.recompile(filename):
                        self.compile(path,settings.COMPILER_FORMATS[ext])
                    basename = os.path.splitext(os.path.basename(filename))[0]
                    elem = BeautifulSoup(re.sub(basename+ext,basename+'.css',unicode(elem)))
                    filename = path + '.css'
                try:
                    self.split_content.append({'filename': filename, 'elem': elem})
                except UncompressableFileError:
                    if django_settings.DEBUG:
                        raise
            if elem.name == 'style':
                data = elem.string            
                elem_type = elem.get('type', '').lower()
                if elem_type and elem_type != "text/css":
                    # it is to be preprocessed
                    # TODO: that dot-adding stuff looks strange.
                    # do we really need dot in COMPILER_FORMATS?
                    ext = '.'+elem_type.split('/')[1]
                    data = pythonic_parse(data, ext)
                    
                self.split_content.append({'data': data, 'elem': elem})
                
        return self.split_content
    
    @staticmethod
    def recompile(filename):
        """ Needed for CCS Compilers, 
            returns True when file needs recompiling """
        path, ext = os.path.splitext(filename)
        compiled_filename = path + '.css'
        if not os.path.exists(compiled_filename):
            return True
        else:
            if os.path.getmtime(filename) > os.path.getmtime(compiled_filename):
                return True
            else:
                return False

class JsCompressor(Compressor):

    def __init__(self, content, ouput_prefix="js", xhtml=False):
        self.extension = ".js"
        self.template_name = "compressor/js.html"
        self.filters = settings.COMPRESS_JS_FILTERS
        self.type = 'js'
        super(JsCompressor, self).__init__(content, ouput_prefix, xhtml)

    def split_contents(self):
        if self.split_content:
            return self.split_content
        split = self.soup.findAll('script')
        for elem in split:
            if elem.has_key('src'):
                try:
                    self.split_content.append(
                        {'filename':self.get_filename(elem['src']), 'elem':elem})
                except UncompressableFileError:
                    if django_settings.DEBUG:
                        raise
            else:
                self.split_content.append({'data':elem.string, 'elem': elem})
        return self.split_content
