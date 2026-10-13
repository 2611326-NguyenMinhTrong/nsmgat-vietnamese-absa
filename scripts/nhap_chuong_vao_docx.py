"""[CD1.12] Đưa các bản nháp Markdown của từng chương vào cuốn Word của Chuyên đề 1.

Bản nháp viết ở chuyende1/report/nhap/ChuongN_*.md, trích dẫn bằng khoá dạng
[@PhoBERT]. Cuốn nộp là chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx.

Script đọc MỌI file ChuongN_*.md đang có trong thư mục nháp, theo thứ tự chương,
rồi làm ba việc trong một lần chạy:
  1. đánh số trích dẫn theo thứ tự xuất hiện lần đầu TRONG TOÀN VĂN (kiểu IEEE);
  2. thay phần thân của từng chương đó trong file Word;
  3. viết lại mục TÀI LIỆU THAM KHẢO từ chuyende1/report/nhap/tai_lieu.json.
Chương nào chưa có file nháp thì giữ nguyên trong Word. Luôn ghép tất cả cùng
lúc, vì thêm một trích dẫn ở Chương 1 làm đổi số ở mọi chương sau.

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
from typing import Dict, List, Tuple

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, RGBColor

sys.path.insert(0, str(Path(__file__).parent))

from ute_docx import CAPTION_SIZE, FONT, LINE_SPACING, SIZE, TABLE_TEXT_SIZE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOCX_MAC_DINH = Path("chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx")
NHAP_MAC_DINH = Path("chuyende1/report/nhap")
TEN_FILE_TAI_LIEU = "tai_lieu.json"
TIEU_DE_TAI_LIEU = "TÀI LIỆU THAM KHẢO"
SO_CHUONG = range(1, 7)
DO = RGBColor(0xB0, 0x00, 0x00)
DAU_KHUNG_RONG = "(Ngân sách:"
DAU_HET_THAN = "## Tài liệu được trích"
MAU_DANH_DAU = re.compile(r"(\[(?:TODO|CẦN KIỂM|CẦN TÌM|CHÈN)[^\]]*\])")
MAU_TRICH_DAN = re.compile(r"\[@([^\]]+)\]")
MAU_TEN_BANG_HINH = re.compile(r"^(Bảng|Hình) \d+\.\d+:")
MAU_CONG_THUC = re.compile(r"\(\d+\.\d+\)$")
MAU_HINH = re.compile(r"^!\[(\d*(?:[.,]\d+)?)\]\(([^)]+)\)$")
RONG_HINH_CM = 15.0  # khổ A4 trừ lề trái 3,5 cm và lề phải 2 cm còn 15,5 cm

# Một khối: (loại, nội dung). Loại: h2 | h3 | ten | bang | cong_thuc | hinh | doan
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


def _them_khoi(doc: DocumentType, khoi: Khoi):
    """Thêm một khối vào CUỐI tài liệu, trả về phần tử XML để dời tới đúng chỗ."""
    loai, nd = khoi
    if loai in ("h2", "h3"):
        return doc.add_paragraph(nd, style="Heading 2" if loai == "h2" else "Heading 3")._p
    if loai == "ten":
        para = doc.add_paragraph(style="Caption")
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _chay(para, nd, co=CAPTION_SIZE, dam=True)
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
    a = ap.parse_args(argv)

    cac_file = tim_file_chuong(a.nhap)
    if not cac_file:
        print(f"Không thấy file ChuongN_*.md nào trong {a.nhap}")
        return 1
    tai_lieu = json.loads((a.nhap / TEN_FILE_TAI_LIEU).read_text(encoding="utf-8"))
    than = {so: p.read_text(encoding="utf-8") for so, p in cac_file.items()}
    than = {so: cat_than(t) for so, t in than.items()}
    than, thu_tu = danh_so_trich_dan(than, tai_lieu)

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
    khoi_tl: List[Khoi] = [("tai_lieu", f"[{n}] {tai_lieu[k]}") for n, k in enumerate(thu_tu, 1)]
    so_ck = sum(1 for _, nd in khoi_tl if MAU_DANH_DAU.search(nd))
    print(f"Tài liệu được trích: {len(thu_tu)} | trong đó còn đánh dấu chưa đối chiếu: {so_ck}")

    if a.chi_xem:
        return 0
    if da_co and not a.ghi_de:
        print(f"DỪNG: chương {da_co} đã có nội dung trong Word. Dùng --ghi-de nếu chắc chắn muốn thay "
              "(chỗ sửa tay trong Word ở các chương này sẽ mất, chỉ còn trong bản sao lưu).")
        return 2
    ban = sao_luu(a.docx)
    for so, khoi in khoi_chuong.items():
        thay_than_muc(doc, f"Chương {so}.", khoi)
    thay_than_muc(doc, TIEU_DE_TAI_LIEU, khoi_tl)
    doc.save(str(a.docx))
    print(f"Đã ghi {a.docx}\nBản sao lưu: {ban}")
    print("Mở Word, bấm Ctrl+A rồi F9 để cập nhật mục lục.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
