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


def save_json(path: str | Path, obj: Any) -> None:
    """Ghi 1 object ra file JSON (indent=2, giu nguyen tieng Viet)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
