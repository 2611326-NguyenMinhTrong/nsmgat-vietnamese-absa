"""[CD1.12d] Đối chiếu bản rút gọn của báo cáo với bản đầy đủ.

Bản rút gọn được tạo bằng cách cắt và chuyển chỗ từ bản đầy đủ, nên nó KHÔNG được chứa điều gì
bản đầy đủ không có. Công cụ này kiểm bốn điều:

  1. Mọi con số trong bản rút gọn đều có trong bản đầy đủ.
  2. Mọi hàng của mọi bảng đều có nguyên văn trong bản đầy đủ, trừ các bảng được khai là bảng mới.
  3. Mọi khoá trích dẫn đều có trong tai_lieu.json.
  4. Câu nào có số mà không còn nguyên văn như bản đầy đủ thì được in ra để đọc lại bằng mắt.

    python scripts/doi_chieu_ban_rut_gon.py                 # kiểm, in tóm tắt
    python scripts/doi_chieu_ban_rut_gon.py --in-cau        # in cả các câu có số đã viết lại

Mã thoát 1 khi có con số lạ, hàng bảng lạ hoặc khoá trích dẫn lạ.

GIỚI HẠN: công cụ không biết một con số có còn gắn với đúng mô hình, đúng tập, đúng độ đo hay
không. Điều đó chỉ kiểm được bằng cách đọc các câu ở mục 4; vì vậy mục 4 tồn tại.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

for _luong in (sys.stdout, sys.stderr):
    if hasattr(_luong, "reconfigure"):
        _luong.reconfigure(encoding="utf-8", errors="replace")

DAY_DU = Path("chuyende1/report/nhap")
RUT_GON = Path("chuyende1/report/nhap_rut_gon")
TEN_PHU_LUC = "PhuLuc.md"
# Bảng chỉ có ở bản rút gọn: hàng của chúng không cần có nguyên văn trong bản đầy đủ (số thì vẫn phải có).
BANG_MOI = ("Bảng A.2:",)

MAU_SO = re.compile(r"\d[\d.,]*\d|\d")
MAU_TRICH = re.compile(r"\[@([^\]]+)\]")
# Nhãn dẫn chéo: số trong đó là số thứ tự của bảng, hình, mục, công thức, không phải số liệu.
MAU_DAN_CHEO = re.compile(
    r"(?:Bảng|Hình|Phụ lục|Chương|[Mm]ục|[Cc]ông thức|[Bb]ậc)\s+(?:[A-Z]\.\d+|\(?\d+(?:\.\d+)*\)?[a-z]?)"
    r"(?:(?:\s+(?:đến|và)\s+|,\s+)(?:[A-Z]\.\d+|\(?\d+(?:\.\d+)*\)?))*")
MAU_SO_CONG_THUC = re.compile(r"\(\d+\.\d+\)\s*$")
MAU_TIEU_DE = re.compile(r"^#+\s+(?:\d+(?:\.\d+)*\.?|Phụ lục [A-Z]\.)\s*")
MAU_HINH = re.compile(r"^!\[[^\]]*\]\([^)]*\)$")


def doc_ban(thu_muc: Path) -> Dict[str, str]:
    """{tên file: nội dung} của các chương và phụ lục, đã chuẩn hoá xuống dòng."""
    ra = {}
    for p in sorted(thu_muc.glob("Chuong[1-9]_*.md")) + [thu_muc / TEN_PHU_LUC]:
        if p.exists():
            ra[p.name] = p.read_text(encoding="utf-8").replace("\r\n", "\n")
    return ra


def bo_nhan(dong: str) -> str:
    """Bỏ khỏi một dòng những thứ mang số nhưng không phải số liệu."""
    if MAU_HINH.match(dong.strip()):
        return ""
    dong = MAU_TRICH.sub(" ", dong)
    dong = MAU_TIEU_DE.sub("", dong)
    dong = MAU_SO_CONG_THUC.sub("", dong)
    return MAU_DAN_CHEO.sub(" ", dong)


def so_trong(van: str) -> Set[str]:
    return {m.group(0) for d in van.split("\n") for m in MAU_SO.finditer(bo_nhan(d))}


def hang_bang(van: str) -> List[Tuple[str, str]]:
    """[(tên bảng đứng ngay trên, hàng)], bỏ hàng phân cách."""
    ra, ten = [], ""
    for d in van.split("\n"):
        s = d.strip()
        if re.match(r"^(Bảng|Hình) (?:\d+|[A-Z])\.\d+:", s):
            ten = s
        elif s.startswith("|") and not re.fullmatch(r"[|:\- ]+", s):
            ra.append((ten, s))
    return ra


def cau_co_so(van: str) -> List[str]:
    """Các câu của phần lời (không phải bảng, tiêu đề, tên bảng) có ít nhất một con số là số liệu."""
    ra = []
    for d in van.split("\n"):
        s = d.strip()
        if not s or s.startswith(("|", "#", "![", "[TODO")) or re.match(r"^(Bảng|Hình) (?:\d+|[A-Z])\.\d+:", s):
            continue
        for c in re.split(r"(?<=[.?!])\s+(?=[A-ZÀ-Ỵ\"“])", s):
            if MAU_SO.search(bo_nhan(c)):
                ra.append(c.strip())
    return ra


def chuan_cau(c: str) -> str:
    return re.sub(r"\s+", " ", bo_nhan(c)).strip()


def kiem(day_du: Dict[str, str], rut_gon: Dict[str, str], tai_lieu: Dict[str, str]) -> Dict[str, object]:
    toan_dd = "\n".join(day_du.values())
    so_dd = so_trong(toan_dd)
    hang_dd = {h for _, h in hang_bang(toan_dd)}
    cau_dd = {chuan_cau(c) for c in cau_co_so(toan_dd)}
    doan_dd = re.sub(r"\s+", " ", "\n".join(bo_nhan(d) for d in toan_dd.split("\n")))

    so_la, hang_la, khoa_la, cau_viet_lai = [], [], [], []
    so_cau = so_giu = so_hang = 0
    for ten, van in rut_gon.items():
        for s in sorted(so_trong(van) - so_dd):
            so_la.append((ten, s))
        for ten_bang, h in hang_bang(van):
            so_hang += 1
            if h not in hang_dd and not ten_bang.startswith(BANG_MOI):
                hang_la.append((ten, ten_bang[:40], h[:120]))
        for k in sorted(set(MAU_TRICH.findall(van)) - set(tai_lieu)):
            khoa_la.append((ten, k))
        for c in cau_co_so(van):
            so_cau += 1
            chuan = chuan_cau(c)
            if chuan in cau_dd or chuan in doan_dd:
                so_giu += 1
            else:
                cau_viet_lai.append((ten, c))
    khoa_rg = set(MAU_TRICH.findall("\n".join(rut_gon.values())))
    khoa_dd = set(MAU_TRICH.findall(toan_dd))
    return {"so_la": so_la, "hang_la": hang_la, "khoa_la": khoa_la, "cau_viet_lai": cau_viet_lai,
            "so_cau_co_so": so_cau, "so_cau_giu_nguyen": so_giu, "so_hang_bang": so_hang,
            "khoa_bi_bo": sorted(khoa_dd - khoa_rg), "so_khoa": len(khoa_rg),
            "so_tu": {ten: len(re.sub(r"^\|.*$", "", van, flags=re.M).split()) for ten, van in rut_gon.items()},
            "so_tu_day_du": {ten: len(re.sub(r"^\|.*$", "", van, flags=re.M).split()) for ten, van in day_du.items()}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đối chiếu bản rút gọn của báo cáo với bản đầy đủ.")
    ap.add_argument("--goc", type=Path, default=Path("."), help="thư mục gốc của repo")
    ap.add_argument("--day-du", type=Path, default=DAY_DU, help=f"thư mục bản đầy đủ (mặc định {DAY_DU})")
    ap.add_argument("--rut-gon", type=Path, default=RUT_GON, help=f"thư mục bản rút gọn (mặc định {RUT_GON})")
    ap.add_argument("--in-cau", action="store_true", help="in các câu có số không còn nguyên văn như bản đầy đủ")
    a = ap.parse_args(argv)

    day_du, rut_gon = doc_ban(a.goc / a.day_du), doc_ban(a.goc / a.rut_gon)
    if not rut_gon:
        print(f"Không thấy file chương nào trong {a.goc / a.rut_gon}")
        return 1
    tai_lieu = json.loads((a.goc / a.rut_gon / "tai_lieu.json").read_text(encoding="utf-8"))
    kq = kiem(day_du, rut_gon, tai_lieu)

    print("Số chữ của phần lời (không kể bảng):")
    for ten, n in kq["so_tu"].items():
        cu = kq["so_tu_day_du"].get(ten)
        print(f"  {ten:28} {n:>6}" + (f"   (bản đầy đủ {cu}, còn {n / cu * 100:.0f} %)".replace(".", ",") if cu else "   (chỉ có ở bản rút gọn)"))
    print(f"Hàng bảng: {kq['so_hang_bang']} | hàng không có nguyên văn trong bản đầy đủ: {len(kq['hang_la'])}")
    for x in kq["hang_la"]:
        print("  HÀNG LẠ:", x)
    print(f"Con số không có trong bản đầy đủ: {len(kq['so_la'])}")
    for x in kq["so_la"]:
        print("  SỐ LẠ:", x)
    print(f"Khoá trích dẫn: {kq['so_khoa']} | không có trong tai_lieu.json: {len(kq['khoa_la'])} | "
          f"có ở bản đầy đủ mà bản rút gọn không dẫn: {len(kq['khoa_bi_bo'])} {kq['khoa_bi_bo']}")
    for x in kq["khoa_la"]:
        print("  KHOÁ LẠ:", x)
    print(f"Câu có số: {kq['so_cau_co_so']} | giữ nguyên văn: {kq['so_cau_giu_nguyen']} | "
          f"đã viết lại, cần đọc bằng mắt: {len(kq['cau_viet_lai'])}")
    if a.in_cau:
        for ten, c in kq["cau_viet_lai"]:
            print(f"  [{ten}] {c}")
    return 1 if (kq["so_la"] or kq["hang_la"] or kq["khoa_la"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
