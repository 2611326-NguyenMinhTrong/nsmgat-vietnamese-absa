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


def test_ca_phai_ghi_dung_nhom_hien_tuong(tmp_path, capsys):
    """Mỗi ca ở mục 5.2 ghi nhóm hiện tượng của tập chẩn đoán; ghi sai nhóm phải bị báo."""
    van = NHAP.read_text(encoding="utf-8")
    cu = "nhóm chuyển ý, nhãn gốc trung tính"
    assert van.count(cu) == 1
    ma, ra = _chay(tmp_path, van.replace(cu, "nhóm thường, nhãn gốc trung tính"), capsys)
    assert ma == 1 and "5.2, ví dụ 2" in ra


def test_doi_so_trong_bang_loai_loi_thi_bao(tmp_path, capsys):
    """Bảng 5.1 mới (loại lỗi theo nhãn gốc và nhãn đoán) phải khớp results/phan_tich_bo_sung.json."""
    van = NHAP.read_text(encoding="utf-8")
    cu = "| Cả hai | 84 | 21,8 | 10,4 |"
    assert van.count(cu) == 1
    ma, ra = _chay(tmp_path, van.replace(cu, "| Cả hai | 84 | 21,8 | 11,4 |"), capsys)
    assert ma == 1 and "Bảng 5.1, both" in ra


def test_doi_muc_tang_toi_da_thi_bao(tmp_path, capsys):
    """Con số trả lời câu hỏi "có căn cứ nào" ở mục 5.6.2 phải khớp phép đo."""
    van = NHAP.read_text(encoding="utf-8")
    assert van.count("tăng khoảng 3,23 điểm") == 1
    ma, ra = _chay(tmp_path, van.replace("tăng khoảng 3,23 điểm", "tăng khoảng 5,23 điểm"), capsys)
    assert ma == 1 and "5.6.2, mức tăng tối đa" in ra


@pytest.mark.skipif(not (GOC / m.NGUON_GOC / "MAMS.txt").exists(), reason="chưa tải bản gốc (doi_chieu_ban_goc.py tai)")
def test_nhan_dinh_ve_tai_lieu_phai_co_cau_lam_chung(monkeypatch, tmp_path, capsys):
    """Mục 5.5: bản gốc mất câu làm chứng cho một nhận định thì công cụ phải báo."""
    for k in m.CHUNG_CU:
        van = (GOC / m.NGUON_GOC / f"{k}.txt").read_text(encoding="utf-8")
        if k == "MAMS":
            van = van.replace("poorly", "nicely")
        (tmp_path / f"{k}.txt").write_text(van, encoding="utf-8")
    monkeypatch.setattr(m, "NGUON_GOC", tmp_path)  # đường dẫn tuyệt đối: goc / tmp_path vẫn là tmp_path
    assert m.main(["--goc", str(GOC)]) == 1
    assert "BẢN GỐC MAMS KHÔNG CÓ CÂU" in capsys.readouterr().out


def test_cau_dinh_tinh_bi_bao_khi_so_lieu_khong_con_do(monkeypatch, tmp_path, capsys):
    """Số liệu không còn đỡ một câu định tính thì câu đó phải bị báo; giả lập bằng cách ép điều kiện của một câu thành sai."""
    goc_neu = m.dc4.neu
    monkeypatch.setattr(m.dc4, "neu", lambda dung, cau, mo_ta: goc_neu(False if "hơn bốn phần năm" in cau else dung, cau, mo_ta))
    ma, ra = _chay(tmp_path, NHAP.read_text(encoding="utf-8"), capsys)
    assert ma == 1 and "SỐ LIỆU KHÔNG CÒN ĐỠ CÂU" in ra
