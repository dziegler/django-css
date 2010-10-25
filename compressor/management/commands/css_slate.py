import os
from optparse import make_option, OptionError
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured

from compressor import CssCompressor

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--chown', action='store', dest='chown', help='Change ownership of generated CSS files to specified user, instead of changing permissions. Can be combined with chgrp.'),
        make_option('--chgrp', action='store', dest='chgrp', help='Change ownership of generated CSS files to specified group, instead of changing permissions. Can be combined with chown.'),
        )
    help = 'Compile CSS files and make the generated files writeable for future compilations.'

    def handle(self, *args, **options):
        # Passing -1 to chown leaves the ownership unchanged, hence the default
        uid = -1
        gid = -1
        chown = options.get('chown', None)
        chgrp = options.get('chgrp', None)
        verbosity = int(options.get('verbosity', 1))
        if chown or chgrp:
            # pwd is only available on POSIX-compliant systems
            try:
                import pwd
            except ImportError:
                raise OptionError('Ownership changes are not supported by your operating system.', '--chown')
            try:
                if chown:
                    uid = pwd.getpwnam(chown).pw_uid
                if chgrp:
                    gid = pwd.getpwnam(chgrp).pw_gid
            except (KeyError, TypeError):
                raise OptionError('The specified username "%s" does not exist or is invalid.' % chown, '--chown')
        if not hasattr(os, 'chmod'):
            raise NotImplementedError('Permission changes are not supported by your operating system')
        if not hasattr(settings, 'COMPILER_FORMATS') or not settings.COMPILER_FORMATS:
            raise ImproperlyConfigured('COMPILER_FORMATS not specified in settings.')
        
        if verbosity:
            print 'Looking for slateable CSS files in %s' % settings.MEDIA_ROOT
        
        # Find all files in MEDIA_ROOT that have a COMPILER_FORMATS-supported
        # extension, and return them as a list of (full path to file without
        # extension, extension) tuples.
        files_to_compile = []
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for _dir in dirs:
                for _file in files:
                    name, ext = os.path.splitext(_file)
                    if ext in settings.COMPILER_FORMATS:
                        files_to_compile.append((os.path.join(root, name), ext))
            
        if verbosity:
            print 'Found %s files to be slated...' % len(files_to_compile)
        
        for filename, extension in files_to_compile:
            if verbosity > 1:
                print 'Compiling %s%s' % (filename, extension)
            CssCompressor.compile(filename, settings.COMPILER_FORMATS[extension])
            css_file = '%s.css' % filename
            if chown or chgrp:
                # Change file ownership to specified group and/or user
                os.chown(css_file, uid, gid)
                # Make sure owner can write and everyone can read
                os.chmod(css_file, 0644)
            else:
                # Allow everyone to read and write
                os.chmod(css_file, 0666)
        
        if verbosity:
            print 'Finished slating.'