"""[S1.2 / CD1.6a] Test GCNLayer.

Dac ta: pLan/PLAN_NSMGAT.md muc S1.2 ("GCNLayer phai viet tong quat de Stage 4
dung lai cho 3 do thi ma khong phai sua").
Cai dat: src/nsmgat/models/layers.py

Do thi mau dung xuyen suot — 3 token, canh hai chieu 0<->1, co self-loop
(dung quy uoc cua SyntacticGraphBuilder), token 2 chi co self-loop:

    adj = [[1, 1, 0],
           [1, 1, 0],
           [0, 0, 1]]
"""

from __future__ import annotations

import pytest
import torch

from nsmgat.models.layers import GCNLayer

ADJ_MAU = torch.tensor(
    [[[1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 1.0]]]
)


@pytest.fixture
def lop() -> GCNLayer:
    torch.manual_seed(0)
    return GCNLayer(4, 6)


def test_shape_dau_ra(lop: GCNLayer) -> None:
    x = torch.randn(1, 3, 4)
    assert lop(x, ADJ_MAU).shape == (1, 3, 6)


def test_chuan_hoa_doi_xung_dung_cong_thuc() -> None:
    """D^(-1/2) A D^(-1/2) tinh tay tren do thi mau.

    Bac: dinh 0 va 1 co bac 2, dinh 2 co bac 1. Nen he so cua canh 0<->1 la
    1/2, con self-loop cua dinh 2 giu nguyen 1.
    """
    lop = GCNLayer(1, 1, bias=False)
    with torch.no_grad():
        lop.linear.weight.fill_(1.0)

    x = torch.tensor([[[1.0], [3.0], [5.0]]])
    out = lop(x, ADJ_MAU)

    mong_doi = torch.tensor([[[2.0], [2.0], [5.0]]])  # (1+3)/2, (1+3)/2, 5/1
    assert torch.allclose(out, mong_doi)


