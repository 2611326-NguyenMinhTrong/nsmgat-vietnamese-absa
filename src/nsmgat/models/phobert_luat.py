"""[CD1.11d] PhoBERTLuatModel — PhoBERT co them tin hieu luat ve phu dinh va chuyen y.

THI NGHIEM CAN THIEP, KHONG PHAI MO HINH DE XUAT
-------------------------------------------------
Khac `phobert` DUNG MOT thu: moi tu cua ve cau duoc cong them mot vector theo nhan luat (xem
data/tin_hieu_luat.py) truoc khi vao bo ma hoa. Cach doc ra, ham mat mat, sieu tham so giu nguyen.
Hieu so `phobert_luat` - `phobert` vi vay tra loi: dua cau truc phu dinh, chuyen y vao PhoBERT dang
gia bao nhieu diem, dung cau hoi muc 5.6.2 cua bao cao de ngo.

Cong vao dau vao chu khong noi vao dau ra vi: tu phu dinh viet tat, ve cau sau "nhung" la thu bo ma
hoa can biet NGAY KHI doc cau, va nho self-attention no noi duoc nhan do voi ve khia canh cua cap cau.

BA RANG BUOC DE HIEU SO SACH
----------------------------
1. Khoi tao bang 0: ban dau mo hinh trung voi `phobert`, luat chi co tac dung neu hoc duoc la co ich.
2. `_weight=` khong rut so ngau nhien: them lop nay khong lam lech day ngau nhien, nen cung seed thi
   lop phan loai, thu tu mini-batch va dropout trung voi `phobert`. Rut so o day la moi seed thanh
   mot lan khoi tao khac, hieu so se lan them dao dong do khoi tao.
3. `padding_idx=0`: tu khong co nhan giu nguyen embedding cua PhoBERT trong suot qua trinh huan
   luyen. Binh luan khong co tu khoa nao vi vay co dau vao y het `phobert`, tro thanh nhom doi chung
   tu nhien (scripts/phan_tich_tin_hieu_luat.py).

HAN CHE DA BIET TRUOC KHI CHAY
------------------------------
Nhan giong nhau cho moi khia canh cua mot binh luan, trong khi muc 5.6.3 noi tin hieu phai khac nhau
theo khia canh. Khia canh cua UIT-ViSFD khong co vi tri trong cau, muon gan theo khia canh phai co tu
dien cum tu la viec cua Chuyen de 2. Ket qua am o day KHONG bac bo huong co tin hieu theo khia canh.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn

from nsmgat.data.tin_hieu_luat import SO_NHAN, tin_hieu_cua
from nsmgat.models.asgcn import ASGCNModel
from nsmgat.models.phobert import PhoBERTClassifier
from nsmgat.utils.io import read_jsonl


class PhoBERTLuatModel(PhoBERTClassifier):
    """`model.tin_hieu_luat` trong config chon kenh nao bat: phu_dinh, chuyen_y hoac ca hai.

    Tham so `encoder` chi dung khi KIEM THU, giong PhoBERTClassifier.
    """

    def __init__(self, cfg: Dict[str, Any], encoder: Optional[nn.Module] = None):
        super().__init__(cfg, encoder)
        kenh = tuple(cfg.get("model", {}).get("tin_hieu_luat", ()))
        la = set(kenh) - set(SO_NHAN)
        if la or not kenh:
            raise ValueError(f"model.tin_hieu_luat phai la tap con khac rong cua {sorted(SO_NHAN)}, dang la {kenh}")

        hidden = self.classifier.in_features
        self.nhung_luat = nn.ModuleDict({
            k: nn.Embedding(SO_NHAN[k], hidden, padding_idx=0, _weight=torch.zeros(SO_NHAN[k], hidden))
            for k in kenh
        })
        self._xay_chi_so(cfg)

    def _xay_chi_so(self, cfg: Dict[str, Any]) -> None:
        """uid -> nhan cua tung tu. Cung cach ASGCNModel: doc ca bon tap, vi nhan chi suy ra tu mat chu
        cua tu, khong dung nhan cam xuc, nen khong ro ri. Moi binh luan chi tinh mot lan."""
        self.uid_to_nhan: Dict[str, Dict[str, List[int]]] = {}
        da_tinh: Dict[tuple, Dict[str, List[int]]] = {}
        for key in ("train_path", "dev_path", "test_path", "diagnostic_path"):
            path = cfg.get("data", {}).get(key)
            if not path or not Path(path).exists():
                continue
            for record in read_jsonl(path):
                khoa = tuple(record["tokens"])
                if khoa not in da_tinh:
                    da_tinh[khoa] = tin_hieu_cua(khoa)
                self.uid_to_nhan[record["uid"]] = da_tinh[khoa]

    def _nhan_subword(self, batch: Dict[str, Any], kenh: str, L: int, device) -> torch.Tensor:
        """(B, L): nhan cua tung subword. Ve khia canh va token dac biet giu nhan 0.

        Nhan dien ve cau bang cau truc cap cau (`_cac_ve`), khong so word_id voi n_tokens: khi cau bi
        cat bot thi phep so do sai, da xay ra o ASGCN 01/10/2026.
        """
        ra = torch.zeros((len(batch["uid"]), L), dtype=torch.long, device=device)
        for b, (uid, danh_sach) in enumerate(zip(batch["uid"], batch["word_ids"])):
            if uid not in self.uid_to_nhan:
                raise KeyError(
                    f"uid '{uid}' khong co trong chi muc tin hieu luat. Kiem tra cac duong dan "
                    "data.* trong config co tro dung file dang danh gia khong"
                )
            doan = ASGCNModel._cac_ve(danh_sach, L)
            if not doan:
                continue
            dau, cuoi = doan[0]
            nhan = self.uid_to_nhan[uid][kenh]
            for l in range(dau, cuoi + 1):
                w = danh_sach[l]
                if w is not None and w < len(nhan):
                    ra[b, l] = nhan[w]
        return ra

    def forward(self, batch: Dict[str, Any]) -> torch.Tensor:
        input_ids = batch["input_ids"]
        vao = self.encoder.get_input_embeddings()(input_ids)
        for kenh, nhung in self.nhung_luat.items():
            vao = vao + nhung(self._nhan_subword(batch, kenh, input_ids.size(1), input_ids.device))
        ra = self.encoder(inputs_embeds=vao, attention_mask=batch["attention_mask"])
        return self.classifier(self.dropout(ra.last_hidden_state[:, 0]))
