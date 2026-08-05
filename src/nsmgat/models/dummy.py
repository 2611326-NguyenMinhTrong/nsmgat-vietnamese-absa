"""DummyModel - baseline toi thieu de kiem thu khung train/eval (Stage 0)."""

from __future__ import annotations

import collections
from typing import Any, Dict

import torch
import torch.nn as nn

from nsmgat.models.base import BaseModel
from nsmgat.utils.io import read_jsonl


class DummyModel(BaseModel):
    """Luon du doan nhan pho bien nhat trong tap train, bat ke dau vao.

    Dung mot tham so hoc duoc (bias 3 chieu, khoi tao thien ve nhan pho
    bien nhat) de tuong thich voi Trainer dung chung - can it nhat 1 tham
    so de AdamW/GradScaler khong loi khi khong co gi de cap nhat. Khong
    phai mo hinh that, chi de kiem thu ha tang.
    """

    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()
        train_records = read_jsonl(cfg["data"]["train_path"])
        majority_label = collections.Counter(r["label"] for r in train_records).most_common(1)[0][0]

        init_logits = torch.zeros(3)
        init_logits[majority_label] = 5.0
        self.bias = nn.Parameter(init_logits)
        self.majority_label = majority_label

    def forward(self, batch: Dict[str, Any]) -> torch.Tensor:
        batch_size = batch["labels"].shape[0]
        return self.bias.unsqueeze(0).expand(batch_size, -1)
