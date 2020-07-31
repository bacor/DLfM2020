import hashlib
import os 

_CUR_DIR = os.path.dirname(__file__)
_ROOT_DIR = os.path.abspath(os.path.join(_CUR_DIR, os.path.pardir))

def relpath(path, start=_ROOT_DIR):
    return os.path.relpath(path, start=start)

def md5checksum(path):
    """Return an md5 checksum of a given file"""
    hash_md5 = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()