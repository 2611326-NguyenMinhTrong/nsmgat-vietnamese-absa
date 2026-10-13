"""[CD1.12b] Kiểm scripts/doi_chieu_ban_goc.py: nhận ra con số viết kiểu Việt trong văn bản tiếng Anh."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import doi_chieu_ban_goc as m  # noqa: E402

VAN = {"A": "Table 2: BERT-SPC 0.8446 0.7698 on 11,122 comments. Accuracy 82.93 and macro F1: 87%.",
       "B": "We obtain 79.66 on the negation set, dropping 24 pp."}


def test_cac_dang_so_viet_kieu_viet_duoc_tim_dung():
    assert m.co_trong("84,46", VAN["A"]) and m.co_trong("76,98", VAN["A"])  # phần trăm viết thành tỉ lệ
    assert m.co_trong("11.122", VAN["A"]) and m.co_trong("82,93", VAN["A"]) and m.co_trong("87", VAN["A"])
    assert not m.co_trong("84,4", VAN["A"]) and not m.co_trong("2,93", VAN["A"])  # không khớp một phần của số khác
    assert not m.co_trong("11.12", VAN["A"])


def test_bo_nam_va_so_muc_khoi_danh_sach_so():
    assert m.so_trong_cau("Năm 2014 [@A], mục 3.8 nêu 84,46 % trên 11.122 bình luận.") == ["84,46", "11.122"]
    assert m.so_trong_cau("Không có con số nào ở đây.") == []


def test_phan_loai_bon_trang_thai():
    md = ("# Chương\n\n"
          "Mô hình đạt 84,46 % [@A]. Tập có 11.122 bình luận.\n\n"
          "Bài [@A] và bài [@B] đều thử. Bài sau đạt 79,66 % [@B], còn 55,5 % thì không có trong bài nào.\n\n"
          "Bài chưa tải [@C] đạt 70,1 %.\n\n"
          "Đoạn này không trích ai nên số 99,9 % không được xét.\n")
    kq, dem = m.kiem_chuong(md, VAN)
    assert dem == 5
    tt = {(s, t) for t, s, *_ in kq}
    assert ("84,46", "thay") in tt and ("11.122", "thay") in tt and ("79,66", "thay") in tt
    assert ("55,5", "khong_thay") in tt and ("70,1", "chua_co_ban_goc") in tt


def test_so_thuoc_cong_trinh_khac_trong_cung_doan_duoc_ghi_rieng():
    md = "Bài [@B] dựng tập thử thách. Trên tập đó, mô hình của [@A] đạt 79,66 %.\n"
    kq, _ = m.kiem_chuong(md, VAN)
    assert [(t, s, k) for t, s, k, _ in kq] == [("thay_cung_doan", "79,66", "B")]


def test_duong_dan_pdf_va_lenh_kiem_bao_khi_chua_co_ban_goc(tmp_path, capsys):
    assert m.duong_dan_pdf("https://aclanthology.org/D19-1464/") == "https://aclanthology.org/D19-1464.pdf"
    assert m.duong_dan_pdf("https://arxiv.org/abs/1902.09314") == "https://arxiv.org/pdf/1902.09314"
    assert m.duong_dan_pdf("https://doi.org/10.1145/3589131") == ""
    (tmp_path / "C.md").write_text("Đạt 84,46 % [@A] và 12,3 % [@A].\n", encoding="utf-8")
    assert m.main(["kiem", "C.md", "--nhap", str(tmp_path), "--nguon", str(tmp_path / "trong")]) == 2
    nguon = tmp_path / "nguon"
    nguon.mkdir()
    (nguon / "A.txt").write_text(VAN["A"], encoding="utf-8")
    assert m.main(["kiem", "C.md", "--nhap", str(tmp_path), "--nguon", str(nguon)]) == 1
    ra = capsys.readouterr().out
    assert "KHÔNG THẤY" in ra and "12,3" in ra and "cần xem tay 1" in ra
