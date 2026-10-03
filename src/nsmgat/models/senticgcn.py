"""[CD1.6b / S1.2] Sentic-GCN — GCN tren cay phu thuoc co trong so cam xuc.

Bai goc: Liang, Su, Gui, Cambria & Xu, "Aspect-based sentiment analysis via
affective knowledge enhanced graph convolutional networks", Knowledge-Based
Systems 235 (2022) 107643.

Vai tro trong thang baseline: bac tren cua `asgcn`. Hieu so `asgcn` -> `senticgcn`
do xem TRI THUC CAM XUC dang bao nhieu diem, sau khi `asgcn` da do xong phan cu phap.


KHAC `asgcn` DUNG MOT THU
=========================
Gia tri trong o cua ma tran ke. Khong gi khac.

Cung bo ma hoa PhoBERT, cung `pair_mode`, cung buoc gop subword, cung truy van
attention, cung so lop GCN, cung sieu tham so, cung tap canh cua cay phu thuoc.
Lop nay ke thua `ASGCNModel` va ghi de dung hai cho: `_xay_chi_so` (lay them diem
tung token) va `_ma_tran_ke` (nhan trong so vao).


CONG THUC — THEO BAI BAO, KHONG THEO MA NGUON
=============================================
Cong thuc (1) den (4) va Thuat toan 1 cua bai:

    D_ij = 1 neu w_i, w_j co quan he phu thuoc, HOAC i = j
    S_ij = SenticNet(w_i) + SenticNet(w_j)        <- TONG diem CA HAI dau canh
    T_ij = 1 neu w_i hoac w_j la tu khia canh
    A_ij = D_ij x (S_ij + T_ij + 1)

Ma nguon chinh chu tren github.com/BinLiang-NLP/Sentic-GCN LECH voi bai o ba cho,
va day la ban cai dat theo BAI:

  1. Ma lay diem cua MOT token roi ghi vao canh; bai lay TONG hai dau.
  2. Ma cho tu la trong so 0, tuc token bi cat khoi do thi; bai co so hang +1 lam
     nen nen canh van mang trong so 1. Voi tu dien tieng Viet phu 83 %, hieu theo
     ma se cat nham 17 % token ma khong co gi bao loi.
  3. Ma cong don `sentic += 1` trong vong lap con nen trong so phu thuoc thu tu
     duyet; bai khong co chuyen do.

He qua dep cua so hang +1: tu dien rong thi A = D, tuc DUNG ma tran ke nhi phan
cua `asgcn`. `senticgcn` la mo rong ngat cua `asgcn`, thang baseline sach san.


HAI CHO LECH KHOI BAI GOC — GIONG HET `asgcn`
=============================================
T_ij LUON BANG 0. UIT-ViSFD la aspect-category: muoi ma khia canh khong bao gio
xuat hien trong cau, nen khong token nao la "tu khia canh". Bang 4 cua bai do
duoc cho nay dang bao nhieu: bo T lam Rest14 tut tu 84,03 xuong 82,92, Lap14
77,90 xuong 76,35, tuc 1,1 den 1,8 diem.

MASKING THEO KHIA CANH (cong thuc 9, 10) cung bo, va truy van attention lay tu
bieu dien ve khia canh cua cap cau. Y nguyen cach `asgcn` da lam, xem docstring
cua `models/asgcn.py`.


MAU SO CO THE AM — CHAY Y HET BAI GOC
=====================================
Cong thuc (7) chuan hoa A~_i = A_i/(E_i + 1) voi E_i = sum_j A_ij. O `asgcn`,
E_i la SO HANG XOM nen mau so >= 2. O day E_i la TONG CO DAU cua diem cam xuc
vung lan can, nen mau so AM DUOC, va khi am thi ca hang doi dau.

Do that tren UIT-ViSFD: 0,079 % token co mau so <= 0, 3,70 % Example dinh it nhat
mot token nhu vay, |mau so| nho nhat la 1,1e-3 nen khuech dai nhieu nhat 909 lan.
Khong token nao co |mau so| < 1e-3, nghia la KHONG sinh NaN.

Hoc vien chot 03/10/2026: chay y het bai goc, khong kep mau so, khong dich thang
diem. Doi dau la dieu cong thuc quy dinh chu khong phai loi cai dat. `GCNLayer`
chi co mot DAY BAY o nguong 1e-6, khong bao gio kich hoat tren du lieu nay.

Hien tuong nay dang mot quan sat trong bao cao: mot bo chuan hoa thiet ke de DEM
duoc dem dung cho TONG CO DAU, nen mat nghia dung o nhung token mang cam xuc manh
nhat. Bai khong ban, du voi SenticNet tieng Anh cung xay ra (Bang 1: "Bad" -0,800
cong "Balefully" -0,810 da am).


TU DIEN CAM XUC — KHAC BAN CHAT VOI SenticNet
=============================================
SenticNet la tri thuc thuong thuc BEN NGOAI, khong biet gi ve bo du lieu. Con
`data/lexicon_from_train.json` duoc quy nap TU NHAN CUA TAP TRAIN o CD1.4a.

Khong co ro ri sang tap test, nen hop le ve ky thuat. Nhung ve dien giai thi khac
han: neu `senticgcn` thang `asgcn`, mot phan co the den tu thong tin nhan cua
train di vong vao trong so canh, chu khong phai tu "tri thuc cam xuc" theo nghia
cua bai. PHAI noi ro cho nay trong muc 4.3 cua bao cao.

`scripts/build_affective_lexicon.py` thuoc S3.2, chua toi luot, nen o day khong
dung tu dien moi nao. Cung ly do, lop nay KHONG tao `graphs/affective.py` (cung
thuoc S3.2) ma tinh trong so ngay trong mo hinh — dung cach `ASGCNModel` da lam
voi do thi cu phap.

Do phu do duoc: 83,3 % token tap train, 81,4 % tap test, khong Example nao rong.
Hinh 3 cua bai cho thay tren 60 % thi diem so tang deu, nen 83 % nam trong vung
tot theo chinh do thi cua tac gia.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn

from nsmgat.models.asgcn import ASGCNModel

MAC_DINH_TU_DIEN = "data/lexicon_from_train.json"


class SenticGCNModel(ASGCNModel):
    """`ASGCNModel` voi ma tran ke mang trong so cam xuc thay vi 0/1."""

    def __init__(self, cfg: Dict[str, Any], encoder: Optional[nn.Module] = None):
        # Nap tu dien TRUOC super().__init__ vi super goi `_xay_chi_so`, ma buoc
        # do can diem de dung chi muc. Gan thuoc tinh thuong truoc nn.Module.__init__
        # la hop le: nn.Module.__setattr__ chi chan Parameter va Module.
        self.tu_dien = self._nap_tu_dien(cfg)
        super().__init__(cfg, encoder)

    # --- Tu dien cam xuc ------------------------------------------------------

    @staticmethod
    def _nap_tu_dien(cfg: Dict[str, Any]) -> Dict[str, float]:
        duong = Path(cfg.get("model", {}).get("lexicon_path", MAC_DINH_TU_DIEN))
        if not duong.exists():
            raise FileNotFoundError(
                f"Khong thay tu dien cam xuc: {duong}\n"
                "  `senticgcn` can mot bang diem cam xuc cho tung tu. Dung lai bang da co\n"
                "  tu CD1.4a, hoac sua `model.lexicon_path` trong configs/senticgcn.yaml.\n"
                "  Dung lenh nay de dung lai neu file bi mat:\n"
                "      python scripts/build_lexicon_from_train.py"
            )
        return json.loads(duong.read_text(encoding="utf-8"))

    def _diem(self, token: str) -> float:
        """Diem cam xuc cua mot token. Khong co trong tu dien thi tra 0 — dung
        cong thuc (2): "SenticNet(w_i) = 0 denotes the word w_i is a neutral word
        or inexistent in SenticNet". Canh van song nho so hang +1 o cong thuc (4)."""
        if token in self.tu_dien:
            return float(self.tu_dien[token])
        return float(self.tu_dien.get(token.lower(), 0.0))

    # --- Chi muc ---------------------------------------------------------------

    def _xay_chi_so(self, cfg: Dict[str, Any]) -> None:
        """Dung chi muc canh nhu `asgcn`, roi lay them diem cam xuc tung token.

        Diem lay tu CHINH khoa cau chu khong doc lai file: khoa cau da la
        "token1 \\x1f token2 ... \\x1e heads", nen tach nguoc ra la duoc dung bo
        token ma chi muc canh dang dung. Cung mot nguon thi khong the lech nhau,
        va khong ton them mot luot doc 34.000 ban ghi.
        """
        super()._xay_chi_so(cfg)

        self.khoa_to_diem: Dict[str, torch.Tensor] = {}
        for khoa in self.khoa_to_canh:
            tokens = khoa.split("\x1e")[0].split("\x1f")
            self.khoa_to_diem[khoa] = torch.tensor(
                [self._diem(t) for t in tokens], dtype=torch.float32
            )

    # --- Ma tran ke ------------------------------------------------------------

    def _ma_tran_ke(self, uids: List[str], so_token: int, device, dtype) -> torch.Tensor:
        """A_ij = D_ij x (s_i + s_j + 1). T_ij = 0, xem docstring dau file.

        Lay D tu lop cha roi nhan trong so vao: `adj` bang 0 ngoai cac canh nen
        phep nhan tu dong giu dung thua so D_ij, va moi buoc kiem uid, cat bot cau
        qua dai deu dung chung mot duong voi `asgcn`.
        """
        adj = super()._ma_tran_ke(uids, so_token, device, dtype)  # D_ij, chi 0 va 1

        for b, uid in enumerate(uids):
            diem = self.khoa_to_diem[self.uid_to_khoa[uid]]
            s = torch.zeros(so_token, dtype=dtype, device=device)
            k = min(len(diem), so_token)  # cau dai hon max_seq_len thi bi cat bot
            s[:k] = diem[:k].to(device=device, dtype=dtype)
            adj[b] = adj[b] * (s.unsqueeze(1) + s.unsqueeze(0) + 1.0)

        return adj
