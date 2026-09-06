"""[CD1.4a] LexiconModel — baseline phan loai bang tu dien cam xuc.

Ban GVHD duyet (docs/Tom_Tat_Dinh_Huong_Final.docx muc 1) liet ke "mo hinh
dua tren tu dien" trong nhom can thuc nghiem lai. Day la SAN TUYET DOI cua
bang ket qua: moi mo hinh khac phai hon no, neu khong thi khong dang dung.

CACH HOAT DONG
--------------
1. Tra cuu diem cam xuc cua tung token trong tu dien (sinh boi
   scripts/build_lexicon_from_train.py, CHI tu tap train)
2. Rut 2 dac trung cho moi Example:
       mean_score : trung binh diem cua cac token TRA CUU DUOC
       coverage   : ti le token tra cuu duoc  (cho biet co bao nhieu bang chung)
3. Mot lop Linear(2, 3) hoc nguong quyet dinh tu tap train

Phan HOC DUOC chi co 9 tham so (2x3 trong so + 3 bias) — thuan tuy de hieu
chinh nguong. Moi tri thuc cam xuc nam trong tu dien, khong nam trong tham so.
Vi sao khong dat nguong bang tay: se phai bia ra mot con so ("score > 0,1 thi
la tich cuc") ma khong co co so nao bien minh. Hoc tu train thi nguong co
nguon goc kiem chung duoc.

GIOI HAN CO BAN — PHAI NEU TRONG BAO CAO
-----------------------------------------
Mo hinh nay MU KHIA CANH. Nhan khia canh cua UIT-ViSFD la ma pham tru tieng
Anh (BATTERY, CAMERA, SER&ACC...) KHONG xuat hien trong cau tieng Viet, nen
khong tra cuu tu dien duoc. Hau qua: moi Example cua CUNG MOT CAU deu nhan
cung mot du doan.

Do duoc: 47,0% cau co cac khia canh TRAI NHAN nhau => tran tuyet doi cua mo
hinh mu khia canh la 80,2% accuracy. Du tu dien hoan hao cung khong vuot duoc.
Con so nay chinh la thu dinh luong "bai toan can nhin khia canh den muc nao".

VE RO RI DU LIEU
----------------
Tu dien sinh TU TAP TRAIN. Mo hinh co doc token cua dev/test luc suy luan —
day la dac trung dau vao, khong phai nhan, nen khong phai ro ri.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import torch
import torch.nn as nn

from nsmgat.models.base import BaseModel
from nsmgat.utils.io import read_jsonl

SO_DAC_TRUNG = 2  # [mean_score, coverage]


class LexiconModel(BaseModel):
    """Phan loai bang tu dien cam xuc + mot lop hieu chinh nguong."""

    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()

        lexicon_path = Path(
            cfg.get("model", {}).get("lexicon_path", "data/lexicon_from_train.json")
        )
        if not lexicon_path.exists():
            raise FileNotFoundError(
                f"Khong thay tu dien: {lexicon_path}\n"
                "Chay truoc: python scripts/build_lexicon_from_train.py"
            )
        self.lexicon: Dict[str, float] = json.loads(lexicon_path.read_text(encoding="utf-8"))

        # collate_fn khong dua token tho vao batch (chi co input_ids da tokenize
        # bang PhoBERT), nen tu dung chi muc uid -> tokens. Cung cach DummyModel
        # doc train_path trong __init__.
        self.uid_to_tokens: Dict[str, List[str]] = {}
        for key in ("train_path", "dev_path", "test_path", "diagnostic_path"):
            path = cfg["data"].get(key)
            if path and Path(path).exists():
                for record in read_jsonl(path):
                    self.uid_to_tokens[record["uid"]] = record["tokens"]

        self.calibrate = nn.Linear(SO_DAC_TRUNG, 3)

        # Dac trung la TAT DINH (chi phu thuoc token + tu dien, khong phu thuoc
        # tham so) nen tinh mot lan roi nho.
        #
        # DO THUC TE: cache nay KHONG rut ngan train_time_sec dang ke (197,8s so
        # voi 189,6s truoc khi cache). Nut that that su nam o ACSADataset:
        # __getitem__ goi tokenizer PhoBERT MOI LAN truy cap, moi epoch — do
        # duoc ~12s/epoch, tuc ~127s cho 11 epoch. LexiconModel khong he dung
        # input_ids, nen toan bo chi phi do la lang phi voi rieng no.
        # Giu cache vi no dung ve mat khai niem va vo hai; van de tokenize la
        # cua ha tang dung chung — xem GAP-008.
        self._cache: Dict[str, tuple[float, float]] = {}

    def _dac_trung(self, uid: str) -> tuple[float, float]:
        """(mean_score, coverage) cho mot Example. Co nho ket qua."""
        if uid in self._cache:
            return self._cache[uid]

        tokens = self.uid_to_tokens.get(uid, [])
        diem = [self.lexicon[t.lower()] for t in tokens if t.lower() in self.lexicon]
        ket_qua = (sum(diem) / len(diem), len(diem) / len(tokens)) if diem else (0.0, 0.0)

        self._cache[uid] = ket_qua
        return ket_qua

    def forward(self, batch: Dict[str, Any]) -> torch.Tensor:
        device = batch["labels"].device
        features = torch.tensor(
            [self._dac_trung(uid) for uid in batch["uid"]], dtype=torch.float, device=device
        )
        return self.calibrate(features)

    def explain(self, batch: Dict[str, Any]) -> List[Dict]:
        """Liet ke token nao dong gop bao nhieu — tu dien GIAI THICH DUOC.

        Day la uu the that cua baseline nay so voi PhoBERT: moi du doan truy
        nguoc duoc ve tung tu cu the. Dung o muc 5.3 (ca dien hinh) cua bao cao.
        """
        ket_qua = []
        for uid in batch["uid"]:
            tokens = self.uid_to_tokens.get(uid, [])
            dong_gop = [
                {"token": t, "diem": self.lexicon[t.lower()]}
                for t in tokens
                if t.lower() in self.lexicon and abs(self.lexicon[t.lower()]) > 0.05
            ]
            dong_gop.sort(key=lambda d: -abs(d["diem"]))
            mean_score, coverage = self._dac_trung(uid)
            ket_qua.append(
                {
                    "uid": uid,
                    "mean_score": round(mean_score, 4),
                    "coverage": round(coverage, 4),
                    "token_dong_gop_manh_nhat": dong_gop[:10],
                }
            )
        return ket_qua
