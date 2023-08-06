import hashlib


def content_md5(content):
    hash_md5 = hashlib.md5(content)
    return hash_md5.hexdigest()
