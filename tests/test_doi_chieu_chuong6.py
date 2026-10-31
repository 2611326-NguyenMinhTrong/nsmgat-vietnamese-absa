"""[CD1.12] Kiểm scripts/doi_chieu_chuong6.py: khớp bản nháp thật, bắt được câu bị sửa, chứng cứ mất ở chương nguồn, số lạ."""

import shutil
import sys
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC / "scripts"))

import doi_chieu_chuong6 as m  # noqa: E402

NHAP = GOC / m.NHAP_MAC_DINH
CAN = [NHAP / m.TEP_C6, NHAP / m.C3, NHAP / m.C4, NHAP / m.C5, GOC / "results/error_analysis.json"]
pytestmark = pytest.mark.skipif(not all(p.exists() for p in CAN),
                                reason="bản nháp hoặc kết quả phân tích lỗi không có trên máy (bản nháp không nằm trong git)")


def _ban_sao(tmp_path: Path) -> Path:
    d = tmp_path / "nhap"
    d.mkdir()
    for ten in (m.TEP_C6, m.C3, m.C4, m.C5):
        shutil.copy2(NHAP / ten, d / ten)
    return d


def _chay(d: Path, capsys):
    ma = m.main(["--goc", str(GOC), "--nhap", str(d)])
    return ma, capsys.readouterr().out


def test_ban_nhap_that_khop(capsys):
    assert m.main(["--goc", str(GOC)]) == 0, capsys.readouterr().out


def test_cau_chuong_6_bi_sua_thi_bao(tmp_path, capsys):
    d = _ban_sao(tmp_path)
    p = d / m.TEP_C6
    p.write_text(p.read_text(encoding="utf-8").replace("ngang nhau.", "khác nhau rõ."), encoding="utf-8")
    ma, ra = _chay(d, capsys)
    assert ma == 1 and "6.1, ba mô hình ngang nhau" in ra


def test_chuong_nguon_mat_chung_cu_thi_bao(tmp_path, capsys):
    """Khi Chương 4 có kết quả GPT-4o và dòng [TODO] mất đi, câu của Chương 6 về GPT-4o phải bị báo để viết lại."""
    d = _ban_sao(tmp_path)
    p = d / m.C4
    van = p.read_text(encoding="utf-8")
    assert "[TODO: kết quả của GPT-4o" in van
    p.write_text(van.replace("[TODO: kết quả của GPT-4o", "Kết quả của GPT-4o"), encoding="utf-8")
    ma, ra = _chay(d, capsys)
    assert ma == 1 and "MẤT CHỨNG CỨ  6.1, GPT-4o chưa có kết quả" in ra


def test_so_moi_trong_chuong_6_bi_bao(tmp_path, capsys):
    d = _ban_sao(tmp_path)
    p = d / m.TEP_C6
    p.write_text(p.read_text(encoding="utf-8").replace("## 6.2.", "Một câu mới có con số 91,79 %.\n\n## 6.2."), encoding="utf-8")
    ma, ra = _chay(d, capsys)
    assert ma == 1 and "SỐ CHƯA CÓ CHỖ KIỂM  91,79" in ra


def test_bang_lich_theo_tuan_bi_bao(tmp_path, capsys):
    """Từ 24/10/2026 mục 6.3 không có lịch theo tuần: một bảng lịch thêm lại bị quét số báo ra."""
    d = _ban_sao(tmp_path)
    p = d / m.TEP_C6
    van = p.read_text(encoding="utf-8")
    assert "Tuần" not in van
    p.write_text(van + "\n| Mốc | Việc |\n|---|---|\n| Tuần 1 – 2 | đặc tả luật |\n", encoding="utf-8")
    ma, ra = _chay(d, capsys)
    assert ma == 1 and "SỐ CHƯA CÓ CHỖ KIỂM  1:" in ra and "SỐ CHƯA CÓ CHỖ KIỂM  2:" in ra
