"""[CD1.11d] Test tin hieu luat va PhoBERTLuatModel.

Nhom quan trong nhat la nhom 3: tin hieu toan 0 thi mo hinh PHAI trung `phobert`, ke ca khi huan
luyen cung seed. Lech o day thi hieu so `phobert_luat` - `phobert` khong con do rieng luat, ma lech
kieu do khong lam gi sap ca.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_diagnostic_candidates as bdc  # noqa: E402
from nsmgat.data import tin_hieu_luat as thl  # noqa: E402
from nsmgat.data.tin_hieu_luat import (  # noqa: E402
    CY_KHONG, CY_TU, CY_VE_NHAN, CY_VE_NHUONG, PD_KHONG, PD_PHAM_VI, PD_TU,
    danh_dau_chuyen_y, danh_dau_phu_dinh, tin_hieu_cua,
)
from nsmgat.models.phobert import PhoBERTClassifier  # noqa: E402
from nsmgat.models.phobert_luat import PhoBERTLuatModel  # noqa: E402
from nsmgat.utils.io import load_config  # noqa: E402

CONFIGS = REPO_ROOT / "configs"


# --- 1. Bo danh dau -------------------------------------------------------------


def test_tu_khoa_trung_voi_danh_sach_cua_tap_chan_doan():
    """Hai noi lech nhau thi luat khong con la luat da do o muc 5.3 cua bao cao."""
    assert thl.PHU_DINH == bdc.PHU_DINH
    assert thl.CHUYEN_Y == bdc.CHUYEN_Y
    assert thl.NHUONG_BO <= thl.CHUYEN_Y


def test_pham_vi_phu_dinh_dung_o_dau_cau_va_tu_noi():
    tu = ["pin", "không", "trâu", "lắm", ",", "màn_hình", "đẹp"]
    assert danh_dau_phu_dinh(tu) == [PD_KHONG, PD_TU, PD_PHAM_VI, PD_PHAM_VI, PD_KHONG, PD_KHONG, PD_KHONG]
    tu = ["ko", "mượt", "nhưng", "rẻ"]
    assert danh_dau_phu_dinh(tu) == [PD_TU, PD_PHAM_VI, PD_KHONG, PD_KHONG]


def test_nhan_ra_dang_viet_tat_va_khong_phan_biet_hoa_thuong():
    assert danh_dau_phu_dinh(["KO", "tốt"]) == [PD_TU, PD_PHAM_VI]


def test_tu_ghep_co_chua_khong_khong_bi_nham():
    """Khop nguyen token: "không_khí" la mot tu rieng."""
    assert danh_dau_phu_dinh(["không_khí", "trong_lành"]) == [PD_KHONG, PD_KHONG]


def test_ve_chuyen_y_doi_lap_nhung():
    tu = ["pin", "trâu", ",", "nhưng", "màn_hình", "xấu"]
    assert danh_dau_chuyen_y(tu) == [CY_VE_NHUONG, CY_VE_NHUONG, CY_KHONG, CY_TU, CY_VE_NHAN, CY_VE_NHAN]


def test_ve_chuyen_y_nhuong_bo_o_dau_cau():
    tu = ["tuy", "pin", "yếu", ",", "máy", "đẹp"]
    assert danh_dau_chuyen_y(tu) == [CY_TU, CY_VE_NHUONG, CY_VE_NHUONG, CY_KHONG, CY_VE_NHAN, CY_VE_NHAN]


def test_ve_chuyen_y_nhuong_bo_giua_cau():
    tu = ["máy", "đẹp", "dù", "pin", "yếu"]
    assert danh_dau_chuyen_y(tu) == [CY_VE_NHAN, CY_VE_NHAN, CY_TU, CY_VE_NHUONG, CY_VE_NHUONG]


def test_tuy_nhung_cung_mot_cau():
    tu = ["tuy", "pin", "yếu", "nhưng", "máy", "đẹp"]
    assert danh_dau_chuyen_y(tu) == [CY_TU, CY_VE_NHUONG, CY_VE_NHUONG, CY_TU, CY_VE_NHAN, CY_VE_NHAN]


def test_chuyen_y_khong_tran_sang_cau_khac():
    tu = ["pin", "trâu", ".", "máy", "đẹp", "nhưng", "nóng"]
    assert danh_dau_chuyen_y(tu) == [
        CY_KHONG, CY_KHONG, CY_KHONG, CY_VE_NHUONG, CY_VE_NHUONG, CY_TU, CY_VE_NHAN,
    ]


def test_binh_luan_khong_tu_khoa_toan_nhan_0():
    tin_hieu = tin_hieu_cua(["pin", "trâu", ",", "máy", "đẹp"])
    assert set(tin_hieu["phu_dinh"]) == {PD_KHONG} and set(tin_hieu["chuyen_y"]) == {CY_KHONG}


# --- 2. Config ------------------------------------------------------------------


def _phang(d, tien_to=""):
    ra = {}
    for k, v in d.items():
        if isinstance(v, dict):
            ra.update(_phang(v, f"{tien_to}{k}."))
        else:
            ra[f"{tien_to}{k}"] = v
    return ra


def _khac(ten_a, ten_b):
    pa, pb = _phang(load_config(CONFIGS / ten_a)), _phang(load_config(CONFIGS / ten_b))
    return {k: (pa.get(k), pb.get(k)) for k in pa.keys() | pb.keys() if pa.get(k) != pb.get(k)}


def test_phobert_luat_khac_phobert_DUNG_MOT_khoa():
    assert _khac("phobert.yaml", "phobert_luat.yaml") == {"model.tin_hieu_luat": (None, ["phu_dinh", "chuyen_y"])}


@pytest.mark.parametrize("ten,kenh", [("phobert_luat_phu_dinh.yaml", ["phu_dinh"]),
                                      ("phobert_luat_chuyen_y.yaml", ["chuyen_y"])])
def test_bien_the_loai_bo_khac_DUNG_MOT_khoa(ten, kenh):
    assert _khac("phobert_luat.yaml", ten) == {"model.tin_hieu_luat": (["phu_dinh", "chuyen_y"], kenh)}


def test_da_dang_ky_trong_MODEL_REGISTRY():
    from nsmgat.train import MODEL_REGISTRY

    assert MODEL_REGISTRY["phobert_luat"] is PhoBERTLuatModel


# --- 3. Mo hinh -----------------------------------------------------------------


def _encoder_ti_hon():
    from transformers import RobertaConfig, RobertaModel

    return RobertaModel(RobertaConfig(
        vocab_size=200, hidden_size=32, num_hidden_layers=1, num_attention_heads=2,
        intermediate_size=64, max_position_embeddings=64,
    ))


def _ghi_du_lieu(tmp_path, dong):
    p = tmp_path / "du_lieu.jsonl"
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in dong) + "\n", encoding="utf-8")
    return str(p)


def _cfg(tmp_path, kenh=("phu_dinh", "chuyen_y")):
    dong = [
        {"uid": "a-X", "tokens": ["pin", "không", "trâu", "nhưng", "đẹp"]},
        {"uid": "b-X", "tokens": ["máy", "đẹp"]},
    ]
    return {"model": {"tin_hieu_luat": list(kenh), "dropout": 0.0}, "data": {"train_path": _ghi_du_lieu(tmp_path, dong)}}


def _batch():
    """`<s> ve cau </s></s> khia canh </s>`, mau thu hai co pad o cuoi."""
    return {
        "uid": ["a-X", "b-X"],
        "input_ids": torch.tensor([[0, 10, 11, 12, 13, 14, 2, 2, 20, 2], [0, 15, 16, 2, 2, 21, 2, 1, 1, 1]]),
        "attention_mask": torch.tensor([[1] * 10, [1] * 7 + [0] * 3]),
        "word_ids": [[None, 0, 1, 2, 3, 4, None, None, 5, None], [None, 0, 1, None, None, 2, None]],
    }


def test_khong_kenh_hoac_kenh_la_thi_nem_loi():
    for kenh in ((), ("phu_dinh", "la")):
        with pytest.raises(ValueError, match="tin_hieu_luat"):
            PhoBERTLuatModel({"model": {"tin_hieu_luat": list(kenh)}}, encoder=_encoder_ti_hon())


def test_uid_la_thi_nem_loi_chu_khong_coi_la_khong_co_nhan(tmp_path):
    model = PhoBERTLuatModel(_cfg(tmp_path), encoder=_encoder_ti_hon())
    batch = _batch()
    batch["uid"] = ["la-X", "b-X"]
    with pytest.raises(KeyError, match="la-X"):
        model(batch)


def test_nhan_chi_gan_cho_ve_cau(tmp_path):
    model = PhoBERTLuatModel(_cfg(tmp_path), encoder=_encoder_ti_hon())
    batch = _batch()
    pd = model._nhan_subword(batch, "phu_dinh", 10, torch.device("cpu"))
    cy = model._nhan_subword(batch, "chuyen_y", 10, torch.device("cpu"))
    assert pd[0].tolist() == [0, 0, PD_TU, PD_PHAM_VI, 0, 0, 0, 0, 0, 0]
    assert cy[0].tolist() == [0, CY_VE_NHUONG, CY_VE_NHUONG, CY_VE_NHUONG, CY_TU, CY_VE_NHAN, 0, 0, 0, 0]
    assert pd[1].sum() == 0 and cy[1].sum() == 0, "binh luan khong tu khoa phai toan nhan 0"


def test_them_lop_khong_lam_lech_day_ngau_nhien(tmp_path):
    """Dieu kien de cung seed thi khoi tao lop phan loai, mini-batch va dropout trung voi `phobert`."""
    enc_a, enc_b = _encoder_ti_hon(), _encoder_ti_hon()
    torch.manual_seed(7)
    PhoBERTClassifier({"model": {}}, encoder=enc_a)
    so_goc = torch.rand(1)
    torch.manual_seed(7)
    PhoBERTLuatModel(_cfg(tmp_path), encoder=enc_b)
    assert torch.rand(1) == so_goc


def test_ban_dau_trung_phobert_tren_mau_co_nhan(tmp_path):
    """Khoi tao 0, ke ca o mau co tu khoa, va inputs_embeds khong doi vi tri cua token."""
    enc = _encoder_ti_hon().eval()
    goc = PhoBERTClassifier({"model": {"dropout": 0.0}}, encoder=enc).eval()
    luat = PhoBERTLuatModel(_cfg(tmp_path), encoder=enc).eval()
    luat.classifier.load_state_dict(goc.classifier.state_dict())
    batch = _batch()
    with torch.no_grad():
        assert torch.allclose(luat(batch), goc(batch), atol=1e-5)


def test_tu_khong_nhan_khong_bao_gio_duoc_hoc(tmp_path):
    """padding_idx=0: dong 0 dung yen, cac dong khac co gradient. Nho do binh luan khong tu khoa co
    dau vao y het `phobert`, tro thanh nhom doi chung tu nhien."""
    model = PhoBERTLuatModel(_cfg(tmp_path), encoder=_encoder_ti_hon()).train()
    model(_batch()).sum().backward()
    for kenh, nhung in model.nhung_luat.items():
        g = nhung.weight.grad
        assert g[0].abs().sum() == 0, f"{kenh}: dong 0 khong duoc co gradient"
        assert g[1:].abs().sum() > 0, f"{kenh}: cac nhan khac phai co gradient"


def test_bien_the_loai_bo_chi_co_mot_kenh(tmp_path):
    model = PhoBERTLuatModel(_cfg(tmp_path, ("chuyen_y",)), encoder=_encoder_ti_hon())
    assert set(model.nhung_luat) == {"chuyen_y"}


def test_tham_so_them_vao_dung_bang_so_nhan(tmp_path):
    enc = _encoder_ti_hon()
    goc = PhoBERTClassifier({"model": {}}, encoder=enc).count_params()
    them = PhoBERTLuatModel(_cfg(tmp_path), encoder=enc).count_params() - goc
    assert them == (3 + 4) * 32


def _cac_o_notebook():
    nb = json.loads((REPO_ROOT / "notebooks/kaggle_tin_hieu_luat.ipynb").read_text(encoding="utf-8"))
    return ["".join(o["source"]) for o in nb["cells"] if o["cell_type"] == "code"]


def test_notebook_khong_loi_cu_phap():
    for chu in _cac_o_notebook():
        compile("\n".join(d for d in chu.splitlines() if not d.startswith(("%", "!"))), "o", "exec")


def test_notebook_dung_dung_config_va_du_hai_ben_cua_phep_so():
    """Doi chung chay config cua `phobert` y nguyen. Config sai thi ca phien mat nghia, ma Kaggle chi bao sau vai gio."""
    chu = "\n".join(_cac_o_notebook())
    assert '("phobert_cung_phien", "configs/phobert.yaml", "phobert", s, 24)' in chu
    assert '("phobert_luat", "configs/phobert_luat.yaml", "phobert_luat", s, 24)' in chu
    for ten in ("phobert_luat", "phobert_luat_phu_dinh", "phobert_luat_chuyen_y"):
        assert f"configs/{ten}.yaml" in chu and (CONFIGS / f"{ten}.yaml").exists()


def test_nhung_luat_hoc_theo_learning_rate_cua_dau_phan_loai(tmp_path):
    """Quy tac san co cua trainer: thu khoi tao moi thi lr lon, bo ma hoa lr nho."""
    from nsmgat.trainer import _build_optimizer

    model = PhoBERTLuatModel(_cfg(tmp_path), encoder=_encoder_ti_hon())
    opt = _build_optimizer(model, {"train": {"lr": 1e-3, "encoder_lr": 2e-5, "weight_decay": 0.01}})
    nhom_dau = next(g for g in opt.param_groups if g["lr"] == 1e-3)
    id_nhom = {id(p) for p in nhom_dau["params"]}
    assert all(id(p) in id_nhom for p in model.nhung_luat.parameters())
