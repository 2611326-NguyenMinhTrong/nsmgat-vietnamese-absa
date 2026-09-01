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
    with path.open(encoding="utf-8", newline="") as fh:
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
        seen[ref] += 1

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
    print(f"Hợp lệ. {len(rows)} dòng, {len(columns)} cột.")
    return 0


def cmd_stats(rows) -> int:
    print(format_stats(compute_stats(rows)))
    return 0


def cmd_table(rows, out_path: Path) -> int:
    verified = [r for r in rows if is_verified(r)]
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
    print(f"OK -> {out_path}  ({len(verified)} công trình, bỏ qua {len(rows) - len(verified)} dòng chưa kiểm chứng)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("validate", "stats", "table"))
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("-o", "--out", type=Path, default=DEFAULT_TABLE_OUT)
    args = parser.parse_args(argv)

    if not args.csv.exists():
        print(f"Không thấy file: {args.csv}", file=sys.stderr)
        return 1

    with args.csv.open(encoding="utf-8", newline="") as fh:
        columns = next(csv.reader(fh))

    try:
        rows = load_rows(args.csv)
    except MalformedCSV as err:
        print(f"FILE CSV SAI CẤU TRÚC\n\n{err}", file=sys.stderr)
        return 1

    if args.command == "validate":
        return cmd_validate(rows, columns)
    if args.command == "stats":
        return cmd_stats(rows)
    return cmd_table(rows, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