def test_chuan_hoa_theo_hang_khac_doi_xung() -> None:
    """normalize="row" chia cho bac cua dinh nhan — cach ASGCN goc lam."""
    lop = GCNLayer(1, 1, bias=False, normalize="row")
    with torch.no_grad():
        lop.linear.weight.fill_(1.0)

    adj = torch.tensor([[[1.0, 1.0, 1.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]])
    x = torch.tensor([[[1.0], [3.0], [5.0]]])
    out = lop(x, adj)

    mong_doi = torch.tensor([[[3.0], [3.0], [5.0]]])  # (1+3+5)/3, 3/1, 5/1
    assert torch.allclose(out, mong_doi)


def test_row_plus1_dung_cong_thuc_asgcn_goc() -> None:
    """ASGCN chia cho (d_i + 1), KHONG phai d_i — xem cong thuc (3) cua bai goc.

    Do thi mau co bac [2, 2, 1], nen mau so la 3, 3, 2.
    """
    lop = GCNLayer(1, 1, bias=False, normalize="row_plus1")
    with torch.no_grad():
        lop.linear.weight.fill_(1.0)

    x = torch.tensor([[[1.0], [3.0], [5.0]]])
    out = lop(x, ADJ_MAU)

    mong_doi = torch.tensor([[[4.0 / 3.0], [4.0 / 3.0], [5.0 / 2.0]]])
    assert torch.allclose(out, mong_doi)


def test_row_plus1_khac_row_that_su() -> None:
    """Hai che do phai cho so KHAC nhau — neu bang nhau thi mot trong hai cai sai."""
    x = torch.tensor([[[1.0], [3.0], [5.0]]])
    ket_qua = {}
    for che_do in ("row", "row_plus1"):
        lop = GCNLayer(1, 1, bias=False, normalize=che_do)
        with torch.no_grad():
            lop.linear.weight.fill_(1.0)
        ket_qua[che_do] = lop(x, ADJ_MAU)

    assert not torch.allclose(ket_qua["row"], ket_qua["row_plus1"])


def test_row_plus1_khong_sinh_nan_voi_bac_0() -> None:
    """Mau so (d_i + 1) >= 1 nen khong the chia cho 0, ke ca o token dem."""
    lop = GCNLayer(4, 6, normalize="row_plus1")
    out = lop(torch.randn(1, 3, 4), torch.zeros(1, 3, 3))

    assert torch.isfinite(out).all()


def test_normalize_none_giu_nguyen_ma_tran_ke() -> None:
    lop = GCNLayer(1, 1, bias=False, normalize="none")
    with torch.no_grad():
        lop.linear.weight.fill_(1.0)

    x = torch.tensor([[[1.0], [3.0], [5.0]]])
    out = lop(x, ADJ_MAU)

    assert torch.allclose(out, torch.tensor([[[4.0], [4.0], [5.0]]]))


def test_dinh_bac_0_khong_sinh_nan() -> None:
    """Token dem va token bi co lap deu cho hang toan 0 trong adj."""
    lop = GCNLayer(4, 6)
    x = torch.randn(1, 3, 4)
    adj = torch.zeros(1, 3, 3)
    adj[0, 0, 0] = 1.0  # chi dinh 0 co self-loop; dinh 1 va 2 bac 0

    out = lop(x, adj)
    assert torch.isfinite(out).all()


def test_gradient_khong_nan_khi_edge_weight_hoc_duoc() -> None:
    """Stage 4 se cho do tin cay cua canh logic hoc duoc — bac 0 phai an toan."""
    lop = GCNLayer(4, 6)
    x = torch.randn(1, 3, 4)
    adj = torch.zeros(1, 3, 3)
    adj[0, 0, 0] = 1.0
    edge_weight = torch.ones(1, 3, 3, requires_grad=True)

    lop(x, adj, edge_weight=edge_weight).sum().backward()

    assert edge_weight.grad is not None
    assert torch.isfinite(edge_weight.grad).all()


def test_edge_weight_bang_0_cat_dut_duong_truyen_tin() -> None:
    lop = GCNLayer(1, 1, bias=False)
    with torch.no_grad():
        lop.linear.weight.fill_(1.0)

    x = torch.tensor([[[1.0], [3.0], [5.0]]])
    # Xoa canh 0<->1, giu self-loop: dinh 0 chi con chinh no
    edge_weight = torch.tensor([[[1.0, 0.0, 1.0], [0.0, 1.0, 1.0], [1.0, 1.0, 1.0]]])
    out = lop(x, ADJ_MAU, edge_weight=edge_weight)

    assert torch.allclose(out, torch.tensor([[[1.0], [3.0], [5.0]]]))


def test_mask_ep_token_dem_ve_0() -> None:
    """Co bias ma khong mask thi vi tri dem se mang gia tri bias khac 0."""
    lop = GCNLayer(4, 6)
    with torch.no_grad():
        lop.bias.fill_(0.7)

    x = torch.randn(1, 3, 4)
    mask = torch.tensor([[1, 1, 0]])

    khong_mask = lop(x, ADJ_MAU)
    co_mask = lop(x, ADJ_MAU, mask=mask)

    assert not torch.allclose(khong_mask[0, 2], torch.zeros(6))
    assert torch.allclose(co_mask[0, 2], torch.zeros(6))


def test_mask_khong_doi_ket_qua_cua_token_that() -> None:
    """Gop batch phai khong doi dau ra: mau ngan don le = chinh no trong batch dem."""
    lop = GCNLayer(4, 6)
    x_that = torch.randn(1, 2, 4)
    adj_that = torch.tensor([[[1.0, 1.0], [1.0, 1.0]]])

    x_dem = torch.cat([x_that, torch.randn(1, 1, 4)], dim=1)
    adj_dem = torch.zeros(1, 3, 3)
    adj_dem[0, :2, :2] = adj_that[0]
    adj_dem[0, 2, 2] = 1.0  # self-loop cua token dem, phai bi mask bo

    rieng = lop(x_that, adj_that)
    trong_batch = lop(x_dem, adj_dem, mask=torch.tensor([[1, 1, 0]]))

    assert torch.allclose(rieng, trong_batch[:, :2], atol=1e-6)


def test_bias_cong_sau_khi_gop_nen_khong_theo_bac() -> None:
    """Bias phai giong nhau o moi dinh, bat ke dinh do co bao nhieu canh."""
    lop = GCNLayer(4, 6, normalize="none")
    with torch.no_grad():
        lop.linear.weight.zero_()
        lop.bias.fill_(0.5)

    x = torch.randn(1, 3, 4)
    adj = torch.tensor([[[1.0, 1.0, 1.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]]])
    out = lop(x, adj)

    assert torch.allclose(out, torch.full((1, 3, 6), 0.5))


def test_tu_choi_che_do_chuan_hoa_la() -> None:
    with pytest.raises(ValueError, match="normalize"):
        GCNLayer(4, 6, normalize="doi_xung")


@pytest.mark.parametrize(
    "x, adj, khop",
    [
        (torch.randn(3, 4), torch.zeros(1, 3, 3), "3 chieu"),          # x thieu chieu batch
        (torch.randn(1, 3, 4), torch.zeros(3, 3), "3 chieu"),          # adj thieu chieu batch
        (torch.randn(1, 3, 4), torch.zeros(1, 2, 2), "khong khop"),    # N lech nhau
        (torch.randn(1, 3, 5), torch.zeros(1, 3, 3), "lop nay nhan"),  # sai so chieu dac trung
    ],
)
def test_bao_loi_khi_shape_sai(x: torch.Tensor, adj: torch.Tensor, khop: str) -> None:
    with pytest.raises(ValueError, match=khop):
        GCNLayer(4, 6)(x, adj)


def test_bao_loi_khi_edge_weight_hoac_mask_sai_shape(lop: GCNLayer) -> None:
    x = torch.randn(1, 3, 4)
    with pytest.raises(ValueError, match="edge_weight"):
        lop(x, ADJ_MAU, edge_weight=torch.ones(1, 3, 2))
    with pytest.raises(ValueError, match="mask"):
        lop(x, ADJ_MAU, mask=torch.ones(1, 2))


def test_dropout_chi_hoat_dong_khi_train() -> None:
    # 32 chieu chu khong phai 4: voi vector qua ngan, dropout co the xoa SACH
    # ca hai lan chay nen hai ket qua bang nhau va test hoa ra vo nghia.
    lop = GCNLayer(32, 8, dropout=0.5)
    x = torch.randn(1, 3, 32)

    lop.eval()
    assert torch.allclose(lop(x, ADJ_MAU), lop(x, ADJ_MAU))

    lop.train()
    torch.manual_seed(0)
    lan_1 = lop(x, ADJ_MAU)
    lan_2 = lop(x, ADJ_MAU)
    assert not torch.allclose(lan_1, lan_2)


# --- [CD1.6b] Mau so cua row_plus1 khi trong so canh mang DAU ------------------
#
# Voi `senticgcn`, adj mang diem cam xuc nen deg la tong co dau, khong phai phep
# dem. Hoc vien chot 03/10/2026: chay Y HET bai goc, khong kep mau so, khong dich
# thang diem. Ba test duoi khoa dung quyet dinh do.


def _adj_mot_canh(gia_tri: float) -> torch.Tensor:
    """Do thi 1 token, chi co self-loop mang trong so cho truoc -> deg = gia_tri."""
    return torch.tensor([[[gia_tri]]])


def test_row_plus1_KHONG_kep_mau_so_am() -> None:
    """Mau so am thi ca hang doi dau. Day la dieu cong thuc (7) quy dinh, khong
    phai loi — ket qua phai am chu khong duoc kep ve 0 hay ve duong."""
    lop = GCNLayer(1, 1, bias=False, normalize="row_plus1")
    with torch.no_grad():
        lop.linear.weight.fill_(1.0)
    lop.eval()

    # deg = -3  ->  mau so = -2  ->  (-3 / -2) * x = 1,5x
    ra = lop(torch.tensor([[[2.0]]]), _adj_mot_canh(-3.0))
    assert ra.item() == pytest.approx(3.0)
    assert torch.isfinite(ra).all()


def test_row_plus1_mau_so_nho_thi_khuech_dai_chu_khong_chan() -> None:
    """|mau so| nho nhat do duoc tren UIT-ViSFD la 1,1e-3, khuech dai 909 lan.
    Day bay dat o 1e-6 nen khong duoc dong vao vung nay."""
    lop = GCNLayer(1, 1, bias=False, normalize="row_plus1")
    with torch.no_grad():
        lop.linear.weight.fill_(1.0)
    lop.eval()

    ra = lop(torch.tensor([[[1.0]]]), _adj_mot_canh(-1.0 + 1.1e-3))
    assert torch.isfinite(ra).all()
    assert abs(ra.item()) > 100.0


def test_row_plus1_DAY_BAY_bao_ro_khi_mau_so_bang_0() -> None:
    """Mau so bang dung 0 moi sinh inf roi NaN. Phai dung han va noi ro, thay vi
    tra ve mot bang ket qua toan NaN ma khong biet vi sao."""
    lop = GCNLayer(1, 1, normalize="row_plus1")
    with pytest.raises(ValueError, match="gan bang 0"):
        lop(torch.tensor([[[1.0]]]), _adj_mot_canh(-1.0))


def test_day_bay_KHONG_kich_hoat_voi_do_thi_nhi_phan() -> None:
    """`asgcn` dung adj nhi phan co self-loop nen deg >= 1 va mau so >= 2. Day bay
    khong duoc cham toi no — neu cham, ba seed asgcn da chay se khong tai lap duoc."""
    lop = GCNLayer(4, 4, normalize="row_plus1")
    for _ in range(50):
        n = int(torch.randint(1, 12, (1,)))
        adj = (torch.rand(3, n, n) > 0.5).float()
        adj = torch.maximum(adj, torch.eye(n).expand(3, n, n))  # luon co self-loop
        assert torch.isfinite(lop(torch.randn(3, n, 4), adj)).all()
