"""Attack strategies: dictionary, mask, brute, hybrid, combinator."""
import itertools
import string
from pathlib import Path
from .rules import RuleEngine


def dict_attack(wordlist: Path, rules: RuleEngine, use_mutations: bool):
    """Yield candidates from wordlist (optionally mutated)."""
    with wordlist.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            word = line.strip()
            if not word:
                continue
            if use_mutations:
                yield from rules.mutate(word)
            else:
                yield word


def mask_attack(mask: str):
    """
    Yield candidates matching a mask.
    ?l = lowercase, ?u = uppercase, ?d = digit, ?s = symbol, ?a = all
    ?1, ?2 = custom sets (skipped in this minimal version)
    """
    charset = {
        "l": string.ascii_lowercase,
        "u": string.ascii_uppercase,
        "d": string.digits,
        "s": "!@#$%^&*()-_=+[]{};:,.<>/?",
    }
    charset["a"] = charset["l"] + charset["u"] + charset["d"] + charset["s"]

    # Parse mask: "?u?l?l?l?d?d" → list of charsets
    pools = []
    i = 0
    while i < len(mask):
        if mask[i] == "?" and i + 1 < len(mask):
            pools.append(charset.get(mask[i + 1], mask[i + 1]))
            i += 2
        else:
            pools.append(mask[i])
            i += 1

    for combo in itertools.product(*pools):
        yield "".join(combo)


def brute_attack(charset: str, min_len: int, max_len: int):
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            yield "".join(combo)


def hybrid_attack(wordlist: Path, mask_suffix: str):
    """Word + masked suffix (e.g. word + 2 digits)."""
    for suffix in mask_attack(mask_suffix):
        with wordlist.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.strip()
                if word:
                    yield word + suffix


def combinator_attack(wl1: Path, wl2: Path):
    """Cartesian product of two wordlists (e.g. first+last names)."""
    words1 = [w.strip() for w in wl1.open(encoding="utf-8", errors="ignore") if w.strip()]
    words2 = [w.strip() for w in wl2.open(encoding="utf-8", errors="ignore") if w.strip()]
    for a in words1:
        for b in words2:
            yield a + b
