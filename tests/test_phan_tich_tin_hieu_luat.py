"""[CD1.11d] Kiểm scripts/phan_tich_tin_hieu_luat.py: phép tính dựng tay, và các tình huống của kết luận trên một repo giả.

Nhóm quan trọng nhất là các test `test_cham_*`: tiêu chí đã đặt trước khi có kết quả, nên công cụ phải ra đúng kết luận ở cả những
tình huống dễ làm mình muốn tin (tăng ở chỗ luật không chạm tới, tăng ở bốn seed trên năm seed).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC / "scripts"))

import phan_tich_tin_hieu_luat as m  # noqa: E402

SEEDS = (42, 1337, 2024, 7, 123)


# --- Phép tính --------------------------------------------------------------------------------------------------------


def test_f1_lop_tinh_dung_theo_vi_du():
    # Lớp 1: tp 2, thật là lớp 1 có 3, đoán là lớp 1 có 3 -> F1 = 4 / 6.
    vang = np.array([1, 1, 1, 0, 2])
    doan = np.array([1, 1, 0, 1, 2])
    o = np.bincount(vang * 3 + doan, minlength=9).astype(np.float64)
    assert m.f1_lop(o, 1) == pytest.approx(4 / 6)
    assert m.f1_lop(o, 2) == pytest.approx(1.0)


def test_lop_khong_co_mau_nao_thi_f1_bang_0_chu_khong_loi():
    assert m.f1_lop(np.zeros(9), 1) == 0.0


def test_cung_dau():
    assert m._cung_dau(np.array([0.1, 0.2])) and m._cung_dau(np.array([-0.1, -0.2]))
    assert not m._cung_dau(np.array([0.1, -0.2]))
    assert not m._cung_dau(np.array([0.1, 0.0])), "hiệu số 0 ở một seed thì không phải cùng dấu"


def test_o_canh_cau_giu_chung_mot_truc_binh_luan():
    uid = ["t-1-A", "t-1-B", "t-2-A", "t-3-A"]
    vang = np.array([0, 1, 2, 0])
    doan = np.array([[0, 1, 2, 0], [1, 1, 2, 2]])
    chon = np.array([True, True, False, False])
    o = m.o_canh_cau(uid, vang, doan, chon)
    assert o.shape == (2, 3, 9), "trục bình luận phải là của cả tập, kể cả bình luận không được chọn"
    assert o[0, 0].sum() == 2 and o[0, 1:].sum() == 0
    assert o[1, 0, 0 * 3 + 1] == 1


def test_hieu_cua_hieu_trung_so_tay():
    # Nhóm 1 (bình luận 0): A đúng hết, B sai hết. Nhóm 2 (bình luận 1): A và B cùng đúng.
    a1 = np.zeros((1, 2, 9)); a1[0, 0, 0] = 2
    b1 = np.zeros((1, 2, 9)); b1[0, 0, 1] = 2
    a2 = np.zeros((1, 2, 9)); a2[0, 1, 0] = 2
    b2 = a2.copy()
    r = m.hieu_cua_hieu(a1, b1, a2, b2, 200, np.random.default_rng(0))["accuracy"]
    assert r["nhom_1"] == pytest.approx(1.0) and r["nhom_2"] == pytest.approx(0.0)
    assert r["hieu_cua_hieu"] == pytest.approx(1.0)


@pytest.mark.parametrize("hieu,p,cung_dau,p_hv,cong_nhan", [
    (0.01, 0.01, True, 0.008, True),
    (-0.01, 0.01, True, 0.008, False),   # giảm có ý nghĩa
    (0.01, 0.20, True, 0.008, False),    # bootstrap không đạt
    (0.01, 0.01, False, 0.008, False),   # không cùng dấu mọi seed
    (0.01, 0.01, True, 0.20, False),     # không vượt dao động giữa các lần huấn luyện
])
def test_ket_luan_doi_du_ca_ba_dieu_kien(hieu, p, cung_dau, p_hv, cong_nhan):
    kl = m.ket_luan({"hieu_so": hieu, "p": p, "cung_dau": cung_dau, "p_hoan_vi_seed": p_hv}, {"ci95_duoi": 0.001})
    assert kl["cong_nhan_cai_thien"] is cong_nhan
    assert kl["quy_duoc_cho_hien_tuong"] is cong_nhan


def test_ket_luan_khong_quy_cho_hien_tuong_khi_khoang_tin_cay_cham_0():
    kl = m.ket_luan({"hieu_so": 0.01, "p": 0.01, "cung_dau": True, "p_hoan_vi_seed": 0.008}, {"ci95_duoi": -0.001})
    assert kl["cong_nhan_cai_thien"] is True and kl["quy_duoc_cho_hien_tuong"] is False


def test_do_phu_dem_moi_binh_luan_mot_lan_va_do_dai_pham_vi():
    ds = [{"tokens": ["pin", "không", "trâu", "lắm"]}, {"tokens": ["pin", "không", "trâu", "lắm"]},  # hai khía cạnh, một bình luận
          {"tokens": ["máy", "đẹp", "nhưng", "nóng"]}, {"tokens": ["máy", "đẹp"]},
          {"tokens": ["ko", ",", "tuy", "rẻ"]}]
    k = m.do_phu(ds)
    assert k["so_mau"] == 5 and k["so_binh_luan"] == 4
    assert k["binh_luan"] == {"co_phu_dinh": 2, "co_chuyen_y": 2, "ca_hai": 1, "khong_tu_khoa": 1, "co_noi_nhuong_bo": 1}
    assert k["pham_vi_phu_dinh"]["luot"] == 2 and k["pham_vi_phu_dinh"]["lon_nhat"] == 2
    assert k["pham_vi_phu_dinh"]["ti_le_rong"] == pytest.approx(0.5)


# --- Repo giả -------------------------------------------------------------------------------------------------------


def _dung_repo(tmp_path, du_doan_luat):
    """60 bình luận, mỗi bình luận hai khía cạnh: 30 có từ phủ định, 30 không từ khoá. PhoBERT đối chứng sai mỗi seed vài chỗ khác nhau.

    `du_doan_luat(i_mau, nhan, doan_doi_chung, co_tu_khoa, i_seed)` trả về nhãn đoán của mô hình có luật.
    """
    (tmp_path / "data/processed").mkdir(parents=True)
    (tmp_path / "data/diagnostic").mkdir(parents=True)
    test, chan_doan = [], []
    for c in range(60):
        co = c % 2 == 0
        tokens = (["pin", "không", "trâu", "lắm", "đâu"] if co else ["pin", "rất", "trâu", "và", "đẹp"]) + ["máy", "ổn"]
        for k, asp in enumerate(("CAMERA", "BATTERY")):
            r = {"uid": f"visfd-test-{c:05d}-{asp}", "tokens": tokens, "label": (c + k) % 3}
            test.append(r)
            if c < 24:
                chan_doan.append({**r, "phenomenon": "negation" if co else "regular", "nhan_kiem_tra": "dong_y"})
    (tmp_path / "data/processed/visfd_test.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in test) + "\n", encoding="utf-8")
    (tmp_path / "data/diagnostic/diagnostic_300.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in chan_doan) + "\n", encoding="utf-8")

    def ghi(exp, seed, nhan_doan):
        d = tmp_path / "results" / exp / f"seed{seed}"
        d.mkdir(parents=True)
        d.joinpath("predictions.jsonl").write_text(
            "\n".join(json.dumps({"uid": r["uid"], "y_true": r["label"], "y_pred": int(p)}) for r, p in zip(test, nhan_doan)) + "\n", encoding="utf-8")

    for s, seed in enumerate(SEEDS):
        doi_chung, luat = [], []
        for i, r in enumerate(test):
            co = "không" in r["tokens"]
            # Sai ở 1/5 số mẫu, lệch theo seed để các seed không trùng nhau hoàn toàn.
            sai = (i + s) % 5 == 0
            d = (r["label"] + 1) % 3 if sai else r["label"]
            doi_chung.append(d)
            luat.append(du_doan_luat(i, r["label"], d, co, s))
        ghi(m.DOI_CHUNG_CHINH, seed, doi_chung)
        ghi(m.MO_HINH, seed, luat)
    return tmp_path


def test_cham_du_doan_y_het_thi_khong_cong_nhan(tmp_path):
    goc = _dung_repo(tmp_path, lambda i, y, d, co, s: d)
    kq = m.cham(goc, SEEDS, m.DOI_CHUNG_CHINH, 200, 0)
    chinh = kq["cap"][m.DOI_CHUNG_CHINH]["toan_tap"]["toan_bo"]["macro_f1"]
    assert chinh["hieu_so"] == 0
    assert kq["ket_luan"]["cong_nhan_cai_thien"] is False
    assert kq["khac_du_doan"]["cung_seed_voi_doi_chung"] == 0


def test_cham_tang_dung_cho_co_tu_khoa_thi_quy_duoc_cho_hien_tuong(tmp_path):
    goc = _dung_repo(tmp_path, lambda i, y, d, co, s: y if co else d)
    kq = m.cham(goc, SEEDS, m.DOI_CHUNG_CHINH, 300, 0)
    assert kq["ket_luan"]["cong_nhan_cai_thien"] is True
    assert kq["ket_luan"]["quy_duoc_cho_hien_tuong"] is True
    h = kq["hieu_cua_hieu"]["tu_khoa"]["accuracy"]
    assert h["nhom_1"] > 0 and h["nhom_2"] == 0
    assert kq["loi_uoc_luong"]["co_hien_tuong"]["thay_doi"] < 0 and kq["loi_uoc_luong"]["thuong"]["thay_doi"] == 0


def test_cham_tang_o_cho_luat_khong_cham_toi_thi_khong_quy_cho_hien_tuong(tmp_path):
    """Dù tổng thể tăng rõ, nếu phần tăng nằm ở bình luận không có từ khoá thì không được nói nhờ xử lý hai hiện tượng."""
    goc = _dung_repo(tmp_path, lambda i, y, d, co, s: d if co else y)
    kq = m.cham(goc, SEEDS, m.DOI_CHUNG_CHINH, 300, 0)
    assert kq["ket_luan"]["cong_nhan_cai_thien"] is True
    assert kq["ket_luan"]["quy_duoc_cho_hien_tuong"] is False


def test_cham_mot_seed_nguoc_chieu_thi_khong_cong_nhan(tmp_path):
    """Bốn seed tăng, một seed giảm: tiêu chí mục 4.2 đòi cùng dấu ở mọi seed."""
    def luat(i, y, d, co, s):
        if s == 0:  # seed đầu: sai thêm
            return (y + 1) % 3 if i % 3 == 0 else d
        return y
    goc = _dung_repo(tmp_path, luat)
    kq = m.cham(goc, SEEDS, m.DOI_CHUNG_CHINH, 300, 0)
    assert kq["cap"][m.DOI_CHUNG_CHINH]["toan_tap"]["toan_bo"]["macro_f1"]["cung_dau"] is False
    assert kq["ket_luan"]["cong_nhan_cai_thien"] is False


def test_cham_thieu_seed_thi_dung_chu_khong_cham_tren_phan_con_lai(tmp_path):
    goc = _dung_repo(tmp_path, lambda i, y, d, co, s: d)
    (goc / "results" / m.MO_HINH / "seed7" / "predictions.jsonl").unlink()
    with pytest.raises(FileNotFoundError, match="phobert_luat"):
        m.cham(goc, SEEDS, m.DOI_CHUNG_CHINH, 50, 0)


def test_cham_ket_qua_in_duoc_va_doc_lai_duoc_bang_json(tmp_path):
    goc = _dung_repo(tmp_path, lambda i, y, d, co, s: y if co else d)
    kq = m.cham(goc, SEEDS, m.DOI_CHUNG_CHINH, 100, 0)
    chu = m.in_ket_qua(kq)
    assert "công nhận cải thiện: True" in chu and "độ phủ lớp trung tính" in chu
    assert json.loads(json.dumps(kq))["seeds"] == list(SEEDS)
