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


# Cac khoa la CACH CHAY / SO SACH, khong phai cau hinh thi nghiem — bo ra
# truoc khi bam van tay. Tieu chi de quyet dinh mot khoa co nam trong day
# khong, chi mot cau: **doi khoa nay co lam doi ket qua khong?**
#
#   train.resume          — lien mach hay chay tiep. Hai duong cho ra ket qua
#                           giong het nhau (tests/test_resume.py), nen phai
#                           cung van tay.
#   output.log_dir        — ghi nhat ky o dau
#   output.save_last      — co ghi last.pt khong
#   output.save_last_every— ghi cach may epoch
#
# Ba khoa `output.*` them vao o CD1.4b. Neu khong loai chung ra, chi viec them
# mot dong vao base.yaml da lam DOI VAN TAY cua moi ket qua da chay xong —
# da xay ra that: lexicon/seed42 doi tu f25b1bbb0fcc sang 34f8cee22a1e trong
# khi moi con so trong metrics.json y nguyen (GAP-014).
#
# KHONG loai `output.save_best`: tat no thi buoc danh gia dung mo hinh o epoch
# CUOI thay vi epoch tot nhat — doi ket qua that.
# Cung KHONG loai `output.results_dir` / `ckpt_dir`: chung khong doi ket qua,
# nhung da nam trong van tay tu S0.4; loai bay gio se doi van tay lan nua ma
# khong duoc gi. Ghi lai day de biet day la lua chon co y thuc.
_KHOA_KHONG_BAM_VAN_TAY = (
    ("train", "resume"),
    ("output", "log_dir"),
    ("output", "save_last"),
    ("output", "save_last_every"),
)


def config_hash(cfg: dict) -> str:
    """Van tay 12 ky tu cua mot config — dinh danh mot cau hinh thi nghiem.

    Dung o hai cho, va cho thu hai moi la ly do ham nay nam o day (dung chung)
    chu khong nam rieng trong train.py:
      1. Ghi vao metrics.json de biet ket qua sinh ra tu cau hinh nao.
      2. `Trainer` doi chieu truoc khi tiep tuc mot lan chay dang do — tiep tuc
         bang cau hinh KHAC se cho ra mot ket qua lai cang khong tai lap duoc.
    """
    import copy
    import hashlib

    sach = copy.deepcopy(cfg)
    for *cha, khoa in _KHOA_KHONG_BAM_VAN_TAY:
        nut = sach
        for buoc in cha:
            nut = nut.get(buoc) if isinstance(nut, dict) else None
            if nut is None:
                break
        if isinstance(nut, dict):
            nut.pop(khoa, None)

    return hashlib.sha256(json.dumps(sach, sort_keys=True).encode()).hexdigest()[:12]


def save_json(path: str | Path, obj: Any) -> None:
    """Ghi 1 object ra file JSON (indent=2, giu nguyen tieng Viet)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
