"""Multiprocessing hash worker pool."""
import hashlib
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Iterable

_ALGOS = {
    "md5": hashlib.md5, "sha1": hashlib.sha1,
    "sha224": hashlib.sha224, "sha256": hashlib.sha256,
    "sha384": hashlib.sha384, "sha512": hashlib.sha512,
}


def _hash(text: str, algo: str, salt: str = "", salt_pos: str = "prefix") -> str:
    if algo not in _ALGOS:
        raise ValueError(f"Unsupported algo: {algo}")
    if salt:
        text = salt + text if salt_pos == "prefix" else text + salt
    return _ALGOS[algo](text.encode("utf-8", errors="ignore")).hexdigest()


def check_batch(args):
    """Worker: (target, algo, salt, salt_pos, batch) -> plaintext|None."""
    target, algo, salt, salt_pos, batch = args
    for cand in batch:
        if _hash(cand, algo, salt, salt_pos) == target:
            return cand
    return None


def batch(iterable: Iterable, size: int):
    """Yield fixed-size chunks from any iterable."""
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def parallel_crack(target, algo, candidates, salt="", salt_pos="prefix",
                   workers=None, batch_size=5000):
    """Return (plaintext_or_None, attempts)."""
    workers = workers or max(1, (os.cpu_count() or 1) - 1)
    attempts = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for chunk in batch(candidates, batch_size):
            attempts += len(chunk)
            results = pool.map(
                check_batch,
                [(target, algo, salt, salt_pos, chunk)],
            )
            for r in results:
                if r:
                    return r, attempts
    return None, attempts