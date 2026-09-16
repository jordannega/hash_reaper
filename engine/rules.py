"""John-the-Ripper-style mutation rules, loaded from JSON."""
import json
import re
from pathlib import Path

LEET = str.maketrans({
    "a": "@", "e": "3", "i": "1", "o": "0", "s": "$", "t": "7",
    "b": "8", "g": "9", "l": "1",
})

SUFFIXES = ["", "1", "12", "123", "1234", "12345", "!", "!!", "@", "#",
            "2020", "2021", "2022", "2023", "2024", "2025", "2026"]

PREFIXES = ["", "!", "@", "1"]


class RuleEngine:
    def __init__(self, config_path: Path | None = None):
        self.rules = self._default_rules()
        if config_path and config_path.exists():
            custom = json.loads(config_path.read_text())
            self.rules.update(custom)

    @staticmethod
    def _default_rules():
        return {
            "lower":   lambda w: w.lower(),
            "upper":   lambda w: w.upper(),
            "cap":     lambda w: w.capitalize(),
            "toggle":  lambda w: "".join(
                c.upper() if i % 2 == 0 else c.lower()
                for i, c in enumerate(w)
            ),
            "reverse": lambda w: w[::-1],
            "leet":    lambda w: w.lower().translate(LEET),
            "leet_cap": lambda w: w.lower().translate(LEET).capitalize(),
            "dup":     lambda w: w + w,
        }

    def mutate(self, word: str, chain: list[str] | None = None):
        """Yield mutations. If chain given, apply those rules only."""
        seen = set()

        def emit(x):
            if x and x not in seen:
                seen.add(x)
                return x
            return None

        # Base word
        for base in (word, word.lower(), word.capitalize(), word.upper()):
            r = emit(base)
            if r: yield r

        # Single-rule mutations
        for name, fn in self.rules.items():
            try:
                r = emit(fn(word))
                if r: yield r
            except Exception:
                pass

        # If a chain was specified, apply it
        if chain:
            cur = word
            for step in chain:
                fn = self.rules.get(step)
                if fn:
                    cur = fn(cur)
            r = emit(cur)
            if r: yield r

        # Suffix / prefix spam (the bread and butter of real cracks)
        bases = [word, word.lower(), word.capitalize(), word.upper(),
                 word.lower().translate(LEET)]
        for base in set(bases):
            for suf in SUFFIXES:
                for pre in PREFIXES:
                    r = emit(pre + base + suf)
                    if r: yield r

    def chained(self, word: str, chain: list[str]):
        """Public helper to apply a named rule chain."""
        return list(self.mutate(word, chain=chain))