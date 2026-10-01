"""[S1.2 / CD1.6a] GCNLayer — mot lop tich chap do thi, dung chung cho ca du an.

Ba lop con lai cua file nay (EdgeAwareAttention, MultiGraphEncoder,
CrossGraphFusion) thuoc S4.1/S4.2 cua Chuyen de 2 — CHUA cai o day.

VI SAO LOP NAY PHAI TONG QUAT
------------------------------
No se duoc dung lai o BA cho, khong duoc sua lai o cho nao:

    CD1.6a  asgcn      : 1 do thi cu phap, canh khong trong so
    CD1.6b  senticgcn  : 1 do thi cu phap, canh CO trong so (diem cam xuc)
    S4.x    NS-MGAT    : 3 do thi (syn / aff / logic), canh logic mang do tin
                         cay da hieu chinh (TypedEdge.conf)

Vi vay `forward` nhan them `edge_weight` tuy chon: nhan thang vao ma tran ke
truoc khi chuan hoa. Ba cach dung tren chi khac nhau o cho truyen gi vao
`edge_weight`, khong khac o kien truc.

QUY UOC DAU VAO
---------------
    x    (B, N, D_in)  bieu dien token, da gop ve muc token
    adj  (B, N, N)     ma tran ke DAY (dense). adj[b, i, j] > 0 nghia la co
                       canh j -> i, tuc token i NHAN tin tu token j.

Do thi cu phap cua du an (graphs/syntactic.py) da tu them self-loop cho MOI
token, ke ca token bi co lap. Nen lop nay KHONG tu them self-loop — them nua
la dem hai lan. Do cung la ly do khong co tham so `add_self_loops`: mot tham
so mac dinh sai thi som muon cung co nguoi bat nham.

CHUAN HOA
---------
`normalize="sym"` (mac dinh): D^(-1/2) A D^(-1/2), cong thuc chuan cua Kipf &
Welling. Gia dinh A doi xung — dung voi do thi cu phap cua du an vi
SyntacticGraphBuilder sinh canh theo CA HAI chieu.

`normalize="row"`: chia cho bac cua dinh nhan, tuc d_i.

`normalize="row_plus1"`: chia cho (d_i + 1). **Day moi la cong thuc ASGCN goc**
(Zhang et al. 2019, cong thuc 3): h_i = ReLU(sum_j A_ij W g_j / (d_i + 1) + b).

Cho nay de hieu sai nen ghi ro: ma tran ke cua ASGCN DA co duong cheo toan 1
("the diagonal values of A are all ones"), nen d_i = sum_j A_ij DA dem ca chinh
token do, roi bai van cong them 1 nua. Vi du cau "pin rat trau" (bac 2, 2, 3):
  row        -> chia cho 2, 2, 3
  row_plus1  -> chia cho 3, 3, 4   <- dung bai goc
Hoc vien chot 02/10/2026: `asgcn` dung `row_plus1` de tai lap trung thanh.
So `sym` voi `row` de danh lam tham do P4 o CD1.11.

`normalize="none"`: dung khi `adj` da duoc chuan hoa san tu ben ngoai.

BAC BANG 0 KHONG SINH NaN
-------------------------
Hai truong hop co bac 0: token dem (padding) va — neu co ai do truyen vao do
thi khong co self-loop — token bi co lap. Ca hai deu cho hang toan 0 trong
`adj`. Chia cho 0 se ra NaN va lam hong ca batch, nen `_normalize` chi nghich
dao o nhung dinh co bac > 0.

BIAS CONG SAU KHI GOP, KHONG CONG TRUOC
---------------------------------------
    dung:  h_i = sum_j  A_ij (W x_j)  +  b
    sai:   h_i = sum_j  A_ij (W x_j + b)

Cach sai lam bias bi nhan len theo bac cua tung dinh, tuc mot token co nhieu
canh se nhan bias lon hon — bias thanh ham cua cau truc do thi. Vi vay
`self.linear` dat bias=False va bias duoc cong rieng sau `bmm`.
"""

from __future__ import annotations

import torch
import torch.nn as nn

NORMALIZE_MODES = ("sym", "row", "row_plus1", "none")
EPS = 1e-12


