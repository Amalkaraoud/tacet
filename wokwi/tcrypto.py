"""TACET - primitives cryptographiques (portables CPython / MicroPython).

Seul hashlib.sha256 est requis : HMAC-SHA256 (RFC 2104) est reconstruit ici car
le module `hmac` n'existe pas dans MicroPython. Le chiffrement est un flux
PRF-CTR (HMAC-SHA256 en mode compteur), construction standard et sans dependance
a cryptolib.
"""
import hashlib

try:
    import os
    urandom = os.urandom
except ImportError:  # pragma: no cover
    urandom = None

BLOCK = 64


def sha256(data):
    return hashlib.sha256(data).digest()


def hmac_sha256(key, msg):
    if len(key) > BLOCK:
        key = sha256(key)
    key = key + bytes(BLOCK - len(key))
    ipad = bytes([k ^ 0x36 for k in key])
    opad = bytes([k ^ 0x5C for k in key])
    return sha256(opad + sha256(ipad + msg))


def ct_equal(a, b):
    """Comparaison a temps constant (autant que possible en Python)."""
    if len(a) != len(b):
        return False
    r = 0
    for x, y in zip(a, b):
        r |= x ^ y
    return r == 0


def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])


def u32(n):
    return bytes([(n >> 24) & 255, (n >> 16) & 255, (n >> 8) & 255, n & 255])


def keystream(kenc, ctr, n, label=b"S"):
    out = b""
    i = 0
    while len(out) < n:
        out += hmac_sha256(kenc, label + u32(ctr) + bytes([i]))
        i += 1
    return out[:n]


def derive(master, label):
    return hmac_sha256(master, label)
