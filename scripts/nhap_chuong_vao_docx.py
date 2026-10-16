"""[CD1.12] Đưa các bản nháp Markdown của từng chương vào cuốn Word của Chuyên đề 1.

Bản nháp viết ở chuyende1/report/nhap_rut_gon/ChuongN_*.md, trích dẫn bằng khoá dạng
[@PhoBERT]. Cuốn nộp là chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx.

Từ 13/10/2026 bản rút gọn là bản chính, nên hai đường dẫn mặc định trỏ vào nó. Bản đầy đủ
(chuyende1/report/nhap/ và ChuyenDe1_NguyenMinhTrong.docx) được giữ nguyên làm bản lưu; muốn
ghép nó thì phải chỉ rõ --nhap và --docx.

Script đọc MỌI file ChuongN_*.md đang có trong thư mục nháp, theo thứ tự chương,
rồi làm ba việc trong một lần chạy:
  1. đánh số trích dẫn theo thứ tự xuất hiện lần đầu TRONG TOÀN VĂN (kiểu IEEE);
  2. thay phần thân của từng chương đó trong file Word;
  3. viết lại mục TÀI LIỆU THAM KHẢO từ tai_lieu.json của thư mục nháp.
Chương nào chưa có file nháp thì giữ nguyên trong Word. Luôn ghép tất cả cùng
lúc, vì thêm một trích dẫn ở Chương 1 làm đổi số ở mọi chương sau.

Nếu thư mục nháp có PhuLuc.md thì mục PHỤ LỤC được thay bằng nội dung đó. Nếu có
TrangDau.md thì các trang trước Chương 1 cũng được ghép:
  - mỗi mục "# TIÊU ĐỀ" trong file thay phần thân của tiêu đề cấp 1 cùng tên trong Word
    (LỜI CẢM ƠN, LỜI CAM ĐOAN, TÓM TẮT, DANH SÁCH CÁC CHỮ VIẾT TẮT);
  - DANH SÁCH CÁC BẢNG và DANH SÁCH CÁC HÌNH được dựng tự động: mỗi tên bảng, tên hình
    mang một trường TC, và danh sách là một trường TOC đọc các trường đó, nên số
    trang do Word tính khi cập nhật trường (Ctrl+A rồi F9);
  - mỗi mục trước Chương 1 bắt đầu ở một trang mới; mục không thuộc quy định của trường
    (MUC_BO_DI) và các dòng chỉ gồm một chỗ đánh dấu [TODO ...] ở các trang đầu bị bỏ.
Ở trang bìa, dòng có chữ không bị đụng tới; chỉ dòng [TODO ...] bị bỏ và các dòng trống
được thu lại cho bìa nằm gọn một trang (thu_gon_trang_bia).

    python scripts/nhap_chuong_vao_docx.py --chi-xem     # chỉ in thống kê, không ghi
    python scripts/nhap_chuong_vao_docx.py               # ghi; dừng nếu có chương đã có nội dung
    python scripts/nhap_chuong_vao_docx.py --ghi-de      # ghi cả khi chương đã có nội dung

CHỐNG MẤT NỘI DUNG SỬA TAY
--------------------------
- Trước mỗi lần ghi, file Word được sao lưu thành <tên>.<ngày-giờ>.docx.bak.
- Chương còn là khung rỗng (dòng đầu là "(Ngân sách: ...)") thì ghi thẳng.
  Có chương đã có nội dung thì dừng, trừ khi có --ghi-de. Lúc đó phần thân của
  các chương có file nháp bị thay bằng file Markdown: mọi chỗ đã sửa tay TRONG
  WORD ở các chương ấy mất, chỉ còn trong bản sao lưu. Vì vậy lúc còn nháp thì
  sửa ở file .md.

Cú pháp Markdown nhận (đủ cho bản nháp chương, cố ý hẹp):
  # ...            dòng tiêu đề chương, BỎ QUA (Word đã có sẵn tiêu đề chương)
  ## / ###         mục cấp 2 / cấp 3
  Bảng N.M: ...    tên bảng, đặt trên bảng
  Hình N.M: ...    tên hình, đặt dưới hình
  ![](đường/dẫn.png)        hình, đường dẫn tính từ thư mục đang đứng (gốc repo); ![12](...) là rộng 12 cm, mặc định 15
  | a | b |        bảng (cần dòng phân cách ---)
  ... (N.M)        dòng kết thúc bằng số công thức thì canh giữa
  [@khoá]          trích dẫn; khoá phải có trong tai_lieu.json
  >> ...           dòng canh giữa (khối chữ ký); ">>" đứng một mình là một dòng trống
  [TODO: ...] [CẦN KIỂM: ...] [CẦN TÌM: ...] [CHÈN ...]   in nghiêng màu đỏ
  ## Tài liệu được trích ...   từ dòng này trở đi KHÔNG đưa vào chương
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).parent))

from ute_docx import CAPTION_SIZE, FONT, LINE_SPACING, SIZE, TABLE_TEXT_SIZE, add_field, ap_lai_dinh_dang  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOCX_MAC_DINH = Path("chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx")
NHAP_MAC_DINH = Path("chuyende1/report/nhap_rut_gon")
TEN_FILE_TAI_LIEU = "tai_lieu.json"
TIEU_DE_TAI_LIEU = "TÀI LIỆU THAM KHẢO"
TEN_FILE_PHU_LUC = "PhuLuc.md"
TIEU_DE_PHU_LUC = "PHỤ LỤC"
SO_PHU_LUC = 99  # khoa cua phu luc trong bang than: lon hon moi so chuong de trich dan duoc danh so sau cung
TEN_FILE_TRANG_DAU = "TrangDau.md"
DAU_CHUONG_DAU = "Chương 1."  # mọi tiêu đề cấp 1 đứng trước tiêu đề này thuộc các trang đầu
# Danh sách dựng tự động: tiêu đề cấp 1 trong Word -> (chữ đầu cột, mã của trường TC)
DANH_SACH_TU_DONG = {"DANH SÁCH CÁC BẢNG": ("BẢNG", "B"), "DANH SÁCH CÁC HÌNH": ("HÌNH", "H")}
MA_TC = {"Bảng": "B", "Hình": "H"}
MUC_BO_DI = ("DANH SÁCH CÔNG THỨC",)  # khung cũ có mục này; quy định của trường (Phần I mục 6.8) không đòi
RONG_PHAN_CHU_CM = 15.5  # khổ A4 trừ lề trái 3,5 cm và lề phải 2 cm
SO_DONG_TRONG_BIA = 3  # số dòng trống liền nhau tối đa trên trang bìa
SO_CHUONG = range(1, 7)
DO = RGBColor(0xB0, 0x00, 0x00)
DAU_KHUNG_RONG = "(Ngân sách:"
DAU_HET_THAN = "## Tài liệu được trích"
MAU_DANH_DAU = re.compile(r"(\[(?:TODO|CẦN KIỂM|CẦN TÌM|CHÈN)[^\]]*\])")
MAU_TRICH_DAN = re.compile(r"\[@([^\]]+)\]")
MAU_TEN_BANG_HINH = re.compile(r"^(Bảng|Hình) (?:\d+|[A-Z])\.\d+:")  # ca dang "Bảng A.1:" cua phu luc
MAU_CONG_THUC = re.compile(r"\(\d+\.\d+\)$")
MAU_HINH = re.compile(r"^!\[(\d*(?:[.,]\d+)?)\]\(([^)]+)\)$")
RONG_HINH_CM = 15.0  # khổ A4 trừ lề trái 3,5 cm và lề phải 2 cm còn 15,5 cm

# Một khối: (loại, nội dung). Loại: h2 | h3 | ten | bang | cong_thuc | hinh | doan | giua | dau_ds | truong_ds
Khoi = Tuple[str, object]


# --- Đọc bản nháp ----------------------------------------------------------------


def tim_file_chuong(thu_muc: Path) -> Dict[int, Path]:
    """{số chương: file nháp}. Mỗi chương tối đa một file ChuongN_*.md."""
    ra: Dict[int, Path] = {}
    for so in SO_CHUONG:
        ung_vien = sorted(thu_muc.glob(f"Chuong{so}_*.md"))
        if len(ung_vien) > 1:
            raise ValueError(f"Chương {so} có {len(ung_vien)} file nháp, chỉ được một: {[p.name for p in ung_vien]}")
        if ung_vien:
            ra[so] = ung_vien[0]
    return ra


def cat_than(van_ban: str) -> str:
    """Bỏ phần từ mục 'Tài liệu được trích' trở đi."""
    return van_ban.replace("\r\n", "\n").split("\n" + DAU_HET_THAN)[0]


def danh_so_trich_dan(than: Dict[int, str], tai_lieu: Dict[str, str]) -> Tuple[Dict[int, str], List[str]]:
    """Thay [@khoá] bằng [n], n theo thứ tự xuất hiện lần đầu qua các chương.

    Trả về (thân đã đánh số, danh sách khoá theo đúng thứ tự số).
    """
    thu_tu: List[str] = []

    def thay(m: re.Match) -> str:
        khoa = m.group(1)
        if khoa not in tai_lieu:
            raise KeyError(f"Trích dẫn [@{khoa}] không có trong {TEN_FILE_TAI_LIEU}")
        if khoa not in thu_tu:
            thu_tu.append(khoa)
        return f"[{thu_tu.index(khoa) + 1}]"

    ra = {so: MAU_TRICH_DAN.sub(thay, than[so]) for so in sorted(than)}
    return ra, thu_tu


def doc_markdown(van_ban: str) -> List[Khoi]:
    """Tách thân một chương thành danh sách khối."""
    khoi: List[Khoi] = []
    dong = cat_than(van_ban).split("\n")
    i = 0
    while i < len(dong):
        d = dong[i].strip()
        if not d or d.startswith("# "):
            i += 1
        elif d.startswith(">>"):
            khoi.append(("giua", d[2:].strip()))
            i += 1
        elif d.startswith("### "):
            khoi.append(("h3", d[4:].strip()))
            i += 1
        elif d.startswith("## "):
            khoi.append(("h2", d[3:].strip()))
            i += 1
        elif d.startswith("|"):
            hang = []
            while i < len(dong) and dong[i].strip().startswith("|"):
                o = [x.strip() for x in dong[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", x) for x in o):
                    hang.append(o)
                i += 1
            so_cot = {len(h) for h in hang}
            if len(so_cot) != 1:
                raise ValueError(f"Bảng có các hàng lệch số cột {sorted(so_cot)}: {hang[0]}")
            khoi.append(("bang", hang))
        elif MAU_TEN_BANG_HINH.match(d):
            khoi.append(("ten", d))
            i += 1
        elif MAU_HINH.match(d):
            rong, duong_dan = MAU_HINH.match(d).groups()
            khoi.append(("hinh", (duong_dan.strip(), float(rong.replace(",", ".")) if rong else RONG_HINH_CM)))
            i += 1
        elif MAU_CONG_THUC.search(d):
            khoi.append(("cong_thuc", d))
            i += 1
        else:
            khoi.append(("doan", d))
            i += 1
    return khoi


def doc_trang_dau(van_ban: str) -> Dict[str, List[Khoi]]:
    """Tách file các trang đầu thành {tiêu đề cấp 1: các khối của mục đó}, theo các dòng '# TIÊU ĐỀ'."""
    muc: Dict[str, List[str]] = {}
    ten = None
    for d in van_ban.replace("\r\n", "\n").split("\n"):
        if d.startswith("# "):
            ten = d[2:].strip()
            if ten in muc:
                raise ValueError(f"{TEN_FILE_TRANG_DAU} có hai mục cùng tên '{ten}'")
            muc[ten] = []
        elif ten is not None:
            muc[ten].append(d)
        elif d.strip():
            raise ValueError(f"{TEN_FILE_TRANG_DAU}: dòng '{d[:40]}' đứng trước mọi tiêu đề '# ...'")
    return {ten: doc_markdown("\n".join(dong)) for ten, dong in muc.items()}


# --- Ghi vào Word ----------------------------------------------------------------


def _chay(para, chu: str, *, co=SIZE, dam=False, nghieng=False, do=False):
    run = para.add_run(chu)
    run.font.name = FONT
    run.font.size = co
    run.bold = dam
    run.italic = nghieng
    if do:
        run.font.color.rgb = DO
    return run


def _doan_co_danh_dau(para, chu: str) -> None:
    for manh in MAU_DANH_DAU.split(chu):
        if manh:
            la_dau = bool(MAU_DANH_DAU.fullmatch(manh))
            _chay(para, manh, nghieng=la_dau, do=la_dau)


def _them_truong_tc(para, chu: str, ma: str) -> None:
    """Trường TC ở cuối một tên bảng hoặc tên hình: khai một mục cho danh sách mang mã `ma`.

    Trường TOC \\f <mã> ở trang danh sách gom các trường này lại, số trang do Word tính. Trường TC không
    có phần kết quả nên không hiện gì trên trang. KHÔNG đánh dấu chữ ẩn (w:vanish) cho trường này: đã thử
    ngày 13/10/2026 trên Word, trường TC mang w:vanish không được trường TOC gom và danh sách ra rỗng.
    """
    run = para.add_run()
    chu = chu.replace('"', "”")
    for tag, attrs, text in (("w:fldChar", {"w:fldCharType": "begin"}, None),
                             ("w:instrText", {"xml:space": "preserve"}, f' TC "{chu}" \\f {ma} \\l 1 '),
                             ("w:fldChar", {"w:fldCharType": "end"}, None)):
        node = OxmlElement(tag)
        for key, value in attrs.items():
            node.set(qn(key), value)
        if text is not None:
            node.text = text
        run._r.append(node)


def _them_khoi(doc: DocumentType, khoi: Khoi):
    """Thêm một khối vào CUỐI tài liệu, trả về phần tử XML để dời tới đúng chỗ."""
    loai, nd = khoi
    if loai in ("h2", "h3"):
        return doc.add_paragraph(nd, style="Heading 2" if loai == "h2" else "Heading 3")._p
    if loai == "ten":
        para = doc.add_paragraph(style="Caption")
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _chay(para, nd, co=CAPTION_SIZE, dam=True)
        _them_truong_tc(para, nd, MA_TC[nd.split(" ", 1)[0]])
        return para._p
    if loai == "giua":
        para = doc.add_paragraph()
        para.paragraph_format.line_spacing = LINE_SPACING
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if nd:
            _chay(para, nd)
        return para._p
    if loai == "dau_ds":  # dòng đầu của danh sách bảng, hình: "BẢNG ... TRANG" theo Phụ lục 8 và 9 của quy định
        para = doc.add_paragraph()
        para.paragraph_format.line_spacing = LINE_SPACING
        para.paragraph_format.tab_stops.add_tab_stop(Cm(RONG_PHAN_CHU_CM), WD_TAB_ALIGNMENT.RIGHT)
        _chay(para, f"{nd}\tTRANG", dam=True)
        return para._p
    if loai == "truong_ds":
        para = doc.add_paragraph()
        para.paragraph_format.line_spacing = LINE_SPACING
        add_field(_chay(para, ""), f"TOC \\f {nd} \\h \\z")
        return para._p
    if loai == "bang":
        bang = doc.add_table(rows=len(nd), cols=len(nd[0]))
        bang.style = "Table Grid"
        for r, hang in enumerate(nd):
            for c, o in enumerate(hang):
                _chay(bang.cell(r, c).paragraphs[0], o, co=TABLE_TEXT_SIZE, dam=(r == 0))
        return bang._tbl
    if loai == "hinh":
        duong_dan, rong = nd
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.keep_with_next = True  # giữ hình cùng trang với tên hình ngay dưới
        para.add_run().add_picture(str(duong_dan), width=Cm(rong))
        return para._p
    para = doc.add_paragraph()
    para.paragraph_format.line_spacing = LINE_SPACING
    if loai == "cong_thuc":
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _chay(para, nd)
        return para._p
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT if loai == "tai_lieu" else WD_ALIGN_PARAGRAPH.JUSTIFY
    _doan_co_danh_dau(para, nd)
    return para._p


def tim_muc_cap_mot(doc: DocumentType, dau_tieu_de: str):
    """Trả về (đoạn Heading 1 bắt đầu bằng `dau_tieu_de`, đoạn Heading 1 kế tiếp hoặc None)."""
    h1 = [p for p in doc.paragraphs if p.style.name == "Heading 1"]
    dau = [p for p in h1 if p.text.strip().startswith(dau_tieu_de)]
    if len(dau) != 1:
        raise ValueError(f"Cần đúng một tiêu đề cấp 1 bắt đầu bằng '{dau_tieu_de}', tìm thấy {len(dau)}.")
    sau = h1[h1.index(dau[0]) + 1:]
    return dau[0], (sau[0] if sau else None)


def _than_muc(dau, cuoi) -> list:
    """Các phần tử XML (đoạn, bảng) nằm giữa hai tiêu đề cấp 1."""
    than, e = [], dau._p.getnext()
    while e is not None and (cuoi is None or e is not cuoi._p) and not e.tag.endswith("}sectPr"):
        than.append(e)
        e = e.getnext()
    return than


def chuong_con_la_khung(doc: DocumentType, so: int) -> bool:
    than = _than_muc(*tim_muc_cap_mot(doc, f"Chương {so}."))
    chu = "".join(than[0].itertext()).strip() if than else ""
    return chu.startswith(DAU_KHUNG_RONG)


def thay_than_muc(doc: DocumentType, dau_tieu_de: str, khoi: List[Khoi]) -> int:
    """Xoá phần thân của một mục cấp 1 rồi chèn các khối vào. Trả về số khối đã chèn.

    Giữ lại phần tử cuối nếu đó là đoạn rỗng: khung dùng nó để ngắt trang trước
    mục sau.
    """
    dau, cuoi = tim_muc_cap_mot(doc, dau_tieu_de)
    than = _than_muc(dau, cuoi)
    giu_cuoi = bool(than) and than[-1].tag.endswith("}p") and not "".join(than[-1].itertext()).strip()
    for e in than[:-1] if giu_cuoi else than:
        e.getparent().remove(e)
    truoc = dau._p
    for k in khoi:
        moi = _them_khoi(doc, k)
        truoc.addnext(moi)
        truoc = moi
    return len(khoi)


def _h1_trang_dau(doc: DocumentType) -> list:
    """Các đoạn tiêu đề cấp 1 đứng trước Chương 1, theo thứ tự trong tài liệu."""
    ra = []
    for p in doc.paragraphs:
        if p.style.name == "Heading 1":
            if p.text.strip().startswith(DAU_CHUONG_DAU):
                return ra
            ra.append(p)
    raise ValueError(f"Không thấy tiêu đề cấp 1 bắt đầu bằng '{DAU_CHUONG_DAU}'")


def muc_con_la_khung(doc: DocumentType, dau_tieu_de: str) -> bool:
    """Một mục ở trang đầu còn là khung khi thân của nó không có bảng và mọi dòng có chữ đều là chỗ đánh dấu."""
    than = _than_muc(*tim_muc_cap_mot(doc, dau_tieu_de))
    if any(e.tag.endswith("}tbl") for e in than):
        return False
    # Lấy chữ từ các nút w:t. Không dùng itertext(): với lớp phần tử của python-docx nó trả chữ của một đoạn nhiều lần.
    chu = ["".join(t.text or "" for t in e.iter(qn("w:t"))).strip() for e in than]
    return all(MAU_DANH_DAU.fullmatch(c) for c in chu if c)


def bo_muc(doc: DocumentType, dau_tieu_de: str) -> bool:
    """Bỏ một mục cấp 1 cùng phần thân của nó. Đoạn mang ngắt section được giữ lại. Trả về False nếu không có mục đó."""
    if not any(p.style.name == "Heading 1" and p.text.strip().startswith(dau_tieu_de) for p in doc.paragraphs):
        return False
    dau, cuoi = tim_muc_cap_mot(doc, dau_tieu_de)
    for el in _than_muc(dau, cuoi):
        if not (el.tag.endswith("}p") and el.xpath(".//w:sectPr")):
            el.getparent().remove(el)
    dau._p.getparent().remove(dau._p)
    return True


def bo_dong_danh_dau_trang_dau(doc: DocumentType) -> int:
    """Xoá các đoạn chỉ gồm một chỗ đánh dấu [TODO ...] nằm trước Chương 1 (kể cả ở trang bìa). Trả về số đoạn đã xoá."""
    so = 0
    for p in list(doc.paragraphs):
        if p.style.name == "Heading 1" and p.text.strip().startswith(DAU_CHUONG_DAU):
            break
        if MAU_DANH_DAU.fullmatch(p.text.strip()) and not p._p.xpath(".//w:sectPr"):
            p._p.getparent().remove(p._p)
            so += 1
    return so


def thu_gon_trang_bia(doc: DocumentType) -> int:
    """Thu các dòng trống của trang bìa cho bìa nằm gọn trong một trang. Trả về số dòng trống đã bỏ.

    Khung bìa có 18 dòng trống giãn dòng 1,5 nên tràn sang trang thứ hai (GAP-038). Ở đây mỗi cụm dòng
    trống liền nhau còn tối đa SO_DONG_TRONG_BIA dòng, và dòng trống dùng giãn dòng đơn, không cách đoạn.
    Dòng có chữ không bị đụng tới. Bìa là mọi đoạn đứng trước tiêu đề cấp 1 đầu tiên.
    """
    da_bo, lien_tiep = 0, 0
    for p in list(doc.paragraphs):
        if p.style.name == "Heading 1":
            break
        if p.text.strip() or p._p.xpath(".//w:sectPr") or p._p.xpath(".//w:drawing"):
            lien_tiep = 0
            continue
        lien_tiep += 1
        if lien_tiep > SO_DONG_TRONG_BIA:
            p._p.getparent().remove(p._p)
            da_bo += 1
        else:
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(0)
    return da_bo


def ghep_trang_dau(doc: DocumentType, muc: Dict[str, List[Khoi]]) -> Dict[str, int]:
    """Ghép các trang trước Chương 1. Trả về vài con số để in."""
    thu_gon_trang_bia(doc)
    da_bo = [ten for ten in MUC_BO_DI if bo_muc(doc, ten)]
    for ten, khoi in muc.items():
        thay_than_muc(doc, ten, khoi)
    co_ds = []
    for ten, (dau_cot, ma) in DANH_SACH_TU_DONG.items():
        if any(p.text.strip().startswith(ten) for p in _h1_trang_dau(doc)):
            thay_than_muc(doc, ten, [("dau_ds", dau_cot), ("truong_ds", ma)])
            co_ds.append(ten)
    so_dong = bo_dong_danh_dau_trang_dau(doc)
    h1 = _h1_trang_dau(doc)
    for p in h1[1:]:  # mục đầu tiên đã ở đầu một section mới
        p.paragraph_format.page_break_before = True
    return {"muc_bo": len(da_bo), "danh_sach": len(co_ds), "dong_danh_dau_bo": so_dong, "so_muc": len(h1)}


def sao_luu(duong_dan: Path) -> Path:
    ban = duong_dan.with_name(f"{duong_dan.stem}.{datetime.now():%Y%m%d-%H%M%S}.docx.bak")
    shutil.copy2(duong_dan, ban)
    return ban


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đưa các bản nháp Markdown của từng chương vào cuốn Word, "
                                             "đánh số trích dẫn theo toàn văn.")
    ap.add_argument("--nhap", type=Path, default=NHAP_MAC_DINH,
                    help=f"thư mục chứa ChuongN_*.md và {TEN_FILE_TAI_LIEU} (mặc định {NHAP_MAC_DINH})")
    ap.add_argument("--docx", type=Path, default=DOCX_MAC_DINH, help=f"cuốn Word (mặc định {DOCX_MAC_DINH})")
    ap.add_argument("--chi-xem", action="store_true", help="chỉ in thống kê, không ghi file")
    ap.add_argument("--ghi-de", action="store_true",
                    help="ghi cả khi có chương đã có nội dung (mất chỗ sửa tay trong Word ở các chương đó, có sao lưu)")
    ap.add_argument("--chi", nargs="+", default=None, metavar="PHAN",
                    help="chỉ thay các phần này: số chương (1 đến 6) và/hoặc phu_luc. Không đụng trang đầu, tài liệu tham khảo "
                         "và các chương khác (dùng từ 17/10/2026: Chương 2 có phương trình Word, học viên sửa thẳng trong Word)")
    ap.add_argument("--sua-dinh-dang", action="store_true",
                    help="áp lại khổ A4, lề và font của các style lên file (file dựng trước 13/10/2026 ở khổ Letter, tiêu đề Calibri)")
    a = ap.parse_args(argv)
    chon_chuong, chon_pl = None, True
    if a.chi:
        la = [x for x in a.chi if not (x.isdigit() or x == "phu_luc")]
        if la:
            print(f"DỪNG: --chi chỉ nhận số chương và phu_luc, có {la}")
            return 1
        chon_chuong, chon_pl = {int(x) for x in a.chi if x.isdigit()}, "phu_luc" in a.chi

    cac_file = tim_file_chuong(a.nhap)
    if not cac_file:
        print(f"Không thấy file ChuongN_*.md nào trong {a.nhap}")
        return 1
    tai_lieu = json.loads((a.nhap / TEN_FILE_TAI_LIEU).read_text(encoding="utf-8"))
    than = {so: p.read_text(encoding="utf-8") for so, p in cac_file.items()}
    tep_phu_luc = a.nhap / TEN_FILE_PHU_LUC
    if tep_phu_luc.exists():
        than[SO_PHU_LUC] = tep_phu_luc.read_text(encoding="utf-8")
    than = {so: cat_than(t) for so, t in than.items()}
    than, thu_tu = danh_so_trich_dan(than, tai_lieu)
    than_phu_luc = than.pop(SO_PHU_LUC, None)
    tep_trang_dau = a.nhap / TEN_FILE_TRANG_DAU
    trang_dau = doc_trang_dau(tep_trang_dau.read_text(encoding="utf-8")) if tep_trang_dau.exists() else None

    doc = Document(str(a.docx))
    da_co = []
    khoi_chuong: Dict[int, List[Khoi]] = {}
    for so in sorted(than):
        khoi_chuong[so] = doc_markdown(than[so])
        dem: Dict[str, int] = {}
        for loai, _ in khoi_chuong[so]:
            dem[loai] = dem.get(loai, 0) + 1
        thieu = [nd[0] for loai, nd in khoi_chuong[so] if loai == "hinh" and not Path(nd[0]).is_file()]
        if thieu:
            print(f"DỪNG: Chương {so} gọi tới hình không có trên đĩa: {thieu}. Vẽ lại bằng scripts/make_figures.py.")
            return 1
        so_dau = len(MAU_DANH_DAU.findall(than[so]))
        la_khung = chuong_con_la_khung(doc, so)
        if not la_khung:
            da_co.append(so)
        print(f"Chương {so} ({cac_file[so].name}): {len(khoi_chuong[so])} khối {dem} | "
              f"chỗ đánh dấu: {so_dau} | trong Word: {'khung rỗng' if la_khung else 'ĐÃ CÓ NỘI DUNG'}")
    khoi_pl: Optional[List[Khoi]] = None
    if than_phu_luc is not None:
        khoi_pl = doc_markdown(than_phu_luc)
        print(f"Phụ lục ({TEN_FILE_PHU_LUC}): {len(khoi_pl)} khối, {sum(1 for loai, _ in khoi_pl if loai == 'bang')} bảng")
    trang_dau_da_co: List[str] = []
    if trang_dau is not None:
        co_dau = [ten for ten, khoi in trang_dau.items() if any(MAU_DANH_DAU.search(str(nd)) for _, nd in khoi)]
        trang_dau_da_co = [ten for ten in trang_dau if not muc_con_la_khung(doc, ten)]
        print(f"Trang đầu ({TEN_FILE_TRANG_DAU}): {len(trang_dau)} mục {list(trang_dau)} | mục còn chỗ đánh dấu: {co_dau} | "
              f"trong Word đã có nội dung: {trang_dau_da_co}")
    so_ten = {loai: sum(1 for ds in list(khoi_chuong.values()) + [khoi_pl or []] for k, nd in ds if k == "ten" and nd.startswith(loai))
              for loai in MA_TC}
    print(f"Tên bảng: {so_ten['Bảng']} | tên hình: {so_ten['Hình']}")
    khoi_tl: List[Khoi] = [("tai_lieu", f"[{n}] {tai_lieu[k]}") for n, k in enumerate(thu_tu, 1)]
    so_ck = sum(1 for _, nd in khoi_tl if MAU_DANH_DAU.search(nd))
    print(f"Tài liệu được trích: {len(thu_tu)} | trong đó còn đánh dấu chưa đối chiếu: {so_ck}")

    if a.chi_xem:
        return 0
    if chon_chuong is not None:
        da_co = [so for so in da_co if so in chon_chuong]
        trang_dau_da_co = []
    if (da_co or trang_dau_da_co) and not a.ghi_de:
        print(f"DỪNG: chương {da_co} và mục trang đầu {trang_dau_da_co} đã có nội dung trong Word. Dùng --ghi-de nếu chắc chắn "
              "muốn thay (chỗ sửa tay trong Word ở các phần này sẽ mất, chỉ còn trong bản sao lưu).")
        return 2
    ban = sao_luu(a.docx)
    for so, khoi in khoi_chuong.items():
        if chon_chuong is None or so in chon_chuong:
            thay_than_muc(doc, f"Chương {so}.", khoi)
    if chon_chuong is None:
        thay_than_muc(doc, TIEU_DE_TAI_LIEU, khoi_tl)
    if khoi_pl is not None and chon_pl:
        thay_than_muc(doc, TIEU_DE_PHU_LUC, khoi_pl)
    if chon_chuong is not None:
        print(f"Chỉ thay: chương {sorted(chon_chuong)}{' và phụ lục' if chon_pl else ''}; giữ nguyên trang đầu, tài liệu tham khảo, các chương khác")
    elif trang_dau is not None:
        kq = ghep_trang_dau(doc, trang_dau)
        print(f"Trang đầu: {kq['so_muc']} mục trước Chương 1, mỗi mục một trang mới; dựng {kq['danh_sach']} danh sách tự động; "
              f"bỏ {kq['muc_bo']} mục ngoài quy định và {kq['dong_danh_dau_bo']} dòng chỉ có chỗ đánh dấu")
    if a.sua_dinh_dang:
        ap_lai_dinh_dang(doc)
    doc.save(str(a.docx))
    print(f"Đã ghi {a.docx}\nBản sao lưu: {ban}")
    print("Mở Word, bấm Ctrl+A rồi F9 để cập nhật mục lục, danh sách bảng và danh sách hình.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
