"""Cac ham doc/ghi file dung chung trong toan bo du an: jsonl, yaml, json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import yaml


def read_jsonl(path: str | Path) -> list[dict]:
    """Doc file .jsonl, moi dong la mot JSON object. Bo qua dong rong."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(path: str | Path, records: Iterable[dict]) -> None:
    """Ghi danh sach dict ra file .jsonl, tao thu muc cha neu chua co."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_yaml(path: str | Path) -> Any:
    """Doc file YAML, tra ve dict/list tuong ung."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _deep_merge(base: dict, override: dict) -> dict:
    """Gop hai dict long nhau: gia tri o `override` thang, theo tung cap."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path) -> dict:
    """Doc YAML config, ho tro ke thua qua khoa "extends: <file cung thu muc>".

    Config con chi can ghi de truong khac base.yaml; cac truong khong ghi de
    duoc giu nguyen tu file cha (deep-merge theo tung cap dict).

    Nam o day chu KHONG o train.py vi day thuan tuy la doc file — khong lien
    quan gi toi huan luyen. De trong train.py thi moi cong cu nho muon doc
    config deu bi keo theo ca `transformers` + `torch` (train.py import
    AutoTokenizer o cap module). Da gap that: scripts/try_lexicon.py sap vi
    ModuleNotFoundError: transformers, du LexiconModel khong dung tokenizer.
    """
    path = Path(path)
    cfg = load_yaml(path) or {}
    parent_name = cfg.pop("extends", None)
    if parent_name:
        cfg = _deep_merge(load_config(path.parent / parent_name), cfg)
    return cfg


def save_json(path: str | Path, obj: Any) -> None:
    """Ghi 1 object ra file JSON (indent=2, giu nguyen tieng Viet)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
