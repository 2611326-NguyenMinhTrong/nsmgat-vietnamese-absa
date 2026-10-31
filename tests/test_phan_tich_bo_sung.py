"""[CD1.12r] Kiểm scripts/phan_tich_bo_sung.py: ví dụ dựng tay, và khớp với các kết quả đã công bố khi có dữ liệu thật."""

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC / "scripts"))

import phan_tich_bo_sung as m  # noqa: E402

TEST = GOC / "data/processed/visfd_test.jsonl"
CHAN_DOAN = GOC / "data/diagnostic/diagnostic_300.jsonl"
co_du_lieu = pytest.mark.skipif(not (TEST.exists() and CHAN_DOAN.exists()),
                                reason="tập kiểm tra hoặc tập chẩn đoán không có trên máy (không nằm trong git)")


def test_loai_loi_dem_dung_cap_va_ti_le_theo_nhan():
    dong = [{"uid": "a", "label": 1}, {"uid": "b", "label": 1}, {"uid": "c", "label": 2}, {"uid": "d", "label": 0}]
    vi_tri = {"a": 0, "b": 1, "c": 2, "d": 3}
    vang = np.array([1, 1, 2, 0])
    du_doan = [(vang, np.array([2, 1, 2, 0])), (vang, np.array([2, 0, 2, 0]))]  # seed 1: 1 lỗi; seed 2: 2 lỗi
    kq = m.loai_loi(dong, vi_tri, du_doan)
    assert kq["n"] == 4 and kq["n_theo_nhan"] == [1, 2, 1]
    assert kq["loi"] == pytest.approx(1.5)
    assert kq["cap"] == {"1->0": pytest.approx(0.5), "1->2": pytest.approx(1.0)}
    assert kq["ti_le_sai_theo_nhan"] == [0.0, pytest.approx(0.75), 0.0]


def test_macro_f1_khop_cach_tinh_cua_cong_cu_kiem_dinh():
    vang = np.array([0, 0, 1, 1, 2, 2, 2])
    doan = np.array([0, 1, 1, 1, 2, 0, 2])
    mt = np.zeros((3, 3))
    np.add.at(mt, (vang, doan), 1)
    o = np.bincount(vang * 3 + doan, minlength=9).astype(np.float64)
    assert m.macro_f1_tu_ma_tran(mt) == pytest.approx(float(m.cb.do_do(o)[0]))


def test_sua_het_loi_thi_macro_f1_bang_mot():
    goc = np.array([[8.0, 1.0, 1.0], [2.0, 6.0, 2.0], [0.0, 3.0, 7.0]])
    sua = goc - np.diag(np.diag(goc))
    assert m.tang_khi_sua(goc, sua) == pytest.approx(1.0 - m.macro_f1_tu_ma_tran(goc))
    assert m.tang_khi_sua(goc, sua, phan=0.0) == 0.0
    assert 0 < m.tang_khi_sua(goc, sua, phan=0.5) < m.tang_khi_sua(goc, sua)


def test_uoc_luong_can_theo_trong_so_cua_o():
    """Ô A có 100 mẫu rút 2 dòng (trọng số 50), ô B có 10 mẫu rút 2 dòng (trọng số 5): tỉ lệ thô sẽ sai."""
    o_a, o_b = ("phu_dinh", 0), ("doi_chung", 0)
    cac_o = {o_a: [{"uid": "a", "label": 0, "phenomenon": "negation", "nhan_kiem_tra": "dong_y"},
                   {"uid": "b", "label": 0, "phenomenon": "regular", "nhan_kiem_tra": "dong_y"}],
             o_b: [{"uid": "c", "label": 0, "phenomenon": "negation", "nhan_kiem_tra": "negative"},
                   {"uid": "d", "label": 0, "phenomenon": "regular", "nhan_kiem_tra": "dong_y"}]}
    so_mau = Counter({o_a: 100, o_b: 10})
    vi_tri = {"a": 0, "b": 1, "c": 2, "d": 3}
    vang = np.zeros(4, dtype=int)
    du_doan = [(vang, np.array([2, 0, 2, 0]))]  # sai ở a và c
    n, ma_tran = m.uoc_luong(cac_o, so_mau, ("negation",), vi_tri, du_doan)
    assert n == pytest.approx(55.0)
    assert ma_tran[0, 2] == pytest.approx(55.0)
    # Chỉ tính dòng đồng ý với nhãn gốc: c bị loại khỏi ma trận, nhưng vẫn được đếm là mẫu có hiện tượng.
    n, ma_tran = m.uoc_luong(cac_o, so_mau, ("negation",), vi_tri, du_doan, chi_dong_y=True)
    assert n == pytest.approx(55.0)
    assert ma_tran[0, 2] == pytest.approx(50.0)


