import os
from django.utils.encoding import smart_str
from django.utils.hashcompat import sha_constructor
from compressor.conf import settings

def get_hexdigest(plaintext):
    p = smart_str(plaintext)
    return sha_constructor(p).hexdigest()

def get_file_hash(filename):
    media_root = os.path.abspath(settings.MEDIA_ROOT)
    if not filename.startswith(media_root):
        filename = os.path.join(media_root, filename)
    try:
        mtime = os.path.getmtime(filename)
        return get_hexdigest(str(int(mtime)))[:12]
    except OSError:
        return None
    