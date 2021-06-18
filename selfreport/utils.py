import base64
import rsa


def rsa_encrypt(pubkey, content):
    """
    rsa encrypt
    :param pubkey: openssl PEM PKCS#1
    :param content: bytes to encrypt
    :return: base64 encoded crypto
    """
    assert isinstance(content, bytes)
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(pubkey)
    crypto = rsa.encrypt(content, pubkey)
    return base64.b64encode(crypto).decode()


def substring(s, start, end):
    """
    Example:
    >>> substring("ba123b", "a", "b")
    '123'

    :param s: string to manipulate
    :param start: start of substring
    :param end: end of substring
    :return: substring (without start and end)
    """
    i = s.index(start) + len(start)
    s = s[i:]
    i = s.index(end)
    s = s[:i]
    return s
