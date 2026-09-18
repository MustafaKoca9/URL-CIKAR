#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
urlcikar — Streaming HTTP/HTTPS URL extractor.

Stdlib-only, designed for very large directory trees and backups.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Optional, Sequence, Set, Tuple
from urllib.parse import unquote, urlsplit, urlunsplit

VERSION = "2.1.0"
CONFIG_NAME = "urlcikar_config.json"
STATE_SCHEMA = 2

DEFAULT_CONFIG: Dict[str, Any] = {
    "dizin": "",
    "cikti": "",
    "durum_dosyasi": "",
    "log_dosyasi": "",
    "ilerleme": True,
    "renkli": True,
    "ilerleme_araligi": 200,
    "uzantilar": [],
    "haric_dizinler": [".git", "node_modules", "__pycache__", ".venv", "venv"],
    "maks_dosya_boyutu": 524288000,
    "symlink_takip": False,
    "binary_kontrol_byte": 4096,
    "maks_satir_uzunlugu": 10485760,
    "maks_url_uzunlugu": 2048,
    "izinli_schemeler": ["http", "https"],
    "domain_blacklist": [],
    "domain_whitelist": [],
    "ip_atla": False,
    "localhost_atla": False,
    "query_temizle": False,
    "fragment_temizle": False,
    "percent_decode": False,
    "dry_run": False,
    "sessiz": False,
    "cikti_rotate_boyut": 0,
    "min_disk_alan": 524288000,
    "checkpoint_araligi": 500,
}

URL_CANDIDATE = re.compile(
    r"""(?i)\b(?:https?://)[^\s<>"'`]+"""
)

TRAILING_PUNCT = ".,;:!?)]}>\"'`"
LEADING_PUNCT = "([<{\"'`"

STOP = False


def config_path() -> Path:
    return Path.home() / "Desktop" / CONFIG_NAME


def atomic_json_write(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, dict):
        raise ValueError("Config kök değeri JSON object olmalı.")
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(raw)
    return cfg


def create_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        cfg = dict(DEFAULT_CONFIG)
        cfg["dizin"] = str(Path.home())
        cfg["cikti"] = str(Path.home() / "Desktop" / "urls_raw.txt")
        cfg["durum_dosyasi"] = str(Path.home() / "Desktop" / "urlcikar_durum.json")
        cfg["log_dosyasi"] = str(Path.home() / "Desktop" / "urlcikar.log")
        with path.open("w", encoding="utf-8") as fh:
            json.dump(cfg, fh, ensure_ascii=False, indent=2)
            fh.write("\n")


def validate_config(cfg: Dict[str, Any]) -> None:
    for key in ("dizin", "cikti"):
        if not cfg.get(key):
            raise ValueError(f"'{key}' ayarı boş bırakılamaz.")

    root = Path(cfg["dizin"]).expanduser().resolve()
    output = Path(cfg["cikti"]).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Taranacak dizin bulunamadı: {root}")

    # Output/state/log must not be inside the tree being scanned.
    for key in ("cikti", "durum_dosyasi", "log_dosyasi"):
        value = cfg.get(key)
        if value:
            p = Path(value).expanduser().resolve()
            try:
                p.relative_to(root)
            except ValueError:
                continue
            raise ValueError(
                f"{key} taranan dizinin içinde olamaz: {p}. "
                "Self-scan/çıktı tekrar tarama riski var."
            )

    for key in ("ilerleme_araligi", "checkpoint_araligi", "binary_kontrol_byte",
                "maks_satir_uzunlugu", "maks_url_uzunlugu", "maks_dosya_boyutu",
                "min_disk_alan", "cikti_rotate_boyut"):
        if int(cfg[key]) < 0:
            raise ValueError(f"{key} negatif olamaz.")

    schemes = {str(x).lower() for x in cfg.get("izinli_schemeler", [])}
    if not schemes:
        raise ValueError("izinli_schemeler en az bir şema içermeli.")


def install_signals() -> None:
    def handler(signum: int, _frame: Any) -> None:
        global STOP
        STOP = True
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


def log(cfg: Dict[str, Any], message: str) -> None:
    if not cfg.get("sessiz"):
        print(message, flush=True)
    path = cfg.get("log_dosyasi")
    if path:
        try:
            with Path(path).expanduser().open("a", encoding="utf-8") as fh:
                fh.write(message + "\n")
        except OSError:
            pass


