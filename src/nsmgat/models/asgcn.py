"""[CD1.6a / S1.2] ASGCNModel — baseline GCN tren cay phu thuoc cu phap.

VI TRI TRONG THANG BAC BASELINE
-------------------------------
    lexicon   mu khia canh                  acc 0,7469
    bilstm    hoc tu dau, thay khia canh    acc 0,8642
    phobert   + tri thuc tien huan luyen    acc 0,9186
    ASGCN     + CU PHAP                     <- step nay
    senticgcn + tri thuc cam xuc            (CD1.6b)

Moi bac them DUNG MOT thu. Hieu so phobert <-> asgcn tra loi: **cay phu thuoc
dang gia bao nhieu diem** khi moi thu khac giu nguyen. Vi vay bo ma hoa van la
PhoBERT y nguyen nhu `phobert`, khong doi sang BiLSTM+GloVe nhu bai goc — doi
hai thu mot luc thi hieu so khong con do duoc gi.

BA CHO PHAI LECH KHOI BAI GOC, VA VI SAO
----------------------------------------
ASGCN goc lam *aspect-term*: khia canh la mot cum tu NAM TRONG cau, co vi tri
cu the (chi so dau tau, do dai m). UIT-ViSFD la *aspect-category*: `BATTERY`
la ma khong xuat hien o dau trong cau tieng Viet. Mat vi tri khia canh thi mat
luon hai co che cot loi cua bai:

1. **Trong so theo vi tri** (cong thuc 5) can tau va m -> BO. Khong co gi thay
   the truc tiep; viec "uu tien token gan khia canh" o day do attention hoc.
2. **Aspect-specific masking** (cong thuc 7) ep ve 0 moi token khong thuoc
   khia canh -> BO. Neu ap dung thi ca cau bi ep ve 0, mo hinh khong con gi.
3. **Attention truy hoi** (cong thuc 8) dung cac token khia canh TRONG CAU lam
   truy van -> lay bieu dien cua VE KHIA CANH trong cap cau
   `<s> cau </s></s> pin </s>`. Khia canh khong nam trong cau nhung co mat
   trong dau vao duoi dang mot ve rieng, nen van co bieu dien that de lam truy
   van, khong phai dung mot embedding hoc tu dau. Day la cho gan cong thuc (8)
   nhat ma bai toan aspect-category cho phep.

   Hoc vien chot 02/10/2026. Ban dau viet bang nn.Embedding rieng, nhung nhu
   vay bo ma hoa KHONG he biet dang duoc hoi ve khia canh nao: cung mot cau
   thi moi khia canh dung chung mot bieu dien, chi khac o buoc gop cuoi. Nhu
   the `asgcn` mu khia canh o tang ma hoa, thap hon ca `bilstm` (noi vector
   khia canh vao tung token truoc khi vao LSTM), trong khi nhan cua bac thang
   lai ghi la "cong them cu phap". Hieu so phobert <-> asgcn se lan hai bien.

VI SAO `pair_mode` PHAI BAT
---------------------------
Khac `phobert` o cho ta con can `word_ids` anh xa subword ve dung chi so token
cua CAU, de khop voi chi so trong cay phu thuoc. Hai viec nay song duoc voi
nhau: hai ve cach nhau bang cac o dac biet (word_id None) nen tach duoc bang
cau truc, xem `_cac_ve`. KHONG tach bang cach so word_id voi n_tokens: khi cau
bi cat bot (truncation="only_first") thi ve khia canh mang chi so nho hon
n_tokens that, va phep so do bao "khong tim thay ve khia canh" — da xay ra that
o seed 42 tren Colab 01/10/2026.

Giu nguyen duoc tinh than cua bai o cho quan trong nhat: GCN sinh ra TRONG SO
chu khong sinh ra bieu dien cuoi. Vector dua vao lop phan loai van la tong co
trong so cua bieu dien BO MA HOA, dung nhu cong thuc (10) cua bai goc.

Ba cho lech nay phai ghi vao muc 4.3 cua bao cao. Hoi dong co the hoi "co con
la ASGCN nua khong" — cau tra loi trung thuc la: giu dong do thi cu phap + GCN
2 lop + attention lay tu GCN, bo phan phu thuoc vi tri khia canh.

CHUAN HOA: chia cho (d_i + 1)
-----------------------------
Dung `normalize="row_plus1"`, la cong thuc (3) cua bai goc. Hoc vien chot
02/10/2026 sau khi doc bai. Chi tiet vi sao khong phai `row` hay `sym`: xem
docstring cua models/layers.py.

DO THI LAY TU DAU
-----------------
`collate_fn` hien tra `edge_index` RONG co chu y — viec gop do thi theo batch
la cua S3.3, chua toi luot. Nen mo hinh nay tu dung chi muc uid -> canh ngay
trong __init__, cung cach LexiconModel tu dung uid -> tokens.

Tiet kiem bo nho: 23.872 Example chi ung voi 7.671 CAU khac nhau, va do thi
chi phu thuoc cau (tokens + heads), khong phu thuoc khia canh. Nen chi muc
luu theo cau, va luu dang cap chi so (2 cot) chu khong luu ma tran day — ma
tran 128x128 cho moi cau se ton khoang 500 MB.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
from transformers import AutoModel

from nsmgat.graphs.adjacency import edges_to_adj
from nsmgat.graphs.syntactic import SyntacticGraphBuilder
from nsmgat.models.base import BaseModel
from nsmgat.models.layers import GCNLayer
from nsmgat.schema import Example
from nsmgat.utils.io import read_jsonl


class ASGCNModel(BaseModel):
    """PhoBERT -> gop subword ve token -> 2 lop GCN tren cay phu thuoc ->
    attention voi truy van la embedding khia canh -> Linear 3 lop.

    Tham so `encoder` chi dung khi KIEM THU, giong PhoBERTClassifier: cho phep
    truyen encoder ti hon de test chay trong mot giay, khong phai tai 540 MB.
    """

    def __init__(self, cfg: Dict[str, Any], encoder: Optional[nn.Module] = None):
        super().__init__()
        mcfg = cfg.get("model", {})

        # Thuoc tinh PHAI ten la `encoder`: trainer._build_optimizer tim dung
        # ten nay de tach learning rate encoder khoi dau phan loai.
        ten = mcfg.get("encoder_name", "vinai/phobert-base-v2")
        self.encoder = encoder if encoder is not None else AutoModel.from_pretrained(ten)
        hidden = int(getattr(self.encoder.config, "hidden_size", mcfg.get("hidden_dim", 768)))

        so_lop = int(mcfg.get("gcn_layers", 2))
        chuan_hoa = str(mcfg.get("normalize", "row_plus1"))
        dropout = float(mcfg.get("dropout", 0.1))

        self.gcn = nn.ModuleList(
            GCNLayer(hidden, hidden, dropout=dropout, normalize=chuan_hoa)
            for _ in range(so_lop)
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden, 3)

        self.link_roots = bool(mcfg.get("link_roots", False))
        self._xay_chi_so(cfg)

        # KHONG co nn.Embedding cho khia canh: truy van attention lay tu bieu
        # dien that cua ve khia canh trong cap cau (xem docstring muc 3).
        # Nho vay `asgcn` khac `phobert` dung mot thu — chay GCN tren cay phu
        # thuoc roi gop theo khia canh, thay vi lay token <s>.

    # --- Chi muc do thi va khia canh ------------------------------------------

    def _xay_chi_so(self, cfg: Dict[str, Any]) -> None:
        """uid -> khoa cau, va khoa cau -> cap chi so canh (E, 2) dang [dst, src].

        Doc CA train/dev/test/diagnostic: day la do thi cu phap suy ra tu cay
        phu thuoc co san trong du lieu, khong phai thong ke hoc duoc tu nhan,
        nen khong co ro ri du lieu. Khac han bang tu vung cua `bilstm` — cai do
        chi duoc doc tap train.
        """
        builder = SyntacticGraphBuilder(link_roots=self.link_roots)

        self.uid_to_khoa: Dict[str, str] = {}
        self.khoa_to_canh: Dict[str, torch.Tensor] = {}

        for key in ("train_path", "dev_path", "test_path", "diagnostic_path"):
            path = cfg["data"].get(key)
            if not path or not Path(path).exists():
                continue
            for record in read_jsonl(path):
                khoa = self._khoa_cau(record)
                self.uid_to_khoa[record["uid"]] = khoa
                if khoa in self.khoa_to_canh:
                    continue
                vi_du = Example.from_dict(record)
                adj = edges_to_adj(builder.build(vi_du), len(vi_du.tokens))
                self.khoa_to_canh[khoa] = adj.nonzero()  # (E, 2): [dst, src]

    @staticmethod
    def _khoa_cau(record: Dict[str, Any]) -> str:
        """Khoa gop theo CAU. Gom ca heads: hai cau giong chu nhung khac cay
        phu thuoc thi phai la hai do thi khac nhau."""
        return "\x1f".join(record["tokens"]) + "\x1e" + ",".join(str(h) for h in record["heads"])

    # --- Cac buoc cua forward -------------------------------------------------

    @staticmethod
    def _cac_ve(danh_sach: List[Optional[int]], L: int) -> List[Tuple[int, int]]:
        """Tach `word_ids` thanh cac doan lien tiep KHONG phai token dac biet.

        Cap cau co dang `<s> cau </s></s> khia_canh </s>`, cac o dac biet mang
        word_id None, nen doan dau la VE CAU va doan cuoi la VE KHIA CANH.

        Vi sao khong so `word_id >= n_tokens` nhu ban dau: tokenizer cat bot VE
        CAU khi qua max_seq_len (truncation="only_first"), nen ve khia canh co
        the mang chi so NHO HON n_tokens that. Luc do phep so chi so bao khong
        tim thay ve khia canh — da xay ra that khi chay seed 42 tren Colab
        01/10/2026, trong khi tap dev khong co cau nao du dai de lo ra.
        """
        doan: List[Tuple[int, int]] = []
        dau: Optional[int] = None
        for l, w in enumerate(danh_sach[:L]):
            if w is None:
                if dau is not None:
                    doan.append((dau, l - 1))
                    dau = None
                continue
            if dau is None:
                dau = l
        if dau is not None:
            doan.append((dau, min(L, len(danh_sach)) - 1))
        return doan

    def _gop_subword(
        self, h: torch.Tensor, batch: Dict[str, Any], so_token: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """(B, L, H) subword -> (B, N, H) muc token, lay trung binh.

        Tra ve them mask (B, N): 1.0 o token co it nhat mot subword. Token bi
        cat mat vi cau dai hon max_seq_len se co mask 0 — dung, vi khong co
        bieu dien nao cho no.
        """
        B, L, H = h.shape
        # Chan theo do dai THAT CUA TUNG MAU, khong theo do dai lon nhat trong
        # batch. Do duoc 02/10/2026: chan theo batch thi khi `pair_mode` bat,
        # subword cua ve khia canh (word_id = n, n+1, ...) van < max cua batch
        # nen lot vao o token cua cau — cau 22 token thanh 25 token co mask.
        # Chan theo tung mau thi `pair_mode` bat hay tat deu dung.
        wid = torch.full((B, L), -1, dtype=torch.long, device=h.device)
        for b, danh_sach in enumerate(batch["word_ids"]):
            doan = self._cac_ve(danh_sach, L)
            if not doan:
                continue
            dau, cuoi = doan[0]  # VE CAU luon la doan dau tien
            for l in range(dau, cuoi + 1):
                w = danh_sach[l]
                if w is not None and w < so_token:
                    wid[b, l] = w

        co = (wid >= 0).to(h.dtype)  # (B, L)
        an_toan = wid.clamp(min=0)

        tong = torch.zeros((B, so_token, H), dtype=h.dtype, device=h.device)
        tong.scatter_add_(1, an_toan.unsqueeze(-1).expand(-1, -1, H), h * co.unsqueeze(-1))
        dem = torch.zeros((B, so_token), dtype=h.dtype, device=h.device)
        dem.scatter_add_(1, an_toan, co)

        token = tong / dem.clamp(min=1.0).unsqueeze(-1)
        return token, (dem > 0).to(h.dtype)

    def _ma_tran_ke(self, uids: List[str], so_token: int, device, dtype) -> torch.Tensor:
        adj = torch.zeros((len(uids), so_token, so_token), dtype=dtype, device=device)
        for b, uid in enumerate(uids):
            khoa = self.uid_to_khoa.get(uid)
            if khoa is None:
                raise KeyError(
                    f"uid '{uid}' khong co trong chi muc do thi. Kiem tra cac duong dan "
                    "data.* trong config co tro dung file dang danh gia khong"
                )
            cap = self.khoa_to_canh[khoa]
            if cap.numel() == 0:
                continue
            dst, src = cap[:, 0], cap[:, 1]
            giu = (dst < so_token) & (src < so_token)  # cau bi cat bot khi qua dai
            adj[b, dst[giu].to(device), src[giu].to(device)] = 1.0
        return adj

    def _truy_van(self, h: torch.Tensor, batch: Dict[str, Any]) -> torch.Tensor:
        """Bieu dien ve khia canh trong cap cau -> vector truy van (B, H).

        Nhan dien ve khia canh bang cau truc cap cau (xem `_cac_ve`), KHONG
        bang cach so word_id voi n_tokens — cau bi cat thi phep so do sai.
        Lay trung binh cac subword cua ve do.
        """
        B, L, H = h.shape
        la_khia_canh = torch.zeros((B, L), dtype=h.dtype, device=h.device)
        for b, danh_sach in enumerate(batch["word_ids"]):
            doan = self._cac_ve(danh_sach, L)
            if len(doan) < 2:  # chi co ve cau -> pair_mode dang tat
                continue
            dau, cuoi = doan[-1]  # VE KHIA CANH luon la doan cuoi cung
            la_khia_canh[b, dau : cuoi + 1] = 1.0

        dem = la_khia_canh.sum(dim=-1)
        if bool((dem == 0).any()):
            raise ValueError(
                "Khong tim thay ve khia canh trong dau vao. `asgcn` doi "
                "`data.pair_mode: true` — khia canh phai di vao duoi dang ve thu hai "
                "cua cap cau de lam truy van attention. Kiem tra configs/asgcn.yaml"
            )
        return (h * la_khia_canh.unsqueeze(-1)).sum(dim=1) / dem.unsqueeze(-1)

    def _chu_y(self, g: torch.Tensor, q: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """Trong so attention (B, N): truy van la bieu dien ve khia canh, khoa
        la dau ra GCN. Thay cho cong thuc (8) cua bai goc.

        Tach rieng khoi forward() de cong cu thu tay xem duoc mo hinh nhin vao
        token nao MA KHONG phai chep lai cong thuc — cung ly do voi
        BiLSTMModel._chu_y().
        """
        diem = torch.bmm(g, q.unsqueeze(-1)).squeeze(-1) / math.sqrt(g.size(-1))
        diem = diem.masked_fill(mask <= 0, torch.finfo(diem.dtype).min)
        return torch.softmax(diem, dim=-1)

    def forward(self, batch: Dict[str, Any]) -> torch.Tensor:
        ra = self.encoder(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
        )
        h = ra.last_hidden_state  # (B, L, H)

        so_token = int(batch["n_tokens"].max().item())
        token, mask = self._gop_subword(h, batch, so_token)
        adj = self._ma_tran_ke(batch["uid"], so_token, token.device, token.dtype)

        g = token
        for lop in self.gcn:
            # ReLU sau TUNG lop, dung cong thuc (3) cua bai goc.
            g = torch.relu(lop(g, adj, mask=mask))

        trong_so = self._chu_y(g, self._truy_van(h, batch), mask)
        # Gop BIEU DIEN BO MA HOA, khong gop dau ra GCN — cong thuc (10) bai goc.
        gop = torch.bmm(trong_so.unsqueeze(1), token).squeeze(1)  # (B, H)
        return self.classifier(self.dropout(gop))

    # explain(): KHONG ghi de, ke thua mac dinh tra ve [] — cung ly do da ghi
    # trong BiLSTMModel: chua co doan code nao tieu thu ket qua explain(), cai
    # bay gio la doan xem CD1.9 can dinh dang gi (quy tac 6). Khi CD1.9 can,
    # ghi de o day: tra ve trong_so attention + canh cu phap da dung.
