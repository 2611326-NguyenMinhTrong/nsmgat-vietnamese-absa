"""[CD1.6b] Test SenticGCNModel + configs/senticgcn.yaml.

Test quan trong nhat la `test_tu_dien_RONG_thi_giong_HET_asgcn`. Ly do: cong
thuc (4) cua bai co so hang +1 lam nen, nen tu dien rong phai cho A = D, tuc
dung ma tran ke nhi phan cua `asgcn`. Do la thu bao dam `senticgcn` khac `asgcn`
DUNG MOT bien. Mat tinh chat do thi hieu so cua bac thang baseline het nghia, ma
mat kieu do khong lam gi sap ca.

Nhom thu hai khoa lai dung cho Claude Code da hieu sai ngay 02/10/2026 khi moi
doc ma nguon GitHub ma chua co bai bao: tu KHONG CO trong tu dien van phai giu
trong so canh bang 1, khong phai 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nsmgat.models.asgcn import ASGCNModel  # noqa: E402
from nsmgat.models.senticgcn import SenticGCNModel  # noqa: E402
from nsmgat.utils.io import load_config  # noqa: E402

DEV_JSONL = REPO_ROOT / "data" / "processed" / "visfd_dev.jsonl"
TU_DIEN = REPO_ROOT / "data" / "lexicon_from_train.json"
CONFIGS = REPO_ROOT / "configs"


# --- 1. Config ----------------------------------------------------------------


def _so_sanh_sau(a: dict, b: dict, tien_to: str = "") -> dict:
    khac = {}
    for key in set(a) | set(b):
        duong = f"{tien_to}{key}"
        va, vb = a.get(key), b.get(key)
        if isinstance(va, dict) and isinstance(vb, dict):
            khac.update(_so_sanh_sau(va, vb, f"{duong}."))
        elif va != vb:
            khac[duong] = (va, vb)
    return khac


def test_senticgcn_khac_asgcn_DUNG_MOT_khoa():
    """Bac asgcn -> senticgcn phai them dung mot bien la tri thuc cam xuc."""
    khac = _so_sanh_sau(load_config(CONFIGS / "asgcn.yaml"),
                        load_config(CONFIGS / "senticgcn.yaml"))
    assert khac == {"model.lexicon_path": (None, "data/lexicon_from_train.json")}, \
        f"hai config lech o: {khac}"


def test_senticgcn_GIU_link_roots_false():
    """Hoc vien chot 02/10/2026: dong chinh thuc tai lap dung bai goc. Doi mot
    minh `senticgcn` sang true se lam hieu so lan hai bien."""
    assert load_config(CONFIGS / "senticgcn.yaml")["model"]["link_roots"] is False


# --- 2. Mo hinh ---------------------------------------------------------------


def _encoder_ti_hon():
    from transformers import RobertaConfig, RobertaModel

    return RobertaModel(RobertaConfig(
        vocab_size=64001, hidden_size=32, num_hidden_layers=1,
        num_attention_heads=2, intermediate_size=64, max_position_embeddings=258,
    ))


@pytest.fixture(scope="module")
def du_lieu_dev():
    if not DEV_JSONL.exists():
        pytest.skip("chua co data/processed (chay scripts/prepare_data.py)")
    if not TU_DIEN.exists():
        pytest.skip("chua co data/lexicon_from_train.json (chay build_lexicon_from_train.py)")
    return DEV_JSONL


def _cfg(du_lieu_dev, tu_dien=None, **ghi_de) -> dict:
    cfg = {
        "data": {"dev_path": str(du_lieu_dev)},
        "model": {
            "dropout": 0.1, "gcn_layers": 2, "normalize": "row_plus1",
            "lexicon_path": str(tu_dien or TU_DIEN),
        },
    }
    cfg["model"].update(ghi_de)
    return cfg


@pytest.fixture(scope="module")
def model(du_lieu_dev):
    return SenticGCNModel(_cfg(du_lieu_dev), encoder=_encoder_ti_hon())


@pytest.fixture(scope="module")
def model_asgcn(du_lieu_dev):
    cfg = {"data": {"dev_path": str(du_lieu_dev)},
           "model": {"dropout": 0.1, "gcn_layers": 2, "normalize": "row_plus1"}}
    return ASGCNModel(cfg, encoder=_encoder_ti_hon())


def _mot_uid(m) -> str:
    return next(iter(m.uid_to_khoa))


# --- 3. Cong thuc (4) ---------------------------------------------------------


def test_cong_thuc_A_bang_D_nhan_S_cong_1(model, model_asgcn):
    """A_ij = D_ij x (s_i + s_j + 1), T_ij = 0 vi khia canh khong co trong cau."""
    uid = _mot_uid(model)
    n = len(model.khoa_to_diem[model.uid_to_khoa[uid]])

    D = model_asgcn._ma_tran_ke([uid], n, "cpu", torch.float32)[0]
    A = model._ma_tran_ke([uid], n, "cpu", torch.float32)[0]

    s = model.khoa_to_diem[model.uid_to_khoa[uid]]
    mong_doi = D * (s.unsqueeze(1) + s.unsqueeze(0) + 1.0)
    assert torch.allclose(A, mong_doi, atol=1e-6)


def test_duong_cheo_bang_hai_lan_diem_cong_1(model):
    """Thuat toan 1 dong 3 co "or i = j", nen self-loop cung mang trong so:
    A_ii = s_i + s_i + 1."""
    uid = _mot_uid(model)
    s = model.khoa_to_diem[model.uid_to_khoa[uid]]
    n = len(s)
    A = model._ma_tran_ke([uid], n, "cpu", torch.float32)[0]
    assert torch.allclose(A.diagonal(), 2 * s + 1.0, atol=1e-6)


def test_ma_tran_doi_xung(model):
    """D vo huong (muc 3.4) va S_ij = s_i + s_j doi xung, nen A doi xung."""
    uid = _mot_uid(model)
    n = len(model.khoa_to_diem[model.uid_to_khoa[uid]])
    A = model._ma_tran_ke([uid], n, "cpu", torch.float32)[0]
    assert torch.allclose(A, A.T, atol=1e-6)


def test_tu_dien_RONG_thi_giong_HET_asgcn(du_lieu_dev, model_asgcn, tmp_path):
    """TEST QUAN TRONG NHAT. So hang +1 cua cong thuc (4) lam nen, nen khi khong
    tu nao co diem thi A = D x (0 + 0 + 1) = D, dung ma tran ke cua `asgcn`.

    Day la thu chung minh `senticgcn` khac `asgcn` DUNG MOT bien."""
    rong = tmp_path / "rong.json"
    rong.write_text("{}", encoding="utf-8")
    m = SenticGCNModel(_cfg(du_lieu_dev, tu_dien=rong), encoder=_encoder_ti_hon())

    uid = _mot_uid(m)
    n = len(m.khoa_to_diem[m.uid_to_khoa[uid]])
    A = m._ma_tran_ke([uid], n, "cpu", torch.float32)
    D = model_asgcn._ma_tran_ke([uid], n, "cpu", torch.float32)
    assert torch.equal(A, D)


def test_tu_LA_trong_tu_dien_van_GIU_trong_so_1(du_lieu_dev, tmp_path):
    """Chot lai cho Claude Code hieu sai ngay 02/10/2026 khi doc ma nguon GitHub:
    ma cho tu la trong so 0 nen token bi cat khoi do thi, con BAI co so hang +1
    nen canh van song. Voi tu dien phu 83 %, hieu theo ma se cat nham 17 % token."""
    # Tu dien chi co dung mot tu, moi tu khac deu "khong co trong tu dien".
    td = tmp_path / "mot_tu.json"
    td.write_text(json.dumps({"khong_bao_gio_xuat_hien_abc": 0.5}), encoding="utf-8")
    m = SenticGCNModel(_cfg(du_lieu_dev, tu_dien=td), encoder=_encoder_ti_hon())

    uid = _mot_uid(m)
    n = len(m.khoa_to_diem[m.uid_to_khoa[uid]])
    A = m._ma_tran_ke([uid], n, "cpu", torch.float32)[0]

    assert (A.diagonal() == 1.0).all(), "tu la phai co self-loop bang 1, khong phai 0"
    assert set(A.unique().tolist()) <= {0.0, 1.0}


def test_trong_so_AM_co_that_tren_du_lieu_that(model):
    """Khoa lai quyet dinh 03/10/2026: chay y het bai goc, KHONG kep trong so.

    Neu mot ngay nao do khong con canh am nao, tuc la da co ai do them cai kep
    hoac dich thang diem — luc do con so khong con tai lap bai goc nua."""
    co_am = False
    for uid in list(model.uid_to_khoa)[:200]:
        n = len(model.khoa_to_diem[model.uid_to_khoa[uid]])
        if (model._ma_tran_ke([uid], n, "cpu", torch.float32) < 0).any():
            co_am = True
            break
    assert co_am, "khong thay trong so am nao — co ai da kep trong so?"


# --- 4. Hanh vi chung ---------------------------------------------------------


def test_bao_loi_RO_khi_thieu_tu_dien(du_lieu_dev, tmp_path):
    with pytest.raises(FileNotFoundError, match="tu dien cam xuc"):
        SenticGCNModel(_cfg(du_lieu_dev, tu_dien=tmp_path / "khong_co.json"),
                       encoder=_encoder_ti_hon())


def test_so_diem_khop_so_token_cua_tung_cau(model):
    """Diem lay tu CHINH khoa cau, nen khong the lech so luong voi chi muc canh."""
    for khoa in list(model.khoa_to_canh)[:300]:
        so_token = len(khoa.split("\x1e")[0].split("\x1f"))
        assert len(model.khoa_to_diem[khoa]) == so_token


def test_forward_ra_dung_shape(model, du_lieu_dev):
    from transformers import AutoTokenizer

    from nsmgat.data.dataset import ACSADataset, collate_fn

    tok = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    ds = ACSADataset(du_lieu_dev, tok, 128, pair_mode=True)
    batch = collate_fn([ds[i] for i in range(4)])

    logits = model(batch)
    assert logits.shape == (4, 3)
    assert torch.isfinite(logits).all(), "mau so am khong duoc sinh NaN"


def test_cau_bi_cat_thi_diem_cung_cat_theo(model):
    """`max_seq_len` nho hon do dai cau thi `so_token` nho hon so diem. Phan du
    phai bi cat chu khong duoc lech chi so — cung ho loi voi GAP-020."""
    uid = max(model.uid_to_khoa, key=lambda u: len(model.khoa_to_diem[model.uid_to_khoa[u]]))
    day_du = len(model.khoa_to_diem[model.uid_to_khoa[uid]])
    cat = max(2, day_du // 3)

    A = model._ma_tran_ke([uid], cat, "cpu", torch.float32)[0]
    s = model.khoa_to_diem[model.uid_to_khoa[uid]][:cat]
    assert A.shape == (cat, cat)
    assert torch.allclose(A.diagonal(), 2 * s + 1.0, atol=1e-6)
