"""[CD1.11] Kiểm scripts/doi_chieu_chuong5.py: khớp bản nháp thật, và bắt được số sai, số chưa có chỗ kiểm, hàng sai bảng."""

import sys
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC / "scripts"))

import doi_chieu_chuong5 as m  # noqa: E402

NHAP = GOC / m.TEP_MAC_DINH
CAN = [NHAP, GOC / "data/processed/visfd_test.jsonl", GOC / "data/diagnostic/diagnostic_300.jsonl"]
pytestmark = pytest.mark.skipif(not all(p.exists() for p in CAN),
                                reason="bản nháp, tập kiểm tra hoặc tập chẩn đoán không có trên máy (không nằm trong git)")


def _chay(tmp_path: Path, van: str, capsys):
    p = tmp_path / "Chuong5.md"
    p.write_text(van, encoding="utf-8")
    ma = m.main(["--goc", str(GOC), "--nhap", str(p)])
    return ma, capsys.readouterr().out


def test_ban_nhap_that_khop(capsys):
    assert m.main(["--goc", str(GOC)]) == 0, capsys.readouterr().out


def test_bat_duoc_so_sai(tmp_path, capsys):
    van = NHAP.read_text(encoding="utf-8")
    assert van.count("khoảng cách là 9,1 điểm") == 1
    ma, ra = _chay(tmp_path, van.replace("khoảng cách là 9,1 điểm", "khoảng cách là 9,2 điểm"), capsys)
    assert ma == 1 and "5.1, khoảng cách ở PhoBERT" in ra


def test_bat_duoc_so_chua_co_cho_kiem(tmp_path, capsys):
    van = NHAP.read_text(encoding="utf-8").replace("## 5.5.", "Một câu mới có con số 42,7 % chưa ai kiểm.\n\n## 5.5.")
    ma, ra = _chay(tmp_path, van, capsys)
    assert ma == 1 and "SỐ CHƯA CÓ CHỖ KIỂM  42,7" in ra


def test_hang_bang_phai_nam_dung_bang(tmp_path, capsys):
    van = NHAP.read_text(encoding="utf-8")
    hang = next(d for d in van.split("\n") if d.startswith("| Phủ định | 119 |"))
    # Đưa hàng ra khỏi Bảng 5.1 xuống cuối chương: chữ vẫn có trong chương nhưng không còn nằm trong bảng.
    van = van.replace(hang + "\n", "") + "\n" + hang + "\n"
    ma, ra = _chay(tmp_path, van, capsys)
    assert ma == 1 and "Bảng 5.1 không có hàng này" in ra


def test_cau_dinh_tinh_bi_bao_khi_so_lieu_khong_con_do(monkeypatch, tmp_path, capsys):
    """Số liệu không còn đỡ một câu định tính thì câu đó phải bị báo; giả lập bằng cách ép điều kiện của một câu thành sai."""
    goc_neu = m.dc4.neu
    monkeypatch.setattr(m.dc4, "neu", lambda dung, cau, mo_ta: goc_neu(False if "hơn bốn phần năm" in cau else dung, cau, mo_ta))
    ma, ra = _chay(tmp_path, NHAP.read_text(encoding="utf-8"), capsys)
    assert ma == 1 and "SỐ LIỆU KHÔNG CÒN ĐỠ CÂU" in ra