def test_ti_le_khac_va_dung_het_sai_het():
    vang = np.array([0, 1, 2])
    a = np.array([[0, 1, 0], [0, 1, 0]])
    b = np.array([[1, 1, 0], [1, 2, 0]])
    assert m.ti_le_khac(a) == 0.0
    assert m.ti_le_khac(a, b) == pytest.approx((1 / 3 + 2 / 3 + 1 / 3 + 2 / 3) / 4)
    assert m.dung_het_sai_het(vang, a, b) == 1  # mẫu đầu: a đúng cả hai seed, b sai cả hai seed; mẫu giữa b đúng một seed
    assert m.dung_het_sai_het(vang, b, a) == 0


def test_nhom_con_tach_dung_dang_viet_tat():
    uid = ["t-1-A", "t-1-B", "t-2-A", "t-3-A"]
    vang = np.array([0, 2, 1, 1])
    test = [{"tokens": ["pin", "ko", "tốt"]}, {"tokens": ["pin", "ko", "tốt"]}, {"tokens": ["pin", "không", "tốt"]}, {"tokens": ["pin", "tốt"]}]
    n = m.mat_na_nhom_con(uid, vang, test)
    assert n["trai_nhan"].tolist() == [True, True, False, False]
    assert n["co_viet_tat"].tolist() == [True, True, False, False]
    assert n["chi_phu_dinh_chuan"].tolist() == [False, False, True, False]
    assert (n["co_viet_tat"] ^ n["khong_viet_tat"]).all()


@co_du_lieu
def test_khop_ket_qua_da_cong_bo():
    """Bảng lỗi ở mục 5.3 (probe_results.json) phải khớp phép đếm mới; tổng các cặp bằng tổng số lỗi."""
    kq = json.loads((GOC / m.TEP_KET_QUA).read_text(encoding="utf-8"))
    p1 = json.loads((GOC / "results/probe_results.json").read_text(encoding="utf-8"))["p1"]["tap_chan_doan"]
    for g in m.NHOM:
        x = kq["loai_loi"]["tat_ca"][g]
        assert x["n"] == p1[g]["n"]
        assert x["loi"] == pytest.approx(p1[g]["loi"])
        assert sum(x["cap"].values()) == pytest.approx(x["loi"])
        assert x["cap"].get("1->0", 0) + x["cap"].get("1->2", 0) == pytest.approx(p1[g]["loi_goc_trung_tinh"])
        assert x["cap"].get("0->2", 0) + x["cap"].get("2->0", 0) == pytest.approx(p1[g]["loi_nguoc_cuc"])
    p = kq["phan_loi"]
    assert p["quan_the"] + p["ngoai_quan_the"] == 6722
    # Mọi mẫu của quần thể là "có hiện tượng" hoặc "thường": hai phần số mẫu và số lỗi phải cộng lại bằng cả quần thể.
    assert p["nhom"]["co_hien_tuong"]["ti_le_mau"] + p["nhom"]["thuong"]["ti_le_mau"] == pytest.approx(1.0, abs=0.01)
    # Trần chỉ tính phần mẫu đồng ý với nhãn gốc phải nhỏ hơn trần tính mọi mẫu.
    assert p["tran"]["co_hien_tuong_dong_y"]["tang"] < p["tran"]["co_hien_tuong"]["tang"]
