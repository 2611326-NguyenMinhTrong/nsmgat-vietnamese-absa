"""[CD1.2] Công cụ cho ma trận khảo sát SOTA.

Giao thức: chuyende1/survey/survey_protocol.md
Dữ liệu:   chuyende1/survey/survey_matrix.csv

Ba lệnh:
    validate  kiểm cấu trúc file — cột, giá trị hợp lệ, trùng ref_key, mâu thuẫn nội tại
    stats     tiến độ khảo sát — phủ 6 nhóm tới đâu, kiểm chứng được bao nhiêu, N4/N5
    table     sinh Bảng 3.9 cho báo cáo — CHỈ từ những dòng đã kiểm chứng

Vì sao có `table` mà không copy tay từ CSV: quy tắc số 7 của repo cấm bịa trích dẫn.
Ở đây quy tắc đó được cưỡng chế bằng code — dòng còn `chua_kiem` không thể lọt vào bảng
của cuốn báo cáo, kể cả khi vô ý.

Dùng:
    python scripts/survey_tools.py validate
    python scripts/survey_tools.py stats
    python scripts/survey_tools.py table [-o duong/dan/ra.md]
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Console Windows mac dinh la cp1252, khong in duoc chu tieng Viet co dau ->
# UnicodeEncodeError. Ep stdout ve UTF-8 ngay dau chuong trinh.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO_ROOT / "chuyende1" / "survey" / "survey_matrix.csv"
DEFAULT_TABLE_OUT = REPO_ROOT / "chuyende1" / "tables" / "bang_3_9_khao_sat.md"

UNKNOWN = "[CẦN TÌM]"

REQUIRED_COLUMNS = [
    "ref_key",
    "tieu_de",
    "trang_thai",
    "nam",
    "hoi_nghi_tap_chi",
    "ho_phuong_phap",
    "bieu_dien_dau_vao",
    "co_dung_do_thi",
    "loai_do_thi",
    "co_tri_thuc_ngoai",
    "ngon_ngu",
    "tap_du_lieu",
    "do_do_bao_cao",
    "ket_qua_tot_nhat",
    "xu_ly_phu_dinh_chuyen_y",
    "co_giai_thich",
    "co_ma_nguon",
    "nguon_url",
    "ghi_chu",
]

# Ba mức kiểm chứng — xem survey_protocol.md mục 7
STATUS_CHUA_KIEM = "chua_kiem"
STATUS_KIEM_URL = "da_kiem_url"
STATUS_TOAN_VAN = "da_doc_toan_van"
VALID_STATUS = (STATUS_CHUA_KIEM, STATUS_KIEM_URL, STATUS_TOAN_VAN)

# Sáu nhóm phương pháp của Chương 3, cộng nhóm tài nguyên (tập dữ liệu, từ điển)
METHOD_GROUPS = {
    "G1_co_dien": "Đặc trưng thủ công + học máy cổ điển",
    "G2_tuan_tu_attention": "Mạng nơ-ron tuần tự + attention",
    "G3_plm": "Mô hình ngôn ngữ tiền huấn luyện",
    "G4_do_thi": "Mạng nơ-ron đồ thị",
    "G5_sinh_prompting": "Sinh và prompting",
    "G6_neuro_symbolic": "Kết hợp nơ-ron và ký hiệu",
}
GROUP_RESOURCE = "TAI_NGUYEN"
VALID_GROUPS = tuple(METHOD_GROUPS) + (GROUP_RESOURCE,)

# Dong chu thich ngay trong file CSV (#MO_TA, #VI_DU): mo ta cot va mot dong
# dien mau, de nguoi dien khong phai mo protocol ra tra. Moi cong cu BO QUA
# chung — nhung `load_rows` van giu lai, neu khong thi vong Excel se xoa mat.
DAU_CHU_THICH = "#"

# Cac cot co tap gia tri dong. Khoa bang code, khong bang tri nho — dung co
# che da dung cho trang_thai. Vi sao can: truoc khi co muc nay, cot
# bieu_dien_dau_vao co hai dong dien hai kieu khac nhau, mot dong con tron ca
# kien truc mo hinh vao o (GAP-016).
VALID_YESNO = ("co", "khong")
VALID_NEGATION = ("co", "khong", "mot_phan")
VALID_GRAPH_TYPES = ("", "cu_phap", "ngu_nghia", "tri_thuc", "khac")
VALID_LANGS = ("vi", "en", "da_ngu", "khac")  # khac: mot ngon ngu KHAC vi/en (vd tieng Ba Lan), ghi ro trong ghi_chu
# Ma bat buoc cua bieu_dien_dau_vao. Chi tiet viet trong ngoac don sau ma,
# vi du: "embedding_tinh (fastText, muc tu)".
VALID_INPUT_REPR = (
    "dac_trung_thu_cong",
    "tu_dien_cam_xuc",
    "embedding_tinh",
    "embedding_ngu_canh",
    "khac",
)

CLOSED_COLUMNS = {
    "co_dung_do_thi": VALID_YESNO,
    "co_tri_thuc_ngoai": VALID_YESNO,
    "co_giai_thich": VALID_YESNO,
    "co_ma_nguon": VALID_YESNO,
    "xu_ly_phu_dinh_chuyen_y": VALID_NEGATION,
    "loai_do_thi": VALID_GRAPH_TYPES,
    "ngon_ngu": VALID_LANGS,
}

# Chỉ tiêu ở PLAN_CHUYENDE1.md mục CD1.2
TARGET_TOTAL = 45
TARGET_PER_GROUP = 4
TARGET_DEEP = 25

# Cột đưa vào Bảng 3.9 — 8 cột vừa một trang khổ ngang
TABLE_COLUMNS = [
    ("ref_key", "Công trình"),
    ("nam", "Năm"),
    ("hoi_nghi_tap_chi", "Nơi công bố"),
    ("ho_phuong_phap", "Nhóm"),
    ("co_dung_do_thi", "Đồ thị"),
    ("xu_ly_phu_dinh_chuyen_y", "Phủ định / chuyển ý"),
    ("tap_du_lieu", "Dữ liệu"),
    ("ket_qua_tot_nhat", "Kết quả"),
]


class MalformedCSV(Exception):
    """File CSV sai cấu trúc — số cột của một dòng không khớp header.

    Hay gặp nhất: ghi chú có chứa dấu phẩy mà không đặt trong dấu nháy kép.
    Excel tự xử lý đúng, nhưng sửa bằng text editor thì rất dễ vấp.
    """


def load_rows(path: Path = DEFAULT_CSV) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            return []

        rows = []
        for line_no, values in enumerate(reader, start=2):
            if not values:
                continue
            if len(values) != len(header):
                raise MalformedCSV(
                    f"Dòng {line_no}: có {len(values)} cột, header có {len(header)} cột.\n"
                    f"  Nguyên nhân hay gặp: ô ghi_chu chứa dấu phẩy mà không đặt trong \"...\".\n"
                    f"  Nội dung dòng: {','.join(values)[:120]}..."
                )
            rows.append({k: (v or "").strip() for k, v in zip(header, values)})
        return rows


def is_verified(row: dict[str, str]) -> bool:
    return row.get("trang_thai") in (STATUS_KIEM_URL, STATUS_TOAN_VAN)


def la_chu_thich(row: dict[str, str]) -> bool:
    """Dong mo ta cot / dong dien mau, khong phai mot cong trinh."""
    return row.get("ref_key", "").startswith(DAU_CHU_THICH)


def chi_du_lieu(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [r for r in rows if not la_chu_thich(r)]


def _ma_bieu_dien(gia_tri: str) -> str:
    """"embedding_tinh (fastText, muc tu)" -> "embedding_tinh"."""
    return gia_tri.split("(", 1)[0].strip()


# --- validate -----------------------------------------------------------------


def validate(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    """Trả về danh sách lỗi. Rỗng nghĩa là file hợp lệ."""
    errors: list[str] = []

    missing = [c for c in REQUIRED_COLUMNS if c not in columns]
    if missing:
        errors.append(f"Thiếu cột bắt buộc: {', '.join(missing)}")
        return errors  # thiếu cột thì các kiểm tra sau vô nghĩa

    extra = [c for c in columns if c not in REQUIRED_COLUMNS]
    if extra:
        errors.append(f"Cột lạ không có trong đặc tả: {', '.join(extra)}")

    seen: Counter[str] = Counter()
    for i, row in enumerate(rows, start=2):  # dòng 1 là header
        ref = row["ref_key"]
        if not ref:
            errors.append(f"Dòng {i}: ref_key rỗng")
            continue
        if la_chu_thich(row):
            continue  # dòng mô tả cột / dòng điền mẫu
        seen[ref] += 1

        for cot, hop_le in CLOSED_COLUMNS.items():
            gia_tri = row.get(cot, "")
            if gia_tri != UNKNOWN and gia_tri not in hop_le:
                duoc_phep = " | ".join(v or "(để trống)" for v in hop_le)
                errors.append(
                    f"Dòng {i} ({ref}): {cot}='{gia_tri}' không hợp lệ, phải là {duoc_phep} "
                    f"hoặc {UNKNOWN}"
                )

        bieu_dien = row.get("bieu_dien_dau_vao", "")
        if bieu_dien != UNKNOWN and _ma_bieu_dien(bieu_dien) not in VALID_INPUT_REPR:
            errors.append(
                f"Dòng {i} ({ref}): bieu_dien_dau_vao='{bieu_dien}' phải bắt đầu bằng một mã "
                f"trong {' | '.join(VALID_INPUT_REPR)}, chi tiết viết trong ngoặc — "
                f"ví dụ: embedding_tinh (fastText, mức từ)"
            )

        # Mâu thuẫn nội tại: không dùng đồ thị mà vẫn ghi loại đồ thị
        if row.get("co_dung_do_thi") == "khong" and row.get("loai_do_thi") not in ("", UNKNOWN):
            errors.append(
                f"Dòng {i} ({ref}): co_dung_do_thi=khong thì loai_do_thi phải để trống, "
                f"đang là '{row['loai_do_thi']}'"
            )

        if row["trang_thai"] not in VALID_STATUS:
            errors.append(
                f"Dòng {i} ({ref}): trang_thai='{row['trang_thai']}' không hợp lệ, "
                f"phải là một trong {VALID_STATUS}"
            )

        if row["ho_phuong_phap"] not in VALID_GROUPS:
            errors.append(
                f"Dòng {i} ({ref}): ho_phuong_phap='{row['ho_phuong_phap']}' không hợp lệ, "
                f"phải là một trong {VALID_GROUPS}"
            )

        # Mâu thuẫn nội tại: đã đánh dấu kiểm chứng nhưng vẫn còn trường chưa biết
        if is_verified(row):
            unknown_fields = [c for c, v in row.items() if v == UNKNOWN]
            if unknown_fields:
                errors.append(
                    f"Dòng {i} ({ref}): đã đánh '{row['trang_thai']}' nhưng còn "
                    f"{UNKNOWN} ở: {', '.join(unknown_fields)}"
                )
            if not row["nguon_url"] or row["nguon_url"] == UNKNOWN:
                errors.append(f"Dòng {i} ({ref}): đã kiểm chứng thì phải có nguon_url")

    for ref, count in seen.items():
        if count > 1:
            errors.append(f"ref_key trùng {count} lần: {ref}")

    return errors


# --- stats --------------------------------------------------------------------


def compute_stats(rows: list[dict[str, str]]) -> dict:
    rows = chi_du_lieu(rows)
    by_status = Counter(r["trang_thai"] for r in rows)
    by_group = Counter(r["ho_phuong_phap"] for r in rows)
    method_rows = [r for r in rows if r["ho_phuong_phap"] in METHOD_GROUPS]

    return {
        "tong": len(rows),
        "tong_phuong_phap": len(method_rows),
        "theo_trang_thai": by_status,
        "theo_nhom": by_group,
        "da_kiem_chung": sum(1 for r in rows if is_verified(r)),
        "n4": sum(1 for r in rows if is_verified(r)),
        "n5": by_status[STATUS_TOAN_VAN],
    }


def format_stats(stats: dict) -> str:
    lines = ["TIẾN ĐỘ KHẢO SÁT", ""]

    total = stats["tong"]
    lines.append(f"Tổng số dòng trong ma trận : {total}")
    lines.append(f"  trong đó là phương pháp  : {stats['tong_phuong_phap']}")
    lines.append(f"  còn lại là tài nguyên    : {total - stats['tong_phuong_phap']}")
    lines.append("")

    lines.append("Mức kiểm chứng:")
    for status in VALID_STATUS:
        lines.append(f"  {status:<18} {stats['theo_trang_thai'][status]:>4}")
    lines.append("")

    lines.append("Phủ theo nhóm phương pháp (chỉ tiêu: mỗi nhóm ≥ 4):")
    for key, label in METHOD_GROUPS.items():
        count = stats["theo_nhom"][key]
        mark = "OK " if count >= TARGET_PER_GROUP else "-- "
        lines.append(f"  {mark} {key:<22} {count:>3}   {label}")
    resource = stats["theo_nhom"][GROUP_RESOURCE]
    lines.append(f"      {GROUP_RESOURCE:<22} {resource:>3}   (không tính vào chỉ tiêu)")
    lines.append("")

    lines.append("Số cho sơ đồ luồng sàng lọc (mục 3.1 của báo cáo):")
    lines.append(f"  N4 (vào ma trận, đã kiểm chứng) = {stats['n4']:>3}   chỉ tiêu ≥ {TARGET_TOTAL}")
    lines.append(f"  N5 (đã đọc toàn văn)            = {stats['n5']:>3}   chỉ tiêu ≈ {TARGET_DEEP}")
    lines.append("")

    remaining = TARGET_TOTAL - stats["n4"]
    if remaining > 0:
        lines.append(f"CÒN THIẾU {remaining} công trình đã kiểm chứng để đạt chỉ tiêu.")
    else:
        lines.append("Đã đạt chỉ tiêu số lượng.")

    return "\n".join(lines)


# --- table --------------------------------------------------------------------


def build_table_markdown(rows: list[dict[str, str]]) -> str:
    rows = chi_du_lieu(rows)
    verified = [r for r in rows if is_verified(r)]
    header = [label for _, label in TABLE_COLUMNS]

    lines = [
        "<!-- Sinh tự động bởi scripts/survey_tools.py — ĐỪNG sửa tay. -->",
        "<!-- Sửa chuyende1/survey/survey_matrix.csv rồi chạy lại. -->",
        "",
        "**Bảng 3.9: Tổng hợp so sánh các công trình đã khảo sát**",
        "",
        "| " + " | ".join(header) + " |",
        "|" + "---|" * len(header),
    ]
    for row in verified:
        lines.append("| " + " | ".join(row[key] for key, _ in TABLE_COLUMNS) + " |")

    skipped = len(rows) - len(verified)
    lines.append("")
    lines.append(
        f"*{len(verified)} công trình đã kiểm chứng. "
        f"{skipped} dòng còn `chua_kiem` đã bị loại khỏi bảng này.*"
    )
    return "\n".join(lines) + "\n"


# --- CLI ----------------------------------------------------------------------


def cmd_validate(rows, columns) -> int:
    errors = validate(rows, columns)
    if errors:
        print(f"KHÔNG HỢP LỆ — {len(errors)} lỗi:\n")
        for err in errors:
            print(f"  - {err}")
        return 1
    du_lieu = chi_du_lieu(rows)
    print(f"Hợp lệ. {len(du_lieu)} dòng dữ liệu "
          f"+ {len(rows) - len(du_lieu)} dòng chú thích, {len(columns)} cột.")
    return 0


def cmd_stats(rows) -> int:
    print(format_stats(compute_stats(rows)))
    return 0


def cmd_table(rows, out_path: Path) -> int:
    verified = [r for r in chi_du_lieu(rows) if is_verified(r)]
    if not verified:
        print(
            "CHƯA SINH ĐƯỢC BẢNG 3.9.\n\n"
            f"Không có dòng nào đạt mức kiểm chứng ({STATUS_KIEM_URL} hoặc {STATUS_TOAN_VAN}).\n"
            "Bảng trong cuốn báo cáo chỉ được dựng từ công trình đã kiểm chứng — xem\n"
            "chuyende1/survey/survey_protocol.md mục 7. Hãy mở nguồn gốc của từng bài,\n"
            "điền đủ các trường và đổi trang_thai, rồi chạy lại lệnh này.",
            file=sys.stderr,
        )
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_table_markdown(rows), encoding="utf-8")
    print(f"OK -> {out_path}  ({len(verified)} công trình, "
          f"bỏ qua {len(chi_du_lieu(rows)) - len(verified)} dòng chưa kiểm chứng)")
    return 0


# --- Cau noi Excel ------------------------------------------------------------
#
# VI SAO CAN: mo thang file .csv bang Excel tren may Windows tieng Viet cho ra
# hai loi cung luc (da gap that ngay 09/09/2026):
#   1. Chu tieng Viet thanh rac: "[CẦN TÌM]" -> "[Cáº¦N TÃŒM]". Vi file la
#      UTF-8 khong BOM, Excel doan nham la ma ANSI cua he thong.
#   2. Ca dong nam gon trong cot A. Vi dau tach danh sach cua Windows locale
#      tieng Viet la ";" chu khong phai ",".
#
# Them BOM chi chua duoc loi 1. Loi 2 khong sua duoc tu phia file (tru khi doi
# sang ";", nhung the thi khong con la CSV chuan cho git/pandas). Nen cach gon
# nhat la lam mot vong: xuat ra .xlsx de sua cho thoai mai, roi nhap nguoc lai.
#
#   .venv\Scripts\python.exe scripts/survey_tools.py excel      # csv -> xlsx
#   ... sua trong Excel roi luu ...
#   .venv\Scripts\python.exe scripts/survey_tools.py tu-excel   # xlsx -> csv
#
# File .csv van la NGUON SU THAT (git theo doi no, moi cong cu doc no).
# File .xlsx chi la ban lam viec tam.

DEFAULT_XLSX = DEFAULT_CSV.with_suffix(".xlsx")

# Trang tinh an trong .xlsx, giu dau van tay cua file .csv luc XUAT RA.
#
# VI SAO: .xlsx la mot BAN CHUP. Ai do (hoac mot cong cu) sua .csv sau khi
# xuat, roi `tu-excel` chay len — the la thay doi do bi nuot mat, khong bao
# gi ca. Da xay ra that ngay 20/09/2026, mat 4 thu trong mot lan (GAP-017).
# Cung co che voi .generated.json cua build_cd1_report.py (REQ-006).
TRANG_VAN_TAY = "_nguon"


def van_tay_csv(path: Path) -> str:
    """Dau van tay theo NOI DUNG (khong theo byte) — doi BOM hay kieu xuong
    dong khong lam bao dong gia."""
    import hashlib

    with path.open(encoding="utf-8-sig", newline="") as fh:
        noi_dung = "\n".join("\x1f".join(hang) for hang in csv.reader(fh))
    return hashlib.sha256(noi_dung.encode("utf-8")).hexdigest()[:16]


def _them_sheet_huongdan(wb) -> None:
    """Them sheet 'HuongDan' — chi dan tim noi dung cho tung cot, co vi du that.

    Sinh lai MOI LAN chay `excel`, giu dong bo voi ma nguon nay chu khong sua
    tay trong Excel — sua tay se mat khi xuat lai. Muon sua noi dung huong dan
    thi sua o day.

    Hai vi du dung xuyen suot bang, ca hai deu LA DONG THAT trong
    survey_matrix.csv, khong phai bia:
      - ASGCN     — moi kiem chung duoc phan tieu su (5/19 o), con 6 o [CẦN TÌM]
                    vi chua doc toan van. Minh hoa "lam dang do" trung thuc.
      - UIT-ViSFD — da dien du 19/19 o (da_doc_toan_van). Minh hoa "lam xong".
    """
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    ws = wb.create_sheet("HuongDan", 1)  # ngay sau survey_matrix, truoc sheet an

    MAU_TIEU_DE = PatternFill("solid", fgColor="1F4E78")
    MAU_MUC = PatternFill("solid", fgColor="DDEBF7")
    MAU_HEADER_BANG = PatternFill("solid", fgColor="BDD7EE")
    MAU_VIDU = PatternFill("solid", fgColor="E2EFDA")
    MAU_CANTIM = PatternFill("solid", fgColor="FFF2CC")
    CHU_TRANG_DAM = Font(bold=True, color="FFFFFF", size=13)
    CHU_MUC = Font(bold=True, size=11)
    CHU_THUONG = Font(size=10)
    NGOAI = Alignment(vertical="top", wrap_text=True)

    hang = 1

    def _ghi(cot: int, noi_dung: str, font=CHU_THUONG, fill=None, canh=NGOAI):
        o = ws.cell(row=hang, column=cot, value=noi_dung)
        o.font = font
        o.alignment = canh
        if fill:
            o.fill = fill
        return o

    def _gop_va_ghi(c1: int, c2: int, noi_dung: str, font=CHU_THUONG, fill=None):
        ws.merge_cells(start_row=hang, start_column=c1, end_row=hang, end_column=c2)
        _ghi(c1, noi_dung, font, fill)

    # --- Tieu de -----------------------------------------------------------
    _gop_va_ghi(1, 6, "HƯỚNG DẪN TÌM NỘI DUNG ĐỂ ĐIỀN survey_matrix — ĐỌC TRƯỚC KHI ĐIỀN",
                CHU_TRANG_DAM, MAU_TIEU_DE)
    ws.row_dimensions[hang].height = 24
    hang += 2

    _gop_va_ghi(1, 6,
        "Đọc kỹ mục 7 và 7b của chuyende1/survey/survey_protocol.md trước — sheet này chỉ là "
        "bản tra nhanh khi đang gõ. Quy tắc quan trọng nhất: một dòng CHỈ được đánh dấu "
        "'da_kiem_url' hay 'da_doc_toan_van' khi TOÀN BỘ 19 cột đã điền xong, không còn ô nào "
        "[CẦN TÌM] — lệnh `validate` sẽ từ chối nếu sai.")
    ws.row_dimensions[hang].height = 32
    hang += 2

    # --- Nguon nen dung ------------------------------------------------------
    _gop_va_ghi(1, 6, "1. NGUỒN NÊN MỞ TRƯỚC — theo thứ tự ưu tiên", CHU_MUC, MAU_MUC)
    hang += 1
    for c, t in enumerate(("Nguồn", "Link", "Dùng khi nào"), start=1):
        _ghi(c, t, Font(bold=True), MAU_HEADER_BANG)
    ws.merge_cells(start_row=hang, start_column=3, end_row=hang, end_column=6)
    hang += 1
    NGUON = [
        ("ACL Anthology", "aclanthology.org",
         "Nguồn GỐC cho hầu hết bài NLP/ABSA — luôn chép tiêu đề/năm/nơi công bố từ đây, "
         "không chép từ Google Scholar (snippet đôi khi sai chữ)"),
        ("arXiv", "arxiv.org",
         "Bản tiền in — dùng khi bài chưa/không có ở ACL Anthology. KHÔNG có trường hội nghị, "
         "phải tra thêm DBLP"),
        ("Google Scholar", "scholar.google.com",
         "Điểm bắt đầu tìm — gõ tên phương pháp, bấm vào kết quả đầu để tới trang gốc"),
        ("DBLP", "dblp.org",
         "Đối chiếu năm/nơi công bố khi ACL Anthology hoặc arXiv không ghi rõ hội nghị"),
        ("GitHub", "github.com",
         "Tìm mã nguồn — gõ '<tên phương pháp> github' hoặc mở link trong bài (thường ở "
         "footnote trang 1)"),
    ]
    for ten, link, khi_nao in NGUON:
        _ghi(1, ten, CHU_THUONG)
        _ghi(2, link, CHU_THUONG)
        ws.merge_cells(start_row=hang, start_column=3, end_row=hang, end_column=6)
        _ghi(3, khi_nao, CHU_THUONG)
        ws.row_dimensions[hang].height = 28
        hang += 1
    hang += 1

    # --- Meo go tim kiem -----------------------------------------------------
    _gop_va_ghi(1, 6, "2. MẪU CÂU TÌM KIẾM — thay <tên> bằng tên phương pháp/bài", CHU_MUC, MAU_MUC)
    hang += 1
    MAU_TIM = [
        '"<tên đầy đủ hoặc viết tắt>" paper  →  tìm nhanh khi chưa biết tên đầy đủ',
        '"<tên>" aspect-based sentiment  →  thêm ngữ cảnh bài toán để khỏi lẫn tên trùng '
        '(nhiều mô hình đặt tên viết tắt giống lĩnh vực khác)',
        'site:aclanthology.org <tên>  →  ép Google chỉ tìm trong ACL Anthology',
        'site:arxiv.org <tên>  →  ép Google chỉ tìm trong arXiv',
        '<tên phương pháp> github  →  tìm mã nguồn',
        '<tên bài đầy đủ trong ngoặc kép> dblp  →  tra năm/nơi công bố khi arXiv không ghi',
    ]
    for dong in MAU_TIM:
        _gop_va_ghi(1, 6, "• " + dong)
        hang += 1
    hang += 1

    # --- Quy trinh 9 buoc ------------------------------------------------------
    _gop_va_ghi(1, 6, "3. QUY TRÌNH 9 BƯỚC CHO MỖI DÒNG — chi tiết + ví dụ ở mục 7b protocol",
                CHU_MUC, MAU_MUC)
    hang += 1
    BUOC = [
        "Tìm nguồn: gõ mẫu câu ở mục 2 trên Google Scholar hoặc thẳng vào ACL Anthology/arXiv",
        "Mở TRỰC TIẾP trang gốc (không tin snippet tìm kiếm) — đây là nguồn duy nhất được chép",
        "Điền 5 ô 'dễ' trước: tieu_de, nam, hoi_nghi_tap_chi, nguon_url, co_ma_nguon",
        "Mở PDF, đọc Abstract + mục Model/Method → điền bieu_dien_dau_vao, co_dung_do_thi, "
        "loai_do_thi, co_tri_thuc_ngoai, ngon_ngu, ho_phuong_phap",
        "Đọc mục Experiments/Dataset → điền tap_du_lieu (liệt kê ĐỦ, không chỉ 1 tập), "
        "do_do_bao_cao (ghi rõ macro/micro)",
        "Tìm đúng DÒNG kết quả của mô hình bài này đề xuất trong bảng kết quả (không lấy dòng "
        "baseline họ so sánh) → điền ket_qua_tot_nhat",
        "Ctrl+F 'negation', 'contrast', 'but', 'however' trong toàn bài → điền "
        "xu_ly_phu_dinh_chuyen_y, co_giai_thich",
        "Viết ghi_chu: cách kiểm chứng những ô khó, ngày kiểm chứng — 3 tháng sau còn phải hiểu "
        "được vì sao điền vậy",
        "CHỈ KHI không còn ô nào [CẦN TÌM] → đổi trang_thai, rồi chạy `validate` để xác nhận",
    ]
    for i, b in enumerate(BUOC, start=1):
        _gop_va_ghi(1, 6, f"{i}. {b}")
        ws.row_dimensions[hang].height = 26
        hang += 1
    hang += 1

    # --- Bang chi tiet tung cot -------------------------------------------------
    _gop_va_ghi(1, 6, "4. TỪNG CỘT — tìm ở đâu, cách tìm, ví dụ thật", CHU_MUC, MAU_MUC)
    hang += 1

    tieu_de_cot = ["Cột", "Ý nghĩa ngắn", "Tìm ở đâu", "Cách tìm / mẹo",
                   "Ví dụ — ASGCN (đang làm dở)", "Ví dụ — UIT-ViSFD (đã xong)"]
    for c, t in enumerate(tieu_de_cot, start=1):
        _ghi(c, t, Font(bold=True), MAU_HEADER_BANG)
    hang += 1

    # (cot, y_nghia, tim_o_dau, cach_tim, vd_asgcn, vd_uitvisfd)
    CHI_TIET_COT = [
        ("ref_key", "Khoá trích dẫn ngắn, duy nhất",
         "Không cần tìm — tự đặt",
         "Tên viết tắt phương pháp hoặc tác_giả+năm. Không dấu cách, không dấu tiếng Việt",
         "ASGCN", "UIT-ViSFD"),
        ("tieu_de", "Tiêu đề đầy đủ, chép NGUYÊN VĂN",
         "Trang nguồn gốc (ACL Anthology/arXiv/DOI) — không chép từ snippet tìm kiếm",
         "Mở trang gốc, Ctrl+C tiêu đề — không tự gõ lại kẻo sai dấu/chữ hoa",
         "Aspect-based Sentiment Classification with Aspect-specific Graph Convolutional "
         "Networks (từ aclanthology.org/D19-1464)",
         "SA2SL: From Aspect-Based Sentiment Analysis to Social Listening System for "
         "Business Intelligence"),
        ("trang_thai", "Mức kiểm chứng: chua_kiem | da_kiem_url | da_doc_toan_van",
         "Không tìm — tự đánh giá SAU KHI điền hết các ô khác",
         "Chỉ nâng mức khi KHÔNG còn [CẦN TÌM] ở bất kỳ cột nào trong dòng — validate sẽ "
         "bắt lỗi nếu sai, xem mục 7b protocol",
         "chua_kiem (còn 6 ô trống)", "da_doc_toan_van"),
        ("nam", "Năm công bố, 4 chữ số",
         "Trang nguồn gốc — ACL Anthology ghi 'Year' ngay đầu trang; arXiv ghi 'Submitted'",
         "Lấy năm KỶ YẾU hội nghị nếu có; chỉ có bản arXiv thì lấy năm nộp, ghi chú rõ trong "
         "ghi_chu vì sao",
         "2019 (ACL Anthology)", "2021 (arXiv: Submitted 31/05/2021)"),
        ("hoi_nghi_tap_chi", "Nơi công bố; chỉ có tiền ấn phẩm thì ghi arXiv",
         "Trang nguồn gốc; nếu arXiv không ghi thì tra thêm DBLP/Google Scholar",
         "'<tên bài đầy đủ>' dblp — DBLP liệt kê rất chuẩn nơi công bố chính thức",
         "EMNLP-IJCNLP 2019", "KSE 2021 (tra thêm — DBLP/Semantic Scholar lúc tra bị chặn, "
         "ghi rõ trong ghi_chu)"),
        ("ho_phuong_phap", "Nhóm phương pháp Chương 3 — G1..G6 / TAI_NGUYEN",
         "Đọc Abstract/Introduction để hiểu bản chất kỹ thuật — không tìm trên mạng",
         "Đối chiếu bảng 6 nhóm ở mục 9 protocol: dùng đồ thị→G4, PLM tiền huấn luyện→G3...",
         "G4_do_thi (GCN trên cây phụ thuộc)", "TAI_NGUYEN (bài công bố dữ liệu, không phải "
         "một mô hình)"),
        ("bieu_dien_dau_vao", "Cách biến văn bản thành số trước khi mô hình lập luận",
         "Mục Model/Method trong PDF — đoạn mô tả tầng đầu tiên",
         "Ctrl+F 'embedding/GloVe/BERT/pretrained/TF-IDF'. 2 câu hỏi phân biệt 5 mã: (1) có "
         "embedding HỌC ĐƯỢC không, hay chỉ đếm/tra bảng? (2) vector 1 từ có ĐỔI theo câu "
         "chứa nó không? — chi tiết đầy đủ ở mục 9 survey_protocol.md, ngay dưới bảng mã",
         "embedding_tinh (GloVe, mức từ, nối thêm vector khía cạnh) — xem ví dụ ATAE-LSTM ở "
         "mục 9 protocol", "embedding_tinh (fastText, mức từ)"),
        ("co_dung_do_thi / loai_do_thi", "Có dùng đồ thị không, loại nào",
         "Abstract thường nói ngay nếu có đồ thị",
         "Ctrl+F 'graph', 'GCN', 'dependency tree' — cú pháp→cu_phap, tri thức ngoài→tri_thuc",
         "co / cu_phap (abstract: 'GCN over the dependency tree')", "khong / (để trống)"),
        ("co_tri_thuc_ngoai", "Có dùng tri thức ngoài dữ liệu train không (từ điển cảm xúc, "
         "SenticNet, ontology)",
         "Mục Method — tìm 'lexicon', 'SenticNet', 'knowledge base', 'affective'",
         "Đọc kỹ Method, không chỉ Abstract — nhiều bài giấu chi tiết này trong một câu ngắn",
         "[CẦN TÌM] — abstract không nhắc, cần đọc Method", "khong"),
        ("ngon_ngu", "Ngôn ngữ thực nghiệm — vi | en | da_ngu | khac (ngôn ngữ khác, ghi rõ trong ghi_chu)",
         "Mục Dataset/Experiments — tên tập dữ liệu thường lộ luôn",
         "SemEval/Twitter/Restaurant→en, VLSP/UIT-*→vi",
         "en (SemEval, benchmark chuẩn tiếng Anh của dòng ABSA này)", "vi"),
        ("tap_du_lieu", "Tập dữ liệu thực nghiệm chính, nhiều tập ngăn bằng '+'",
         "Mục Experiments/Dataset — thường có bảng thống kê số câu",
         "LIỆT KÊ ĐỦ tất cả, không chỉ 1 — đọc đoạn đầu mục Experiments hoặc Table 1",
         "[CẦN TÌM] — README repo chỉ nhắc 'rest14', abstract nói 'three benchmarking "
         "collections' nhưng không nêu tên, phải đọc PDF", "UIT-ViSFD"),
        ("do_do_bao_cao", "Độ đo bài dùng — ghi rõ macro hay micro",
         "Mục Experiments, đoạn 'Evaluation Metrics'",
         "Tìm chữ 'macro' hoặc 'micro' đứng cạnh tên độ đo — nhiều bài không ghi rõ, lúc đó "
         "ghi [CẦN TÌM: không ghi rõ macro/micro] chứ đừng đoán",
         "[CẦN TÌM]", "precision, recall, and F1-score (macro average)"),
        ("ket_qua_tot_nhat", "Con số tốt nhất, KÈM tập đạt được",
         "Bảng kết quả (Table) ở mục Experiments/Results",
         "Lấy đúng DÒNG của mô hình bài này ĐỀ XUẤT, không lấy dòng baseline họ so sánh",
         "[CẦN TÌM]", "84,48% (khía cạnh) và 63,06% (cảm xúc)"),
        ("xu_ly_phu_dinh_chuyen_y", "Có xử lý phủ định/chuyển ý không — câu hỏi khảo sát CH3",
         "Toàn bài — không chỉ Abstract",
         "Ctrl+F 'negation', 'contrast', 'but', 'however', 'phủ định' trong PDF",
         "[CẦN TÌM]", "khong (đọc toàn văn không thấy bàn tới)"),
        ("co_giai_thich", "Có đưa giải thích cho dự đoán không",
         "Mục Analysis/Case study — hay có hình minh hoạ attention",
         "Tìm hình có tô đậm/tô màu từ trong câu ví dụ, hoặc mục 'Case Study'",
         "[CẦN TÌM]", "khong"),
        ("co_ma_nguon", "Có công khai mã nguồn không",
         "Footnote trang 1 của bài ('Code is available at...'), hoặc tìm trực tiếp",
         "'<tên phương pháp> github'",
         "co — github.com/GeneZC/ASGCN (repo tự nhận là mã của đúng bài này)",
         "co — github.com/LuongPhan/UIT-ViSFD"),
        ("nguon_url", "Link bản gốc — DOI, arXiv hoặc ACL Anthology",
         "Chính là link đã mở ở bước 2 của quy trình 9 bước",
         "Copy nguyên URL trên thanh địa chỉ trình duyệt lúc đang xem trang gốc",
         "https://aclanthology.org/D19-1464/", "https://arxiv.org/abs/2105.15079"),
        ("ghi_chu", "Tự do — LUÔN ghi cách kiểm chứng ô khó",
         "Bạn tự viết, không tìm ở đâu cả",
         "Ghi ngày kiểm chứng + nguồn đối chiếu — 3 tháng sau còn phải hiểu vì sao điền vậy",
         "Đã ghi rõ cách kiểm chứng + 6 ô còn thiếu vì sao",
         "Xem dòng thật trong survey_matrix.csv — ghi chú dài, là mẫu tốt để bắt chước"),
    ]
    for cot, y_nghia, tim_dau, cach_tim, vd1, vd2 in CHI_TIET_COT:
        _ghi(1, cot, Font(bold=True))
        _ghi(2, y_nghia)
        _ghi(3, tim_dau)
        _ghi(4, cach_tim)
        _ghi(5, vd1, fill=MAU_CANTIM if "[CẦN TÌM]" in vd1 else MAU_VIDU)
        _ghi(6, vd2, fill=MAU_VIDU)
        ws.row_dimensions[hang].height = 60
        hang += 1

    # --- Do rong cot + dong bang -----------------------------------------------
    for i, w in enumerate((22, 30, 30, 38, 38, 38), start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A1"


def cmd_excel(rows: list[dict[str, str]], columns: list[str], out: Path,
              csv_path: Path = DEFAULT_CSV) -> int:
    """Xuat CSV ra .xlsx de sua bang Excel ma khong vap ma hoa lan dau tach cot."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.worksheet.datavalidation import DataValidation
    except ImportError:
        print(r"Thieu openpyxl. Cai bang:  .venv\Scripts\python.exe -m pip install openpyxl",
              file=sys.stderr)
        return 1

    wb = Workbook()
    ws = wb.active
    ws.title = "survey_matrix"

    ws.append(columns)
    for o in ws[1]:
        o.font = Font(bold=True)
        o.fill = PatternFill("solid", fgColor="DDEBF7")
        o.alignment = Alignment(vertical="center", wrap_text=True)

    for r in rows:
        ws.append([r.get(c, "") for c in columns])

    # Hai dong #MO_TA / #VI_DU: to khac di va cho xuong dong, de doc duoc ma
    # khong bi nham la du lieu that.
    so_chu_thich = sum(1 for r in rows if la_chu_thich(r))
    for hang in range(2, 2 + so_chu_thich):
        for o in ws[hang]:
            o.font = Font(italic=True, color="7F6000")
            o.fill = PatternFill("solid", fgColor="FFF2CC")
            o.alignment = Alignment(vertical="top", wrap_text=True)

    # Do rong cot theo DU LIEU THAT — tinh ca dong mo ta thi cot nao cung kich
    # het co, vi mo ta dai hon moi o du lieu.
    du_lieu = chi_du_lieu(rows)
    for i, c in enumerate(columns, start=1):
        dai = max([len(c)] + [len(str(r.get(c, ""))) for r in du_lieu])
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(max(dai + 2, 12), 60)

    # Giu header + hai dong chu thich + cot ref_key khi cuon
    ws.freeze_panes = f"B{2 + so_chu_thich}"

    # Khoa cot trang_thai vao 3 gia tri hop le — chan loi go sai ngay tu Excel,
    # thay vi de `validate` bao loi sau khi da sua ca file.
    if "trang_thai" in columns:
        cot = ws.cell(row=1, column=columns.index("trang_thai") + 1).column_letter
        dv = DataValidation(
            type="list", formula1=f'"{",".join(VALID_STATUS)}"', allow_blank=False,
            errorTitle="Trang thai khong hop le",
            error=f"Chi duoc mot trong: {', '.join(VALID_STATUS)}",
        )
        ws.add_data_validation(dv)
        dv.add(f"{cot}{2 + so_chu_thich}:{cot}{len(rows) + 1}")  # chừa dòng chú thích ra

    _them_sheet_huongdan(wb)

    # Dau van tay cua .csv luc xuat, de `tu-excel` biet file goc co doi khong
    ws_van_tay = wb.create_sheet(TRANG_VAN_TAY)
    ws_van_tay["A1"] = "Dau van tay cua file .csv luc xuat ra — dung xoa, dung sua."
    ws_van_tay["A2"] = van_tay_csv(csv_path)
    ws_van_tay["A3"] = f"Xuat luc {datetime.now():%d/%m/%Y %H:%M} tu {csv_path}"
    ws_van_tay.sheet_state = "hidden"

    # Sheet du lieu van la sheet duoc chon khi mo file, du "HuongDan" nam
    # truoc no trong thu tu tab — tranh doi hanh vi mo file hien co.
    wb.active = wb.sheetnames.index("survey_matrix")

    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        wb.save(out)
    except PermissionError:
        print(f"Khong ghi duoc {out} — file dang bi mo trong Excel. Dong no roi chay lai.",
              file=sys.stderr)
        return 1
    print(f"OK -> {out}  ({len(rows)} dong x {len(columns)} cot)")
    print()
    print("Sua xong thi nhap nguoc lai bang:")
    print(r"  .venv\Scripts\python.exe scripts/survey_tools.py tu-excel")
    print()
    print("LUU Y: file .csv moi la nguon su that. File .xlsx chi la ban lam viec,")
    print("khong commit — sua xong nho nhap nguoc lai roi moi commit .csv.")
    return 0


