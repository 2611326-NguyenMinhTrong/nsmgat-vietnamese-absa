"""[CD1.12] Đối chiếu Chương 6 (bản chính) với các chương mà nó tóm lại.

Chương 6 không đưa số liệu mới: mỗi nhận định ở mục 6.1 và 6.2 là kết luận đã có ở Chương 3, 4 hoặc 5, mỗi việc ở mục 6.3
lấy từ hướng đề xuất ở mục 5.6, và số liệu của các chương đó đã có công cụ kiểm riêng (doi_chieu_chuong4.py,
doi_chieu_chuong5.py). Công cụ này kiểm ba điều:

1. Dẫn chiếu: mỗi câu của Chương 6 trong bảng DAN_CHIEU phải còn trong Chương 6, và câu làm chứng của nó phải còn trong
   chương nguồn. Chương nguồn đổi câu làm chứng (ví dụ khi có kết quả GPT-4o, dòng [TODO] ở mục 4.4 mất đi) thì câu tương ứng
   của Chương 6 bị báo để viết lại.
2. Một nhận định tính lại từ kết quả: ở các mô hình dùng PhoBERT, phần lớn lỗi có lớp trung tính ở một đầu và nằm ở bình
   luận trái nhãn, còn lỗi ngược cực chỉ là phần nhỏ.
3. Quét số: ngoài số mục, số chương, khoá trích dẫn và số thứ tự đầu dòng, chương không được có con số nào. Từ 24/10/2026
   mục 6.3 chỉ nêu các việc sẽ làm, không có lịch theo tuần (học viên bỏ Bảng 6.1), nên một bảng lịch thêm lại cũng bị báo.

    python scripts/doi_chieu_chuong6.py

Mã thoát 0 khi mọi chỗ đều khớp, 1 khi có chỗ lệch.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NHAP_MAC_DINH = Path("chuyende1/report/nhap_rut_gon")
TEP_C6 = "Chuong6_KetLuan.md"
C3, C4, C5 = "Chuong3_KhaoSat.md", "Chuong4_ThucNghiem.md", "Chuong5_HanCheVaDinhHuong.md"
MANH = ("phobert", "asgcn", "asgcn_linked", "senticgcn")

# (mô tả, cụm chữ phải có trong Chương 6, chương nguồn, cụm chữ làm chứng phải có trong chương nguồn)
DAN_CHIEU: Tuple[Tuple[str, str, str, str], ...] = (
    ("6.1, khảo sát có chọn lọc", "Đây là một khảo sát có chọn lọc chứ không phải một tổng quan hệ thống", C3,
     "đây là một khảo sát có chọn lọc chứ không phải một tổng quan hệ thống"),
    ("6.1, bốn khoảng trống", "rút ra bốn khoảng trống nghiên cứu", C3, "có thể xác định bốn khoảng trống"),
    ("6.1, năm seed", "mỗi mô hình được huấn luyện năm lần với năm seed", C4, "Mỗi mô hình được huấn luyện năm lần với năm seed"),
    ("6.1, hai mô hình đối chứng", "cùng hai mô hình đối chứng", C4, "Ngoài ra có hai mô hình đối chứng"),
    ("6.1, tính lại từ file", "mọi kết quả thực nghiệm trong Chương 4 và Chương 5 được tính lại từ kết quả và dự đoán đã lưu", C4,
     "mọi con số trong chương được tính lại từ các file này"),
    ("6.1, GPT-4o chưa có kết quả", "Mốc tham chiếu GPT-4o đã có phương pháp và công cụ nhưng chưa có kết quả", C4,
     "[TODO: kết quả của GPT-4o"),
    ("6.1, ba mô hình ngang nhau", "PhoBERT tinh chỉnh, Sentic-GCN và ASGCN nối câu ngang nhau", C4,
     "PhoBERT tinh chỉnh, Sentic-GCN và ASGCN nối câu được coi là ngang nhau"),
    ("6.1, tiền huấn luyện", "Tri thức tiền huấn luyện đem lại mức tăng lớn nhất trong các bậc có nhìn khía cạnh", C4,
     "tri thức tiền huấn luyện đem lại mức tăng lớn nhất trong các bậc có nhìn khía cạnh"),
    ("6.1, đồ thị không có lợi ích đo được", "không thành phần đồ thị nào cho lợi ích đo được", C4,
     "không thành phần đồ thị nào cho lợi ích đo được"),
    ("6.1, thời gian suy luận", "làm thời gian suy luận tăng rõ", C4, "Thời gian suy luận thì tăng rõ"),
    ("6.1, cách đọc ra", "chỉ phần do đổi cách đọc ra là vượt được dao động giữa các lần huấn luyện lại", C4,
     "chỉ phần do đổi cách đọc ra là vượt được dao động giữa các lần huấn luyện lại"),
    ("6.1, chuyển ý khó hơn", "mẫu có chuyển ý khó hơn mẫu thường ở mọi mô hình", C4,
     "mẫu có chuyển ý cũng thấp hơn mẫu thường ở mọi mô hình"),
    ("6.1, lỗi xoay quanh trung tính", "Phân tích lỗi cho thấy lỗi xoay quanh lớp trung tính", C5,
     "Lỗi của mọi mô hình xoay quanh lớp trung tính"),
    ("6.1, không nằm ở lật cực", "nếu có, không nằm ở việc lật cực", C5, "nếu có, không nằm ở việc lật cực"),
    ("6.1, câu hỏi 1", "PhoBERT tinh chỉnh là một mốc mạnh mà các mô hình phức tạp hơn trong chuyên đề chưa vượt được có ý nghĩa", C4,
     "Không mô hình đồ thị nào cao hơn PhoBERT có ý nghĩa ở bất kỳ nhóm nào"),
    ("6.1, câu hỏi 2, điểm cảm xúc", "vì điểm cảm xúc được suy ra từ nhãn của tập huấn luyện", C4,
     "và điểm cảm xúc được suy ra từ nhãn của tập huấn luyện"),
    ("6.1, câu hỏi 3, phủ định", "tác động của phủ định đứng một mình chưa đo được một cách vững", C4,
     "Nhận định rằng phủ định đứng một mình không làm mô hình kém đi chỉ dựa trên cách chia bốn nhóm của lần gán đầu"),
    ("6.2, không dò siêu tham số", "Mỗi mô hình chỉ chạy một cấu hình và không được dò siêu tham số", C4,
     "Không có mô hình nào được dò siêu tham số: mỗi mô hình chỉ chạy đúng một cấu hình"),
    ("6.2, hai nền tảng", "Các lần chạy của cùng một mô hình dùng hai nền tảng phần cứng khác nhau", C4,
     "ba seed đầu trên Google Colab, hai seed sau trên Kaggle"),
    ("6.2, độ chính xác hỗn hợp", "PhoBERT tinh chỉnh dùng độ chính xác hỗn hợp còn ba mô hình đồ thị thì không", C4,
     "PhoBERT tinh chỉnh được huấn luyện với độ chính xác hỗn hợp, ba mô hình đồ thị thì không"),
    ("6.2, PhoBERT fp32 ba seed", "mô hình đối chứng PhoBERT fp32 chỉ chạy ba seed", C4, "PhoBERT fp32 chạy ba seed"),
    ("6.2, tài nguyên tiếng Việt", "vì các tài nguyên tiếng Việt có sẵn chưa dùng được ngay", C4, "Hai tài nguyên có sẵn chưa được thực nghiệm"),
    ("6.2, gán lại sớm", "Hai lần gán cách nhau ngắn hơn dự định nên độ nhất quán đo được là cận trên", C4,
     "ngắn hơn mức 14 ngày mà chuyên đề dự định"),
    ("6.2, nhận định đồng ý kém ổn định", "nhận định đồng ý hay không với nhãn gốc cũng kém ổn định", C4,
     "Nhận định này kém ổn định giữa hai lần gán"),
    ("6.2, không hiệu chỉnh so nhiều lần", "không được hiệu chỉnh cho việc so nhiều lần", C4,
     "không được hiệu chỉnh cho việc so nhiều lần"),
    ("6.2, khảo sát không hệ thống", "chứ không theo một quy trình tìm kiếm hệ thống", C3,
     "Việc mở rộng không theo một quy trình tìm kiếm hệ thống"),
    ("6.1, vì sao đồ thị chưa giúp", "Mục 5.4 giải thích vì sao các mô hình đồ thị chưa phát huy hiệu quả", C5,
     "## 5.4. Vì sao ASGCN và Sentic-GCN chưa phát huy hiệu quả"),
    ("6.1, hướng đề xuất là giả thuyết", "Các kết quả trên không chứng minh hướng Neuro-Symbolic Multi-Graph sẽ tốt hơn PhoBERT", C5,
     "Hướng này được giữ như một giả thuyết cần kiểm chứng"),
    ("6.2, chưa đánh giá tổng quát hoá", "chưa đánh giá chéo miền (mục 4.1.1), nên chưa nói được về khả năng tổng quát hoá", C4,
     "Chuyên đề không dùng thêm tập dữ liệu khác, nên chưa đánh giá khả năng tổng quát hoá của các mô hình"),
    ("6.3, đánh giá trên VLSP", "Đánh giá khả năng tổng quát hoá trên tập dữ liệu của VLSP", C4,
     "Việc này được chuyển sang chuyên đề tiếp theo (mục 6.3)"),
    ("6.3, luật tách mệnh đề", "tách bình luận thành các mệnh đề tại từ nối chuyển ý", C5,
     "Luật chuyển ý tách bình luận thành các mệnh đề tại từ nối chuyển ý"),
    ("6.3, độ tin cậy học từ dữ liệu", "Ước lượng độ tin cậy của từng luật từ dữ liệu chưa gán nhãn theo hướng lập trình dữ liệu", C5,
     "độ chính xác của từng luật có thể ước lượng từ chính dữ liệu chưa gán nhãn"),
    ("6.3, người chú thích thứ hai", "tập chẩn đoán được người chú thích thứ hai gán lại một phần", C5,
     "sau khi tập chẩn đoán có thêm người chú thích thứ hai"),
    ("6.3, tách hai quyết định", "tách quyết định khía cạnh có được đánh giá rõ hay không khỏi quyết định cực", C5,
     "Quyết định khía cạnh có được đánh giá rõ hay không được tách khỏi quyết định cực"),
    ("6.3, mốc so sánh", "So mô hình đề xuất với PhoBERT tinh chỉnh và ASGCN bỏ GCN theo giao thức ở mục 4.2, với năm seed và hai phép kiểm định",
     C5, "Mốc so sánh là PhoBERT tinh chỉnh và ASGCN bỏ GCN, mô hình có cùng cách đọc ra, với năm seed và cả hai phép kiểm định ở mục 4.2"),
    ("6.3, đánh giá theo nhóm", "lớp trung tính, bình luận trái nhãn, nhóm chuyển ý và nhóm cả hai của tập chẩn đoán", C5,
     "lớp trung tính, bình luận trái nhãn, nhóm chuyển ý và nhóm cả hai của tập chẩn đoán"),
)
CAU_LOI = "ở các mô hình dùng PhoBERT, phần lớn lỗi có lớp trung tính ở một đầu và nằm ở bình luận trái nhãn, còn lỗi ngược cực chỉ là phần nhỏ"
# Bỏ qua khi quét số: tham chiếu mục, chương, bảng, hình (kể cả "mục 5.1 và 5.3"), khoá trích dẫn, số thứ tự đầu dòng,
# tiêu đề và tên riêng có chữ số (fp32, GPT-4o, Chuyên đề 1, 2).
MAU_BO = re.compile(r"(?:mục|Mục|Bảng|Hình|Chương|bảng|hình) \d+(?:\.\d+)*(?: và \d+(?:\.\d+)*)?|\[@[^\]]+\]"
                    r"|^\d+\. |^#+ .*$|\bfp32\b|\bGPT-4o\b|Chuyên đề [12]\b", re.M)
MAU_SO = re.compile(r"\d[\d.,]*\d|\d")


def chuan(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def doc(nhap: Path, ten: str) -> str:
    return chuan((nhap / ten).read_text(encoding="utf-8"))


def kiem_dan_chieu(nhap: Path) -> List[str]:
    c6 = doc(nhap, TEP_C6)
    nguon = {t: doc(nhap, t) for t in (C3, C4, C5)}
    loi = []
    for mo_ta, cau, tep, chung in DAN_CHIEU:
        if chuan(cau) not in c6:
            loi.append(f"KHÔNG THẤY  {mo_ta}: Chương 6 không còn câu này\n            cần có: {cau}")
        if chuan(chung) not in nguon[tep]:
            loi.append(f"MẤT CHỨNG CỨ  {mo_ta}: {tep} không còn câu làm chứng, câu ở Chương 6 cần viết lại\n            câu làm chứng: {chung}")
    return loi


def kiem_loi(goc: Path, nhap: Path) -> List[str]:
    """Ở bốn mô hình dùng PhoBERT: lỗi có lớp trung tính > 1/2, lỗi ở bình luận trái nhãn > 1/2, lỗi ngược cực < 1/5."""
    a = json.loads((goc / "results/error_analysis.json").read_text(encoding="utf-8"))
    dung = True
    for e in MANH:
        cap, so_loi = a["ma_tran"][e]["phan_loi_theo_cap"], a["ma_tran"][e]["so_loi"]
        nguoc_cuc = cap["0->2"] + cap["2->0"]
        trai = a["loai_cau"][e]["da_trai"]  # n: số mẫu thuộc bình luận trái nhãn; accuracy trung bình năm seed
        loi_trai = trai["n"] * (1 - trai["accuracy"]["gia_tri"])
        dung &= (1 - nguoc_cuc) > 0.5 and loi_trai / so_loi > 0.5 and nguoc_cuc < 0.2
    if not dung:
        return [f"SỐ LIỆU KHÔNG CÒN ĐỠ CÂU  6.1, câu hỏi 3: {CAU_LOI}"]
    if chuan(CAU_LOI) not in doc(nhap, TEP_C6):
        return [f"KHÔNG THẤY  6.1, câu hỏi 3: Chương 6 không còn câu này\n            cần có: {CAU_LOI}"]
    return []


def kiem_so(nhap: Path) -> List[str]:
    tho = (nhap / TEP_C6).read_text(encoding="utf-8")
    return [f"SỐ CHƯA CÓ CHỖ KIỂM  {s}: Chương 6 không đưa số liệu mới; dẫn về chương nguồn hoặc thêm chỗ kiểm"
            for s in dict.fromkeys(MAU_SO.findall(MAU_BO.sub(" ", tho)))]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đối chiếu Chương 6 với các chương mà nó tóm lại.")
    ap.add_argument("--goc", type=Path, default=Path("."), help="thư mục gốc của repo")
    ap.add_argument("--nhap", type=Path, default=NHAP_MAC_DINH, help=f"thư mục bản nháp (mặc định {NHAP_MAC_DINH})")
    a = ap.parse_args(argv)
    nhap = a.nhap if a.nhap.is_absolute() else a.goc / a.nhap
    loi = kiem_dan_chieu(nhap) + kiem_loi(a.goc, nhap) + kiem_so(nhap)
    for x in loi:
        print(x)
    tong = len(DAN_CHIEU) + 1
    print(f"Đã kiểm {tong} nhận định của {TEP_C6} và quét số: {'mọi chỗ khớp' if not loi else f'{len(loi)} chỗ lệch'}.")
    return 1 if loi else 0


if __name__ == "__main__":
    raise SystemExit(main())
