"""[CD1.6a] Test doi List[TypedEdge] thanh ma tran ke day.

Cai dat: src/nsmgat/graphs/adjacency.py

Cau mau dung xuyen suot (giong tests/test_graphs.py de doi chieu duoc):

    "pin rất trâu" — heads=[2, 2, -1]
    pin(0) -> trau(2), rat(1) -> trau(2), trau la goc

SyntacticGraphBuilder sinh canh HAI CHIEU + self-loop cho moi token, nen ma
tran ke ky vong la:

    [[1, 0, 1],
     [0, 1, 1],
     [1, 1, 1]]
"""

from __future__ import annotations

import pytest
import torch

from nsmgat.graphs.adjacency import edges_to_adj, edges_to_adj_batch
from nsmgat.graphs.syntactic import SyntacticGraphBuilder
from nsmgat.models.layers import GCNLayer
from nsmgat.schema import Example, TypedEdge

CAU_MAU = Example(
    uid="test-0001-BATTERY",
    text="pin rất trâu",
    tokens=["pin", "rất", "trâu"],
    pos=["N", "R", "A"],
    heads=[2, 2, -1],
    deprels=["nsubj", "adv", "root"],
    aspect="BATTERY",
    label=2,
    domain="visfd",
    split="train",
)

ADJ_MONG_DOI = torch.tensor(
    [[1.0, 0.0, 1.0], [0.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
)


def canh(src: int, dst: int, *, view: str = "syn", conf: float = 1.0) -> TypedEdge:
    return TypedEdge(src=src, dst=dst, view=view, etype="DEP:test", conf=conf, rule_id=None)


def test_do_thi_cu_phap_cau_mau() -> None:
    edges = SyntacticGraphBuilder().build(CAU_MAU)
    assert torch.equal(edges_to_adj(edges, 3), ADJ_MONG_DOI)


def test_chieu_canh_dst_la_hang() -> None:
    """Chot quy uoc bang mot do thi BAT DOI XUNG — doi xung thi test vo dung."""
    adj = edges_to_adj([canh(0, 2)], 3)

    assert adj[2, 0] == 1.0, "canh 0 -> 2 phai nam o adj[2][0]"
    assert adj[0, 2] == 0.0, "khong duoc tu them chieu nguoc lai"


def test_bo_dung_do_thi_luon_them_self_loop() -> None:
    """Dieu nay la ly do GCNLayer khong tu them self-loop — tranh dem hai lan."""
    adj = edges_to_adj(SyntacticGraphBuilder().build(CAU_MAU), 3)
    assert torch.equal(adj.diagonal(), torch.ones(3))


def test_loc_theo_view() -> None:
    edges = [canh(0, 1, view="syn"), canh(1, 2, view="aff"), canh(0, 2, view="logic")]

    chi_syn = edges_to_adj(edges, 3, views=("syn",))
    assert chi_syn.sum() == 1.0 and chi_syn[1, 0] == 1.0

    syn_va_logic = edges_to_adj(edges, 3, views=("syn", "logic"))
    assert syn_va_logic.sum() == 2.0

    tat_ca = edges_to_adj(edges, 3)
    assert tat_ca.sum() == 3.0


def test_weight_conf_lay_do_tin_cay() -> None:
    edges = [canh(0, 1, conf=0.25), canh(1, 2, conf=0.8)]

    nhi_phan = edges_to_adj(edges, 3)
    assert nhi_phan[1, 0] == 1.0 and nhi_phan[2, 1] == 1.0

    theo_conf = edges_to_adj(edges, 3, weight="conf")
    assert theo_conf[1, 0] == pytest.approx(0.25)
    assert theo_conf[2, 1] == pytest.approx(0.8)


def test_canh_trung_lay_max_khong_cong_don() -> None:
    """Cong don se thoi phong bac cua dinh va lam lech phep chuan hoa."""
    # Ba canh cung cap (0 -> 1). Cong don thi nhi phan ra 3.0 va conf ra 1.7.
    edges = [canh(0, 1, conf=0.3), canh(0, 1, view="logic", conf=0.9), canh(0, 1, conf=0.5)]

    assert edges_to_adj(edges, 2)[1, 0] == 1.0
    assert edges_to_adj(edges, 2, weight="conf")[1, 0] == pytest.approx(0.9)


def test_size_lon_hon_thi_dem_bang_0() -> None:
    adj = edges_to_adj(SyntacticGraphBuilder().build(CAU_MAU), 3, size=5)

    assert adj.shape == (5, 5)
    assert torch.equal(adj[:3, :3], ADJ_MONG_DOI)
    assert adj[3:].sum() == 0.0 and adj[:, 3:].sum() == 0.0


def test_gop_batch_hai_mau_khac_do_dai() -> None:
    ngan = [canh(0, 1), canh(1, 0)]
    dai = SyntacticGraphBuilder().build(CAU_MAU)

    adj, mask = edges_to_adj_batch([ngan, dai], [2, 3])

    assert adj.shape == (2, 3, 3)
    assert torch.equal(mask, torch.tensor([[1.0, 1.0, 0.0], [1.0, 1.0, 1.0]]))
    assert torch.equal(adj[1], ADJ_MONG_DOI)
    assert adj[0, 2].sum() == 0.0, "hang cua token dem phai trong"


def test_gop_batch_ton_trong_max_len() -> None:
    adj, mask = edges_to_adj_batch([[canh(0, 1)]], [2], max_len=4)
    assert adj.shape == (1, 4, 4) and mask.shape == (1, 4)


def test_link_roots_them_canh_noi_hai_cay_con() -> None:
    """Bien the chan doan cua GAP-007: cau bi tach thanh 2 cay con."""
    hai_cay = Example(
        uid="test-0002-BATTERY",
        text="pin trâu máy đẹp",
        tokens=["pin", "trâu", "máy", "đẹp"],
        pos=["N", "A", "N", "A"],
        heads=[1, -1, 3, -1],  # hai goc: token 1 va token 3
        deprels=["nsubj", "root", "nsubj", "root"],
        aspect="BATTERY",
        label=2,
        domain="visfd",
        split="train",
    )

    roi = edges_to_adj(SyntacticGraphBuilder(link_roots=False).build(hai_cay), 4)
    noi = edges_to_adj(SyntacticGraphBuilder(link_roots=True).build(hai_cay), 4)

    assert roi[1, 3] == 0.0 and roi[3, 1] == 0.0, "khong noi thi 2 goc roi nhau"
    assert noi[1, 3] == 1.0 and noi[3, 1] == 1.0, "noi thi 2 goc thanh hang xom"
    assert noi.sum() == roi.sum() + 2


def test_rap_thang_vao_gcnlayer() -> None:
    """Duong di that: Example -> canh -> ma tran ke -> GCNLayer."""
    lop = GCNLayer(1, 1, bias=False, normalize="row")
    with torch.no_grad():
        lop.linear.weight.fill_(1.0)

    adj, mask = edges_to_adj_batch([SyntacticGraphBuilder().build(CAU_MAU)], [3])
    x = torch.tensor([[[1.0], [3.0], [5.0]]])
    out = lop(x, adj, mask=mask)

    # bac = [2, 2, 3]; (1+5)/2 = 3, (3+5)/2 = 4, (1+3+5)/3 = 3
    assert torch.allclose(out, torch.tensor([[[3.0], [4.0], [3.0]]]))


def test_bao_loi_khi_canh_vuot_qua_so_token() -> None:
    with pytest.raises(ValueError, match="vuot qua n_tokens"):
        edges_to_adj([canh(0, 7)], 3)


def test_bao_loi_khi_tham_so_sai() -> None:
    with pytest.raises(ValueError, match="weight"):
        edges_to_adj([], 3, weight="conf_score")
    with pytest.raises(ValueError, match="nho hon n_tokens"):
        edges_to_adj([], 3, size=2)
    with pytest.raises(ValueError, match="so mau khong khop"):
        edges_to_adj_batch([[canh(0, 1)]], [2, 2])
    with pytest.raises(ValueError, match="batch rong"):
        edges_to_adj_batch([], [])
    with pytest.raises(ValueError, match="nho hon mau dai nhat"):
        edges_to_adj_batch([[canh(0, 1)]], [3], max_len=2)
