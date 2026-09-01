"""[CD1.1] Dựng khung cuốn Chuyên đề 1 và file mẫu định dạng.

Sinh ra hai file trong chuyende1/report/:
  reference.docx                  — mẫu định dạng: trưng bày từng style kèm tên
  ChuyenDe1_NguyenMinhTrong.docx  — khung rỗng đủ bìa + trang đầu + 6 chương

Nguồn cấu trúc: pLan/chuyende1/OUTLINE_BAOCAO_CD1.md
Nguồn định dạng: scripts/ute_docx.py

CHỐNG GHI ĐÈ NỘI DUNG ĐÃ SỬA TAY [REQ-006]
-------------------------------------------
Chạy lại script này AN TOÀN — nó tự phát hiện file đã bị sửa tay (so với lần
chính script này ghi gần nhất) và TỪ CHỐI ghi đè, thay vì âm thầm mất nội dung.
Cơ chế: sau mỗi lần ghi, lưu "dấu vân tay nội dung" vào `.generated.json` cùng
thư mục. Lần chạy sau so dấu vân tay hiện tại của file với dấu đã lưu.

  python scripts/build_cd1_report.py                 # an toàn: chặn nếu đã sửa tay
  python scripts/build_cd1_report.py --adopt          # "tôi đã sửa tay, đừng đụng vào nữa"
  python scripts/build_cd1_report.py --force           # ghi đè bằng bản mới (tự sao lưu trước)

Chi tiết cơ chế: xem `sync_generated_file()` bên dưới và
`chuyende1/notes/CD1.2b_chong-ghi-de-report.md`.

Dùng:
    python scripts/build_cd1_report.py [thư_mục_đích] [--force | --adopt]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.path.insert(0, str(Path(__file__).parent))

from ute_docx import (  # noqa: E402
    FONT,
    SIZE,
    TABLE_TEXT_SIZE,
    add_caption,
    add_paragraph,
    add_todo,
    add_toc_field,
    content_fingerprint_of_document,
    content_fingerprint_of_file,
    new_document,
    new_section,
)

MANIFEST_NAME = ".generated.json"
NGUON_SINH = "sinh_tu_dong"   # dấu vân tay ứng với lần script tự ghi gần nhất
NGUON_SUA_TAY = "da_sua_tay"  # dấu vân tay được người dùng xác nhận qua --adopt

CENTER = WD_ALIGN_PARAGRAPH.CENTER

HOC_VIEN = "NGUYỄN MINH TRỘNG"
MSHV = "2611326"
GVHD = "TS. PHAN THỊ HUYỀN TRANG"
NGANH = "KHOA HỌC MÁY TÍNH"
MA_SO = "8480101"

# Tên đề tài CHÍNH THỨC, chép nguyên văn từ bản đã được GVHD duyệt:
#   docs/Tom_Tat_Dinh_Huong_Final.docx — mục "Tên chuyên đề"
# KHÔNG tự đặt lại. Mẫu bìa (Phần III Phụ lục 1) yêu cầu đặt trong ngoặc kép.
HUONG_NGHIEN_CUU = (
    "Mạng Neuro-Symbolic đa đồ thị với mô hình hóa tường minh phủ định và chuyển ý "
    "cho phân loại cảm xúc theo khía cạnh tiếng Việt"
)
HUONG_NGHIEN_CUU_EN = (
    "A Neuro-Symbolic Multi-Graph Network with Explicit Modeling of Negation "
    "and Contrast for Vietnamese Aspect-Category Sentiment Analysis"
)
KHOA = "2026A"

# --- Cấu trúc cuốn báo cáo ----------------------------------------------------
# (tiêu đề chương, ngân sách trang, [(tiêu đề mục, việc cần điền), ...])

CHUONG: list[tuple[str, int, list[tuple[str, str]]]] = [
    (
        "Chương 1. TỔNG QUAN",
        4,
        [
            ("1.1. Đặt vấn đề", "CD1.12a — nhu cầu phân tích phản hồi khách hàng tiếng Việt; vì sao phân loại cảm xúc mức tài liệu không đủ, phải xuống mức khía cạnh"),
            ("1.2. Tình hình nghiên cứu trong và ngoài nước", "CD1.12a — tóm tắt 1 trang, chi tiết để ở Chương 3; nêu vấn đề khoa học còn tồn tại"),
            ("1.3. Tính cấp thiết, ý nghĩa khoa học và thực tiễn", "CD1.12a — bắt buộc theo Phần I mục 2 của quy định UTE"),
            ("1.4. Mục tiêu nghiên cứu", "CD1.12a — 4 mục tiêu tương ứng 4 nhiệm vụ: khảo sát / thực nghiệm / so sánh / tìm hạn chế và định hướng. Mục 6.1 sẽ đối chiếu ngược lại từng mục tiêu"),
            ("1.5. Đối tượng và phạm vi nghiên cứu", "CD1.12a — đối tượng: ACSA tiếng Việt. Phạm vi: UIT-ViSFD, 3 nhãn, 4 mô hình, tập chẩn đoán 300 câu. NÓI RÕ CÁI KHÔNG LÀM: không cross-domain, không cài mô hình mới"),
            ("1.6. Phương pháp nghiên cứu", "CD1.12a — khảo sát có hệ thống + thực nghiệm có kiểm soát (cùng split, cùng ngân sách tinh chỉnh, 3 seed) + phân tích lỗi định lượng"),
            ("1.7. Cấu trúc của chuyên đề", "CD1.12a — 1 đoạn"),
        ],
    ),
    (
        "Chương 2. CƠ SỞ LÝ THUYẾT",
        5,
        [
            ("2.1. Bài toán ABSA và các biến thể", "CD1.12a — ATSC / ACSA / E2E-ABSA; định nghĩa hình thức cặp (câu, khía cạnh) -> nhãn thuộc {POS, NEU, NEG}"),
            ("2.2. Mô hình ngôn ngữ tiền huấn luyện", "CD1.12a — Transformer, self-attention (1 hình), PhoBERT và vai trò tách từ tiếng Việt, ViSoBERT/XLM-R"),
            ("2.3. Mạng nơ-ron trên đồ thị", "CD1.12a — cây phụ thuộc, công thức truyền tin GCN và GAT (2 công thức), vì sao cú pháp có ích cho ABSA"),
            ("2.4. Tri thức cảm xúc bên ngoài", "CD1.12a — SenticNet và ý tưởng của Sentic-GCN; nêu vấn đề thiếu tài nguyên tương đương cho tiếng Việt (xem GAP-002)"),
            ("2.5. Hiện tượng phủ định và chuyển ý trong tiếng Việt", "CD1.12a — 'không', 'chẳng', 'chưa', 'nhưng', 'tuy nhiên', 'mặc dù'; khái niệm PHẠM VI của từ phủ định. Mục này là nền cho Chương 5, đừng bỏ"),
            ("2.6. Độ đo đánh giá", "CD1.12a — accuracy, F1 từng lớp, macro-F1; VÌ SAO chọn macro-F1 khi dữ liệu lệch lớp; paired bootstrap; Cohen's kappa"),
        ],
    ),
    (
        "Chương 3. KHẢO SÁT CÁC PHƯƠNG PHÁP TIÊN TIẾN",
        7,
        [
            ("3.1. Giao thức khảo sát", "CD1.2 — nguồn, từ khoá, tiêu chí nhận/loại, số lượng. Kèm sơ đồ luồng sàng lọc N1->N2->N3->N4. Số lấy từ chuyende1/survey/survey_protocol.md"),
            ("3.2. Đặc trưng thủ công và học máy cổ điển", "CD1.2 — SVM, CRF; ~0,8 trang"),
            ("3.3. Mạng nơ-ron tuần tự và cơ chế attention", "CD1.2 — ATAE-LSTM, IAN, MemNet, RAM; ~0,8 trang"),
            ("3.4. Mô hình ngôn ngữ tiền huấn luyện", "CD1.2 — BERT-SPC, PhoBERT, ViSoBERT, XLM-R, BARTpho; ~0,8 trang"),
            ("3.5. Mạng nơ-ron đồ thị", "CD1.2 — ASGCN, Sentic-GCN, DualGCN, SSEGCN, kumaGCN; ~0,8 trang"),
            ("3.6. Phương pháp sinh và prompting", "CD1.2 — generative ABSA, InstructABSA, LLM zero/few-shot; ~0,8 trang"),
            ("3.7. Kết hợp nơ-ron và ký hiệu (neuro-symbolic)", "CD1.2 — SenticNet, luật ngôn ngữ, ràng buộc logic. ĐÂY LÀ NHÓM THƯA NHẤT cho tiếng Việt — chỗ đứng của Chuyên đề 2"),
            ("3.8. Nghiên cứu ABSA cho tiếng Việt", "CD1.2 — tập dữ liệu (UIT-ViSFD, VLSP 2018, UIT-ViSD4SA), mô hình đã áp dụng, kết quả đã công bố; ~1 trang + bảng"),
            ("3.9. Bảng tổng hợp so sánh", "CD1.2 — trích từ chuyende1/survey/survey_matrix.csv. Được phép để khổ ngang, cỡ chữ tối thiểu 10"),
            ("3.10. Khoảng trống nghiên cứu", "CD1.2 — >= 3 khoảng trống, mỗi cái trỏ về >= 2 dòng cụ thể của bảng 3.9. Nguồn: chuyende1/survey/gap_analysis.md"),
        ],
    ),
    (
        "Chương 4. THỰC NGHIỆM VÀ SO SÁNH CÁC MÔ HÌNH",
        8,
        [
            ("4.1. Tập dữ liệu", "CD1.12a — UIT-ViSFD: nguồn gốc, số câu/số mẫu theo split, phân bố nhãn và khía cạnh (1 bảng + 1 biểu đồ). Tập chẩn đoán 300 câu: cách xây, kappa"),
            ("4.2. Giao thức thực nghiệm", "CD1.12a — MỤC QUAN TRỌNG NHẤT VỀ PHƯƠNG PHÁP LUẬN. Split cố định, tiền xử lý, max_len, 3 seed, cách chọn checkpoint, NGÂN SÁCH TINH CHỈNH BẰNG NHAU, phần cứng. Định nghĩa riêng 'seed' cho baseline không huấn luyện (xem GAP-003)"),
            ("4.3. Bốn mô hình được thực nghiệm", "CD1.4-CD1.7 — mỗi mô hình ~0,5 trang: kiến trúc, siêu tham số, số tham số, NGUỒN CÀI ĐẶT (tự cài / thư viện nào / checkpoint nào). Với Sentic-GCN: ghi độ phủ từ điển cảm xúc (GAP-002)"),
            ("4.4. Kết quả chính", "CD1.10 — bảng accuracy / macro-F1 / F1 từng lớp, mean ± std trên 3 seed, kèm cột p-value. Bảng sinh từ scripts/compare_baselines.py, KHÔNG gõ tay"),
            ("4.5. Chi phí tính toán", "CD1.10 — số tham số / thời gian huấn luyện / thời gian suy luận / VRAM đỉnh, từ results/cost_profile.json + biểu đồ đánh đổi"),
            ("4.6. Kết quả trên tập chẩn đoán", "CD1.9 — macro-F1 theo 3 nhóm phủ định / chuyển ý / thường"),
            ("4.7. Nhận xét và đánh giá", "CD1.10 — trả lời trực tiếp: mô hình nào tốt nhất, tốt hơn CÓ Ý NGHĨA THỐNG KÊ không, đắt hơn bao nhiêu, đánh đổi ra sao. Không né kết luận"),
        ],
    ),
    (
        "Chương 5. PHÂN TÍCH HẠN CHẾ VÀ ĐỊNH HƯỚNG CẢI TIẾN",
        4,
        [
            ("5.1. Phân tích lỗi", "CD1.9 — 6 lát cắt, mỗi lát cắt 1 bảng hoặc 1 hình + 2-3 câu nhận xét. Lát cắt quan trọng nhất: các câu CẢ 4 MÔ HÌNH CÙNG SAI"),
            ("5.2. Các hạn chế được phát hiện", "CD1.9 — 4-6 hạn chế, mỗi cái viết theo khung 4 phần [Hiện tượng] [Phạm vi] [Nguyên nhân] [Hệ quả], xem PLAN_CHUYENDE1.md mục 7. MỖI HẠN CHẾ PHẢI KÈM MỘT CON SỐ"),
            ("5.3. Các ca điển hình", "CD1.9 — 4-6 câu thật từ UIT-ViSFD mà cả 4 mô hình cùng sai, kèm nhãn vàng, 4 dự đoán, 1 câu giải thích"),
            ("5.4. Thí nghiệm thăm dò hướng cải tiến", "CD1.11 — P1 (trần oracle phủ định), P2 (độ chính xác luật thô), P3 (giá trị của cú pháp); nguồn results/probe_results.json"),
            ("5.5. Định hướng đề xuất", "CD1.11 — phát biểu hướng NS-MGAT ở mức ý tưởng, lý do chọn dựa trên 5.2 + 5.4. KHÔNG sa vào chi tiết cài đặt, đó là Chuyên đề 2"),
        ],
    ),
    (
        "Chương 6. KẾT LUẬN VÀ KẾ HOẠCH CHUYÊN ĐỀ 2",
        2,
        [
            ("6.1. Các kết quả đạt được", "CD1.12a — đối chiếu THẲNG với 4 mục tiêu ở mục 1.4, từng mục một"),
            ("6.2. Hạn chế của Chuyên đề 1", "CD1.12a — trung thực: chỉ 1 tập dữ liệu, tập chẩn đoán do một người gán, LLM không tái lập tuyệt đối, chưa cross-domain. NGUỒN CÓ SẴN: chuyende1/gaps/INDEX.md"),
            ("6.3. Kế hoạch Chuyên đề 2", "CD1.12a — bảng mốc theo tuần trích Stage S2->S5 của PLAN_NSMGAT.md, kèm sản phẩm dự kiến và tiêu chí thành công. HỘI ĐỒNG DÙNG MỤC NÀY ĐỂ CHẤM TIẾN ĐỘ"),
        ],
    ),
]

VIET_TAT = [
    ("ABSA", "Aspect-Based Sentiment Analysis — Phân tích cảm xúc theo khía cạnh"),
    ("ACSA", "Aspect-Category Sentiment Analysis — Phân tích cảm xúc theo phạm trù khía cạnh"),
    ("GAT", "Graph Attention Network — Mạng attention trên đồ thị"),
    ("GCN", "Graph Convolutional Network — Mạng tích chập trên đồ thị"),
    ("GNN", "Graph Neural Network — Mạng nơ-ron trên đồ thị"),
    ("LLM", "Large Language Model — Mô hình ngôn ngữ lớn"),
    ("PLM", "Pre-trained Language Model — Mô hình ngôn ngữ tiền huấn luyện"),
    ("NEG / NEU / POS", "Nhãn cảm xúc tiêu cực / trung tính / tích cực"),
    ("UIT-ViSFD", "Vietnamese Smartphone Feedback Dataset"),
    ("VnCoreNLP", "Bộ công cụ xử lý ngôn ngữ tiếng Việt (tách từ, gán nhãn từ loại, phân tích phụ thuộc)"),
]

IEEE_MAU = [
    ("Sách", "[1] Tác giả. Tên sách. Nhà xuất bản, năm, trang."),
    ("Tạp chí", "[2] Tác giả. Tên bài báo. Tên tạp chí, số, trang, năm."),
    ("Hội nghị", "[3] Tác giả. Tên bài báo. Tên hội thảo, năm, trang."),
    ("Internet", "[4] Tác giả. Tên bài. Internet: <địa chỉ đầy đủ>, ngày truy cập."),
]

PHU_LUC = [
    ("Phụ lục A. Ma trận khảo sát đầy đủ", "CD1.2 — trích chuyende1/survey/survey_matrix.csv"),
    ("Phụ lục B. Hướng dẫn chú thích tập chẩn đoán", "CD1.8b — trích docs/annotation_guideline.md"),
    ("Phụ lục C. Câu lệnh dùng cho baseline LLM", "CD1.7 — toàn văn prompt, tên model, phiên bản, ngày gọi API"),
    ("Phụ lục D. Cấu hình của bốn thí nghiệm", "CD1.4-CD1.7 — 4 file YAML trong configs/"),
    ("Phụ lục E. Hướng dẫn tái lập", "CD1.12b — lệnh chạy scripts/reproduce.sh và yêu cầu phần cứng"),
]


# --- Bìa ----------------------------------------------------------------------


def build_cover(doc) -> None:
    """Bìa theo Phần III Phụ lục 1 của quy định UTE."""
    for text in ("BỘ GIÁO DỤC VÀ ĐÀO TẠO", "TRƯỜNG ĐẠI HỌC CÔNG NGHỆ KỸ THUẬT", "THÀNH PHỐ HỒ CHÍ MINH"):
        add_paragraph(doc, text, align=CENTER, bold=(text != "BỘ GIÁO DỤC VÀ ĐÀO TẠO"))

    for _ in range(4):
        add_paragraph(doc)

    para = add_paragraph(doc, f"“{HUONG_NGHIEN_CUU}”", align=CENTER, bold=True)
    para.runs[0].font.size = SIZE
    add_paragraph(doc, f"({HUONG_NGHIEN_CUU_EN})", align=CENTER, italic=True)

    for _ in range(3):
        add_paragraph(doc)

    add_paragraph(doc, f"NGÀNH: {NGANH}", align=CENTER, bold=True)
    add_paragraph(doc, f"MÃ SỐ: {MA_SO}", align=CENTER, bold=True)

    for _ in range(3):
        add_paragraph(doc)

    add_paragraph(doc, "CHUYÊN ĐỀ", align=CENTER, bold=True)

    for _ in range(4):
        add_paragraph(doc)

    add_paragraph(doc, f"Học viên: {HOC_VIEN} — MSHV {MSHV} — Khoá {KHOA}", align=CENTER)
    add_paragraph(doc, f"Giảng viên hướng dẫn: {GVHD}", align=CENTER)

    for _ in range(4):
        add_paragraph(doc)

    add_paragraph(doc, "Tp. Hồ Chí Minh, tháng ...... năm 2026", align=CENTER)
    add_todo(doc, "CD1.1 — điền tháng bảo vệ sau khi GVHD chốt hạn nộp").alignment = CENTER


# --- Trang đầu (đánh số La Mã thường) -----------------------------------------


def build_front_matter(doc) -> None:
    new_section(doc, fmt="lowerRoman", start=1)

    doc.add_paragraph("LỜI CẢM ƠN", style="Heading 1").alignment = CENTER
    add_todo(doc, "CD1.12b — ngắn gọn, không quá 1 trang")

    doc.add_paragraph("TÓM TẮT", style="Heading 1").alignment = CENTER
    add_todo(
        doc,
        "CD1.12b — VIẾT SAU CÙNG, khoảng 1 trang. Người đọc phải hiểu được nội dung chính "
        "mà không cần đọc cả cuốn. Kiểm tra: mọi con số ở đây phải khớp với Chương 4",
    )

    doc.add_paragraph("MỤC LỤC", style="Heading 1").alignment = CENTER
    add_toc_field(doc)
    add_todo(
        doc,
        "Mục lục tự động: mở file trong Word, bấm Ctrl+A rồi F9, chọn "
        "'Update entire table'. Trước khi cập nhật, chỗ này hiện dòng nhắc là bình thường",
    )

    doc.add_paragraph("DANH SÁCH CÁC CHỮ VIẾT TẮT", style="Heading 1").alignment = CENTER
    table = doc.add_table(rows=len(VIET_TAT) + 1, cols=2)
    table.style = "Table Grid"
    for row_idx, (short, full) in enumerate([("Chữ viết tắt", "Diễn giải")] + VIET_TAT):
        for col_idx, text in enumerate((short, full)):
            para = table.cell(row_idx, col_idx).paragraphs[0]
            run = para.add_run(text)
            run.font.name = FONT
            run.font.size = TABLE_TEXT_SIZE
            run.bold = row_idx == 0
    add_todo(doc, "CD1.12b — bổ sung các chữ viết tắt phát sinh khi viết")

    doc.add_paragraph("DANH SÁCH CÁC BẢNG", style="Heading 1").alignment = CENTER
    add_todo(
        doc,
        "CD1.12b — liệt kê 'Bảng x.y: tên bảng ..... trang'. Trong Word: References > "
        "Insert Table of Figures, chọn nhãn 'Bảng'",
    )

    doc.add_paragraph("DANH SÁCH CÁC HÌNH", style="Heading 1").alignment = CENTER
    add_todo(doc, "CD1.12b — tương tự, chọn nhãn 'Hình'")


# --- Phần chính (đánh số Ả Rập) -----------------------------------------------


def build_main_matter(doc) -> None:
    new_section(doc, fmt="decimal", start=1)

    for idx, (title, pages, sections) in enumerate(CHUONG):
        if idx > 0:
            doc.add_page_break()
        doc.add_paragraph(title, style="Heading 1")
        add_paragraph(doc, f"(Ngân sách: khoảng {pages} trang)", italic=True)

        for sec_title, todo in sections:
            doc.add_paragraph(sec_title, style="Heading 2")
            add_todo(doc, todo)

            # Minh hoạ quy ước đánh số bảng/hình một lần, ở đúng chỗ sẽ dùng
            if sec_title.startswith("4.4."):
                add_caption(doc, "Bảng 4.1: Kết quả chính của bốn mô hình trên tập kiểm tra")
                add_todo(doc, "CD1.10 — tên BẢNG đặt TRÊN bảng (Phần I mục 3). Dán bảng ngay dưới dòng này")
            if sec_title.startswith("3.1."):
                add_todo(doc, "CD1.2 — chèn sơ đồ luồng sàng lọc ngay dưới dòng này")
                add_caption(doc, "Hình 3.1: Sơ đồ quy trình sàng lọc tài liệu khảo sát")
                add_todo(doc, "CD1.2 — tên HÌNH đặt DƯỚI hình (Phần I mục 3)")

    doc.add_page_break()
    doc.add_paragraph("TÀI LIỆU THAM KHẢO", style="Heading 1")
    add_paragraph(
        doc,
        "Trích dẫn theo chuẩn IEEE: đánh số theo thứ tự xuất hiện lần đầu trong bài, "
        "trích dẫn trong văn bản bằng [1], [2], ... Bốn dạng thường dùng:",
    )
    for kind, sample in IEEE_MAU:
        add_paragraph(doc, f"{kind}: {sample}", italic=True)
    add_todo(
        doc,
        "CD1.12a — điền danh mục đầy đủ. Kiểm tra chéo: mọi [n] trong bài có mục tương ứng "
        "ở đây và ngược lại; không còn [CẦN TÌM: ...]",
    )

    doc.add_page_break()
    doc.add_paragraph("PHỤ LỤC", style="Heading 1")
    add_paragraph(doc, "Phụ lục không tính vào khoảng 30 trang của phần chính.", italic=True)
    for title, todo in PHU_LUC:
        doc.add_paragraph(title, style="Heading 2")
        add_todo(doc, todo)


# --- File mẫu định dạng -------------------------------------------------------


def build_reference_doc() -> DocumentType:
    """reference.docx — trưng bày từng style kèm tên, để đối chiếu bằng mắt.

    Chỉ dựng nội dung trong bộ nhớ, KHÔNG lưu ra đĩa — để sync_generated_file()
    có thể so dấu vân tay TRƯỚC KHI quyết định có ghi đè hay không.
    """
    doc = new_document()
    new_section(doc, fmt="decimal", start=1)

    doc.add_paragraph("MẪU ĐỊNH DẠNG THEO QUY ĐỊNH UTE", style="Heading 1")
    add_paragraph(
        doc,
        "File này không phải nội dung báo cáo. Nó trưng bày từng kiểu định dạng kèm tên style "
        "trong Word, để đối chiếu khi gõ bài và để dùng làm mẫu khi tạo tài liệu mới.",
    )

    doc.add_paragraph("Thông số bắt buộc", style="Heading 2")
    specs = [
        ("Khổ giấy", "A4, in một mặt"),
        ("Phông chữ", "Times New Roman, cỡ 13 — MỘT kiểu phông cho toàn cuốn"),
        ("Giãn dòng", "1,5"),
        ("Lề trái", "3,5 cm"),
        ("Lề phải", "2,0 cm"),
        ("Lề trên", "3,0 cm"),
        ("Lề dưới", "3,5 cm"),
        ("Số trang", "giữa lề dưới; trang bìa không đánh số"),
        ("Đánh số trang", "trước Chương 1 dùng i, ii, iii; từ Chương 1 dùng 1, 2, 3"),
        ("Trích dẫn", "IEEE — đánh số theo thứ tự xuất hiện"),
    ]
    table = doc.add_table(rows=len(specs), cols=2)
    table.style = "Table Grid"
    for row_idx, (key, value) in enumerate(specs):
        for col_idx, text in enumerate((key, value)):
            run = table.cell(row_idx, col_idx).paragraphs[0].add_run(text)
            run.font.name = FONT
            run.font.size = TABLE_TEXT_SIZE
            run.bold = col_idx == 0
    doc.add_paragraph()

    doc.add_paragraph("Tiêu đề cấp 1 — style 'Heading 1'", style="Heading 1")
    doc.add_paragraph("Tiêu đề cấp 2 — style 'Heading 2'", style="Heading 2")
    doc.add_paragraph("Tiêu đề cấp 3 — style 'Heading 3'", style="Heading 3")
    add_paragraph(
        doc,
        "Đoạn thân bài dùng style 'Normal'. Chỉ ba cấp tiêu đề trên được đưa vào mục lục "
        "tự động, nên đừng tự tạo tiêu đề bằng cách bôi đậm chữ thường — mục lục sẽ bỏ sót.",
    )

    doc.add_paragraph("Quy ước bảng và hình", style="Heading 2")
    add_paragraph(
        doc,
        "Phần I mục 3: tên BẢNG đặt PHÍA TRÊN thân bảng; tên HÌNH đặt PHÍA DƯỚI hình. "
        "Số thứ tự phản ánh số chương.",
    )
    add_caption(doc, "Bảng 2.1: Ví dụ chú thích bảng — đặt TRÊN bảng, dùng style 'Caption'")
    demo = doc.add_table(rows=2, cols=3)
    demo.style = "Table Grid"
    for row_idx, row in enumerate((("Mô hình", "Macro-F1", "Ghi chú"), ("(ví dụ)", "--", "--"))):
        for col_idx, text in enumerate(row):
            run = demo.cell(row_idx, col_idx).paragraphs[0].add_run(text)
            run.font.name = FONT
            run.font.size = TABLE_TEXT_SIZE
            run.bold = row_idx == 0
    doc.add_paragraph()
    add_paragraph(doc, "[chỗ đặt hình]", align=CENTER, italic=True)
    add_caption(doc, "Hình 2.1: Ví dụ chú thích hình — đặt DƯỚI hình")

    doc.add_paragraph("Cách viết số", style="Heading 2")
    add_paragraph(doc, "Đúng: 85,3 %   |   18 – 25 km   |   15,8 cm", bold=True)
    add_paragraph(doc, "Sai:  85.3%    |   18-25km      |   15.8cm")
    add_paragraph(
        doc,
        "Phần I mục 4: số thập phân dùng dấu phẩy; khoảng giá trị cách nhau một ký tự trắng "
        "mỗi bên dấu gạch; giữa số và đơn vị có một khoảng trắng.",
    )

    add_todo(doc, "File mẫu — không cần điền gì, chỉ dùng để đối chiếu")
    return doc


def build_reference(path: Path) -> None:
    """Tương thích ngược cho test/gọi trực tiếp: dựng rồi lưu ngay, KHÔNG qua
    cơ chế chống ghi đè. Dùng `sync_generated_file()` nếu cần bảo vệ."""
    doc = build_reference_doc()
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))


# --- Điểm vào -----------------------------------------------------------------


def build_skeleton_doc() -> DocumentType:
    """Khung cuốn chuyên đề — chỉ dựng trong bộ nhớ, không lưu. Xem build_reference_doc()."""
    doc = new_document()
    build_cover(doc)
    build_front_matter(doc)
    build_main_matter(doc)
    return doc


def build_skeleton(path: Path) -> None:
    """Tương thích ngược — xem ghi chú ở build_reference()."""
    doc = build_skeleton_doc()
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))


# --- Cơ chế chống ghi đè nội dung đã sửa tay [REQ-006] ------------------------


def load_manifest(out_dir: Path) -> dict:
    path = out_dir / MANIFEST_NAME
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(out_dir: Path, manifest: dict) -> None:
    path = out_dir / MANIFEST_NAME
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _backup_path(target: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return target.with_name(f"{target.stem}.backup-{stamp}{target.suffix}")


def sync_generated_file(
    name: str,
    build_doc: Callable[[], DocumentType],
    out_dir: Path,
    manifest: dict,
    *,
    force: bool = False,
    adopt: bool = False,
) -> str:
    """Đồng bộ MỘT file sinh ra, có bảo vệ chống ghi đè nội dung đã sửa tay.

    Nguyên tắc: chỉ tự động ghi đè khi CHẮC CHẮN chưa ai đụng vào file kể từ lần
    chính script này ghi gần nhất — tức dấu vân tay hiện tại của file trên đĩa
    khớp với dấu vân tay đã ghi nhận VÀ dấu đó có nguồn là "sinh_tu_dong" (không
    phải "da_sua_tay" từ một lần --adopt trước đó — file đã adopt thì được bảo
    vệ vĩnh viễn cho tới khi người dùng chủ động --force).

    Trả về: "written" | "adopted" | "forced" | "blocked".
    """
    target = out_dir / name

    if not target.exists():
        doc = build_doc()
        fp = content_fingerprint_of_document(doc)
        target.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(target))
        manifest[name] = {"fingerprint": fp, "nguon": NGUON_SINH}
        return "written"

    current_fp = content_fingerprint_of_file(target)
    recorded = manifest.get(name)

    if adopt:
        manifest[name] = {"fingerprint": current_fp, "nguon": NGUON_SUA_TAY}
        return "adopted"

    if recorded is None:
        # Chưa từng ghi nhận gì về file này (vd. file có từ trước khi cơ chế
        # này tồn tại). Chỉ tự nhận làm mốc an toàn nếu nội dung hiện tại khớp
        # CHÍNH XÁC với những gì script sẽ sinh ra ngay bây giờ — tức chắc chắn
        # còn nguyên bản, chưa ai sửa gì.
        doc = build_doc()
        fresh_fp = content_fingerprint_of_document(doc)
        if current_fp == fresh_fp:
            # Nội dung đã khớp sẵn -> không cần ghi file, chỉ cần lập mốc.
            manifest[name] = {"fingerprint": fresh_fp, "nguon": NGUON_SINH}
            return "baseline"
        # Khác bản mới sinh mà lại không có ghi nhận -> không rõ nguồn gốc,
        # rơi xuống nhánh bảo vệ bên dưới.
    elif recorded.get("nguon") == NGUON_SINH and current_fp == recorded.get("fingerprint"):
        # An toàn: đúng là bản script ghi lần trước, chưa ai sửa tay.
        # Ghi đè bằng bản mới nhất của script (kể cả khi template đã đổi).
        doc = build_doc()
        fresh_fp = content_fingerprint_of_document(doc)
        target.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(target))
        manifest[name] = {"fingerprint": fresh_fp, "nguon": NGUON_SINH}
        return "written"

    # Còn lại: đã sửa tay (nguồn = da_sua_tay), hoặc lệch so với ghi nhận cũ.
    if force:
        backup = _backup_path(target)
        shutil.copy2(target, backup)
        doc = build_doc()
        fresh_fp = content_fingerprint_of_document(doc)
        doc.save(str(target))
        manifest[name] = {"fingerprint": fresh_fp, "nguon": NGUON_SINH}
        return "forced"

    return "blocked"


def sync_all(out_dir: Path, *, force: bool = False, adopt: bool = False) -> int:
    """Đồng bộ cả reference.docx và khung cuốn chuyên đề. Trả về mã thoát."""
    targets = [
        ("reference.docx", build_reference_doc),
        ("ChuyenDe1_NguyenMinhTrong.docx", build_skeleton_doc),
    ]

    manifest = load_manifest(out_dir)
    blocked = []
    locked = []

    try:
        for name, build_doc in targets:
            path = out_dir / name
            try:
                outcome = sync_generated_file(name, build_doc, out_dir, manifest, force=force, adopt=adopt)
            except PermissionError:
                # Gần như luôn là file đang mở trong Word (Word khoá ghi).
                # KHÔNG để exception thoát ra ngoài: nếu thoát, manifest sẽ không
                # được lưu và những file đã ghi thành công trước đó sẽ bị coi là
                # "đã sửa tay" ở lần chạy sau -> chặn oan.
                locked.append((name, path))
                print(f"ĐANG BỊ KHOÁ -> {path}")
                continue

            if outcome == "written":
                print(f"OK          -> {path}")
            elif outcome == "baseline":
                print(f"LẬP MỐC     -> {path}  (nội dung đã đúng bản chuẩn, không cần ghi lại)")
            elif outcome == "adopted":
                print(f"ĐÃ GHI NHẬN -> {path}  (từ nay được bảo vệ — không tự động ghi đè nữa)")
            elif outcome == "forced":
                print(f"GHI ĐÈ      -> {path}  (bản cũ đã sao lưu vào *.backup-*)")
            elif outcome == "blocked":
                blocked.append((name, path))
                print(f"BỊ CHẶN     -> {path}")
    finally:
        # Luôn lưu manifest, kể cả khi có file lỗi giữa chừng — nếu không, những
        # file đã ghi xong sẽ lệch với manifest và bị chặn oan ở lần chạy sau.
        save_manifest(out_dir, manifest)

    if locked:
        print()
        print(f"{len(locked)} file đang bị khoá ghi — thường là do đang mở trong Word:")
        for _, path in locked:
            print(f"  - {path}")
        print()
        print("Đóng file trong Word rồi chạy lại. Không có nội dung nào bị mất.")
        return 1

    if blocked:
        print()
        print(f"{len(blocked)} file có nội dung khác với lần sinh gần nhất — KHÔNG bị đụng vào:")
        for name, path in blocked:
            print(f"  - {path}")
        print()
        print("Đây thường là vì bạn đã sửa tay file trong Word. Chọn một trong hai:")
        print("  --adopt   giữ nguyên nội dung đã sửa, chỉ đánh dấu 'đây là bản chính thức'")
        print("            (từ nay công cụ này sẽ KHÔNG BAO GIỜ tự ghi đè file nữa)")
        print("  --force   ghi đè bằng bản khung mới nhất (bản cũ tự động được sao lưu)")
        return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("out_dir", nargs="?", default="chuyende1/report", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--force", action="store_true", help="Ghi đè kể cả đã sửa tay (tự sao lưu trước)")
    group.add_argument("--adopt", action="store_true", help="Nhận nội dung hiện tại làm bản chính thức, không ghi đè")
    args = parser.parse_args(argv)

    return sync_all(args.out_dir, force=args.force, adopt=args.adopt)


if __name__ == "__main__":
    raise SystemExit(main())
