"""[CD1.12k] Test scripts/kiem_sua_tay_word.py: đọc chữ file Word, so khác, và lệnh không đụng file thật."""

from __future__ import annotations

import sys
from pathlib import Path

import docx

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import kiem_sua_tay_word as k  # noqa: E402


def _word(duong: Path, doan, hang=None) -> Path:
    d = docx.Document()
    for t in doan:
        d.add_paragraph(t)
    if hang:
        bang = d.add_table(rows=len(hang), cols=len(hang[0]))
        for i, h in enumerate(hang):
            for j, o in enumerate(h):
                bang.cell(i, j).text = o
    d.save(str(duong))
    return duong


def test_cac_khoi_bo_doan_rong_va_doc_hang_bang(tmp_path):
    p = _word(tmp_path / "a.docx", ["Một", "", "Hai"], [["x", "y"]])
    assert k.cac_khoi(p) == ["Một", "Hai", "| x | y |"]


def test_so_khac_bat_doan_sua_them_va_bo():
    nhap = ["A", "B", "C"]
    word = ["A", "B sửa", "C", "D thêm"]
    assert k.so_khac(nhap, word) == [(["B"], ["B sửa"]), ([], ["D thêm"])]
    assert k.so_khac(nhap, list(nhap)) == []


def test_chu_khac():
    assert k.chu_khac("Tính cấp thiết. Hướng", "Tính cấp thiết, hướng") == "- thiết. + thiết, - Hướng + hướng"


def test_lenh_bao_cho_sua_tay_va_khong_dung_file_that(tmp_path, monkeypatch, capsys):
    that = _word(tmp_path / "bao_cao.docx", ["Đoạn học viên đã sửa", "Đoạn chung"])
    truoc = that.read_bytes()

    def ghep_gia(argv):  # giả lệnh ghép: ghi chữ của bản nháp vào file được chỉ định
        duong = Path(argv[argv.index("--docx") + 1])
        _word(duong, ["Đoạn trong bản nháp", "Đoạn chung"])
        return 0

    monkeypatch.setattr(k.nc, "main", ghep_gia)
    ma = k.main(["--docx", str(that), "--nhap", str(tmp_path)])
    ra = capsys.readouterr().out
    assert ma == 1
    assert "WORD (sẽ mất)         : Đoạn học viên đã sửa" in ra
    assert that.read_bytes() == truoc, "file Word thật bị sửa"


def test_lenh_tra_0_khi_trung(tmp_path, monkeypatch):
    that = _word(tmp_path / "bao_cao.docx", ["Đoạn chung"])
    monkeypatch.setattr(k.nc, "main", lambda argv: (_word(Path(argv[argv.index("--docx") + 1]), ["Đoạn chung"]), 0)[1])
    assert k.main(["--docx", str(that), "--nhap", str(tmp_path)]) == 0
