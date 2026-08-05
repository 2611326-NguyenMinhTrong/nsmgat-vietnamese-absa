"""ACSADataset + collate_fn - dung chung cho MOI mo hinh (baseline va NS-MGAT).

Ghi chu quan trong - kiem chung THUC TE khi viet step nay (khong doan):
- `AutoTokenizer.from_pretrained("vinai/phobert-base-v2")` la PhobertTokenizer,
  KHONG PHAI fast tokenizer -> `.word_ids()` khong dung duoc (nem ValueError).
  PhoBERT dung BPE kieu fairseq voi hau to "@@" de danh dau mot subword
  CON TIEP TUC sang subword ke tiep CUNG mot tu goc; subword khong co "@@"
  la subword CUOI CUNG cua tu. Ta tu suy word_ids tu quy uoc nay
  (_phobert_word_ids), ket hop voi return_special_tokens_mask=True.
- Da kiem chung: truyen list token da tach tu qua is_split_into_words=True
  cho ra DUNG cung input_ids nhu noi tokens bang dau cach roi tokenize
  chuoi thuong (ca hai cach deu hop le, dung is_split_into_words truc tiep
  vi tu nhien hon cho viec suy word_ids).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import torch
from torch.utils.data import Dataset

from nsmgat.utils.io import read_jsonl

# Xac nhan thuc te: AutoTokenizer.from_pretrained("vinai/phobert-base-v2").pad_token_id == 1
PHOBERT_PAD_TOKEN_ID = 1


def _phobert_word_ids(pieces: List[str], special_tokens_mask: List[int]) -> List[Optional[int]]:
    """Anh xa subword -> chi so token goc cho PhobertTokenizer (xem module docstring)."""
    word_ids: List[Optional[int]] = []
    current = 0
    for piece, is_special in zip(pieces, special_tokens_mask):
        if is_special:
            word_ids.append(None)
            continue
        word_ids.append(current)
        if not piece.endswith("@@"):
            current += 1
    return word_ids


class ACSADataset(Dataset):
    """Doc jsonl (schema Example; tap chan doan co them truong tuy chon
    "phenomenon") va tokenize bang PhoBERT tokenizer.

    Tra ve moi item mot dict: uid, input_ids, attention_mask, aspect_text,
    label, n_tokens, word_ids, phenomenon (None neu khong co).
    """

    def __init__(self, jsonl_path, tokenizer, max_seq_len: int = 128):
        self.records = read_jsonl(jsonl_path)
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        record = self.records[idx]
        tokens = record["tokens"]

        enc = self.tokenizer(
            tokens,
            is_split_into_words=True,
            truncation=True,
            max_length=self.max_seq_len,
            return_special_tokens_mask=True,
        )
        pieces = self.tokenizer.convert_ids_to_tokens(enc["input_ids"])
        word_ids = _phobert_word_ids(pieces, enc["special_tokens_mask"])

        return {
            "uid": record["uid"],
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "aspect_text": record["aspect"],
            "label": record["label"],
            "n_tokens": len(tokens),
            "word_ids": word_ids,
            "phenomenon": record.get("phenomenon"),
        }


def collate_fn(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pad dong (theo do dai lon nhat trong batch), tra ve dict tensor.

    THIET KE SAN edge_index/edge_type/edge_conf/edge_view - RONG o day vi
    chua co graph builder (Stage 2-3) - de cac step sau dien vao ma khong
    phai sua ham nay.
    """
    max_len = max(len(item["input_ids"]) for item in batch)
    batch_size = len(batch)

    input_ids = torch.full((batch_size, max_len), PHOBERT_PAD_TOKEN_ID, dtype=torch.long)
    attention_mask = torch.zeros((batch_size, max_len), dtype=torch.long)

    for i, item in enumerate(batch):
        length = len(item["input_ids"])
        input_ids[i, :length] = torch.tensor(item["input_ids"], dtype=torch.long)
        attention_mask[i, :length] = torch.tensor(item["attention_mask"], dtype=torch.long)

    return {
        "uid": [item["uid"] for item in batch],
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "aspect_text": [item["aspect_text"] for item in batch],
        "labels": torch.tensor([item["label"] for item in batch], dtype=torch.long),
        "n_tokens": torch.tensor([item["n_tokens"] for item in batch], dtype=torch.long),
        "word_ids": [item["word_ids"] for item in batch],
        "phenomenon": [item["phenomenon"] for item in batch],
        # Do thi da gop batch (Stage 2-4 dien vao) - rong o day, khong crash.
        "edge_index": torch.zeros((2, 0), dtype=torch.long),
        "edge_type": torch.zeros((0,), dtype=torch.long),
        "edge_conf": torch.zeros((0,), dtype=torch.float),
        "edge_view": torch.zeros((0,), dtype=torch.long),
    }
