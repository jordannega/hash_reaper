#!/usr/bin/env python3
"""
THE HASH REAPER — godtier educational hash cracker.
Auto-detect · multi-attack · rule engine · multiprocess · potfile.

Examples:
  python reaper.py 5f4dcc3b5aa765d61d8327deb882cf99 --dict wordlists/sample.txt --mutate
  python reaper.py <sha1> --mask "?u?l?l?l?d?d"
  python reaper.py <md5>  --brute --charset lower+digits --max-len 5
  python reaper.py <hash> --dict wl.txt --salt abc123 --salt-pos prefix
  python reaper.py --show-pot
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from engine.detectors import detect_hash
from engine.rules import RuleEngine
from engine.attacks import (
    dict_attack, mask_attack, brute_attack,
    hybrid_attack, combinator_attack,
)
from engine.workers import parallel_crack
from engine.potfile import Potfile
from engine.dashboard import Dashboard


CHARSETS = {
    "lower":      "abcdefghijklmnopqrstuvwxyz",
    "upper":      "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "digits":     "0123456789",
    "symbols":    "!@#$%^&*()-_=+",
    "lower+digits": "abcdefghijklmnopqrstuvwxyz0123456789",
    "alnum":      "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "all":        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+",
}


def banner():
    print("=" * 66)
    print("  💀  THE HASH REAPER — educational hash cracker  💀")
    print("     auto-detect · multi-attack · rule engine · potfile")
    print("=" * 66)


def main():
    p = argparse.ArgumentParser(description="The Hash Reaper")
    p.add_argument("hash", nargs="?", help="target hash")
    p.add_argument("--algo", help="force algorithm (skip auto-detect)")

    # Attacks
    p.add_argument("--dict", type=Path, help="wordlist attack")
    p.add_argument("--mutate", action="store_true", help="apply rule engine")
    p.add_argument("--mask", help='mask attack, e.g. "?u?l?l?l?d?d"')
    p.add_argument("--brute", action="store_true")
    p.add_argument("--charset", default="lower+digits", choices=list(CHARSETS.keys()))
    p.add_argument("--min-len", type=int, default=1)
    p.add_argument("--max-len", type=int, default=4)
    p.add_argument("--hybrid", metavar="MASK", help="wordlist + mask suffix")
    p.add_argument("--combinator", nargs=2, metavar=("WL1", "WL2"))

    # Salt
    p.add_argument("--salt", default="")
    p.add_argument("--salt-pos", choices=["prefix", "suffix"], default="prefix")

    # Runtime
    p.add_argument("--workers", type=int, default=None)
    p.add_argument("--batch", type=int, default=5000)
    p.add_argument("--show-pot", action="store_true", help="show potfile stats")

    args = p.parse_args()

    banner()

    pot = Potfile()
    if args.show_pot:
        s = pot.stats()
        print(f"  Potfile: {s['total']} cracked hashes stored.")
        return

    if not args.hash:
        p.print_help()
        return

    target = args.hash.strip().lower()

    # Potfile lookup
    cached = pot.lookup(target, args.salt)
    if cached:
        print(f"  🎯 Found in potfile: {cached!r}")
        return

    # Detect algo
    if args.algo:
        algo = args.algo
        print(f"  🔧 Forced algo: {algo}")
    else:
        matches = detect_hash(target)
        if not matches:
            print("  ❌ Could not auto-detect hash type. Use --algo.")
            return
        algo = matches[0][0]
        print(f"  🔎 Detected: {matches[0][1]}")
        if len(matches) > 1:
            print(f"     Also possible: {', '.join(m[0] for m in matches[1:])}")

    rules = RuleEngine(Path(__file__).parent / "rules" / "best64.json")

    # Build candidate generator based on chosen attack
    if args.combinator:
        print(f"  ⚔️  Combinator: {args.combinator[0]} × {args.combinator[1]}")
        candidates = combinator_attack(Path(args.combinator[0]), Path(args.combinator[1]))
    elif args.hybrid:
        print(f"  ⚔️  Hybrid: {args.dict} + mask {args.hybrid}")
        candidates = hybrid_attack(args.dict, args.hybrid)
    elif args.mask:
        print(f"  ⚔️  Mask: {args.mask}")
        candidates = mask_attack(args.mask)
    elif args.brute:
        cs = CHARSETS[args.charset]
        print(f"  ⚔️  Brute: charset={args.charset}, len {args.min_len}–{args.max_len}")
        candidates = brute_attack(cs, args.min_len, args.max_len)
    elif args.dict:
        print(f"  ⚔️  Dictionary: {args.dict}  (mutate={args.mutate})")
        candidates = dict_attack(args.dict, rules, args.mutate)
    else:
        print("  ❌ No attack specified. Use --dict, --mask, --brute, --hybrid, or --combinator.")
        return

    # Wrap candidate iterator with live dashboard via a thin adapter
    dash = Dashboard(label=f"{algo} crack")

    # Since parallel_crack consumes an iterator, wrap it
    def counting_iterator(it, dash):
        n = 0
        for item in it:
            n += 1
            if n % 5000 == 0:
                dash.update(n)
            yield item
        dash.update(n)

    found, attempts = parallel_crack(
        target, algo,
        counting_iterator(candidates, dash),
        salt=args.salt,
        salt_pos=args.salt_pos,
        workers=args.workers,
        batch_size=args.batch,
    )

    dash.finish(found)
    if found:
        pot.save(target, algo, found, args.salt)


if __name__ == "__main__":
    main()
