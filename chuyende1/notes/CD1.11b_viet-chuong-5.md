# PHIẾU BÀN GIAO — [CD1.11b] Viết Chương 5 (mục 5.1 đến 5.4); mục 5.5 chờ lượt tìm tài liệu

**Ngày:** 18/10/2026 · **Step:** CD1.11 (phần "Viết Chương 5") · **Thời gian thực tế:** khoảng 3 giờ

Học viên: "ok bắt đầu viết report theo hướng đó", sau khi Claude rút lại đề xuất "gắn hiện tượng vào đúng khía cạnh" làm
hướng Chuyên đề 2 (vấn đề đó không mới, phiếu CD1.11 mục 8). Claude hiểu là: viết Chương 5 ngay; mục 5.4 chỉ báo cáo số đo;
mục 5.5 (định hướng) để sau một lượt tìm tài liệu có chủ đích.

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `chuyende1/report/nhap_rut_gon/Chuong5_HanCheVaDinhHuong.md` (không push) | Sửa | Viết mục 5.1 đến 5.4, mục 5.5 còn một đoạn giữ chỗ; 1 hình, 1 bảng |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` (không push) | Sửa | Ghép riêng Chương 5 (`--chi 5 --ghi-de`), cập nhật mục lục và hai danh sách; 62 trang |
| `scripts/doi_chieu_chuong5.py` + `tests/test_doi_chieu_chuong5.py` | Tạo | Công cụ đối chiếu Chương 5, 5 test |
| `scripts/nhap_chuong_vao_docx.py`, `scripts/kiem_sua_tay_word.py` + hai file test | Sửa | Cờ `--ghep-thu`: công cụ kiểm sửa tay chạy lại được (GAP-043) |
| `chuyende1/gaps/GAP-043_...md`, `INDEX.md` | Tạo, sửa | Lớp chặn mã 3 làm hỏng công cụ kiểm sửa tay |
| `scripts/error_analysis.py`, `chuyende1/tables/bang_5_phan_tich_loi.md` | Sửa | "12 lần chạy" ghi cứng thành số tính ra (20 lần với 5 seed); `results/error_analysis.json` chạy lại giống hệt |
| `scripts/doi_chieu_chuong4.py` | Sửa | Ba chỗ kiểm ở mục 4.7 theo câu chữ mới của học viên, điều kiện số liệu giữ nguyên |
| `nhap_rut_gon/Chuong1_TongQuan.md`, `Chuong4_ThucNghiem.md` (không push) | Sửa | Đưa ba chỗ học viên sửa trong Word lúc 17:47 ngày 17/10 vào bản nháp |
| `chuyende1/MODULE.md`, `SO_TAY_LENH.md` (chỉ ở máy) | Sửa | Dòng công cụ mới, cờ mới |

Sao lưu: bản nháp ở `nhap_rut_gon/sao_luu/20261018-sua-tay-1747/` (Chương 1, 4) và `20261018-viet-chuong-5/` (Chương 5 giữ chỗ);
file Word ở `..._rutgon.20261018-150432.docx.bak`. File Word lưu lúc 15:04:55 ngày 18/10.

---

## 2. ĐỂ LÀM GÌ

- **Vấn đề:** Chương 5 mới có năm câu giữ chỗ. Số liệu của phân tích lỗi (CD1.9) và ba phép thăm dò (CD1.11) đã có nhưng chưa
  vào báo cáo.
- **Sau step này:** bốn mục đầu của Chương 5 có nội dung, mọi con số có chỗ kiểm. Còn thiếu mục 5.5 và Chương 6.

---

## 3. CƠ CHẾ — Chương 5 nói gì

| Mục | Nội dung | Bảng, hình |
|---|---|---|
| 5.1 | Lỗi xoay quanh lớp trung tính; khía cạnh và độ dài; bình luận trái nhãn khó hơn và lỗi rơi vào nhãn của khía cạnh kia; 191 mẫu cả bốn mô hình dùng PhoBERT cùng sai | Hình 5.1 (accuracy theo loại bình luận) |
| 5.2 | Bốn hạn chế: (1) khó phân biệt có ý kiến hay không; (2) gán nhầm ý kiến giữa các khía cạnh; (3) chuyển ý, nhất là đi cùng phủ định, nhưng lỗi không phải lỗi ngược cực; (4) nhãn gốc kém tin cậy ở chỗ khó | |
| 5.3 | Bốn ca cùng sai, đều thuộc tập chẩn đoán nên có ý kiến của học viên (3 đồng ý nhãn gốc, 1 gán tiêu cực) | Danh sách |
| 5.4 | Ba phép thăm dò P1, P2, P3; kết luận: lợi ích, nếu có, không nằm ở lật cực | Bảng 5.1 (P1 trên tập chẩn đoán) |
| 5.5 | Một đoạn giữ chỗ: hướng sẽ xác định sau khi đối chiếu với công trình đã có | |

Bốn ca được chọn trong giao của 191 mẫu cùng sai với tập chẩn đoán (30 mẫu), để mỗi ca có ý kiến của người thật chứ không chỉ
lời giải thích của Claude. Trong 30 mẫu đó học viên không đồng ý với nhãn gốc ở 17, và 14 trong 17 là nhãn gốc trung tính mà
học viên cho là có cực: câu này vào hạn chế 1.

Chỗ dễ hiểu sai: một phát hiện mới khi viết là 786 trên 817 mẫu trung tính nằm trong bình luận trái nhãn. Vì vậy "bình luận trái
nhãn khó" và "lớp trung tính khó" là hai mặt dính nhau; chương nói rõ chưa tách được.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Mục 5.5 | Một đoạn giữ chỗ | Viết hướng đề xuất ngay | Học viên hỏi vấn đề đã được giải chưa; cần tìm tài liệu trước |
| Số hình | 1 (loại bình luận) | 2 hình (thêm ma trận nhầm lẫn) | Bản thử đầu 8 trang, hình ma trận bị đẩy sang trang sau, để trống nửa trang; ý chính nói được bằng một câu |
| Bốn ca | Danh sách có câu nguyên văn | Bảng 5 cột | Bản thử đầu: cột câu quá hẹp, bảng dài gần hai trang |
| Đơn vị | "bình luận" | "câu" như trong `error_analysis.py` | Chương 4 dùng "bình luận" cho một mẫu văn bản, "câu" cho câu của VnCoreNLP (biến thể nối câu) |
| Khung bốn phần của hạn chế (hiện tượng, phạm vi, nguyên nhân, hệ quả) | Viết liền trong đoạn | Bốn nhãn "Hiện tượng. ..." | Quy tắc văn phong số 9 |
| Ghép vào Word | `--chi 5 --ghi-de` | Sửa bằng COM | Chương 5 trong Word chỉ có câu giữ chỗ, không phương trình; chạy thử trên bản sao, so chữ: ngoài Chương 5 không đổi gì |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Mục 5.5 cần lượt tìm tài liệu có chủ đích (10 đến 15 bài) về phạm vi phủ định và chuyển ý ở mức khía cạnh: dòng của Moore và
  Barnes 2021, bài "Exploring Scope Detection for Aspect-Based Sentiment Analysis" (2024, chưa đọc), dòng AC-MIMLLN cho nhóm
  khía cạnh. Kết quả quyết định mục 5.5 và một phần Chương 6.
- Chương 6 còn là khung. Đoạn "Chương này còn một số điều chưa trả lời được" học viên xoá ở mục 4.7 (Word, 17:47) có thể là
  nguyên liệu cho mục 6.2.
- Viết thêm câu có số vào Chương 5 thì phải thêm chỗ kiểm vào `doi_chieu_chuong5.py`; lượt quét ngược sẽ báo nếu quên.

---

## 6. KIỂM CHỨNG

```
doi_chieu_chuong5.py          50 chỗ, khớp 50; mọi con số trong chương có chỗ kiểm
doi_chieu_chuong4.py          234 chỗ, khớp 234 (sau khi đổi ba chỗ kiểm ở mục 4.7)
kiem_sua_tay_word.py          trước khi ghép: mã 1, sáu chỗ, cả sáu là câu giữ chỗ cũ của Chương 5; sau khi ghép: mã 2
so phương trình trong Word    9 trước, 9 sau
pytest tests -q               564 passed, 1 skipped in 135.25s
```

- Ghép thử trên bản sao: mọi khối chữ trước "Chương 5." và từ "Chương 6." trở đi giống hệt file thật; Chương 2 và 4 vẫn đủ
  phương trình và chỉ số dưới.
- Xem bố cục bằng ảnh xuất từ Word (trang 38 đến 44): Chương 5 dài 6 trang, file 62 trang (trước 58).
- Sự cố: (1) công cụ kiểm sửa tay hỏng từ CD1.12p, GAP-043; (2) một lần sửa công cụ bằng heredoc làm hỏng dấu gạch chéo
  ngược, lệnh tự dừng ở bước kiểm trước khi ghi, không file nào bị hỏng; (3) Claude chạy lệnh ghép ngay sau lệnh kiểm trả mã 1
  mà chưa đọc kết quả; đọc lại sau đó thì cả sáu chỗ đúng là câu giữ chỗ của Chương 5, không mất chỗ sửa tay nào.

---

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi cần bạn quyết:**

1. Bạn sửa trong Word lúc 17:47 ngày 17/10, câu ở mục 1.3 thành "Trước khi đề xuất mô hình đó, có điều mà tài liệu đã công bố
   chưa trả lời được", rồi kể "Thứ nhất, Thứ hai, Thứ ba". Có phải bạn định viết "có ba điều" không? Và ở mục 4.7, câu
   "Xét đóng góp của từng thành phần, Việc bổ sung ..." có chữ "Việc" viết hoa giữa câu. Tôi đã đưa nguyên văn vào bản nháp,
   chưa sửa.
2. Chương 5 dài 6 trang, file 62 trang. Giữ, hay cắt tiếp (ví dụ bỏ đoạn khía cạnh và độ dài ở mục 5.1, khoảng nửa trang)?
3. Làm lượt tìm tài liệu cho mục 5.5 bây giờ không?

**Kết:**
> Bạn đọc Chương 5 trong Word (trang 38 đến 43) rồi cho ý kiến, hay tôi làm tiếp lượt tìm tài liệu cho mục 5.5?
