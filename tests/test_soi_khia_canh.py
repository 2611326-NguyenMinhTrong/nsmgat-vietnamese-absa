"""[CD1.6a'] Test công cụ soi predictions.jsonl theo khía cạnh.

Vì sao công cụ này cần test: nó sinh ra những con số sẽ đi thẳng vào Chương 4 của
cuốn chuyên đề. Một công cụ phân tích tính SAI còn tệ hơn là không có, vì nó cho ra
một bảng trông rất thuyết phục mà không ai đối chiếu lại.

Test quan trọng nhất là `test_f1_khop_voi_f1_per_class_trong_metrics`: nó đối chiếu
F1 do script tự tính với `f1_per_class` mà đường huấn luyện thật đã ghi ra. Hai con
số đi qua hai đường hoàn toàn khác nhau, trùng nhau thì mới tin được.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from soi_khia_canh import (  # noqa: E402
    doc_du_doan,
    f1_cua_lop,
    ho_tro_theo_khia_canh,
    main,
    _tb_lech,
)

KET_QUA = REPO_ROOT / "results"
LAN_CHAY = [(e, s) for e in ("phobert", "asgcn", "asgcn_linked") for s in (42, 1337, 2024)]


def _co_du_ket_qua() -> bool:
    return all((KET_QUA / e / f"seed{s}" / "predictions.jsonl").exists() for e, s in LAN_CHAY)


can_ket_qua = pytest.mark.skipif(
    not _co_du_ket_qua(),
    reason="Chua tai du predictions.jsonl cua 3 mo hinh x 3 seed tu Colab ve",
)


# --- Cong thuc F1 -------------------------------------------------------------

def test_f1_tinh_dung_tren_vi_du_tay():
    # Lop 1: 2 dung, 1 bo sot, 1 bao nham -> precision 2/3, recall 2/3, F1 2/3
    rows = [
        {"aspect": "A", "y_true": 1, "y_pred": 1},
        {"aspect": "A", "y_true": 1, "y_pred": 1},
        {"aspect": "A", "y_true": 1, "y_pred": 0},
        {"aspect": "A", "y_true": 0, "y_pred": 1},
    ]
    assert f1_cua_lop(rows, 1) == pytest.approx(2 / 3)


def test_f1_bang_0_khi_khong_doan_dung_ca_nao():
    """Xay ra that o khia canh rat mong, vd SER&ACC chi co 27 cau trung lap."""
    rows = [{"aspect": "A", "y_true": 1, "y_pred": 0} for _ in range(5)]
    assert f1_cua_lop(rows, 1) == 0.0


def test_f1_khong_lay_lop_khac_lam_nhieu():
    """F1 cua lop 1 khong duoc doi khi them cau cua lop khac ma mo hinh doan dung."""
    goc = [{"aspect": "A", "y_true": 1, "y_pred": 1}, {"aspect": "A", "y_true": 1, "y_pred": 0}]
    them = goc + [{"aspect": "A", "y_true": 2, "y_pred": 2} for _ in range(50)]
    assert f1_cua_lop(goc, 1) == f1_cua_lop(them, 1)


@can_ket_qua
@pytest.mark.parametrize("exp,seed", LAN_CHAY)
def test_f1_khop_voi_f1_per_class_trong_metrics(exp, seed):
    """Doi chieu voi con so do duong huan luyen that ghi ra.

    `metrics.json` sinh tu `nsmgat.evaluate`, con day tu dem tay tren
    `predictions.jsonl`. Hai duong doc lap nhau, trung nhau thi moi tin duoc ca hai.
    """
    rows = doc_du_doan(KET_QUA, exp, seed)
    m = json.loads((KET_QUA / exp / f"seed{seed}" / "metrics.json").read_text(encoding="utf-8"))
    for lop in range(3):
        assert f1_cua_lop(rows, lop) == pytest.approx(m["test"]["f1_per_class"][lop], abs=1e-6)


# --- Ho tro theo khia canh ----------------------------------------------------

def test_ho_tro_dem_dung_va_khong_sot_cau():
    rows = [
        {"aspect": "PRICE", "y_true": 1, "y_pred": 1},
        {"aspect": "PRICE", "y_true": 1, "y_pred": 0},
        {"aspect": "PRICE", "y_true": 2, "y_pred": 2},
        {"aspect": "SCREEN", "y_true": 0, "y_pred": 0},
    ]
    d = ho_tro_theo_khia_canh(rows)
    assert d["PRICE"] == [0, 2, 1]
    assert d["SCREEN"] == [1, 0, 0]
    assert sum(sum(v) for v in d.values()) == len(rows)


@can_ket_qua
def test_nhan_that_giong_nhau_o_MOI_mo_hinh_va_seed():
    """Script in ra cau "nhan that nen bang nay giong nhau o moi mo hinh".

    Day la cho khoa lai cau do. Neu mot ngay nao do khong con dung — vi du mot lan
    chay dung tap test khac, hoac thu tu dong bi xao — thi bang phan bo o
    `chuyende1/notes/` khong con mo ta dung du lieu cua ca ba mo hinh nua.
    """
    chuan = None
    for exp, seed in LAN_CHAY:
        nhan = [(r["uid"], r["aspect"], r["y_true"]) for r in doc_du_doan(KET_QUA, exp, seed)]
        if chuan is None:
            chuan = nhan
        assert nhan == chuan, f"{exp}/seed{seed} co nhan that khac lan chay dau tien"


# --- Gop nhieu seed -----------------------------------------------------------

def test_mot_seed_thi_do_lech_bang_0_chu_khong_nem_loi():
    """statistics.stdev nem StatisticsError khi chi co 1 gia tri — chay
    `--seeds 42` la chuyen binh thuong nen khong duoc vo o day."""
    assert _tb_lech([0.5]) == (0.5, 0.0)
    tb, sd = _tb_lech([0.4, 0.6])
    assert tb == pytest.approx(0.5) and sd > 0


# --- CLI ----------------------------------------------------------------------

def test_bao_loi_RO_khi_thieu_file_chu_khong_nem_traceback(tmp_path, capsys):
    ma = main(["f1", "--exp", "khong_ton_tai", "--seeds", "42", "--results", str(tmp_path)])
    assert ma == 1
    loi = capsys.readouterr().err
    assert "khong_ton_tai" in loi and "Colab" in loi


@can_ket_qua
@pytest.mark.parametrize("lenh", ["phan-bo", "f1", "nham", "loi"])
def test_bon_lenh_deu_chay_duoc(lenh, capsys):
    assert main([lenh, "--results", str(KET_QUA)]) == 0
    assert capsys.readouterr().out.strip()


@can_ket_qua
def test_doi_lop_thi_bang_doi_theo(capsys):
    main(["f1", "--exp", "phobert", "--lop", "1", "--results", str(KET_QUA)])
    trung_lap = capsys.readouterr().out
    main(["f1", "--exp", "phobert", "--lop", "2", "--results", str(KET_QUA)])
    tich_cuc = capsys.readouterr().out
    assert "TRUNG LẬP" in trung_lap and "TÍCH CỰC" in tich_cuc
    assert trung_lap != tich_cuc
