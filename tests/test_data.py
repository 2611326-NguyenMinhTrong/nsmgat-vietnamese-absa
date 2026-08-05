"""Test data/loaders.py va data/preprocess.py.

Khong goi VnCorePipeline that (can Java + tai model ~100MB) - dung mot
pipeline gia lap chi can dung interface .annotate(text) -> (tokens, pos,
heads, deprels), giong het VnCorePipeline that, de test build_examples
chay nhanh va khong phu thuoc moi truong.
"""

from __future__ import annotations

from typing import List, Tuple

from nsmgat.data.loaders import _parse_vlsp_blocks, parse_label
from nsmgat.data.preprocess import build_examples


def test_parse_label_visfd_bracket_format():
    # dinh dang that cua HF dataset visolex/ViSFD (kiem tra truc tiep 2026-08)
    raw = "{CAMERA#Positive};{BATTERY#Negative};{OTHERS};"
    assert parse_label(raw) == {"CAMERA": "positive", "BATTERY": "negative"}


def test_parse_label_dict_passthrough():
    assert parse_label({"CAMERA": "Positive"}) == {"CAMERA": "positive"}


def test_parse_label_json_string():
    raw = '{"CAMERA": "Positive", "BATTERY": "Negative"}'
    assert parse_label(raw) == {"CAMERA": "positive", "BATTERY": "negative"}


def test_parse_label_others_only_is_empty():
    assert parse_label("{OTHERS};") == {}


_VLSP_SAMPLE = """#1
Phong dep nhung hoi on.
{ROOMS#DESIGN&FEATURES, positive}, {ROOMS#COMFORT, negative}

#2
Nhan vien nhiet tinh.
{SERVICE#GENERAL, positive}

"""


def test_parse_vlsp_blocks_two_samples():
    records = _parse_vlsp_blocks(_VLSP_SAMPLE)
    assert len(records) == 2
    assert records[0]["text"] == "Phong dep nhung hoi on."
    assert records[0]["labels"] == {
        "ROOMS#DESIGN&FEATURES": "positive",
        "ROOMS#COMFORT": "negative",
    }
    assert records[1]["text"] == "Nhan vien nhiet tinh."
    assert records[1]["labels"] == {"SERVICE#GENERAL": "positive"}


class _FakePipeline:
    """Gia lap VnCorePipeline: interface giong het that, khong can Java."""

    def annotate(self, text: str) -> Tuple[List[str], List[str], List[int], List[str]]:
        tokens = text.split()
        n = len(tokens)
        pos = ["N"] * n
        heads = ([-1] + list(range(n - 1))) if n > 0 else []
        deprels = (["root"] + ["dep"] * (n - 1)) if n > 0 else []
        return tokens, pos, heads, deprels


def test_build_examples_one_sentence_three_aspects():
    raw_records = [
        {
            "text": "Pin tot camera dep gia re",
            "labels": {"BATTERY": "positive", "CAMERA": "positive", "PRICE": "negative"},
        }
    ]
    examples = build_examples(raw_records, domain="visfd", split="train", pipeline=_FakePipeline())
    assert len(examples) == 3
    assert {ex.aspect for ex in examples} == {"BATTERY", "CAMERA", "PRICE"}
    assert examples[0].uid == "visfd-train-00000-BATTERY"
    assert all(ex.label in (0, 1, 2) for ex in examples)


def test_build_examples_skips_records_without_labels():
    raw_records = [{"text": "khong co gi de noi", "labels": {}}]
    examples = build_examples(raw_records, domain="visfd", split="train", pipeline=_FakePipeline())
    assert examples == []


def test_build_examples_skips_empty_text():
    raw_records = [{"text": "", "labels": {"GENERAL": "neutral"}}]
    examples = build_examples(raw_records, domain="visfd", split="train", pipeline=_FakePipeline())
    assert examples == []
