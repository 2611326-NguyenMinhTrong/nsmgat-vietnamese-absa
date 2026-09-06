"""[CD1.4a] Test baseline tu dien cam xuc.

Hai phan:
  1. scripts/build_lexicon_from_train.py — cach tinh diem, chong ro ri
  2. src/nsmgat/models/lexicon.py — LexiconModel

Trong tam: CHONG RO RI (tu dien chi duoc sinh tu train) va tinh dung cua
cong thuc tinh diem (lam muot + tru ti le nen).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_lexicon_from_train import (  # noqa: E402
    do_do_phu,
    do_tran_mu_khia_canh,
    main as build_main,
    tinh_diem_tu_dien,
)

from nsmgat.models.lexicon import LexiconModel  # noqa: E402


def rec(uid: str, tokens: list[str], label: int, text: str | None = None) -> dict:
    return {
        "uid": uid,
        "text": text if text is not None else " ".join(tokens),
        "tokens": tokens,
        "pos": ["X"] * len(tokens),
        "heads": [-1] * len(tokens),
        "deprels": ["root"] * len(tokens),
        "aspect": "BATTERY",
        "label": label,
        "domain": "visfd",
        "split": "train",
    }


# --- Cach tinh diem -----------------------------------------------------------


def test_tu_chi_xuat_hien_o_nhan_duong_thi_diem_duong():
    records = [rec(f"u{i}", ["pin", "trâu"], 2) for i in range(20)]
    records += [rec(f"v{i}", ["pin", "yếu"], 0) for i in range(20)]

    tu_dien, _ = tinh_diem_tu_dien(records, min_freq=1, smoothing=1.0)

    assert tu_dien["trâu"] > 0.5, "tu chi di voi nhan tich cuc phai co diem duong manh"
    assert tu_dien["yếu"] < -0.5, "tu chi di voi nhan tieu cuc phai co diem am manh"
    assert abs(tu_dien["pin"]) < 0.1, "tu xuat hien deu o ca hai nhan phai gan 0"


def test_lam_muot_keo_tu_hiem_ve_0():
    """Tu xuat hien 1 lan khong duoc co diem tuyet doi — day la nguon nhieu chinh."""
    records = [rec(f"u{i}", ["ổn"], 1) for i in range(50)]
    records.append(rec("hiem", ["từ_hiếm"], 2))

    it_muot, _ = tinh_diem_tu_dien(records, min_freq=1, smoothing=0.01)
    nhieu_muot, _ = tinh_diem_tu_dien(records, min_freq=1, smoothing=50.0)

    assert abs(nhieu_muot["từ_hiếm"]) < abs(it_muot["từ_hiếm"]), (
        "lam muot manh hon phai keo tu hiem ve gan 0 hon"
    )


def test_tru_ti_le_nen_lam_tu_trung_tinh_ve_0():
    """Du lieu lech lop: neu khong tru ti le nen, tu trung tinh van co diem duong."""
    # 90% tich cuc, "may" xuat hien deu khap
    records = [rec(f"p{i}", ["máy", "tốt"], 2) for i in range(90)]
    records += [rec(f"n{i}", ["máy", "tệ"], 0) for i in range(10)]

    tu_dien, thong_ke = tinh_diem_tu_dien(records, min_freq=1, smoothing=1.0)

    assert thong_ke["ti_le_nen"]["lech_nen"] > 0.5, "du lieu phai that su lech lop"
    assert abs(tu_dien["máy"]) < 0.15, (
        "tu xuat hien theo dung ti le nen phai gan 0 sau khi tru ti le nen"
    )


def test_bo_token_it_gap():
    records = [rec(f"u{i}", ["hay"], 2) for i in range(10)]
    records.append(rec("x", ["chỉ_1_lần"], 0))

    tu_dien, thong_ke = tinh_diem_tu_dien(records, min_freq=5, smoothing=1.0)

    assert "hay" in tu_dien
    assert "chỉ_1_lần" not in tu_dien
    assert thong_ke["so_token_bi_loai_vi_it_gap"] >= 1


def test_token_lap_trong_mot_cau_chi_dem_mot_lan():
    """Tu lap 10 lan trong 1 cau khong duoc tinh manh hon tu xuat hien 1 lan."""
    records = [rec("a", ["tốt"] * 10, 2), rec("b", ["ổn"], 2)]
    records += [rec(f"n{i}", ["tệ"], 0) for i in range(2)]

    tu_dien, _ = tinh_diem_tu_dien(records, min_freq=1, smoothing=1.0)

    assert tu_dien["tốt"] == pytest.approx(tu_dien["ổn"], abs=1e-6), (
        "so lan lap trong CUNG mot cau khong duoc anh huong diem"
    )


def test_bo_dau_cau_va_tu_chuc_nang():
    records = [rec(f"u{i}", ["và", "của", ".", "đẹp"], 2) for i in range(10)]
    tu_dien, _ = tinh_diem_tu_dien(records, min_freq=1, smoothing=1.0)

    assert "đẹp" in tu_dien
    for bo in ("và", "của", "."):
        assert bo not in tu_dien


# --- Do phu va tran mu khia canh ----------------------------------------------


def test_do_do_phu():
    records = [rec("a", ["đẹp", "xyz"], 2)]
    phu = do_do_phu(records, {"đẹp": 0.5})

    assert phu["tong_token"] == 2
    assert phu["token_co_trong_tu_dien"] == 1
    assert phu["ti_le_phu_token"] == 50.0
    assert phu["example_khong_tra_cuu_duoc_tu_nao"] == 0


def test_example_khong_tra_cuu_duoc_tu_nao():
    records = [rec("a", ["xyz"], 2)]
    assert do_do_phu(records, {"đẹp": 0.5})["example_khong_tra_cuu_duoc_tu_nao"] == 1


def test_tran_mu_khia_canh_khi_moi_cau_mot_nhan():
    """Cau nao cung chi 1 khia canh -> mo hinh mu khia canh khong bi thiet -> tran 100%."""
    records = [rec("a", ["x"], 2, text="cau A"), rec("b", ["y"], 0, text="cau B")]
    assert do_tran_mu_khia_canh(records)["tran_accuracy"] == 100.0


def test_tran_mu_khia_canh_khi_cau_co_khia_canh_trai_nhan():
    """Cung 1 cau, 2 khia canh trai nhan -> chi doan dung duoc 1 -> tran 50%."""
    records = [rec("a", ["x"], 2, text="cung cau"), rec("b", ["x"], 0, text="cung cau")]
    ket_qua = do_tran_mu_khia_canh(records)

    assert ket_qua["tran_accuracy"] == 50.0
    assert ket_qua["cau_co_khia_canh_trai_nhan"] == 1


# --- CHONG RO RI — quan trong nhat --------------------------------------------


def test_script_chi_doc_tap_train(tmp_path, capsys):
    """Tu dien PHAI chi sinh tu train. Neu doc nham dev/test thi moi ket qua
    cua baseline nay vo gia tri, va loi rat kho phat hien."""
    train = tmp_path / "train.jsonl"
    train.write_text(
        "\n".join(json.dumps(rec(f"u{i}", ["chỉ_có_ở_train"], 2)) for i in range(10)),
        encoding="utf-8",
    )
    # File nay ton tai canh train nhung KHONG duoc doc
    (tmp_path / "test.jsonl").write_text(
        json.dumps(rec("t", ["chỉ_có_ở_test"], 0)), encoding="utf-8"
    )

    out = tmp_path / "lex.json"
    code = build_main(["--train", str(train), "-o", str(out), "--stats", str(tmp_path / "s.json"),
                       "--min-freq", "1"])

    assert code == 0
    tu_dien = json.loads(out.read_text(encoding="utf-8"))
    assert "chỉ_có_ở_train" in tu_dien
    assert "chỉ_có_ở_test" not in tu_dien, "RO RI: tu dien chua token cua tap test"


# --- LexiconModel -------------------------------------------------------------


@pytest.fixture
def model_va_batch(tmp_path):
    lex = tmp_path / "lex.json"
    lex.write_text(json.dumps({"đẹp": 0.8, "tệ": -0.7}, ensure_ascii=False), encoding="utf-8")

    data = tmp_path / "train.jsonl"
    data.write_text(
        "\n".join(
            json.dumps(r)
            for r in [
                rec("u-pos", ["máy", "đẹp"], 2),
                rec("u-neg", ["máy", "tệ"], 0),
                rec("u-trong", ["xyz", "abc"], 1),
            ]
        ),
        encoding="utf-8",
    )

    cfg = {
        "model": {"lexicon_path": str(lex)},
        "data": {"train_path": str(data), "dev_path": "", "test_path": ""},
    }
    model = LexiconModel(cfg)
    batch = {"uid": ["u-pos", "u-neg", "u-trong"], "labels": torch.tensor([2, 0, 1])}
    return model, batch


def test_forward_tra_ve_dung_shape(model_va_batch):
    model, batch = model_va_batch
    logits = model.forward(batch)
    assert logits.shape == (3, 3)


def test_dac_trung_tinh_dung(model_va_batch):
    model, _ = model_va_batch

    mean_pos, cov_pos = model._dac_trung("u-pos")
    assert mean_pos == pytest.approx(0.8)
    assert cov_pos == pytest.approx(0.5), "1/2 token tra cuu duoc"

    mean_neg, _ = model._dac_trung("u-neg")
    assert mean_neg == pytest.approx(-0.7)

    assert model._dac_trung("u-trong") == (0.0, 0.0), "khong tra cuu duoc tu nao -> (0, 0)"


def test_uid_la_khong_biet_thi_tra_ve_0_khong_sap(model_va_batch):
    model, _ = model_va_batch
    assert model._dac_trung("uid-khong-ton-tai") == (0.0, 0.0)


def test_rat_it_tham_so_hoc_duoc(model_va_batch):
    """Phan hoc duoc chi la Linear(2,3) = 9 tham so. Neu con so nay phinh to
    thi mo hinh khong con la 'baseline tu dien' nua."""
    model, _ = model_va_batch
    assert model.count_params() == 9


def test_explain_liet_ke_token_dong_gop(model_va_batch):
    """Tu dien GIAI THICH DUOC — uu the that so voi PhoBERT."""
    model, batch = model_va_batch
    giai_thich = model.explain(batch)

    assert len(giai_thich) == 3
    pos = giai_thich[0]
    assert pos["uid"] == "u-pos"
    assert [d["token"] for d in pos["token_dong_gop_manh_nhat"]] == ["đẹp"]
    assert giai_thich[2]["token_dong_gop_manh_nhat"] == [], "Example khong co tu nao trong tu dien"


def test_bao_loi_ro_rang_khi_thieu_tu_dien(tmp_path):
    cfg = {
        "model": {"lexicon_path": str(tmp_path / "khong_ton_tai.json")},
        "data": {"train_path": ""},
    }
    with pytest.raises(FileNotFoundError, match="build_lexicon_from_train"):
        LexiconModel(cfg)


def test_dang_ky_trong_model_registry():
    from nsmgat.train import MODEL_REGISTRY

    assert MODEL_REGISTRY["lexicon"] is LexiconModel
