"""[CD1.12b] Đối chiếu các con số mà báo cáo dẫn từ công trình khác với chính văn bản của bản gốc.

Hai lệnh:

    python scripts/doi_chieu_ban_goc.py tai                       # tải bản gốc về data/cache/nguon_goc/ và trích chữ
    python scripts/doi_chieu_ban_goc.py kiem                      # kiểm Chương 1 đến 4
    python scripts/doi_chieu_ban_goc.py kiem Chuong3_KhaoSat.md   # kiểm một chương
    python scripts/doi_chieu_ban_goc.py kiem --tat-ca             # in cả những con số đã thấy

CÁCH KIỂM
---------
Với mỗi câu trong bản nháp, lấy các khoá trích dẫn [@khoá] và các con số của câu đó. Một con số
được coi là "thấy" khi nó có mặt trong văn bản bản gốc của một công trình được trích ở cùng câu,
hoặc ở cùng đoạn. Con số của báo cáo viết kiểu Việt (84,46 hay 11.122) được thử ở các dạng mà bài
tiếng Anh có thể viết: 84.46, 0.8446, 11,122, 11122.

GIỚI HẠN, PHẢI BIẾT KHI ĐỌC KẾT QUẢ
-----------------------------------
- "Thấy" chỉ nói con số CÓ trong bài, không nói nó được gắn đúng mô hình, đúng tập dữ liệu, đúng độ
  đo. Phần đó phải đọc ngữ cảnh. Đợt rà ngày 13/10/2026 tìm ra mười chỗ số đúng mà lời gắn kèm sai.
- "Không thấy" không có nghĩa là sai: con số có thể do chuyên đề tự tính từ số của bài (hiệu, trung
  bình), hoặc là số của chính chuyên đề đứng cạnh một trích dẫn. Mỗi chỗ như vậy phải xem tay.
- Bản gốc là file tải về từ ACL Anthology, arXiv và trang của nhà xuất bản. Công trình không có bản
  mở thì đặt tay file <khoá>.pdf hoặc <khoá>.txt vào thư mục nguồn rồi chạy lại `tai`.

Thư mục data/cache/ không nằm trong git: bản gốc không được đưa lên GitHub.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NGUON_MAC_DINH = Path("data/cache/nguon_goc")
NHAP_MAC_DINH = Path("chuyende1/report/nhap")
MA_TRAN = Path("chuyende1/survey/survey_matrix.csv")
CHUONG_MAC_DINH = ("Chuong1_TongQuan.md", "Chuong2_CoSoLyThuyet.md", "Chuong3_KhaoSat.md", "Chuong4_ThucNghiem.md")
# Đường dẫn bản mở cho những công trình mà cột nguon_url của ma trận không suy ra được file PDF,
# và cho tài liệu nền của Chương 2 không nằm trong ma trận.
DUONG_DAN_RIENG = {
    "IAN": "https://arxiv.org/pdf/1709.00893",
    "Sentic-GCN": "https://sentic.net/sentic-gcn.pdf",
    "VoZhang2015": "https://www.ijcai.org/Proceedings/15/Papers/194.pdf",
    "KoconNeuroSymbolic": "https://link.springer.com/content/pdf/10.1007/978-3-031-08754-7_69.pdf",
    "PhoBERTPhoneReviewsCTU": "https://ctujs.ctu.edu.vn/index.php/ctujs/article/download/1146/726",
    "Transformer": "https://arxiv.org/pdf/1706.03762",
    "BERT": "https://aclanthology.org/N19-1423.pdf",
    "RoBERTa": "https://arxiv.org/pdf/1907.11692",
    "KipfGCN": "https://arxiv.org/pdf/1609.02907",
    "GAT": "https://arxiv.org/pdf/1710.10903",
    "VnCoreNLP": "https://aclanthology.org/N18-5012.pdf",
    "BootstrapNLP": "https://aclanthology.org/D12-1091.pdf",
}
MAU_KHOA = re.compile(r"\[@([^\]]+)\]")
MAU_SO = re.compile(r"(?<![\w.,])\d[\d.]*(?:,\d+)?(?![\w])")
MAU_NAM = re.compile(r"(19|20)\d\d")
MAU_SO_MUC = re.compile(r"[1-6]\.\d{1,2}")  # 3.8, 4.1: số mục và số bảng, không phải số liệu


# --- tải ---------------------------------------------------------------------------------------------


def duong_dan_pdf(url: str) -> str:
    if "aclanthology.org" in url:
        return url.rstrip("/") + ".pdf"
    if "arxiv.org/abs/" in url:
        return url.replace("/abs/", "/pdf/")
    return ""


def danh_sach_tai(ma_tran: Path) -> Dict[str, str]:
    viec = dict(DUONG_DAN_RIENG)
    with ma_tran.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            k = r["ref_key"]
            if k.startswith("#") or k in viec:
                continue
            viec[k] = duong_dan_pdf(r["nguon_url"])
    return viec


def trich_chu(pdf: Path) -> str:
    from pypdf import PdfReader

    doc = PdfReader(str(pdf))
    thuong = "\n".join((tr.extract_text() or "") for tr in doc.pages)
    try:  # chế độ layout giữ được hàng của bảng, nhưng hỏng với vài file
        bo_cuc = "\n".join((tr.extract_text(extraction_mode="layout") or "") for tr in doc.pages)
    except Exception as loi:  # noqa: BLE001
        bo_cuc = f"[layout hỏng: {loi}]"
    return thuong + "\n\n=====LAYOUT=====\n\n" + bo_cuc


def cmd_tai(ma_tran: Path, nguon: Path) -> int:
    nguon.mkdir(parents=True, exist_ok=True)
    thieu = []
    for k, url in sorted(danh_sach_tai(ma_tran).items()):
        pdf, txt = nguon / f"{k}.pdf", nguon / f"{k}.txt"
        if txt.exists():
            continue
        if not pdf.exists() and url:
            subprocess.run(["curl", "-sL", "-m", "90", "-A", "Mozilla/5.0", "-o", str(pdf), url], check=False)
        if not pdf.exists() or pdf.read_bytes()[:5] != b"%PDF-":
            pdf.unlink(missing_ok=True)
            thieu.append(k)
            continue
        try:
            txt.write_text(trich_chu(pdf), encoding="utf-8")
            print(f"đã trích {k}")
        except Exception as loi:  # noqa: BLE001
            print(f"LỖI khi đọc {pdf}: {loi}")
            thieu.append(k)
    co = len(list(nguon.glob("*.txt")))
    print(f"{co} bản gốc đã có chữ trong {nguon}.")
    if thieu:
        print("Chưa có bản gốc (không có bản mở hoặc tải hỏng). Đặt tay <khoá>.pdf vào thư mục trên rồi chạy lại:\n  " + ", ".join(thieu))
    return 0


# --- kiểm --------------------------------------------------------------------------------------------


def cac_dang(so: str) -> Set[str]:
    """Các cách một bài tiếng Anh có thể viết con số mà báo cáo viết kiểu Việt."""
    ung: Set[str] = set()
    if "," in so:  # thập phân: 84,46 -> 84.46 | 0.8446 ; 0,61 -> 0.61 | .61
        a = so.replace(".", "").replace(",", ".")
        ung.add(a)
        if a.startswith("0."):
            ung.add(a[1:])
        nguyen, le = a.split(".")
        if len(nguyen) <= 2 and nguyen != "0":  # phần trăm viết thành tỉ lệ: 84.46 -> 0.8446, 71.5 -> 0.715
            ung.add("0." + nguyen.zfill(2) + le)
    elif "." in so:  # hàng nghìn: 11.122 -> 11,122 | 11122 | 11 122
        ung |= {so.replace(".", ","), so.replace(".", ""), so.replace(".", " ")}
    else:
        ung.add(so)
        if len(so) == 2:  # 87 % viết thành 0.87
            ung.add("0." + so)
    return ung


def co_trong(so: str, van: str) -> bool:
    return any(re.search(r"(?<![\d.])" + re.escape(u) + r"(?!\d)", van) for u in cac_dang(so))


def so_trong_cau(cau: str) -> List[str]:
    sach = MAU_KHOA.sub("", cau)
    ra = [s.rstrip(".") for s in MAU_SO.findall(sach)]
    return [s for s in ra if not MAU_NAM.fullmatch(s) and not MAU_SO_MUC.fullmatch(s)]


def tach_cau(doan: str) -> List[str]:
    return [c for c in re.split(r"(?<=[.!?:;])\s+(?=[A-ZĐÀ-Ỹ\[\"])|\|", doan) if c.strip()]


def kiem_chuong(van_ban: str, van: Dict[str, str]) -> Tuple[List[tuple], int]:
    """Trả về (danh sách (trạng thái, số, khoá, câu), số con số đã xét).

    Trạng thái: thay | thay_cung_doan | khong_thay | chua_co_ban_goc.
    """
    ra, dem = [], 0
    for doan in van_ban.split("\n"):
        if doan.startswith("#") or doan.startswith("|---") or not doan.strip():
            continue
        khoa_doan = list(dict.fromkeys(MAU_KHOA.findall(doan)))
        truoc: List[str] = []
        for cau in tach_cau(doan):
            khoa = MAU_KHOA.findall(cau)
            if khoa:
                truoc = khoa
            for s in so_trong_cau(cau):
                if not truoc:
                    continue  # không gắn với công trình nào: số của chính chuyên đề, kiểm bằng công cụ khác
                dem += 1
                gon = MAU_KHOA.sub("", cau).strip()[:110]
                co_van = [k for k in truoc if k in van]
                if any(co_trong(s, van[k]) for k in co_van):
                    ra.append(("thay", s, ",".join(co_van), gon))
                elif any(co_trong(s, van[k]) for k in khoa_doan if k in van):
                    noi = [k for k in khoa_doan if k in van and co_trong(s, van[k])]
                    ra.append(("thay_cung_doan", s, ",".join(noi), gon))
                elif not co_van:
                    ra.append(("chua_co_ban_goc", s, ",".join(truoc), gon))
                else:
                    ra.append(("khong_thay", s, ",".join(co_van), gon))
    return ra, dem


def cmd_kiem(nhap: Path, nguon: Path, chuong: List[str], tat_ca: bool) -> int:
    van = {p.stem: p.read_text(encoding="utf-8", errors="replace") for p in nguon.glob("*.txt")}
    if not van:
        print(f"Chưa có bản gốc nào trong {nguon}. Chạy lệnh `tai` trước.")
        return 2
    can_xem = 0
    for ten in chuong:
        kq, dem = kiem_chuong((nhap / ten).read_text(encoding="utf-8"), van)
        nhan = {"thay": "thấy", "thay_cung_doan": "thấy ở công trình khác cùng đoạn", "khong_thay": "KHÔNG THẤY", "chua_co_ban_goc": "CHƯA CÓ BẢN GỐC"}
        for tt, s, k, cau in kq:
            if tat_ca or tt in ("khong_thay", "chua_co_ban_goc"):
                print(f"{nhan[tt]:<32} {s:>9} | {k[:34]} | {cau}")
        xau = sum(tt in ("khong_thay", "chua_co_ban_goc") for tt, *_ in kq)
        can_xem += xau
        print(f"{ten}: {dem} con số gắn với công trình khác | thấy {sum(tt == 'thay' for tt, *_ in kq)} | "
              f"thấy ở công trình khác cùng đoạn {sum(tt == 'thay_cung_doan' for tt, *_ in kq)} | cần xem tay {xau}\n")
    return 1 if can_xem else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đối chiếu con số dẫn từ công trình khác với văn bản của bản gốc.")
    sub = ap.add_subparsers(dest="lenh", required=True)
    p = sub.add_parser("tai", help="tải bản gốc và trích chữ")
    p.add_argument("--ma-tran", type=Path, default=MA_TRAN)
    p.add_argument("--nguon", type=Path, default=NGUON_MAC_DINH, help=f"thư mục chứa bản gốc (mặc định {NGUON_MAC_DINH})")
    p = sub.add_parser("kiem", help="kiểm con số trong các bản nháp chương")
    p.add_argument("chuong", nargs="*", default=list(CHUONG_MAC_DINH), help="tên file chương trong thư mục nháp (mặc định: Chương 1 đến 4)")
    p.add_argument("--nhap", type=Path, default=NHAP_MAC_DINH)
    p.add_argument("--nguon", type=Path, default=NGUON_MAC_DINH)
    p.add_argument("--tat-ca", action="store_true", help="in cả những con số đã thấy")
    a = ap.parse_args(argv)
    if a.lenh == "tai":
        return cmd_tai(a.ma_tran, a.nguon)
    return cmd_kiem(a.nhap, a.nguon, a.chuong, a.tat_ca)


if __name__ == "__main__":
    raise SystemExit(main())
