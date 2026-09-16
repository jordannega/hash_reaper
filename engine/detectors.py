"""Hash type auto-detection by regex + length."""
import re

# (name, regex, description)
HASH_SIGNATURES = [
    ("md5",           r"^[a-f0-9]{32}$",                  "MD5 (unsalted)"),
    ("md5",           r"^[a-f0-9]{32}:[a-f0-9]+$",        "MD5 (salted, $pass:$salt)"),
    ("sha1",          r"^[a-f0-9]{40}$",                  "SHA-1"),
    ("sha224",        r"^[a-f0-9]{56}$",                  "SHA-224"),
    ("sha256",        r"^[a-f0-9]{64}$",                  "SHA-256"),
    ("sha384",        r"^[a-f0-9]{96}$",                  "SHA-384"),
    ("sha512",        r"^[a-f0-9]{128}$",                 "SHA-512"),
    ("ntlm",          r"^[a-f0-9]{32}$",                  "NTLM (same length as MD5)"),
    ("mysql41",       r"^\*[A-F0-9]{40}$",                "MySQL 4.1+"),
    ("bcrypt",        r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$", "bcrypt"),
    ("sha512crypt",   r"^\$6\$[^\$]+\$[./A-Za-z0-9]{86}$", "SHA-512 crypt"),
    ("sha256crypt",   r"^\$5\$[^\$]+\$[./A-Za-z0-9]{43}$", "SHA-256 crypt"),
    ("md5crypt",      r"^\$1\$[^\$]+\$[./A-Za-z0-9]{22}$", "MD5 crypt"),
    ("argon2",        r"^\$argon2(i|d|id)\$",             "Argon2"),
    ("scrypt",        r"^\$scrypt\$",                     "scrypt"),
    ("phpass",        r"^\$P\$[./A-Za-z0-9]{31}$",        "phpass (WordPress)"),
    ("whirlpool",     r"^[a-f0-9]{128}$",                 "Whirlpool (also 128 hex)"),
    ("ripemd160",     r"^[a-f0-9]{40}$",                  "RIPEMD-160 (same as SHA-1)"),
]


def detect_hash(hash_str: str):
    """Return (possible_types, description)."""
    h = hash_str.strip()
    matches = []
    for name, pattern, desc in HASH_SIGNATURES:
        if re.match(pattern, h):
            matches.append((name, desc))
    return matches