"""Kiểm chỗ học viên sửa tay trong file Word trước khi ghép bản nháp vào (học viên dặn 16/10/2026).

Từ 16/10/2026 học viên sửa thẳng trong `ChuyenDe1_NguyenMinhTrong_rutgon.docx`. Lệnh ghép
`nhap_chuong_vao_docx.py --ghi-de` thay toàn bộ trang đầu, các chương, phụ lục và tài liệu tham khảo bằng bản nháp,
nên mọi chỗ sửa tay chưa có trong bản nháp sẽ mất. Lệnh này trả lời trước: GHÉP BÂY GIỜ THÌ MẤT NHỮNG GÌ.

    python scripts/kiem_sua_tay_word.py            # mã thoát 0: ghép an toàn; 1: có chỗ sẽ bị ghi đè (in ra từng chỗ)

Cách làm: chép file Word ra thư mục tạm, ghép bản nháp vào BẢN SAO đó bằng chính lệnh ghép, rồi so chữ của bản sao với
file thật theo từng đoạn văn và từng hàng bảng. File Word thật không bị đụng tới (chỉ đọc, đọc được cả khi đang mở trong
Word, nhưng chỉ thấy bản đã lưu).

Giới hạn: chỉ so CHỮ. Không thấy được chỗ sửa định dạng (font, in đậm, giãn dòng), hình, chú thích, hay dòng trống.
Bỏ qua mục lục, danh sách bảng, danh sách hình vì Word tự sinh. Trang bìa không bị lệnh ghép thay chữ nên không bao giờ
hiện ở đây.

PHƯƠNG TRÌNH WORD (từ 16/10/2026): học viên chuyển các công thức của Chương 2 sang phương trình của Word (OMML). Bản
nháp chỉ có công thức dạng chữ, nên ghép sẽ biến chúng về chữ thường. Lệnh bỏ qua dòng công thức ở cả hai phía khi so
chữ (đoạn chỉ có phương trình và số hiệu như "(2.2)"), nhưng hễ file Word còn phương trình thì trả mã 2: chữ đã khớp
bản nháp, nhưng KHÔNG ĐƯỢC GHÉP, mọi chỗ sửa làm thẳng trong Word.

    mã 0: chữ khớp, không có phương trình Word, ghép an toàn
    mã 1: có chỗ sửa tay chưa có trong bản nháp (in từng chỗ)
    mã 2: chữ khớp, nhưng file Word có phương trình: không được ghép
"""

from __future__ import annotations

import argparse
import contextlib
import difflib
import io
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

import docx
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nhap_chuong_vao_docx as nc  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

STYLE_BO_QUA = ("toc", "table of figures")
OMATH = "{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath"
# Dòng công thức: chữ thường (ngoài phương trình) chỉ còn số hiệu, hoặc công thức dạng chữ của bản nháp kết thúc bằng số hiệu
# Phương trình Word: chữ thường ngoài phương trình chỉ còn vài ký tự lọt ra (như ")V") và số hiệu, hoặc rỗng
MAU_CHI_SO_HIEU = re.compile(r"(.{0,12}\(\d+\.\d+\))?")
MAU_CONG_THUC_CHU = re.compile(r"=.*\(\d+\.\d+\)\s*$")


def so_phuong_trinh(duong_dan: Path) -> int:
    return sum(1 for _ in docx.Document(str(duong_dan)).element.body.iter(OMATH))


def la_dong_cong_thuc(p: Paragraph) -> bool:
    chu = p.text.strip()
    if p._p.find(".//" + OMATH) is not None:
        return MAU_CHI_SO_HIEU.fullmatch(chu) is not None
    return MAU_CONG_THUC_CHU.search(chu) is not None


