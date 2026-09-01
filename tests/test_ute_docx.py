"""[CD1.1] Kiểm tra định dạng Word khớp quy định trình bày của UTE.

Quy định nguồn: forms/cacHuongDan_2.HuongDanTrinhBayLVThS_TomTat_ChuyenDe-Kỹ thuật.docx
Đặc tả kiểm: pLan/chuyende1/OUTLINE_BAOCAO_CD1.md mục C (checklist định dạng)

Các test này thay cho việc "in ra đo bằng thước" mỗi lần sửa script.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from docx import Document
from docx.oxml.ns import qn

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_cd1_report import CHUONG, build_reference, build_skeleton  # noqa: E402
from md_to_docx_ute import convert  # noqa: E402
from ute_docx import new_document  # noqa: E402

TOLERANCE_CM = 0.01


@pytest.fixture(scope="module")
def skeleton(tmp_path_factory) -> Document:
    path = tmp_path_factory.mktemp("cd11") / "skeleton.docx"
    build_skeleton(path)
    return Document(str(path))


@pytest.fixture(scope="module")
def reference(tmp_path_factory) -> Document:
    path = tmp_path_factory.mktemp("cd11") / "reference.docx"
    build_reference(path)
    return Document(str(path))


def page_number_format(section) -> tuple[str | None, str | None]:
    """Trả về (fmt, start) khai báo trong w:pgNumType của section."""
    node = section._sectPr.find(qn("w:pgNumType"))
    if node is None:
        return None, None
    return node.get(qn("w:fmt")), node.get(qn("w:start"))


def footer_has_page_field(section) -> bool:
    return "PAGE" in section.footer.paragraphs[0]._p.xml


# --- Quy định chung (Phần I mục 1) -------------------------------------------


def test_le_trang_dung_quy_dinh(skeleton):
    """Lề trái 3,5 | phải 2,0 | trên 3,0 | dưới 3,5 cm — áp cho MỌI section."""
    assert len(skeleton.sections) == 3, "bìa / trang đầu / phần chính"
    for i, section in enumerate(skeleton.sections):
        assert abs(section.left_margin.cm - 3.5) < TOLERANCE_CM, f"section {i}"
        assert abs(section.right_margin.cm - 2.0) < TOLERANCE_CM, f"section {i}"
        assert abs(section.top_margin.cm - 3.0) < TOLERANCE_CM, f"section {i}"
        assert abs(section.bottom_margin.cm - 3.5) < TOLERANCE_CM, f"section {i}"


def test_font_va_gian_dong(skeleton):
    normal = skeleton.styles["Normal"]
    assert normal.font.name == "Times New Roman"
    assert normal.font.size.pt == 13
    assert normal.paragraph_format.line_spacing == 1.5


def test_heading_dung_font_va_mau_den(skeleton):
    """Heading mặc định của Word màu xanh — phải đổi về đen, cùng phông thân bài."""
    for level, expected_pt in ((1, 16), (2, 14), (3, 13)):
        style = skeleton.styles[f"Heading {level}"]
        assert style.font.name == "Times New Roman", f"Heading {level}"
        assert style.font.size.pt == expected_pt, f"Heading {level}"
        assert style.font.bold is True, f"Heading {level}"
        assert style.font.color.rgb is not None
        assert str(style.font.color.rgb) == "000000", f"Heading {level} phải màu đen"


# --- Đánh số trang (Phần I mục 6.8) ------------------------------------------


def test_bia_khong_danh_so_trang(skeleton):
    fmt, _ = page_number_format(skeleton.sections[0])
    assert fmt is None
    assert not footer_has_page_field(skeleton.sections[0])


def test_trang_dau_danh_so_la_ma_thuong(skeleton):
    fmt, start = page_number_format(skeleton.sections[1])
    assert fmt == "lowerRoman"
    assert start == "1"
    assert footer_has_page_field(skeleton.sections[1])


def test_phan_chinh_danh_so_a_rap_bat_dau_lai_tu_1(skeleton):
    fmt, start = page_number_format(skeleton.sections[2])
    assert fmt == "decimal"
    assert start == "1"
    assert footer_has_page_field(skeleton.sections[2])


def test_footer_khong_ke_thua_section_truoc(skeleton):
    """Không tách footer thì cả ba section dùng chung một kiểu số trang."""
    for i, section in enumerate(skeleton.sections):
        assert section.footer.is_linked_to_previous is False, f"section {i}"


# --- Cấu trúc cuốn báo cáo ----------------------------------------------------


def test_du_sau_chuong(skeleton):
    headings = [p.text for p in skeleton.paragraphs if p.style.name == "Heading 1"]
    for title, _, _ in CHUONG:
        assert title in headings, f"thiếu {title}"


def test_du_muc_con_cua_tung_chuong(skeleton):
    headings = [p.text for p in skeleton.paragraphs if p.style.name == "Heading 2"]
    for _, _, sections in CHUONG:
        for sec_title, _ in sections:
            assert sec_title in headings, f"thiếu mục {sec_title}"


def test_co_truong_muc_luc_tu_dong(skeleton):
    assert any("TOC" in p._p.xml for p in skeleton.paragraphs), "thiếu trường TOC"


def test_co_tai_lieu_tham_khao_va_phu_luc(skeleton):
    headings = [p.text for p in skeleton.paragraphs if p.style.name == "Heading 1"]
    assert "TÀI LIỆU THAM KHẢO" in headings
    assert "PHỤ LỤC" in headings


def test_bia_ghi_dung_nganh_va_ma_so(skeleton):
    """Mã 8480101 (hệ hiện hành), không phải 601401 trong mẫu 2015."""
    text = "\n".join(p.text for p in skeleton.paragraphs[:40])
    assert "KHOA HỌC MÁY TÍNH" in text
    assert "8480101" in text
    assert "601401" not in text
    assert "CHUYÊN ĐỀ" in text


def test_bia_ghi_dung_ten_hoc_vien_va_hoc_vi_gvhd(skeleton):
    """GAP-005: tên học viên và học vị GVHD từng bị sai, lan ra cả bìa lẫn phiếu gửi Cô.

    Chốt giá trị đúng và cấm chuỗi sai quay lại. Đây là thông tin về người thật —
    không suy đoán, không chép lại từ file cũ.
    """
    text = "\n".join(p.text for p in skeleton.paragraphs[:40])
    assert "NGUYỄN MINH TRỘNG" in text, "sai tên học viên"
    assert "TS. PHAN THỊ HUYỀN TRANG" in text, "sai học vị GVHD"
    assert "TRỌNG" not in text, "tên học viên là Trộng, không phải Trọng"
    assert "ThS." not in text, "GVHD là Tiến sĩ, không phải Thạc sĩ"


def test_khung_con_nguyen_cac_cho_trong_todo(skeleton):
    """Khung mới dựng phải còn TODO; hết TODO là điều kiện nộp, không phải điều kiện dựng."""
    todos = [p.text for p in skeleton.paragraphs if p.text.startswith("[TODO:")]
    assert len(todos) >= 40, f"chỉ có {len(todos)} chỗ trống, khung có vẻ thiếu mục"


def test_chu_thich_bang_dat_tren_bang(skeleton):
    """Phần I mục 3: tên bảng đặt TRÊN thân bảng."""
    captions = [p.text for p in skeleton.paragraphs if p.style.name == "Caption"]
    assert any(c.startswith("Bảng 4.1:") for c in captions)
    assert any(c.startswith("Hình 3.1:") for c in captions)


# --- File mẫu định dạng -------------------------------------------------------


def test_reference_co_bang_thong_so(reference):
    text = "\n".join(cell.text for table in reference.tables for row in table.rows for cell in row.cells)
    assert "3,5 cm" in text
    assert "Times New Roman, cỡ 13" in text.replace("co 13", "cỡ 13")


# --- Bộ chuyển Markdown -------------------------------------------------------


def test_md_to_docx_giu_dinh_dang_ute(tmp_path):
    md = tmp_path / "a.md"
    md.write_text(
        "# Tiêu đề\n\nĐoạn **đậm** và *nghiêng*.\n\n"
        "- [ ] ô chưa tích\n- [x] ô đã tích\n\n"
        "| A | B |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )
    out = tmp_path / "a.docx"
    convert(md, out)

    doc = Document(str(out))
    assert abs(doc.sections[0].left_margin.cm - 3.5) < TOLERANCE_CM
    assert doc.styles["Normal"].font.size.pt == 13
    assert len(doc.tables) == 1
    # Tài liệu sinh từ Markdown không có trang bìa -> phải đánh số trang từ 1.
    # Không có assert này thì việc dùng lại new_document() (vốn tắt số trang cho
    # trang bìa) sẽ âm thầm làm mất số trang của mọi tài liệu chuyển từ Markdown.
    assert page_number_format(doc.sections[0]) == ("decimal", "1")
    assert footer_has_page_field(doc.sections[0])
    texts = [p.text for p in doc.paragraphs]
    assert any("☐ ô chưa tích" in t for t in texts)
    assert any("☒ ô đã tích" in t for t in texts)


def test_new_document_khong_danh_so_trang_section_dau():
    doc = new_document()
    assert page_number_format(doc.sections[0]) == (None, None)
