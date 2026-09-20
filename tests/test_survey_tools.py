"""[CD1.2] Kiểm công cụ ma trận khảo sát.

Trọng tâm: chốt chặn chống bịa trích dẫn — dòng chưa kiểm chứng KHÔNG được lọt vào
Bảng 3.9 của cuốn báo cáo (quy tắc số 7 của repo, survey_protocol.md mục 7).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from survey_tools import (  # noqa: E402
    DEFAULT_CSV,
    METHOD_GROUPS,
    REQUIRED_COLUMNS,
    STATUS_CHUA_KIEM,
    STATUS_KIEM_URL,
    STATUS_TOAN_VAN,
    UNKNOWN,
    build_table_markdown,
    compute_stats,
    la_chu_thich,
    load_rows,
    main,
    validate,
)


def make_row(**overrides) -> dict[str, str]:
    """Một dòng hợp lệ, đã kiểm chứng, đủ mọi trường."""
    row = {col: "x" for col in REQUIRED_COLUMNS}
    row.update(
        ref_key="Bai-A",
        trang_thai=STATUS_KIEM_URL,
        ho_phuong_phap="G4_do_thi",
        bieu_dien_dau_vao="embedding_ngu_canh (BERT-base, subword)",
        co_dung_do_thi="co",
        loai_do_thi="cu_phap",
        co_tri_thuc_ngoai="khong",
        ngon_ngu="en",
        xu_ly_phu_dinh_chuyen_y="khong",
        co_giai_thich="khong",
        co_ma_nguon="co",
        nguon_url="https://example.org/bai-a",
    )
    row.update(overrides)
    return row


# --- File thật trong repo -----------------------------------------------------


def test_file_that_trong_repo_hop_le():
    rows = load_rows(DEFAULT_CSV)
    # utf-8-sig chứ không phải utf-8: `tu-excel` ghi lại file kèm BOM (cố ý, để
    # mở thẳng bằng Excel vẫn đúng tiếng Việt), nên sau một vòng Excel là có BOM.
    with DEFAULT_CSV.open(encoding="utf-8-sig", newline="") as fh:
        columns = next(csv.reader(fh))
    assert validate(rows, columns) == []
    assert len(rows) >= 20, "ma trận hạt giống phải có sẵn danh sách việc cần kiểm chứng"


def test_file_that_moi_dung_deu_chua_kiem_chung():
    """Chưa ai mở nguồn nào -> mọi dòng phải là chua_kiem. Nếu test này đỏ nghĩa là
    có dòng được đánh dấu đã kiểm chứng mà chưa thực sự kiểm — đúng thứ cần bắt."""
    rows = load_rows(DEFAULT_CSV)
    verified = [r for r in rows if r["trang_thai"] != STATUS_CHUA_KIEM]
    for row in verified:
        assert row["nguon_url"] and row["nguon_url"] != UNKNOWN, (
            f"{row['ref_key']}: đánh dấu đã kiểm chứng thì bắt buộc có nguon_url"
        )


def test_file_that_co_dong_mo_ta_va_vi_du_cho_moi_cot():
    """Hai dòng #MO_TA / #VI_DU nằm ngay trong CSV để tra khi đang điền. Chúng
    dễ bị xoá nhầm lúc sửa bằng Excel — test này canh."""
    rows = load_rows(DEFAULT_CSV)
    chu_thich = {r["ref_key"].split()[0]: r for r in rows if la_chu_thich(r)}
    assert "#MO_TA" in chu_thich and "#VI_DU" in chu_thich

    for col in REQUIRED_COLUMNS:
        assert chu_thich["#MO_TA"][col].strip(), f"cột {col} chưa có mô tả trong dòng #MO_TA"
    # Dòng ví dụ phải là dòng điền ĐÚNG, nếu không thì dạy người điền cách sai
    assert validate([{**chu_thich["#VI_DU"], "ref_key": "VI-DU"}], REQUIRED_COLUMNS) == []


def test_dong_chu_thich_khong_bi_tinh_la_cong_trinh():
    rows = [
        make_row(ref_key="A", trang_thai=STATUS_TOAN_VAN),
        {col: "nội dung mô tả bất kỳ" for col in REQUIRED_COLUMNS} | {"ref_key": "#MO_TA"},
    ]
    assert validate(rows, REQUIRED_COLUMNS) == [], "dòng # không bị soi giá trị hợp lệ"
    assert compute_stats(rows)["tong"] == 1
    assert "#MO_TA" not in build_table_markdown(rows)


# --- validate -----------------------------------------------------------------


def test_bat_trang_thai_khong_hop_le():
    errors = validate([make_row(trang_thai="da_doc_luot")], REQUIRED_COLUMNS)
    assert any("trang_thai" in e for e in errors)


def test_bat_nhom_phuong_phap_khong_hop_le():
    errors = validate([make_row(ho_phuong_phap="G9_khong_ton_tai")], REQUIRED_COLUMNS)
    assert any("ho_phuong_phap" in e for e in errors)


def test_bat_gia_tri_ngoai_tu_vung():
    """Cột có tập giá trị đóng thì phải khoá bằng code. Không khoá thì mỗi dòng
    một cách viết, tới lúc dựng Bảng 3.9 các ô không so được với nhau."""
    errors = validate([make_row(co_dung_do_thi="yes")], REQUIRED_COLUMNS)
    assert any("co_dung_do_thi" in e and "co | khong" in e for e in errors)


def test_bieu_dien_dau_vao_phai_bat_dau_bang_ma():
    """Lỗi thật đã xảy ra (GAP-016): ô ghi 'embedding + BiLSTM' — trộn biểu diễn
    đầu vào với kiến trúc mô hình, thứ thuộc cột ho_phuong_phap."""
    errors = validate([make_row(bieu_dien_dau_vao="embedding + BiLSTM")], REQUIRED_COLUMNS)
    assert any("bieu_dien_dau_vao" in e for e in errors)

    ok = validate([make_row(bieu_dien_dau_vao="embedding_tinh (fastText, mức từ)")], REQUIRED_COLUMNS)
    assert ok == [], "có mã đúng thì phần chi tiết trong ngoặc là tự do"


def test_bat_mau_thuan_khong_dung_do_thi_ma_van_ghi_loai():
    errors = validate(
        [make_row(co_dung_do_thi="khong", loai_do_thi="cu_phap")], REQUIRED_COLUMNS
    )
    assert any("loai_do_thi phải để trống" in e for e in errors)


def test_bat_ref_key_trung():
    errors = validate([make_row(), make_row()], REQUIRED_COLUMNS)
    assert any("trùng" in e for e in errors)


def test_bat_thieu_cot():
    errors = validate([], [c for c in REQUIRED_COLUMNS if c != "nguon_url"])
    assert any("Thiếu cột" in e for e in errors)


def test_bat_mau_thuan_da_kiem_chung_nhung_con_can_tim():
    """Đánh dấu đã kiểm chứng mà trường vẫn là [CẦN TÌM] là mâu thuẫn nội tại."""
    errors = validate([make_row(nam=UNKNOWN)], REQUIRED_COLUMNS)
    assert any(UNKNOWN in e for e in errors)


def test_bat_da_kiem_chung_nhung_thieu_url():
    errors = validate([make_row(nguon_url="")], REQUIRED_COLUMNS)
    assert any("nguon_url" in e for e in errors)


def test_dong_chua_kiem_duoc_phep_con_can_tim():
    """Ngược lại: dòng chua_kiem thì [CẦN TÌM] là bình thường, không phải lỗi."""
    row = make_row(trang_thai=STATUS_CHUA_KIEM, nam=UNKNOWN, nguon_url=UNKNOWN)
    assert validate([row], REQUIRED_COLUMNS) == []


# --- stats --------------------------------------------------------------------


def test_stats_dem_dung():
    rows = [
        make_row(ref_key="A", trang_thai=STATUS_TOAN_VAN),
        make_row(ref_key="B", trang_thai=STATUS_KIEM_URL),
        make_row(ref_key="C", trang_thai=STATUS_CHUA_KIEM, nam=UNKNOWN, nguon_url=UNKNOWN),
        make_row(ref_key="D", ho_phuong_phap="TAI_NGUYEN"),
    ]
    stats = compute_stats(rows)
    assert stats["tong"] == 4
    assert stats["tong_phuong_phap"] == 3, "TAI_NGUYEN không tính vào nhóm phương pháp"
    assert stats["da_kiem_chung"] == 3
    assert stats["n5"] == 1, "N5 chỉ đếm dòng đã đọc toàn văn"


def test_stats_phu_du_sau_nhom():
    stats = compute_stats([make_row(ref_key=g, ho_phuong_phap=g) for g in METHOD_GROUPS])
    for group in METHOD_GROUPS:
        assert stats["theo_nhom"][group] == 1


# --- table: chốt chặn chống bịa trích dẫn ------------------------------------


def test_bang_chi_lay_dong_da_kiem_chung():
    rows = [
        make_row(ref_key="DaKiem"),
        make_row(ref_key="ChuaKiem", trang_thai=STATUS_CHUA_KIEM, nam=UNKNOWN, nguon_url=UNKNOWN),
    ]
    table = build_table_markdown(rows)
    assert "DaKiem" in table
    assert "ChuaKiem" not in table, "dòng chưa kiểm chứng lọt vào bảng của báo cáo"
    assert "1 dòng còn `chua_kiem` đã bị loại" in table


def test_table_tu_choi_khi_chua_co_dong_nao_kiem_chung(tmp_path, capsys):
    """Ma trận mà chưa dòng nào được kiểm chứng thì lệnh phải thoát khác 0.

    Dựng file tạm toàn `chua_kiem` thay vì dùng file thật: file thật rồi sẽ có
    dòng đã kiểm chứng, và khi đó test này mất ý nghĩa nếu bám vào nó."""
    with DEFAULT_CSV.open(encoding="utf-8-sig", newline="") as fh:
        header, *rows = list(csv.reader(fh))
    i = header.index("trang_thai")
    for row in rows:
        row[i] = STATUS_CHUA_KIEM
    toan_chua_kiem = tmp_path / "chua_kiem.csv"
    with toan_chua_kiem.open("w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh).writerows([header, *rows])

    code = main(["table", "--csv", str(toan_chua_kiem), "-o", str(tmp_path / "bang.md")])
    assert code == 1
    assert not (tmp_path / "bang.md").exists(), "không được ghi file bảng khi chưa kiểm chứng"
    assert "CHƯA SINH ĐƯỢC BẢNG" in capsys.readouterr().err


def test_table_sinh_duoc_khi_da_co_dong_kiem_chung(tmp_path):
    csv_path = tmp_path / "m.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerow(make_row(ref_key="Bai-Da-Kiem"))

    out = tmp_path / "bang.md"
    assert main(["table", "--csv", str(csv_path), "-o", str(out)]) == 0
    assert "Bai-Da-Kiem" in out.read_text(encoding="utf-8")


def test_validate_qua_cli_tren_file_that():
    assert main(["validate", "--csv", str(DEFAULT_CSV)]) == 0


@pytest.mark.parametrize("command", ["validate", "stats"])
def test_cli_bao_loi_khi_khong_thay_file(command, tmp_path, capsys):
    assert main([command, "--csv", str(tmp_path / "khong_ton_tai.csv")]) == 1
    assert "Không thấy file" in capsys.readouterr().err


# --- CSV sai cấu trúc: phải báo rõ, không được crash -------------------------


def test_csv_sai_so_cot_thi_bao_loi_ro_rang(tmp_path):
    """Lỗi thật gặp 02/09/2026: thêm ghi chú có dấu phẩy mà không đặt trong
    dấu nháy -> dòng thừa cột. Trước đây `validate` crash với traceback thay vì
    chỉ ra dòng nào sai. Học viên sẽ sửa file này bằng tay nên phải báo rõ."""
    from survey_tools import MalformedCSV

    csv_path = tmp_path / "hong.csv"
    csv_path.write_text(
        ",".join(REQUIRED_COLUMNS) + "\n" + "A,chua_kiem" + ",x" * (len(REQUIRED_COLUMNS) - 1) + ",thua\n",
        encoding="utf-8",
    )

    with pytest.raises(MalformedCSV) as err:
        load_rows(csv_path)
    assert "Dòng 2" in str(err.value)
    assert "dấu phẩy" in str(err.value)


def test_cli_bao_loi_csv_hong_thay_vi_crash(tmp_path, capsys):
    csv_path = tmp_path / "hong.csv"
    csv_path.write_text(
        ",".join(REQUIRED_COLUMNS) + "\n" + "A,chua_kiem" + ",x" * (len(REQUIRED_COLUMNS) - 1) + ",thua\n",
        encoding="utf-8",
    )

    assert main(["validate", "--csv", str(csv_path)]) == 1
    assert "SAI CẤU TRÚC" in capsys.readouterr().err
