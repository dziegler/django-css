from django.utils.encoding import smart_str
from django.utils.hashcompat import sha_constructor

def get_hexdigest(plaintext):
    p = smart_str(plaintext)
    return sha_constructor(p).hexdigest()
