import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')

setup(
    name = "django-css",
    version = "2.1.5",
    description='django-css provides an easy way to use CSS compilers with Django projects, and an automated system for compressing CSS and JavaScript files',
    url = 'http://github.com/dziegler/django-css',
    license = 'BSD',
    long_description=README,

    author = 'David Ziegler',
    author_email = 'david.ziegler@gmail.com',
    packages = [
        'compressor',
        'compressor.conf',
        'compressor.filters',
        'compressor.filters.jsmin',
        'compressor.templatetags',
    ],
    package_data = {'compressor': [
        'templates/compressor/js.html',
        'templates/compressor/css.html'
    ],},
    requires = [
        'BeautifulSoup',
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
