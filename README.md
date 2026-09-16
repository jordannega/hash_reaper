# 💀 The Hash Reaper

An advanced educational hash cracker with auto-detection, rule-based mutations, mask attacks, and multiprocessing. Built for CTFs, labs, and learning how password attacks actually work.

---

## ✨ Features

- **Auto-detect** 20+ hash formats (MD5, SHA-1/2, NTLM, bcrypt, crypt, Argon2, phpass, …)
- **Attack modes**: Dictionary · Mask · Brute · Hybrid · Combinator
- **Rule engine** — leetspeak, capitalization, suffix/prefix spam, chaining
- **Salt support** — prefix or suffix, any algorithm
- **Multiprocessing** — uses all CPU cores by default
- **SQLite potfile** — never re-crack the same hash twice
- **Live dashboard** — H/s rate, elapsed time, attempts counter
- **Modular engine** — swap in a GPU backend by replacing one file

---

## 📁 Structure

```text
hash_reaper/
├── reaper.py         # CLI entry point
├── engine/
│   ├── __init__.py   # empty
│   ├── detectors.py  # hash auto-detection
│   ├── rules.py      # mutation rule engine
│   ├── attacks.py    # attack strategies
│   ├── workers.py    # multiprocessing pool
│   ├── potfile.py    # SQLite crack history
│   └── dashboard.py  # live progress display
├── rules/
│   └── best64.json   # optional rule config
└── wordlists/
    └── sample.txt    # small test wordlist
📦 RequirementsPython 3.9+
No external dependencies (stdlib only)


---

## 📦 Requirements

- **Python 3.9+**
- No external dependencies (stdlib only)

---

# 🚀 Usage Guide

### Dictionary attack
```bash
python reaper.py <hash> --dict wordlists/sample.txt
Dictionary + mutations (leetspeak, suffixes, caps)
Bash
python reaper.py <hash> --dict wordlists/sample.txt --mutate
Mask attack
Bash
python reaper.py <hash> --mask "?u?l?l?l?d?d"
Mask symbols: ?l lowercase · ?u uppercase · ?d digit · ?s symbol · ?a all

Brute force
Bash
python reaper.py <hash> --brute --charset lower+digits --max-len 5
Hybrid (wordlist + masked suffix)
Bash
python reaper.py <hash> --dict wordlists/names.txt --hybrid "?d?d"
Combinator (cartesian product of two lists)
Bash
python reaper.py <hash> --combinator wordlists/first.txt wordlists/last.txt
Salted hashes
Bash
python reaper.py <hash> --dict wordlists/sample.txt --salt "abc" --salt-pos prefix
Force a specific algorithm
Bash
python reaper.py <hash> --algo sha256 --dict wordlists/sample.txt
Show potfile statistics
Bash
python reaper.py --show-pot

🧪 Quick TestBash# 1. Generate a test hash
python -c "import hashlib; print(hashlib.sha256(b'Dragon2024!').hexdigest())"

# 2. Crack it (auto-detect + mutations will recover it)
python reaper.py <hash> --dict wordlists/sample.txt --mutate
Expected output:Plaintext🔎 Detected: SHA-256
⚔️  Dictionary: wordlists/sample.txt  (mutate=True)
✅ CRACKED: 'Dragon2024!'  (48,231 tries in 3.12s)
🧠 How It WorksDetect — regex signatures identify hash type by length & prefix.Potfile check — if already cracked, return instantly.Generate candidates — depending on the attack mode.Dispatch — candidates are chunked and hashed across CPU cores.Compare — each worker hashes its batch and compares to target.Report — first hit wins; result is saved to the potfile.🎓 Why Rules Beat WordlistsA user picking password is rare. A user picking:Password1P@ssw0rd!PASSWORD2024drowssap…is extremely common. Raw wordlists miss these. Mutation rules turn one word into ~200 candidates — this is what real cracking tools do.🔧 ExtendingWant to add…Edit this fileNew hash algorithmengine/detectors.py, engine/workers.pyNew mutation ruleengine/rules.pyNew attack modeengine/attacks.pyGPU backendReplace engine/workers.pyRemote worker poolReplace ProcessPoolExecutor in engine/workers.py⚠️ Legal & Ethical UseAllowed:Your own hashesCTF challengesLab VMs / isolated environmentsPassword audits with written authorizationNot allowed:Cracking hashes you don't ownAttacking production systemsAny use without explicit permissionHash cracking is dual-use. Learn defense by understanding offense — never weaponize it.