def cmd_tu_excel(xlsx: Path, csv_path: Path, columns: list[str], ghi_de: bool = False) -> int:
    """Nhap .xlsx nguoc lai .csv, giu nguyen thu tu cot."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        print("Thieu openpyxl.", file=sys.stderr)
        return 1

    if not xlsx.exists():
        print(f"Khong thay {xlsx}. Chay `excel` truoc de xuat ra.", file=sys.stderr)
        return 1

    wb = load_workbook(xlsx, data_only=True)

    # .xlsx la ban chup luc xuat. Neu .csv da doi sau do, nhap nguoc se nuot
    # mat thay doi do — im lang. Chan lai, tru khi nguoi dung noi ro --ghi-de.
    van_tay_cu = wb[TRANG_VAN_TAY]["A2"].value if TRANG_VAN_TAY in wb.sheetnames else None
    if van_tay_cu and not ghi_de and van_tay_cu != van_tay_csv(csv_path):
        print(f"DUNG LAI: {csv_path.name} da thay doi SAU khi xuat ra Excel.", file=sys.stderr)
        print(f"  Van tay luc xuat : {van_tay_cu}", file=sys.stderr)
        print(f"  Van tay hien tai : {van_tay_csv(csv_path)}", file=sys.stderr)
        print("  Nhap nguoc bay gio se XOA nhung thay doi do. Chon mot trong hai:", file=sys.stderr)
        print("    - Giu ban Excel, bo thay doi trong .csv:  them --ghi-de", file=sys.stderr)
        print("    - Giu ban .csv, bo thay doi trong Excel:  chay lai lenh `excel`", file=sys.stderr)
        print("  Xem ky truoc khi chon:  git diff chuyende1/survey/survey_matrix.csv",
              file=sys.stderr)
        return 1

    # Tim theo TEN, khong tin "sheet dang duoc chon" (wb.active): tu khi co them
    # sheet "HuongDan", nguoi dung bam xem huong dan roi luu se doi active sheet
    # trong Excel ma khong biet — doc nham sheet do se bao loi kho hieu.
    ws = wb["survey_matrix"] if "survey_matrix" in wb.sheetnames else wb.active
    du_lieu = list(ws.iter_rows(values_only=True))
    if not du_lieu:
        print("File Excel rong.", file=sys.stderr)
        return 1

    header = [str(c or "").strip() for c in du_lieu[0]]
    if header != columns:
        print("Header trong Excel da bi doi — khong nhap nguoc duoc.", file=sys.stderr)
        print(f"  Mong doi: {columns}", file=sys.stderr)
        print(f"  Nhan duoc: {header}", file=sys.stderr)
        print("  Dung them/bot/doi ten cot trong Excel; chi sua NOI DUNG o.", file=sys.stderr)
        return 1

    ban_ghi = []
    for hang in du_lieu[1:]:
        o = ["" if v is None else str(v).strip() for v in hang]
        if not any(o):
            continue
        o += [""] * (len(columns) - len(o))
        ban_ghi.append(o[:len(columns)])

    # Sao luu truoc khi ghi de: con duong lui neu ban Excel hoa ra sai
    sao_luu: Path | None = csv_path.with_suffix(".csv.bak")
    try:
        sao_luu.write_bytes(csv_path.read_bytes())
    except OSError:
        sao_luu = None

    # utf-8-sig: giu BOM de lan sau mo thang bang Excel van doc dung tieng Viet
    try:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(columns)
            w.writerows(ban_ghi)
    except PermissionError:
        # Hay gap: chinh file .csv dang mo trong Excel. Bao ro thay vi do
        # traceback — va nhat la KHONG duoc ghi de mot phan roi bo do.
        print(f"Khong ghi duoc {csv_path} — file dang bi mo boi chuong trinh khac.",
              file=sys.stderr)
        print("  Thuong la Excel dang mo chinh file .csv nay. Dong no roi chay lai.",
              file=sys.stderr)
        print("  Khong co gi bi ghi de — file .csv van nguyen ven.", file=sys.stderr)
        return 1

    print(f"OK -> {csv_path}  ({len(ban_ghi)} dong)")
    if sao_luu:
        print(f"Ban truoc khi nhap duoc luu o: {sao_luu.name}")
    print()
    print("Chay kiem tra ngay:")
    print(r"  .venv\Scripts\python.exe scripts/survey_tools.py validate")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("validate", "stats", "table", "excel", "tu-excel"))
    parser.add_argument("--xlsx", type=Path, default=None,
                        help="Duong dan file Excel (mac dinh: canh file csv)")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("-o", "--out", type=Path, default=DEFAULT_TABLE_OUT)
    parser.add_argument("--ghi-de", action="store_true",
                        help="tu-excel: nhập ngược DÙ file .csv đã đổi sau khi xuất "
                             "(mọi thay đổi trong .csv sẽ mất)")
    args = parser.parse_args(argv)

    if not args.csv.exists():
        print(f"Không thấy file: {args.csv}", file=sys.stderr)
        return 1

    with args.csv.open(encoding="utf-8-sig", newline="") as fh:
        columns = next(csv.reader(fh))

    try:
        rows = load_rows(args.csv)
    except MalformedCSV as err:
        print(f"FILE CSV SAI CẤU TRÚC\n\n{err}", file=sys.stderr)
        return 1

    xlsx = args.xlsx or args.csv.with_suffix(".xlsx")
    if args.command == "excel":
        return cmd_excel(rows, columns, xlsx, args.csv)
    if args.command == "tu-excel":
        return cmd_tu_excel(xlsx, args.csv, columns, args.ghi_de)
    if args.command == "validate":
        return cmd_validate(rows, columns)
    if args.command == "stats":
        return cmd_stats(rows)
    return cmd_table(rows, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
