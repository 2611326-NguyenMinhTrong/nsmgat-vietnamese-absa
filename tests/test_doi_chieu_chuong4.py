"""[CD1.12f] Kiểm phần tìm kiếm của scripts/doi_chieu_chuong4.py trên văn bản tí hon, không cần dữ liệu thật."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import doi_chieu_chuong4 as m  # noqa: E402

VAN = """## 4.4. Kết quả

Lời văn có câu cần tìm, cao hơn 1,07 điểm.

Bảng 4.3: Kết quả trên tập kiểm tra của X

| Mô hình | Accuracy |
|---|---|
| PhoBERT   tinh chỉnh | 91,86 |

Bảng C.4: Macro-F1 trên bốn nhóm của tập chẩn đoán

| Mô hình | Thường |
|---|---|
| PhoBERT tinh chỉnh | 90,0 |

Bảng 4.2: Thang mô hình và thành phần được thêm ở mỗi bậc

| Bậc | Mô hình | Số tham số |
|---|---|---|
| 1 | Từ điển | 9 |
| 4 | ASGCN | 136.181.763 |
| 4b | ASGCN nối gốc | 136.181.763 |
"""


def test_moi_bang_duoc_kiem_deu_co_so_o_ban_chinh_va_tu_khoa():
    assert set(m.SO_BANG_RUT_GON) == set(m.TU_KHOA_BANG)
    assert len(set(m.SO_BANG_RUT_GON.values())) == len(m.SO_BANG_RUT_GON)  # không hai bảng nào trỏ về cùng một số


def test_tach_bang_lay_ten_va_hang_bo_khoang_trang_thua():
    b = m.tach_bang(VAN)
    assert list(b) == ["4.3", "C.4", "4.2"]
    assert b["4.3"]["ten"] == "Kết quả trên tập kiểm tra của X"
    assert "| PhoBERT tinh chỉnh | 91,86 |" in b["4.3"]["van"]
    assert b["4.2"]["hang"][-1] == "| 4b | ASGCN nối gốc | 136.181.763 |"
    with pytest.raises(ValueError):
        m.tach_bang(VAN + "\nBảng 4.3: Trùng số\n\n| a |\n")


def test_hang_bang_phai_nam_o_dung_bang():
    b, van = m.tach_bang(VAN), m.chuan(VAN)
    # Bảng 4.5 của bản đầy đủ là Bảng 4.3 của bản chính
    da_kiem, lech, bo_qua = m.tim([("Bảng 4.5, phobert", "| PhoBERT tinh chỉnh | 91,86 |")], van, b, "rut_gon")
    assert (da_kiem, lech, bo_qua) == (1, [], 0)
    # hàng của bảng macro-F1 (4.12, tức C.4) không được tính là có ở bảng accuracy 4.11 (tức 4.8)
    _, lech, _ = m.tim([("Bảng 4.12, dòng 1", "| PhoBERT tinh chỉnh | 91,86 |")], van, b, "rut_gon")
    assert len(lech) == 1 and "nằm ở Bảng 4.3 chứ không ở Bảng C.4" in lech[0][2] and lech[0][0] == "Bảng C.4, dòng 1"
    _, lech, _ = m.tim([("Bảng 4.11, dòng 1", "| PhoBERT tinh chỉnh | 90,0 |")], van, b, "rut_gon")
    assert "bản nháp không có Bảng 4.8" in lech[0][2]
    # ở bản đầy đủ số bảng giữ nguyên
    _, lech, _ = m.tim([("Bảng 4.5, phobert", "| PhoBERT tinh chỉnh | 91,86 |")], van, b, "day_du")
    assert "bản nháp không có Bảng 4.5" in lech[0][2]


def test_cum_chu_loi_van_cau_bo_qua_va_cau_cua_phan_tom_tat():
    b, van = m.tach_bang(VAN), m.chuan(VAN)
    kiem = [("Lời văn, a", "cao hơn 1,07 điểm"), ("Lời văn, b", "cao hơn 1,08 điểm"), ("4.6, chỉ ở bản kia", None),
            (m.DAU_TOM_TAT + "c", "đạt 86,64 %")]
    da_kiem, lech, bo_qua = m.tim(kiem, van, b, "rut_gon")
    assert (da_kiem, [x[0] for x in lech], bo_qua) == (2, ["Lời văn, b"], 2)  # chưa có phần tóm tắt thì bỏ qua chỗ của nó
    da_kiem, lech, bo_qua = m.tim(kiem, van, b, "rut_gon", tom_tat="PhoBERT đạt  86,64 % trên tập kiểm tra.")
    assert (da_kiem, [x[0] for x in lech], bo_qua) == (3, ["Lời văn, b"], 1)
    # cụm của phần tóm tắt chỉ tìm trong phần tóm tắt, dù thân bài có đúng cụm đó
    _, lech, _ = m.tim([(m.DAU_TOM_TAT + "d", "cao hơn 1,07 điểm")], van, b, "rut_gon", tom_tat="Không có cụm ấy.")
    assert len(lech) == 1 and "phần tóm tắt" in lech[0][2]


def test_theo_ban_va_doi_so_bang():
    assert m.theo_ban("day_du", day_du="a", rut_gon="b") == "a" and m.theo_ban("rut_gon", day_du="a") is None
    assert m.doi_so_bang("rut_gon", "4.6, số phép so ở Bảng 4.15") == "4.6, số phép so ở Bảng C.6"
    assert m.doi_so_bang("day_du", "Bảng 4.15, dòng 2") == "Bảng 4.15, dòng 2"


def test_ten_bang_phai_chua_tu_khoa():
    b, van = m.tach_bang(VAN), m.chuan(VAN)
    kiem = m.kiem_ten_bang(b, "rut_gon", ["4.5", "4.12"])
    assert m.tim(kiem, van, b, "rut_gon")[1] == []
    # đổi tên hai bảng cho nhau: hàng vẫn còn nhưng tên không còn đúng
    doi = VAN.replace("Kết quả trên tập kiểm tra của X", "Macro-F1 gì đó")
    b2 = m.tach_bang(doi)
    lech = m.tim(m.kiem_ten_bang(b2, "rut_gon", ["4.5"]), m.chuan(doi), b2, "rut_gon")[1]
    assert len(lech) == 1 and "Kết quả trên tập kiểm tra" in lech[0][1]
    # bảng không có trong bản nháp cũng bị báo
    assert len(m.tim(m.kiem_ten_bang(b, "rut_gon", ["4.9"]), van, b, "rut_gon")[1]) == 1


def test_so_tham_so_phai_o_dung_hang_cua_bac():
    b, van = m.tach_bang(VAN), m.chuan(VAN)
    dung = m.kiem_thang_mo_hinh(b, "rut_gon", {"1": "9", "4": "136.181.763", "4b": "136.181.763"})
    assert m.tim(dung, van, b, "rut_gon")[1] == []
    sai = m.kiem_thang_mo_hinh(b, "rut_gon", {"1": "136.181.763", "5": "9"})  # sai số ở bậc 1, không có hàng của bậc 5
    assert [x[0] for x in m.tim(sai, van, b, "rut_gon")[1]] == ["Bảng 4.2, số tham số của bậc 1", "Bảng 4.2, số tham số của bậc 5"]


def test_doc_tom_tat_va_so_la(tmp_path):
    f = tmp_path / "TrangDau.md"
    assert m.doc_tom_tat(f) is None
    f.write_text("# LỜI CẢM ƠN\n\nCảm ơn 3 lần.\n\n# TÓM TẮT\n\nĐạt 86,64 % trên 799 mẫu.\n\n# MỤC KHÁC\n\n12 thứ khác.\n", encoding="utf-8")
    tom_tat = m.doc_tom_tat(f)
    assert tom_tat == "Đạt 86,64 % trên 799 mẫu."
    assert m.so_la_trong_tom_tat(tom_tat, "Thân bài có 86,64 và 799.") == []
    assert m.so_la_trong_tom_tat(tom_tat, "Thân bài chỉ có 86,46 và 799.") == ["86,64"]


def test_cau_dinh_tinh_va_cach_viet_p():
    assert m.neu(True, "câu", "mô tả") == ("mô tả", "câu")
    assert m.neu(False, "câu", "mô tả")[1].startswith("SỐ LIỆU KHÔNG CÒN ĐỠ CÂU")
    assert m.p_loi(0.0004) == "p nhỏ hơn 0,001" and m.p_loi(0.2049) == "p bằng 0,205"
