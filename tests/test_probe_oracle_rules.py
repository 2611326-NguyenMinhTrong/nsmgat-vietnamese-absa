"""[CD1.11] Kiểm scripts/probe_oracle_rules.py: luật lý tưởng, ước lượng theo ô, khoảng cách trên cây, và khớp kết quả thật."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import probe_oracle_rules as m  # noqa: E402

GOC = Path(__file__).resolve().parents[1]


def test_nguoc_cuc_chi_bat_cap_tich_cuc_tieu_cuc():
    vang = np.array([0, 0, 1, 2, 2, 1])
    doan = np.array([2, 1, 0, 0, 2, 1])
    assert m.nguoc_cuc(vang, doan).tolist() == [True, False, False, True, False, False]


def test_sua_theo_mat_na_khong_dong_vao_mang_goc():
    vang, doan = np.array([0, 1, 2]), np.array([2, 0, 2])
    ra = m.sua_theo_mat_na(vang, doan, np.array([True, False, False]))
    assert ra.tolist() == [0, 0, 2]
    assert doan.tolist() == [2, 0, 2]


def test_do_do_khop_cach_tinh_tay():
    vang, doan = np.array([0, 0, 1, 2]), np.array([0, 1, 1, 2])
    f, a = m.do_do(vang, doan)
    # Lớp 0: P = 1, R = 0,5, F1 = 2/3. Lớp 1: P = 0,5, R = 1, F1 = 2/3. Lớp 2: F1 = 1.
    assert f == pytest.approx((2 / 3 + 2 / 3 + 1) / 3)
    assert a == pytest.approx(0.75)


def test_khoang_cach_cay_va_hai_cay_rieng():
    # Câu 1: token 0 -> 2, 1 -> 2, 2 là gốc. Câu 2: token 3 là gốc, 4 -> 3.
    heads = [2, 2, -1, -1, 3]
    assert m.khoang_cach_cay(heads, 1, 2) == 1
    assert m.khoang_cach_cay(heads, 0, 1) == 2
    assert m.khoang_cach_cay(heads, 2, 2) == 0
    assert m.khoang_cach_cay(heads, 1, 4) is None


def test_cay_co_vong_thi_dung():
    with pytest.raises(ValueError, match="vòng"):
        m.khoang_cach_cay([1, 0], 0, 1)


def _mau(cau: str, aspect: str, tokens, label: int, **them):
    return {"uid": f"visfd-test-{cau}-{aspect}", "tokens": tokens, "label": label, **them}


def test_p2_uoc_luong_theo_o_dung_trong_so_cua_tap_kiem_tra():
    """Hai ô: (phu_dinh, tích cực) có 4 mẫu, rút 2 dòng, 1 dòng có phủ định; (doi_chung, tích cực) có 6 mẫu, rút 2,
    1 dòng có phủ định. Luật bắt ô đầu: độ chính xác 2/4, độ phủ 2/(2 + 3)."""
    co = ["máy", "không", "tốt", "lắm", "đâu_đó"]  # "không" là từ khoá chắc; "đâu_đó" không phải từ ngờ
    khong = ["máy", "rất", "tốt", "luôn", "nhé"]
    test = [_mau(f"0000{i}", "GENERAL", co, 2) for i in range(4)] + [_mau(f"0001{i}", "GENERAL", khong, 2) for i in range(6)]
    test += [_mau("00020", "GENERAL", ["máy", "mà", "tốt", "lắm", "nhé"], 2),   # chỉ có từ ngờ: ngoài quần thể
             _mau("00021", "GENERAL", ["không", "tốt"], 2)]                      # 2 từ: ngoài độ dài
    chan_doan = [dict(test[0], phenomenon="negation"), dict(test[1], phenomenon="regular"),
                 dict(test[4], phenomenon="negation"), dict(test[5], phenomenon="regular"),
                 dict(test[11], phenomenon="negation")]
    kq = m.p2_luat_tho(chan_doan, test, so_lan=200, rng=np.random.default_rng(0))
    assert kq["quan_the"] == 10 and kq["mau_cau_chi_co_tu_ngo"] == 1 and kq["mau_ngoai_do_dai"] == 1
    assert kq["dong_ngoai_quan_the"] == 1
    pd = kq["phu_dinh"]
    assert pd["do_chinh_xac"] == pytest.approx(0.5)
    assert pd["do_phu"] == pytest.approx(0.4)
    assert pd["tho"] == {"dong_luat_bat": 2, "dong_luat_bat_dung": 1, "dong_co_hien_tuong": 2}
    # Bỏ sót đếm trên cả tập chẩn đoán, kể cả dòng ngoài quần thể: chỉ dòng của câu 00010 không có "không".
    assert pd["bo_sot_tren_tap_chan_doan"] == {"dong": 1, "co_tu_ngo": 0}


def test_p2_o_khong_co_dong_nao_thi_dung():
    test = [_mau("00000", "GENERAL", ["máy", "không", "tốt", "lắm", "nhé"], 2),
            _mau("00001", "GENERAL", ["máy", "không", "tốt", "lắm", "nhé"], 0)]
    with pytest.raises(ValueError, match="Không ước lượng được"):
        m.p2_luat_tho([dict(test[0], phenomenon="negation")], test, so_lan=10, rng=np.random.default_rng(0))


@pytest.mark.filterwarnings("ignore:invalid value")  # ba nhóm còn lại không có dòng nào
def test_p1_tap_chan_doan_lat_dung_loi_nguoc_cuc():
    test = [_mau(f"0000{i}", "GENERAL", ["x"], y) for i, y in enumerate([2, 2, 0, 1])]
    chan_doan = [dict(r, phenomenon="negation", nhan_kiem_tra=k) for r, k in zip(test, ["dong_y", "negative", "dong_y", "dong_y"])]
    # Seed nào cũng: mẫu 1 ngược cực (2 -> 0), mẫu 3 sai có trung tính (1 -> 2).
    du_doan = [(np.array([2, 2, 0, 1]), np.array([2, 0, 0, 2]))] * len(m.cb.SEEDS)
    kq = m.p1_tap_chan_doan(chan_doan, test, du_doan)["negation"]
    assert (kq["n"], kq["loi"], kq["loi_nguoc_cuc"], kq["loi_goc_trung_tinh"], kq["loi_o_dong_khong_dong_y"]) == (4, 2, 1, 1, 1)
    assert kq["macro_f1_sau_khi_lat"] == pytest.approx(m.do_do(np.array([2, 2, 0, 1]), np.array([2, 2, 0, 2]))[0])
    assert kq["tang"] > 0


def test_p1_toan_tap_chi_lat_o_cau_co_tu_khoa_phu_dinh():
    test = [_mau("00000", "GENERAL", ["không", "tốt"], 2), _mau("00001", "GENERAL", ["rất", "tốt"], 2),
            _mau("00002", "GENERAL", ["nhưng", "tốt"], 1)]
    du_doan = [(np.array([2, 2, 1]), np.array([0, 0, 2]))] * len(m.cb.SEEDS)
    kq = m.p1_toan_tap(test, du_doan)
    assert kq["nguoc_cuc_o_cau_co_phu_dinh"]["so_loi_sua"] == 1
    assert kq["nguoc_cuc_moi_cho"]["so_loi_sua"] == 2
    assert kq["moi_loi_o_cau_co_tu_khoa"]["so_loi_sua"] == 2
    assert kq["moi_loi_o_cau_co_tu_khoa"]["tang_accuracy"] == pytest.approx(2 / 3)


def test_p3_tach_dang_chuan_va_viet_tat():
    test = [
        # "pin không trâu": không -> trâu (phó từ), kề nhau trên cây.
        {"uid": "visfd-test-00000-BATTERY", "tokens": ["pin", "không", "trâu"], "pos": ["N", "R", "A"], "heads": [2, 2, -1]},
        {"uid": "visfd-test-00000-GENERAL", "tokens": ["pin", "không", "trâu"], "pos": ["N", "R", "A"], "heads": [2, 2, -1]},
        # "pin ko trâu": ko bị coi là động từ gốc, trâu gắn vào pin: ko - pin - trâu, cách 2 cạnh.
        {"uid": "visfd-test-00001-BATTERY", "tokens": ["pin", "ko", "trâu"], "pos": ["N", "V", "A"], "heads": [1, -1, 0]},
        # "ko ." : sau từ phủ định là dấu câu, chỉ tính lượt.
        {"uid": "visfd-test-00002-BATTERY", "tokens": ["ổn", "ko", "."], "pos": ["A", "V", "CH"], "heads": [1, -1, 1]},
    ]
    kq = m.p3_cu_phap(test)
    assert kq["so_cau"] == 3  # câu 00000 có hai khía cạnh, chỉ đếm một lần
    assert kq["chuan"]["luot"] == 1 and kq["chuan"]["ti_le_pho_tu"] == 1 and kq["chuan"]["ti_le_ke_nhau"] == 1
    vt = kq["viet_tat"]
    assert (vt["luot"], vt["co_tu_sau"], vt["ti_le_pho_tu"], vt["ti_le_ke_nhau"], vt["khoang_cach_tb"]) == (2, 1, 0, 0, 2)


def test_nap_du_doan_lech_thu_tu_thi_dung(tmp_path):
    test = [_mau("00000", "GENERAL", ["x"], 2), _mau("00001", "GENERAL", ["x"], 0)]
    for s in m.cb.SEEDS:
        d = tmp_path / "phobert" / f"seed{s}"
        d.mkdir(parents=True)
        dong = [{"uid": r["uid"], "aspect": "GENERAL", "y_true": r["label"], "y_pred": r["label"]} for r in reversed(test)]
        (d / "predictions.jsonl").write_text("".join(json.dumps(x) + "\n" for x in dong), encoding="utf-8")
    with pytest.raises(ValueError, match="không cùng thứ tự"):
        m.nap_du_doan(tmp_path, "phobert", test)


@pytest.mark.skipif(not (GOC / "data/processed/visfd_test.jsonl").exists() or not (GOC / "data/diagnostic/diagnostic_300.jsonl").exists(),
                    reason="tập kiểm tra hoặc tập chẩn đoán không có trên máy (không nằm trong git)")
def test_khop_ket_qua_da_cong_bo():
    """Macro-F1 gốc của P1 phải khớp hai kết quả đã công bố: theo nhóm (diagnostic_eval.json) và toàn tập (metrics.json)."""
    kq = m.tham_do(GOC / "results", GOC / "data/processed/visfd_test.jsonl", GOC / "data/diagnostic/diagnostic_300.jsonl",
                   "phobert", so_lan=200, seed=0)
    da = json.loads((GOC / "results/diagnostic_eval.json").read_text(encoding="utf-8"))["ket_qua"]["tat_ca"]["phobert"]
    for g in m.NHOM:
        assert kq["p1"]["tap_chan_doan"][g]["macro_f1"] == pytest.approx(da[g]["macro_f1"]["gia_tri"])
        assert kq["p1"]["tap_chan_doan"][g]["n"] == da[g]["n"]
    f = [json.loads((GOC / f"results/phobert/seed{s}/metrics.json").read_text(encoding="utf-8"))["test"]["macro_f1"] for s in m.cb.SEEDS]
    assert kq["p1"]["toan_tap_kiem_tra"]["macro_f1"] == pytest.approx(np.mean(f), abs=1e-6)
    assert kq["p2"]["dong_dung_de_uoc_luong"] + kq["p2"]["dong_ngoai_quan_the"] == sum(da[g]["n"] for g in m.NHOM)