def cac_khoi(duong_dan: Path) -> List[str]:
    """Chữ của file Word theo thứ tự: mỗi đoạn văn khác rỗng một khối, mỗi hàng bảng một khối.
    Bỏ qua mục lục, hai danh sách tự động và dòng công thức (xem docstring của module)."""
    d = docx.Document(str(duong_dan))
    ra: List[str] = []
    for el in d.element.body.iterchildren():
        if el.tag == qn("w:p"):
            p = Paragraph(el, d)
            ten = (p.style.name if p.style is not None else "") or ""
            if ten.lower().startswith(STYLE_BO_QUA) or la_dong_cong_thuc(p) or not p.text.strip():
                continue
            ra.append(p.text.strip())  # dấu cách thừa ở hai đầu đoạn không thấy được, không tính là sửa
        elif el.tag == qn("w:tbl"):
            for hang in Table(el, d).rows:
                ra.append("| " + " | ".join(o.text.strip() for o in hang.cells) + " |")
    return ra


def so_khac(nhap: List[str], word: List[str]) -> List[Tuple[List[str], List[str]]]:
    """Các cụm khác nhau: (khối ở bản ghép từ nháp, khối ở file Word của học viên)."""
    sm = difflib.SequenceMatcher(a=nhap, b=word, autojunk=False)
    return [(nhap[i1:i2], word[j1:j2]) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]


def chu_khac(a: str, b: str) -> str:
    """Các từ bị bỏ (-) và thêm (+) giữa hai đoạn."""
    return " ".join(t for t in difflib.ndiff(a.split(), b.split()) if t[:1] in "+-")


def ghep_thu(docx_that: Path, nhap: Path, tam: Path) -> Path:
    """Ghép bản nháp vào bản sao của file Word, trả về đường dẫn bản sao đã ghép."""
    ban_sao = tam / docx_that.name
    shutil.copy2(docx_that, ban_sao)
    with contextlib.redirect_stdout(io.StringIO()) as ra:
        ma = nc.main(["--nhap", str(nhap), "--docx", str(ban_sao), "--ghi-de"])
    if ma != 0:
        raise RuntimeError(f"lệnh ghép thử báo lỗi (mã {ma}):\n{ra.getvalue()}")
    return ban_sao


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Liệt kê chỗ sửa tay trong file Word sẽ mất nếu ghép bản nháp vào bây giờ.")
    ap.add_argument("--docx", type=Path, default=nc.DOCX_MAC_DINH, help=f"file Word (mặc định {nc.DOCX_MAC_DINH})")
    ap.add_argument("--nhap", type=Path, default=nc.NHAP_MAC_DINH, help=f"thư mục bản nháp (mặc định {nc.NHAP_MAC_DINH})")
    a = ap.parse_args(argv)

    with tempfile.TemporaryDirectory() as t:
        ban_ghep = ghep_thu(a.docx, a.nhap, Path(t))
        khac = so_khac(cac_khoi(ban_ghep), cac_khoi(a.docx))

    for i, (x, y) in enumerate(khac, 1):
        print(f"===== CHỖ {i}")
        for k in x:
            print(f"  NHÁP (sẽ ghi vào Word): {k}")
        for k in y:
            print(f"  WORD (sẽ mất)         : {k}")
        if len(x) == len(y) == 1:
            print(f"  TỪ KHÁC: {chu_khac(x[0], y[0])}")
    so_pt = so_phuong_trinh(a.docx)
    if khac:
        print(f"\nGHÉP BÂY GIỜ SẼ GHI ĐÈ {len(khac)} chỗ trong {a.docx.name}. Đưa các chỗ sửa ở dòng WORD vào bản nháp "
              "trước, hoặc sửa thẳng trong Word thay vì ghép.")
        return 1
    if so_pt:
        print(f"Chữ của {a.docx.name} khớp bản nháp (không kể định dạng, mục lục, trang bìa, dòng công thức). NHƯNG file "
              f"Word có {so_pt} phương trình dạng Word: KHÔNG ĐƯỢC GHÉP, ghép sẽ đổi chúng về chữ thường. Sửa thẳng trong Word.")
        return 2
    print(f"Ghép an toàn: chữ của {a.docx.name} trùng với bản nháp (không kể định dạng, mục lục, trang bìa).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