def config_fingerprint(cfg: Dict[str, Any]) -> str:
    relevant = dict(cfg)
    relevant.pop("dry_run", None)
    payload = json.dumps(relevant, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def is_excluded_dir(name: str, excluded: Set[str]) -> bool:
    return name in excluded


def iter_files(root: Path, cfg: Dict[str, Any]) -> Iterator[Path]:
    excluded = set(map(str, cfg.get("haric_dizinler", [])))
    extensions = {str(x).lower() for x in cfg.get("uzantilar", [])}
    follow = bool(cfg.get("symlink_takip", False))

    stack = [root]
    while stack and not STOP:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                dirs = []
                for entry in entries:
                    try:
                        if entry.is_dir(follow_symlinks=follow):
                            if entry.name not in excluded:
                                dirs.append(entry.path)
                        elif entry.is_file(follow_symlinks=follow):
                            if extensions:
                                suffix = Path(entry.name).suffix.lower()
                                if suffix not in extensions:
                                    continue
                            yield Path(entry.path)
                    except OSError:
                        continue
                # Deterministic traversal improves resume reproducibility.
                dirs.sort(reverse=True)
                stack.extend(Path(d) for d in dirs)
        except OSError:
            continue


def is_binary(path: Path, nbytes: int) -> bool:
    if nbytes <= 0:
        return False
    try:
        with path.open("rb") as fh:
            sample = fh.read(nbytes)
        return b"\x00" in sample
    except OSError:
        return True


def clean_candidate(candidate: str) -> str:
    candidate = candidate.strip()
    candidate = candidate.lstrip(LEADING_PUNCT)
    # Balance common closing punctuation instead of blindly stripping it.
    while candidate and candidate[-1] in TRAILING_PUNCT:
        ch = candidate[-1]
        pairs = {")": "(", "]": "[", "}": "{"}
        if ch in pairs and candidate.count(ch) <= candidate.count(pairs[ch]):
            break
        candidate = candidate[:-1]
    return candidate


def domain_matches(host: str, patterns: Sequence[str]) -> bool:
    host = host.lower().rstrip(".")
    for raw in patterns:
        pattern = str(raw).strip().lower().rstrip(".")
        if host == pattern or host.endswith("." + pattern):
            return True
    return False


def normalize_url(url: str, cfg: Dict[str, Any]) -> Optional[str]:
    if len(url) > int(cfg["maks_url_uzunlugu"]):
        return None

    try:
        parts = urlsplit(url)
    except ValueError:
        return None

    scheme = parts.scheme.lower()
    allowed = {str(x).lower() for x in cfg["izinli_schemeler"]}
    if scheme not in allowed or scheme not in {"http", "https"}:
        return None
    if not parts.netloc:
        return None

    try:
        hostname = parts.hostname
    except ValueError:
        return None
    if not hostname:
        return None

    hostname = hostname.lower().rstrip(".")
    if cfg.get("localhost_atla") and (
        hostname == "localhost" or hostname.endswith(".localhost")
    ):
        return None

    try:
        ip = ipaddress.ip_address(hostname)
        if cfg.get("ip_atla"):
            return None
    except ValueError:
        ip = None

    blacklist = cfg.get("domain_blacklist", [])
    whitelist = cfg.get("domain_whitelist", [])
    if blacklist and domain_matches(hostname, blacklist):
        return None
    if whitelist and not domain_matches(hostname, whitelist):
        return None

    query = "" if cfg.get("query_temizle") else parts.query
    fragment = "" if cfg.get("fragment_temizle") else parts.fragment

    path = parts.path
    if cfg.get("percent_decode"):
        # Deliberately optional: decoding can change URL semantics.
        path = unquote(path)
        query = unquote(query)

    # Preserve credentials/port if present; hostname filtering above is separate.
    netloc = parts.netloc
    return urlunsplit((scheme, netloc, path, query, fragment))


def extract_from_line(line: str, cfg: Dict[str, Any]) -> Iterator[str]:
    for match in URL_CANDIDATE.finditer(line):
        candidate = clean_candidate(match.group(0))
        normalized = normalize_url(candidate, cfg)
        if normalized:
            yield normalized


def scan_file(path: Path, cfg: Dict[str, Any]) -> Iterator[str]:
    max_line = int(cfg["maks_satir_uzunlugu"])
    # UTF-8 first; replacement keeps malformed backups processable.
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
            for raw in fh:
                if STOP:
                    return
                if len(raw) > max_line:
                    # Process bounded chunks to avoid a pathological single line
                    # allocating unbounded memory.
                    for start in range(0, len(raw), max_line):
                        chunk = raw[start:start + max_line]
                        yield from extract_from_line(chunk, cfg)
                else:
                    yield from extract_from_line(raw, cfg)
    except (OSError, UnicodeError):
        return


def enough_disk_space(path: Path, minimum: int) -> bool:
    if minimum <= 0:
        return True
    try:
        usage = os.statvfs(path.parent)
        free = usage.f_bavail * usage.f_frsize
        return free >= minimum
    except (AttributeError, OSError):
        return True


def load_state(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            state = json.load(fh)
        return state if isinstance(state, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(path: Path, cfg: Dict[str, Any], processed: int,
               last_path: Optional[Path], output_size: int) -> None:
    atomic_json_write(path, {
        "schema_version": STATE_SCHEMA,
        "config_fingerprint": config_fingerprint(cfg),
        "root": str(Path(cfg["dizin"]).expanduser().resolve()),
        "output_path": str(Path(cfg["cikti"]).expanduser().resolve()),
        "files_processed": processed,
        "last_path": str(last_path) if last_path else None,
        "output_size": output_size,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    })


def should_skip_for_resume(path: Path, state: Dict[str, Any], cfg: Dict[str, Any]) -> bool:
    last = state.get("last_path")
    if not last:
        return False
    try:
        return str(path) <= str(last)
    except Exception:
        return False


def run_scan(cfg: Dict[str, Any]) -> int:
    validate_config(cfg)
    install_signals()

    root = Path(cfg["dizin"]).expanduser().resolve()
    output = Path(cfg["cikti"]).expanduser().resolve()
    state_path = Path(cfg.get("durum_dosyasi") or str(output) + ".state.json").expanduser().resolve()

    if not enough_disk_space(output, int(cfg["min_disk_alan"])):
        raise RuntimeError("Çıktı filesystem'inde minimum boş disk alanı yok.")

    state = load_state(state_path)
    fingerprint = config_fingerprint(cfg)
    resume_ok = (
        state.get("schema_version") == STATE_SCHEMA
        and state.get("config_fingerprint") == fingerprint
        and state.get("root") == str(root)
        and state.get("output_path") == str(output)
        and output.exists()
    )

    if cfg.get("dry_run"):
        count = 0
        for _ in iter_files(root, cfg):
            count += 1
            if count % max(1, int(cfg["ilerleme_araligi"])) == 0 and not cfg.get("sessiz"):
                print(f"\rDry-run: {count:,} dosya", end="", flush=True)
        print()
        log(cfg, f"Dry-run tamamlandı: {count:,} uygun dosya.")
        return 0

    processed = int(state.get("files_processed", 0)) if resume_ok else 0
    last_path = state.get("last_path") if resume_ok else None
    mode = "a" if resume_ok else "w"

    if resume_ok:
        log(cfg, f"Resume: {processed:,} dosyadan devam ediliyor.")
    else:
        processed = 0
        last_path = None

    output.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    written = 0
    skipped = 0

    with output.open(mode, encoding="utf-8", buffering=1024 * 1024) as out:
        for path in iter_files(root, cfg):
            if STOP:
                break
            if resume_ok and should_skip_for_resume(path, state, cfg):
                continue

            try:
                st = path.stat()
                if st.st_size > int(cfg["maks_dosya_boyutu"]):
                    skipped += 1
                    continue
                if is_binary(path, int(cfg["binary_kontrol_byte"])):
                    skipped += 1
                    continue
            except OSError:
                skipped += 1
                continue

            for url in scan_file(path, cfg):
                out.write(url + "\n")
                written += 1

            processed += 1
            last_path = path
            if processed % max(1, int(cfg["checkpoint_araligi"])) == 0:
                out.flush()
                save_state(state_path, cfg, processed, path, output.stat().st_size)

            if (
                cfg.get("ilerleme")
                and processed % max(1, int(cfg["ilerleme_araligi"])) == 0
                and not cfg.get("sessiz")
            ):
                elapsed = max(0.001, time.monotonic() - start)
                rate = processed / elapsed
                print(
                    f"\rDosya: {processed:,} | URL: {written:,} | "
                    f"Atlanan: {skipped:,} | {rate:,.1f} dosya/s",
                    end="", flush=True
                )

        out.flush()
        if last_path:
            save_state(state_path, cfg, processed, Path(last_path), output.stat().st_size)

    if not cfg.get("sessiz"):
        print()
    if STOP:
        log(cfg, f"Temiz çıkış: {processed:,} dosya, {written:,} URL.")
        return 130

    elapsed = max(0.001, time.monotonic() - start)
    log(
        cfg,
        f"Tamamlandı: {processed:,} dosya | {written:,} URL | "
        f"{skipped:,} atlandı | {elapsed:.1f} sn"
    )
    return 0


TESTS = [
    ("basic", lambda: normalize_url("https://example.com/a", DEFAULT_CONFIG)),
    ("scheme", lambda: normalize_url("ftp://example.com/a", DEFAULT_CONFIG) is None),
    ("blacklist", lambda: normalize_url(
        "https://sub.example.com/a",
        {**DEFAULT_CONFIG, "domain_blacklist": ["example.com"]}
    ) is None),
    ("whitelist", lambda: normalize_url(
        "https://sub.example.com/a",
        {**DEFAULT_CONFIG, "domain_whitelist": ["example.com"]}
    ) is not None),
    ("localhost", lambda: normalize_url(
        "http://localhost:8080/a",
        {**DEFAULT_CONFIG, "localhost_atla": True}
    ) is None),
    ("query", lambda: normalize_url(
        "https://example.com/a?utm=x",
        {**DEFAULT_CONFIG, "query_temizle": True}
    ) == "https://example.com/a"),
    ("fragment", lambda: normalize_url(
        "https://example.com/a#x",
        {**DEFAULT_CONFIG, "fragment_temizle": True}
    ) == "https://example.com/a"),
    ("length", lambda: normalize_url(
        "https://example.com/" + "x" * 3000,
        {**DEFAULT_CONFIG, "maks_url_uzunlugu": 100}
    ) is None),
]


def run_tests() -> int:
    failures = 0
    for name, test in TESTS:
        try:
            result = bool(test())
        except Exception as exc:
            result = False
            print(f"FAIL {name}: {exc}")
        if result:
            print(f"PASS {name}")
        else:
            failures += 1
            print(f"FAIL {name}")
    print(f"\n{len(TESTS) - failures}/{len(TESTS)} test başarılı.")
    return 1 if failures else 0


def show_readme() -> None:
    readme = Path(__file__).with_name("README.md")
    try:
        print(readme.read_text(encoding="utf-8"))
    except OSError:
        print("README.md bulunamadı.")


def main(argv: Sequence[str]) -> int:
    command = argv[1].lower() if len(argv) > 1 else "run"
    path = config_path()

    if command in {"versiyon", "version"}:
        print(f"urlcikar {VERSION}")
        return 0
    if command == "test":
        return run_tests()
    if command == "readme":
        show_readme()
        return 0
    if command == "config":
        create_config(path)
        print(path.read_text(encoding="utf-8"))
        return 0
    if command in {"config-yenile", "config-reset"}:
        create_config(path)
        cfg = dict(DEFAULT_CONFIG)
        cfg["dizin"] = str(Path.home())
        cfg["cikti"] = str(Path.home() / "Desktop" / "urls_raw.txt")
        cfg["durum_dosyasi"] = str(Path.home() / "Desktop" / "urlcikar_durum.json")
        cfg["log_dosyasi"] = str(Path.home() / "Desktop" / "urlcikar.log")
        path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Config yenilendi: {path}")
        return 0
    if command in {"sifirla", "reset"}:
        cfg = load_config(path) if path.exists() else DEFAULT_CONFIG
        state = Path(cfg.get("durum_dosyasi") or str(Path(cfg["cikti"]) .with_suffix(".state.json"))).expanduser()
        try:
            state.unlink()
            print(f"Resume durumu silindi: {state}")
        except FileNotFoundError:
            print("Silinecek resume durumu yok.")
        return 0

    if not path.exists():
        create_config(path)
        print(f"Config oluşturuldu: {path}")
        print("Config'i düzenleyip komutu tekrar çalıştırın.")
        return 0

    try:
        cfg = load_config(path)
        return run_scan(cfg)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
