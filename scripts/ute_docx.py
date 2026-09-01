"""Thư viện dùng chung: định dạng Word theo quy định trình bày của UTE.

[CD1.1] Nguồn quy định: forms/cacHuongDan_2.HuongDanTrinhBayLVThS_TomTat_ChuyenDe-Kỹ thuật.docx
  Phần I mục 1 — Times New Roman 13, giãn dòng 1,5,
                 lề trái 3,5 cm | phải 2 cm | trên 3 cm | dưới 3,5 cm,
                 số trang ở giữa lề dưới
  Phần I mục 3 — tên bảng đặt TRÊN bảng, tên hình đặt DƯỚI hình
  Phần I mục 6.8 — trang trước Chương 1 đánh số La Mã thường; từ Chương 1 đánh số Ả Rập

Đây là Vùng 1 (dùng chung). Người dùng hiện tại:
  - scripts/md_to_docx_ute.py   — chuyển Markdown sang Word
  - scripts/build_cd1_report.py — dựng khung cuốn Chuyên đề 1
Chuyên đề 2 và luận văn dùng lại module này, không viết lại.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# --- Hằng số quy định UTE -----------------------------------------------------

FONT = "Times New Roman"
SIZE = Pt(13)
LINE_SPACING = 1.5

MARGIN_LEFT = Cm(3.5)
MARGIN_RIGHT = Cm(2.0)
MARGIN_TOP = Cm(3.0)
MARGIN_BOTTOM = Cm(3.5)

# Cỡ chữ tiêu đề. Phần I Phụ lục 10: "Chương 1" cỡ 16, "TỔNG QUAN" cỡ 18.
# Ở đây gộp làm một dòng tiêu đề chương cỡ 16 cho gọn; mục con dùng cỡ thân bài.
HEADING_SIZES = {1: Pt(16), 2: Pt(14), 3: Pt(13), 4: Pt(13)}

CAPTION_SIZE = Pt(12)
TABLE_TEXT_SIZE = Pt(11)  # Phần I mục 3 cho phép nhỏ hơn, tối thiểu 10

BLACK = RGBColor(0, 0, 0)


# --- Nguyên thuỷ: trường Word (field) ----------------------------------------


def add_field(run, instruction: str) -> None:
    """Chèn một trường Word (PAGE, TOC, ...) vào run.

    Word lưu trường dưới dạng ba nút XML: begin -> instrText -> end.
    python-docx không bọc sẵn nên phải dựng tay.
    """
    for tag, attrs, text in (
        ("w:fldChar", {"w:fldCharType": "begin"}, None),
        ("w:instrText", {"xml:space": "preserve"}, instruction),
        ("w:fldChar", {"w:fldCharType": "separate"}, None),
        ("w:t", {}, ""),  # chỗ Word ghi kết quả sau khi cập nhật trường
        ("w:fldChar", {"w:fldCharType": "end"}, None),
    ):
        node = OxmlElement(tag)
        for key, value in attrs.items():
            node.set(qn(key), value)
        if text is not None:
            node.text = text
        run._r.append(node)


# --- Trang và style -----------------------------------------------------------


def apply_page_setup(section) -> None:
    """Lề theo Phần I mục 1. Gọi cho MỌI section, không dựa vào kế thừa."""
    section.left_margin = MARGIN_LEFT
    section.right_margin = MARGIN_RIGHT
    section.top_margin = MARGIN_TOP
    section.bottom_margin = MARGIN_BOTTOM


def _style_font(style, size, *, bold=False, italic=False) -> None:
    style.font.name = FONT
    style.font.size = size
    style.font.bold = bold
    style.font.italic = italic
    style.font.color.rgb = BLACK
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), FONT)


def apply_styles(doc: DocumentType) -> None:
    """Đặt Normal, Heading 1–4 và Caption theo quy định UTE.

    Dùng đúng style dựng sẵn của Word (không tạo style tên riêng) để:
      - Mục lục tự động (trường TOC) nhận diện được tiêu đề;
      - Học viên gõ tiếp trong Word thì style đã có sẵn trong danh sách.
    """
    normal = doc.styles["Normal"]
    _style_font(normal, SIZE)
    normal.paragraph_format.line_spacing = LINE_SPACING
    normal.paragraph_format.space_after = Pt(6)

    for level, size in HEADING_SIZES.items():
        style = doc.styles[f"Heading {level}"]
        _style_font(style, size, bold=True)
        pf = style.paragraph_format
        pf.line_spacing = LINE_SPACING
        pf.space_before = Pt(12 if level <= 2 else 8)
        pf.space_after = Pt(6)
        pf.keep_with_next = True

    caption = doc.styles["Caption"]
    _style_font(caption, CAPTION_SIZE, bold=True)
    caption.paragraph_format.line_spacing = 1.0
    caption.paragraph_format.space_after = Pt(6)
    caption.paragraph_format.keep_with_next = True


# --- Đánh số trang ------------------------------------------------------------


def set_page_numbering(section, fmt: str | None = "decimal", start: int | None = None) -> None:
    """Đặt kiểu đánh số trang cho một section.

    fmt: "decimal" (1, 2, 3) | "lowerRoman" (i, ii, iii) | None (không chèn số).
    start: số trang bắt đầu lại; None là tiếp tục section trước.

    Trang bìa không đánh số (Phần I mục 1) -> gọi với fmt=None.
    """
    sect_pr = section._sectPr
    existing = sect_pr.find(qn("w:pgNumType"))
    if existing is not None:
        sect_pr.remove(existing)

    if fmt is not None:
        pg = OxmlElement("w:pgNumType")
        pg.set(qn("w:fmt"), fmt)
        if start is not None:
            pg.set(qn("w:start"), str(start))
        sect_pr.append(pg)

    # Footer phải tách khỏi section trước, nếu không sẽ dùng chung nội dung
    section.footer.is_linked_to_previous = False
    footer = section.footer.paragraphs[0]
    for run in list(footer.runs):
        run._r.getparent().remove(run._r)

    if fmt is None:
        return

    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.line_spacing = 1.0
    run = footer.add_run()
    run.font.name = FONT
    run.font.size = SIZE
    add_field(run, "PAGE")


def new_section(doc: DocumentType, fmt: str | None = "decimal", start: int | None = None):
    """Mở section mới ở trang mới, đã áp lề và kiểu đánh số."""
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    apply_page_setup(section)
    set_page_numbering(section, fmt, start)
    return section


# --- Khối nội dung ------------------------------------------------------------


def new_document() -> DocumentType:
    """Tài liệu trắng đã áp đủ quy định UTE, section đầu không đánh số trang."""
    from docx import Document

    doc = Document()
    apply_page_setup(doc.sections[0])
    apply_styles(doc)
    set_page_numbering(doc.sections[0], fmt=None)
    return doc


def add_paragraph(doc: DocumentType, text: str = "", *, align=None, italic=False, bold=False):
    para = doc.add_paragraph()
    para.paragraph_format.line_spacing = LINE_SPACING
    if align is not None:
        para.alignment = align
    if text:
        run = para.add_run(text)
        run.font.name = FONT
        run.font.size = SIZE
        run.italic = italic
        run.bold = bold
    return para


def add_toc_field(doc: DocumentType, levels: str = "1-3"):
    """Chèn trường mục lục tự động.

    Word chỉ hiện nội dung sau khi người dùng bấm cập nhật (Ctrl+A rồi F9).
    Trước đó chỗ này hiện dòng nhắc — đó là hành vi bình thường của Word.
    """
    para = doc.add_paragraph()
    para.paragraph_format.line_spacing = LINE_SPACING
    run = para.add_run()
    run.font.name = FONT
    run.font.size = SIZE
    add_field(run, f'TOC \\o "{levels}" \\h \\z \\u')
    return para


def add_caption(doc: DocumentType, text: str):
    """Chú thích bảng/hình. Phần I mục 3: tên BẢNG đặt TRÊN, tên HÌNH đặt DƯỚI."""
    para = doc.add_paragraph(style="Caption")
    run = para.add_run(text)
    run.font.name = FONT
    run.font.size = CAPTION_SIZE
    run.bold = True
    return para


def add_todo(doc: DocumentType, text: str):
    """Chỗ trống chờ điền, dạng [TODO: ...] — quy tắc số 7 của repo.

    Trước khi nộp phải không còn dòng nào như thế này
    (checklist trong pLan/chuyende1/OUTLINE_BAOCAO_CD1.md mục C).
    """
    para = doc.add_paragraph()
    para.paragraph_format.line_spacing = LINE_SPACING
    run = para.add_run(f"[TODO: {text}]")
    run.font.name = FONT
    run.font.size = SIZE
    run.italic = True
    run.font.color.rgb = RGBColor(0xB0, 0x00, 0x00)
    return para


# --- Chống ghi đè nội dung đã sửa tay ------------------------------------------
#
# Vì sao KHÔNG băm nguyên byte file .docx: .docx là một file zip (OOXML), và hai
# lần lưu CÙNG một nội dung ra hai file khác nhau vẫn cho hai chuỗi byte khác
# nhau (thứ tự nén, timestamp nội bộ của zip...). Băm byte thô sẽ báo "đã đổi"
# ngay cả khi không ai sửa gì — vô dụng làm chốt chặn.
#
# Cách đúng: trích xuất phần NỘI DUNG CÓ Ý NGHĨA (chữ trong từng đoạn kèm style,
# chữ trong từng ô bảng) rồi băm chuỗi đó. Đã kiểm chứng thực nghiệm: sinh hai
# lần từ cùng code cho ra cùng một giá trị băm nội dung, dù byte file khác nhau.


def content_fingerprint_of_document(doc: DocumentType) -> str:
    """Băm nội dung có ý nghĩa của một Document đang có trong bộ nhớ (chưa cần lưu)."""
    parts: list[str] = []
    for p in doc.paragraphs:
        parts.append(f"{p.style.name}|{p.text}")
    for table in doc.tables:
        for row in table.rows:
            parts.append("|".join(cell.text for cell in row.cells))
    blob = "\n".join(parts).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def content_fingerprint_of_file(path: Path) -> str:
    """Băm nội dung có ý nghĩa của một file .docx đã có trên đĩa."""
    return content_fingerprint_of_document(Document(str(path)))
