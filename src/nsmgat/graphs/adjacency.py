"""[CD1.6a] Doi List[TypedEdge] thanh ma tran ke day cho GCNLayer.

VI SAO LA MODULE MOI CHU KHONG PHAI VIET VAO CHO CU
----------------------------------------------------
- `graphs/base.py` da dong bang o S0.2 — khong duoc them ham vao.
- `graphs/builder.py` la cho cua S3.3 (MultiGraphBuilder + cache) — step do
  chua toi luot, viet vao do la lan san.
- `data/dataset.py` de san `edge_index` rong cung cho S3.3 — cung ly do.

Nen CD1.6a dung module rieng nay. Khi S3.3 lam that, no goi lai ham o day chu
khong viet lai; hoac neu luc do chon duong thua (sparse) thi module nay van
dung duoc cho `asgcn`/`senticgcn` da chay xong.

QUY UOC CHIEU CANH — doc ky cho nay
------------------------------------
    adj[i][j] > 0  <=>  co canh j -> i  <=>  token i NHAN tin tu token j

Tuc HANG i la danh sach nhung ai gui tin cho i. Quy uoc nay khop voi
`GCNLayer`: phep `adj @ x` gop dung hang xom cua tung dinh. Viet nguoc lai thi
code VAN CHAY, khong bao loi, chi ra ket qua sai — vi vay co test rieng chot
chieu bang mot cay phu thuoc bat doi xung.

`TypedEdge(src=a, dst=b)` nghia la canh a -> b, nen no vao o `adj[b][a]`.

CANH TRUNG NHAU
---------------
Hai canh cung cap (i, j) co the xuat hien khi gop nhieu view, hoac khi cay phu
thuoc co ca canh xuoi lan canh nguoc giua hai token. Lay MAX chu khong cong
don: ma tran ke o day la "co duong di hay khong" cho `binary`, va "do tin cay
cao nhat" cho `conf`. Cong don se lam bac cua dinh phong len va lam lech phep
chuan hoa.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import torch

from nsmgat.schema import TypedEdge

WEIGHT_MODES = ("binary", "conf")


def edges_to_adj(
    edges: Iterable[TypedEdge],
    n_tokens: int,
    *,
    views: Optional[Sequence[str]] = None,
    weight: str = "binary",
    size: Optional[int] = None,
) -> torch.Tensor:
    """Dung ma tran ke day cho MOT mau.

    Tham so:
        edges: danh sach canh cua mau do (thuong tu GraphSample.edges)
        n_tokens: so token THAT cua mau
        views: chi giu canh thuoc cac view nay, vd ("syn",). None = giu het.
            Stage 4 se dung de tach 3 do thi ma khong phai loc o ngoai.
        weight: "binary" (1.0 cho moi canh) hoac "conf" (lay TypedEdge.conf)
        size: canh cua ma tran vuong tra ve; mac dinh bang n_tokens. Truyen
            so lon hon khi can dem cho bang do dai lon nhat trong batch.

    Tra ve: (size, size) float32.
    """
    if weight not in WEIGHT_MODES:
        raise ValueError(f"weight phai thuoc {WEIGHT_MODES}, nhan duoc {weight!r}")
    if n_tokens < 0:
        raise ValueError(f"n_tokens phai >= 0, nhan duoc {n_tokens}")

    dim = n_tokens if size is None else size
    if dim < n_tokens:
        raise ValueError(f"size={size} nho hon n_tokens={n_tokens}")

    keep = None if views is None else set(views)

    # Gom trong dict Python roi ghi vao tensor MOT LAN. Ban dau viet thang
    # `if value > adj[dst, src]: adj[dst, src] = value` cho tung canh, do duoc
    # 10 ms moi cau -> 73 giay moi lan khoi tao mo hinh tren train+dev+test.
    # Thu pham la phep so sanh tren tensor cho tung canh (~50 us mot lan).
    tot_nhat: Dict[Tuple[int, int], float] = {}
    for edge in edges:
        if keep is not None and edge.view not in keep:
            continue
        if not (0 <= edge.src < n_tokens) or not (0 <= edge.dst < n_tokens):
            raise ValueError(
                f"canh ({edge.src} -> {edge.dst}) vuot qua n_tokens={n_tokens}"
            )
        value = 1.0 if weight == "binary" else float(edge.conf)
        # dst la dinh NHAN tin, nen dst la HANG. Lay max de canh trung khong cong don.
        o = (edge.dst, edge.src)
        if value > tot_nhat.get(o, 0.0):
            tot_nhat[o] = value

    adj = torch.zeros((dim, dim), dtype=torch.float32)
    if tot_nhat:
        chi_so = torch.tensor(list(tot_nhat.keys()), dtype=torch.long)
        gia_tri = torch.tensor(list(tot_nhat.values()), dtype=torch.float32)
        adj[chi_so[:, 0], chi_so[:, 1]] = gia_tri
    return adj


def edges_to_adj_batch(
    edges_per_sample: Sequence[Iterable[TypedEdge]],
    n_tokens_per_sample: Sequence[int],
    *,
    views: Optional[Sequence[str]] = None,
    weight: str = "binary",
    max_len: Optional[int] = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Gop ca batch, dem ve cung do dai.

    Tra ve cap (adj, mask):
        adj: (B, N, N) float32
        mask: (B, N) float32 — 1.0 o token that, 0.0 o token dem

    `mask` tra ve luon de goi thang vao GCNLayer(mask=...): neu khong mask,
    bias cua lop se ro ri thanh gia tri khac 0 tai cho dang le khong co token.
    """
    if len(edges_per_sample) != len(n_tokens_per_sample):
        raise ValueError(
            f"so mau khong khop: {len(edges_per_sample)} danh sach canh nhung "
            f"{len(n_tokens_per_sample)} do dai"
        )
    if not edges_per_sample:
        raise ValueError("batch rong")

    dim = max(n_tokens_per_sample) if max_len is None else max_len
    if dim < max(n_tokens_per_sample):
        raise ValueError(f"max_len={max_len} nho hon mau dai nhat {max(n_tokens_per_sample)}")

    adjs: List[torch.Tensor] = [
        edges_to_adj(edges, n, views=views, weight=weight, size=dim)
        for edges, n in zip(edges_per_sample, n_tokens_per_sample)
    ]

    mask = torch.zeros((len(adjs), dim), dtype=torch.float32)
    for i, n in enumerate(n_tokens_per_sample):
        mask[i, :n] = 1.0

    return torch.stack(adjs), mask