class GCNLayer(nn.Module):
    """Mot lop GCN: (x, adj) -> x'. KHONG kem ham kich hoat.

    Ham kich hoat de ben ngoai goi, vi hai ly do: lop cuoi cua mot chong GCN
    thuong khong kich hoat, va Stage 4 can chen chuan hoa giua cac lop.

    Tham so:
        in_dim, out_dim: so chieu vao / ra
        dropout: ap len DAC TRUNG DAU VAO (giong ASGCN), khong ap len canh
        bias: co cong bias sau khi gop hay khong
        normalize: "sym" | "row" | "row_plus1" | "none" — xem docstring cua module.
            `asgcn` dung "row_plus1" (cong thuc ASGCN goc).
    """

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        *,
        dropout: float = 0.0,
        bias: bool = True,
        normalize: str = "sym",
    ) -> None:
        super().__init__()
        if normalize not in NORMALIZE_MODES:
            raise ValueError(f"normalize phai thuoc {NORMALIZE_MODES}, nhan duoc {normalize!r}")

        self.in_dim = in_dim
        self.out_dim = out_dim
        self.normalize = normalize

        self.linear = nn.Linear(in_dim, out_dim, bias=False)
        self.bias = nn.Parameter(torch.zeros(out_dim)) if bias else None
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        adj: torch.Tensor,
        edge_weight: torch.Tensor | None = None,
        mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Gop tin tu hang xom mot buoc.

        Tham so:
            x: (B, N, in_dim)
            adj: (B, N, N) — adj[b, i, j] > 0 la co canh j -> i
            edge_weight: (B, N, N) tuy chon, nhan theo tung phan tu vao adj.
                Dung cho trong so cam xuc (CD1.6b) va do tin cay cua canh
                logic (Stage 4).
            mask: (B, N) tuy chon, 1 = token that, 0 = token dem. Khi co mask,
                canh dinh vao token dem bi bo va dau ra tai token dem bi ep ve
                0 — neu khong, bias se ro ri thanh gia tri khac 0 o cho dang
                le khong co token nao.

        Tra ve: (B, N, out_dim)
        """
        if x.dim() != 3:
            raise ValueError(f"x phai co 3 chieu (B, N, D), nhan duoc {tuple(x.shape)}")
        if adj.dim() != 3:
            raise ValueError(f"adj phai co 3 chieu (B, N, N), nhan duoc {tuple(adj.shape)}")
        if adj.shape[0] != x.shape[0] or adj.shape[1] != adj.shape[2] or adj.shape[1] != x.shape[1]:
            raise ValueError(
                f"adj {tuple(adj.shape)} khong khop x {tuple(x.shape)}: can (B, N, N) voi cung B va N"
            )
        if x.shape[2] != self.in_dim:
            raise ValueError(f"x co {x.shape[2]} chieu, lop nay nhan {self.in_dim}")

        adj = adj.to(x.dtype)
        if edge_weight is not None:
            if edge_weight.shape != adj.shape:
                raise ValueError(
                    f"edge_weight {tuple(edge_weight.shape)} phai cung shape voi adj {tuple(adj.shape)}"
                )
            adj = adj * edge_weight.to(x.dtype)

        if mask is not None:
            if mask.shape != x.shape[:2]:
                raise ValueError(
                    f"mask {tuple(mask.shape)} phai co shape (B, N) = {tuple(x.shape[:2])}"
                )
            keep = mask.to(x.dtype)
            adj = adj * keep.unsqueeze(2) * keep.unsqueeze(1)

        support = self.linear(self.dropout(x))
        out = torch.bmm(self._normalize(adj), support)

        if self.bias is not None:
            out = out + self.bias
        if mask is not None:
            out = out * keep.unsqueeze(-1)
        return out

    def _normalize(self, adj: torch.Tensor) -> torch.Tensor:
        if self.normalize == "none":
            return adj

        deg = adj.sum(dim=-1)  # (B, N) — bac cua dinh NHAN tin
        has_deg = deg > 0
        # Kep TRUOC khi nghich dao, khong phai loc sau bang torch.where: neu de
        # inf loc vao nhanh khong duoc chon, gradient van di qua no va ra NaN.
        # Dieu nay se can o Stage 4, luc `edge_weight` mang do tin cay HOC DUOC.
        deg_safe = deg.clamp(min=EPS)

        if self.normalize == "row_plus1":
            # Cong thuc ASGCN goc. Khong can torch.where: mau so (d_i + 1) >= 1 nen
            # khong bao gio chia cho 0, va hang cua token dem von da toan 0.
            return adj * (deg + 1.0).reciprocal().unsqueeze(2)

        if self.normalize == "row":
            inv = torch.where(has_deg, deg_safe.reciprocal(), torch.zeros_like(deg))
            return adj * inv.unsqueeze(2)

        inv_sqrt = torch.where(has_deg, deg_safe.pow(-0.5), torch.zeros_like(deg))
        return inv_sqrt.unsqueeze(2) * adj * inv_sqrt.unsqueeze(1)

    def extra_repr(self) -> str:
        return f"in_dim={self.in_dim}, out_dim={self.out_dim}, normalize={self.normalize!r}"
