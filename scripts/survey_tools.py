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
VALID_LANGS = ("vi", "en", "da_ngu")
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


def cmd_excel(rows: list[dict[str, str]], columns: list[str], out: Path) -> int:
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


def cmd_tu_excel(xlsx: Path, csv_path: Path, columns: list[str]) -> int:
    """Nhap .xlsx nguoc lai .csv, giu nguyen thu tu cot."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        print("Thieu openpyxl.", file=sys.stderr)
        return 1

    if not xlsx.exists():
        print(f"Khong thay {xlsx}. Chay `excel` truoc de xuat ra.", file=sys.stderr)
        return 1

    ws = load_workbook(xlsx, data_only=True).active
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
        return cmd_excel(rows, columns, xlsx)
    if args.command == "tu-excel":
        return cmd_tu_excel(xlsx, args.csv, columns)
    if args.command == "validate":
        return cmd_validate(rows, columns)
    if args.command == "stats":
        return cmd_stats(rows)
    return cmd_table(rows, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
