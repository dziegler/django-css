Django css
=================

Django-css is a fork of django_compressor_ that makes it easy to use CSS compilers with your Django projects. CSS compilers extend CSS syntax to include more powerful features such as variables and nested blocks, and pretty much rock_ all around. Django-css can currently be used with any CSS compiler that can be called from the command line, such as HSS_, Sass_, CleverCSS_, or LESS_.

.. _rock: http://blog.davidziegler.net/post/92203003/css-compilers-rock
.. _HSS: http://ncannasse.fr/projects/hss 
.. _Sass: http://haml.hamptoncatlin.com/docs/rdoc/classes/Sass.html
.. _CleverCSS: http://github.com/dziegler/clevercss/tree/master 
.. _LESS: http://lesscss.org/
.. _django_compressor: http://github.com/mintchaos/django_compressor/tree/master 

Thanks to django_compressor, django-css will also version and compress linked and inline javascript or CSS into a single cached file. These cached files will get served through whatever frontend server you use for serving static files, because serving static files through Django is just silly.

Note: The pypi version of CleverCSS is buggy and will not work with django-css. Use the updated version on github: http://github.com/dziegler/clevercss/tree/master 

Installation
************

Add ``compressor`` to INSTALLED_APPS. You should also enable some type of caching backend such as memcached, e.g. ``CACHE_BACKEND = 'memcached://127.0.0.1:11211/'``. Don't worry, your static files are not being served through Django. The only thing stored in cache is the path to the static file.

Usage
*****

Syntax::

    {% load compress %}
    {% compress <js/css> %}
    <html of inline or linked JS/CSS>
    {% endcompress %}

Examples::

    {% load compress %}
    {% compress css %}
    <link rel="stylesheet" href="/media/css/one.css" type="text/css" charset="utf-8">
    <link rel="stylesheet" href="/media/css/two.sass" type="text/css" charset="utf-8">
    {% endcompress %}

Which would be rendered like::

    <link rel="stylesheet" href="/media/CACHE/css/f7c661b7a124.css" type="text/css" media="all" charset="utf-8">

or::

    {% load compress %}
    {% compress js %}
    <script src="/media/js/one.js" type="text/javascript" charset="utf-8"></script>
    <script type="text/javascript" charset="utf-8">obj.value = "value";</script>
    {% endcompress %}

Which would be rendered like::

    <script type="text/javascript" src="/media/CACHE/js/3f33b9146e12.js" charset="utf-8"></script>

If you're using xhtml, you should use::

    {% load compress %}
    {% compress css xhtml %}
    <link rel="stylesheet" href="/media/css/one.css" type="text/css" charset="utf-8" />
    <link rel="stylesheet" href="/media/css/two.sass" type="text/css" charset="utf-8" />
    {% compress css %}

Which would be rendered like::

    <link rel="stylesheet" href="/media/CACHE/css/f7c661b7a124.css" type="text/css" media="all" charset="utf-8" />


Settings
********

`COMPILER_FORMATS` default: {}
  A dictionary specifying the compiler and arguments to associate with each extension. 


django-css will select which CSS compiler to use based off a file's extension. For example::

    COMPILER_FORMATS = {
        '.sass': {
            'binary_path':'sass',
            'arguments': '*.sass *.css' 
        },
        '.hss': {
            'binary_path':'/home/dziegler/hss',
            'arguments':'*.hss'
        },
        '.ccss': {
            'binary_path':'clevercss',
            'arguments': '*.ccss'
        },
    }


will use Sass to compile `*.sass` files, HSS to compile `*.hss` files, and clevercss to compile `*.ccss` files. `*.css` files will be treated like normal css files. 

binary_path is the path to the CSS compiler. In the above example, sass and clevercss are installed in my path, and   hss is located at /home/dziegler/hss.

arguments are arguments you would call in the command line to the compiler. The order and format of these will depend on the CSS compiler you use. Prior to compilation, * will be replaced with the name of your file to be compiled.

If this seems a little hacky, it's because I wanted to make it easy to use whatever CSS compiler you want with as little setup as possible. 


`COMPRESS` default: the opposite of `DEBUG`
  Boolean that decides if compression will happen.

`COMPRESS_CSS_FILTERS` default: []
  A list of filters that will be applied to CSS.

`COMPRESS_JS_FILTERS` default: ['compressor.filters.jsmin.JSMinFilter'])
  A list of filters that will be applied to javascript.

`COMPRESS_URL` default: `MEDIA_URL`
  Controls the URL that linked media will be read from and compressed media
  will be written to.

`COMPRESS_ROOT` default: `MEDIA_ROOT`
  Controls the absolute file path that linked media will be read from and
  compressed media will be written to.

`COMPRESS_OUTPUT_DIR` default: `"CACHE"`
  Controls the directory inside `COMPRESS_ROOT` that compressed files will
  be written to.


Notes
*****

All relative url() bits specified in linked CSS files are automatically
converted to absolute URLs while being processed. Any local absolute urls (those
starting with a '/') are left alone.

Stylesheets that are @import'd are not compressed into the main file. They are
left alone.

Set the media attribute as normal on your <style> and <link> elements and
the combined CSS will be wrapped in @media blocks as necessary.

Linked files must be on your COMPRESS_URL (which defaults to MEDIA_URL).
If DEBUG is true off-site files will throw exceptions. If DEBUG is false
they will be silently stripped.

CSS files are compiled only when needed, because it would be silly to re-compile on every page request. The way this works is that django-css looks at the time your css was last modified, and the time your CleverCSS, HSS, etc file was modified. If the modification time for the CleverCSS, HSS, etc file is after the css file's, then the css file gets re-compiled. 

If COMPRESS is False (defaults to the opposite of DEBUG) CSS files will still be compiled if needed, but files will not be compressed and versioned.

The pypi version of CleverCSS is buggy and will not work with django-css. Use the updated version on github: http://github.com/dziegler/clevercss/tree/master 

**Recommendations:**

* Use only relative or full domain absolute urls in your CSS files.
* Avoid @import! Simply list all your CSS files in the HTML, they'll be combined anyway.


Changes from 1.0.0, aka the version from google code
****************************************************

Django-css was previously using django-compress_ for versioning and compression, and it now uses django_compressor_. The main reasons being that with django_compressor, css/js files are included in the template itself, not in settings, and versioning is much cleaner. Version 2 requires much less setup and is easier to use, but is not compatible with version 1.

.. _django-compress: http://code.google.com/p/django-compress/
.. _django_compressor: http://github.com/mintchaos/django_compressor/tree/master 

Special thanks to Christian Metts and Andreas Pelme for all their hard work on django_compressor and django-compress.




Dependecies
***********

* BeautifulSoup