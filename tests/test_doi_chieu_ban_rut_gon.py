"""[CD1.12d] Kiểm scripts/doi_chieu_ban_rut_gon.py: bản rút gọn không được chứa điều gì bản đầy đủ không có."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import doi_chieu_ban_rut_gon as m  # noqa: E402

DAY_DU = """# Chương 4. THỬ

## 4.1. Dữ liệu

Tập kiểm tra có 6.722 mẫu thuộc 2.187 bình luận [@A]. Mô hình đạt accuracy 91,86 % và macro-F1 86,64 %.

Bảng 4.2: Kết quả

| Mô hình | Accuracy |
|---|---|
| PhoBERT [@A] | 91,86 |
| ASGCN | 91,33 |

Xem thêm Bảng 4.7 và mục 4.6, công thức (2.4).

s = a + b    (4.1)
"""


def _viet(thu_muc: Path, chuong: str, phu_luc: str = "") -> None:
    thu_muc.mkdir(parents=True, exist_ok=True)
    (thu_muc / "Chuong4_Thu.md").write_text(chuong, encoding="utf-8")
    if phu_luc:
        (thu_muc / m.TEN_PHU_LUC).write_text(phu_luc, encoding="utf-8")
    (thu_muc / "tai_lieu.json").write_text(json.dumps({"A": "Tác giả A."}), encoding="utf-8")


def _kiem(tmp_path: Path, chuong: str, phu_luc: str = ""):
    _viet(tmp_path / "dd", DAY_DU)
    _viet(tmp_path / "rg", chuong, phu_luc)
    return m.kiem(m.doc_ban(tmp_path / "dd"), m.doc_ban(tmp_path / "rg"), {"A": "x"})


def test_so_trong_bo_qua_nhan_dan_cheo_trich_dan_va_so_cong_thuc():
    so = m.so_trong(DAY_DU)
    assert {"6.722", "2.187", "91,86", "86,64", "91,33"} <= so
    # 4.2, 4.7, 4.6, 2.4, 4.1 chỉ là số thứ tự của bảng, mục, công thức
    assert not {"4.2", "4.7", "4.6", "2.4", "4.1"} & so


def test_ban_cat_dung_thi_khong_co_gi_la(tmp_path):
    kq = _kiem(tmp_path, "# Chương 4. THỬ\n\nTập kiểm tra có 6.722 mẫu thuộc 2.187 bình luận [@A].\n\n"
                         "Bảng 4.1: Kết quả\n\n| Mô hình | Accuracy |\n|---|---|\n| PhoBERT [@A] | 91,86 |\n")
    assert kq["so_la"] == [] and kq["hang_la"] == [] and kq["khoa_la"] == []
    assert kq["so_cau_co_so"] == 1 and kq["so_cau_giu_nguyen"] == 1 and kq["cau_viet_lai"] == []


def test_so_go_sai_bi_bat(tmp_path):
    kq = _kiem(tmp_path, "# Chương 4. THỬ\n\nMô hình đạt accuracy 91,68 % trên 6.722 mẫu.\n")
    assert [s for _, s in kq["so_la"]] == ["91,68"]


def test_hang_bang_bi_sua_thi_bi_bat_tru_bang_khai_la_moi(tmp_path):
    chuong = "# Chương 4. THỬ\n\nBảng 4.1: Kết quả\n\n| Mô hình | Accuracy |\n|---|---|\n| ASGCN | 91,86 |\n"
    kq = _kiem(tmp_path, chuong)
    assert len(kq["hang_la"]) == 1 and kq["so_la"] == []  # số có thật nhưng nằm sai hàng
    phu_luc = "# PHỤ LỤC\n\nBảng A.2: Bảng mới\n\n| Mô hình | Accuracy |\n|---|---|\n| ASGCN | 91,86 |\n"
    kq = _kiem(tmp_path, "# Chương 4. THỬ\n\nKhông có số.\n", phu_luc)
    assert kq["hang_la"] == []
    phu_luc = phu_luc.replace("91,86", "99,99")
    assert [s for _, s in _kiem(tmp_path, "# Chương 4. THỬ\n", phu_luc)["so_la"]] == ["99,99"]  # số của bảng mới vẫn phải có thật


def test_cau_co_so_viet_lai_duoc_liet_ke_de_doc(tmp_path):
    kq = _kiem(tmp_path, "# Chương 4. THỬ\n\nTrên 6.722 mẫu, mô hình đạt macro-F1 86,64 %.\n")
    assert kq["so_la"] == [] and kq["so_cau_giu_nguyen"] == 0
    assert [c for _, c in kq["cau_viet_lai"]] == ["Trên 6.722 mẫu, mô hình đạt macro-F1 86,64 %."]


def test_khoa_trich_dan_la_va_khoa_bi_bo(tmp_path):
    kq = _kiem(tmp_path, "# Chương 4. THỬ\n\nTheo [@B], không có số.\n")
    assert [k for _, k in kq["khoa_la"]] == ["B"] and kq["khoa_bi_bo"] == ["A"]


def test_ma_thoat(tmp_path, capsys):
    _viet(tmp_path / "dd", DAY_DU)
    _viet(tmp_path / "rg", "# Chương 4. THỬ\n\nTập kiểm tra có 6.722 mẫu thuộc 2.187 bình luận [@A].\n")
    chung = ["--goc", str(tmp_path), "--day-du", "dd", "--rut-gon", "rg"]
    assert m.main(chung) == 0
    _viet(tmp_path / "rg", "# Chương 4. THỬ\n\nTập kiểm tra có 6.723 mẫu.\n")
    assert m.main(chung + ["--in-cau"]) == 1
    assert "SỐ LẠ" in capsys.readouterr().out
