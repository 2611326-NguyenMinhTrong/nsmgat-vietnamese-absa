"""[CD1.5 / S1.1] PhoBERTClassifier — baseline fine-tune PhoBERT cho ACSA.

VI TRI TRONG CHUYEN DE
----------------------
Day la moc so sanh chinh cua Chuong 4, va la buoc dau tien cua ky nguyen
tien huan luyen trong day baseline:

    lexicon   (CD1.4a)  mu khia canh, san 80,88%      -> acc 0,7469
    bilstm    (CD1.4b)  hoc tu dau, thay khia canh    -> acc 0,8642
    phobert   (CD1.5)   co tri thuc tien huan luyen   -> ?

`bilstm` da vuot tran mu khia canh, nen cau hoi cua step nay khong con la
"co hon tu dien khong" ma la: **tri thuc tien huan luyen tieng Viet dang gia
bao nhieu diem** khi moi thu khac giu nguyen (cung du lieu, cung split, cung
do do, cung 3 seed).

DUA KHIA CANH VAO BANG CAP CAU
------------------------------
    <s> pin trau nhung man_hinh toi </s></s> pin </s>
                                             ^^^ ve khia canh

Vi sao cap cau chu khong noi mot vector khia canh nhu `bilstm`: PhoBERT da
duoc huan luyen de doc quan he giua hai ve cua mot cap, nen day la cach dung
dung so truong cua no. Doi khia canh la doi ve thu hai, mo hinh tu doc lai
ca cau duoi goc nhin khac.

Ve khia canh viet bang TIENG VIET da tach tu (`schema.ASPECT_VI`), khong phai
ma "BATTERY" — xem ly do trong schema.py. Hoc vien duyet 21/09/2026.

CHO DE SAI NHAT
---------------
PhoBERT doi van ban DA TACH TU bang VnCoreNLP ("man_hinh" la mot tu). Buoc
tien xu ly S0.3 da lam viec do, va `ASPECT_VI` cung viet theo dung quy uoc
gach duoi — neu sau nay them khia canh moi ma quen gach duoi thi mo hinh van
chay, chi la kem di ma khong bao loi.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import torch
import torch.nn as nn
from transformers import AutoModel

from nsmgat.models.base import BaseModel


class PhoBERTClassifier(BaseModel):
    """Encoder PhoBERT + dau phan loai tuyen tinh tren bieu dien token <s>.

    Tham so `encoder` chi dung khi KIEM THU: cho phep truyen vao mot encoder
    ti hon khoi tao ngau nhien, de test chay trong mot giay ma khong phai tai
    540 MB trong so that ve. Khi chay that (MODEL_REGISTRY goi voi mot tham
    so) thi encoder = None va mo hinh nap trong so tien huan luyen.
    """

    def __init__(self, cfg: Dict[str, Any], encoder: Optional[nn.Module] = None):
        super().__init__()
        mcfg = cfg.get("model", {})
        ten = mcfg.get("encoder_name", "vinai/phobert-base-v2")

        # Thuoc tinh PHAI ten la `encoder`: trainer._build_optimizer tim dung
        # ten nay de tach learning rate encoder (2e-5) khoi dau (1e-3).
        self.encoder = encoder if encoder is not None else AutoModel.from_pretrained(ten)

        hidden = int(getattr(self.encoder.config, "hidden_size", mcfg.get("hidden_dim", 768)))
        self.dropout = nn.Dropout(float(mcfg.get("dropout", 0.1)))
        self.classifier = nn.Linear(hidden, 3)

    def forward(self, batch: Dict[str, Any]) -> torch.Tensor:
        ra = self.encoder(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
        )
        # Token dau tien (<s>) gom thong tin ca cap cau — cach chuan cua
        # RoBERTa/PhoBERT cho bai toan phan loai cap cau.
        bieu_dien_cau = ra.last_hidden_state[:, 0]
        return self.classifier(self.dropout(bieu_dien_cau))
