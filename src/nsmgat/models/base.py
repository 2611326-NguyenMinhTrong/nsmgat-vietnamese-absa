"""Interface BaseModel - hop dong bat bien cho moi mo hinh phan loai ACSA.

CHOT O S0.2 - KHONG SUA SAU BUOC NAY. Moi baseline (PhoBERT o S1.1,
Sentic-GCN o S1.2) va mo hinh de xuat (NS-MGAT o S4.3) deu ke thua class nay.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

import torch
import torch.nn as nn


class BaseModel(nn.Module, ABC):
    """Interface chung cho moi mo hinh phan loai ACSA.

    `batch` (sinh ra tu collate_fn trong data/dataset.py) chua cac key:
      - input_ids, attention_mask: token hoa cau (+ khia canh, sentence-pair)
      - aspect_text: chuoi khia canh goc (vd "BATTERY"); tung model tu
        quyet dinh cach dung (nhung vao sentence-pair, tra cuu embedding, ...)
      - uid, word_ids, phenomenon: thong tin phu (list thuong, khong phai tensor)
      - edge_index, edge_type, edge_conf, edge_view: do thi da gop batch
        theo kieu block-diagonal; co the rong voi baseline khong dung do thi
      - labels: nhan vang, shape (B,)
      - n_tokens: so token thuc cua tung mau trong batch

    Ghi chu (S0.4): ban dau S0.2 du kien key "aspect_ids", nhung dataset.py
    (S0.4) tra ve "aspect_text" (chuoi tho) de linh hoat hon - sua lai
    docstring nay cho khop thuc te. Day chi la sua mo ta, KHONG doi chu ky
    ham forward()/explain()/count_params() ben duoi.
    """

    @abstractmethod
    def forward(self, batch: Dict[str, Any]) -> torch.Tensor:
        """batch -> logits, shape (B, 3)."""

    def explain(self, batch: Dict[str, Any]) -> List[Dict]:
        """Tra ve duong dan ly do cho tung mau trong batch.

        Mac dinh tra [] - dung cho cac baseline khong giai thich duoc.
        """
        return []

    def count_params(self) -> int:
        """Tong so tham so co the huan luyen (requires_grad=True)."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
