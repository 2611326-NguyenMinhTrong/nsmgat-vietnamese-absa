"""Tai va chuan hoa nhan tho cho UIT-ViSFD (HuggingFace) va VLSP 2018 (file .txt).

Ca hai ham load_* deu tra ve list dict dang thong nhat:
    {"text": str, "labels": {aspect: polarity}}
(polarity la chuoi thuong: "negative" | "neutral" | "positive")
de preprocess.build_examples() dung chung mot logic bung Example cho moi domain.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

from datasets import load_dataset

# --- UIT-ViSFD (HuggingFace "visolex/ViSFD") --------------------------------

_VISFD_LABEL_PATTERN = re.compile(r"\{([^,{}#]+)#([^,{}#]+)\}")


def parse_label(value) -> Dict[str, str]:
    """Chuan hoa truong 'label' cua UIT-ViSFD ve dict {aspect: polarity}.

    Kiem chung thuc te tren HF dataset "visolex/ViSFD" (truy cap 2026-08):
    moi ban ghi la MOT CHUOI dang "{ASPECT#Polarity};{ASPECT#Polarity};...",
    vi du '{BATTERY#Negative};{OTHERS};'. "{OTHERS}" khong di kem polarity
    (khong the gan nhan cam xuc) nen bi bo qua. Ham nay xu ly them 2 dang
    du phong - dict dung san, hoac chuoi JSON hop le - de an toan neu mot
    ban dataset khac tra ve dinh dang khac.
    """
    if isinstance(value, dict):
        return {str(k): str(v).lower() for k, v in value.items()}

    text = str(value).strip()

    if text.startswith("{") and '"' in text:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            return {str(k): str(v).lower() for k, v in parsed.items()}

    pairs = _VISFD_LABEL_PATTERN.findall(text)
    return {aspect.strip(): polarity.strip().lower() for aspect, polarity in pairs}


def load_visfd(split: str) -> List[Dict]:
    """Tai UIT-ViSFD tu HuggingFace 'visolex/ViSFD'.

    QUAN TRONG (loi da gap o phien truoc): dataset chi co MOT split HF ten
    "train" chua het 11122 dong; train/dev/test that su duoc phan biet qua
    cot "type" (Counter: train=7786, dev=1112, test=2224 - khop thong ke
    trong plan). Phai loc bang vong lap/list-comprehension nhu duoi day -
    dung ds["train"].filter(...) se nem KeyError: "Invalid key: 0".
    """
    ds = load_dataset("visolex/ViSFD")
    all_rows = ds["train"]

    records: List[Dict] = []
    for row in all_rows:
        if row["type"] != split:
            continue
        records.append({"text": row["comment"], "labels": parse_label(row["label"])})
    return records


# --- VLSP 2018 (file .txt tai thu cong tu github.com/ds4v/absa-vlsp-2018) ---

# Ten thu muc/file that su tren repo goc (kiem tra qua GitHub API 2026-08):
#   datasets/vlsp2018_hotel/{1,2,3}-VLSP2018-SA-Hotel-{train,dev,test}.txt
#   datasets/vlsp2018_restaurant/{1,2,3}-VLSP2018-SA-Restaurant-{train,dev,test}.txt
_VLSP_DOMAIN_DIRS = {"vlsp-hotel": "vlsp2018_hotel", "vlsp-restaurant": "vlsp2018_restaurant"}
_VLSP_DOMAIN_LABELS = {"vlsp-hotel": "Hotel", "vlsp-restaurant": "Restaurant"}
_VLSP_SPLIT_PREFIX = {"train": "1", "dev": "2", "test": "3"}

_VLSP_BLOCK_SPLIT = re.compile(r"^#\d+\s*$", flags=re.MULTILINE)
_VLSP_LABEL_PATTERN = re.compile(r"\{([^,}]+),\s*([^}]+)\}")


def _parse_vlsp_blocks(content: str) -> List[Dict]:
    """Parse noi dung file VLSP 2018: block '#<so>' / cau / dong nhan / dong trong.

    Tach thanh nhung parser rieng (khong doc file) de test duoc bang block
    hardcode, khong phu thuoc file that tren dia.
    """
    records: List[Dict] = []
    for block in _VLSP_BLOCK_SPLIT.split(content):
        lines = [line.strip() for line in block.strip().splitlines() if line.strip()]
        if len(lines) < 2:
            continue
        text, label_line = lines[0], lines[1]
        pairs = _VLSP_LABEL_PATTERN.findall(label_line)
        labels = {aspect.strip(): polarity.strip().lower() for aspect, polarity in pairs}
        if labels:
            records.append({"text": text, "labels": labels})
    return records


def load_vlsp(domain: str, split: str, raw_dir: str | Path = "data/raw/vlsp2018") -> List[Dict]:
    """Doc file VLSP 2018 da tai thu cong ve raw_dir.

    Cau truc thu muc ky vong (giu nguyen nhu repo goc ds4v/absa-vlsp-2018,
    chi copy 2 thu muc con "datasets/vlsp2018_hotel" va
    "datasets/vlsp2018_restaurant" vao raw_dir):
        {raw_dir}/vlsp2018_hotel/1-VLSP2018-SA-Hotel-train.txt
        {raw_dir}/vlsp2018_hotel/2-VLSP2018-SA-Hotel-dev.txt
        {raw_dir}/vlsp2018_hotel/3-VLSP2018-SA-Hotel-test.txt
        {raw_dir}/vlsp2018_restaurant/... (tuong tu, prefix Restaurant)
    """
    if domain not in _VLSP_DOMAIN_DIRS:
        raise ValueError(f"domain VLSP khong hop le: {domain!r}")
    if split not in _VLSP_SPLIT_PREFIX:
        raise ValueError(f"split khong hop le: {split!r}")

    subdir = _VLSP_DOMAIN_DIRS[domain]
    prefix = _VLSP_SPLIT_PREFIX[split]
    label = _VLSP_DOMAIN_LABELS[domain]
    path = Path(raw_dir) / subdir / f"{prefix}-VLSP2018-SA-{label}-{split}.txt"

    if not path.exists():
        raise FileNotFoundError(
            f"Khong thay file VLSP: {path}. Tai thu cong thu muc 'datasets/' tu "
            f"https://github.com/ds4v/absa-vlsp-2018 va dat vao {path}."
        )

    content = path.read_text(encoding="utf-8-sig")
    return _parse_vlsp_blocks(content)
