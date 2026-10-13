# CD1.12c — Kiểm file báo cáo trước lần nộp bốn chương đầu

Ngày 13/10/2026. Học viên cần nộp tiến độ gồm bốn chương đầu hoàn chỉnh và hỏi còn thiếu gì.
Phiếu này chỉ ghi kết quả kiểm. Chưa sửa gì trong báo cáo, trong file Word hay trong mã.

## 1. ĐÃ LÀM GÌ

- Đọc lại toàn văn bốn bản nháp chương trong `chuyende1/report/nhap/`.
- Đo file `chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx` (bản ghép lúc 10:44 ngày 13/10) theo
  từng mục của quy định trình bày của trường: khổ giấy, lề, font, cỡ chữ, giãn dòng, đánh số
  trang, chú thích bảng và hình, số công thức, trích dẫn.
- Đếm số trang từng chương bằng chính Word, trên một bản sao tạm, ở khổ giấy hiện tại và ở khổ A4.
- Chạy lại hai công cụ đối chiếu số liệu.
- Ghi một lỗi định dạng vào sổ: `chuyende1/gaps/GAP-034_file-word-kho-letter-va-tieu-de-calibri.md`.

## 2. KẾT QUẢ TÓM TẮT

Nội dung bốn chương đã đủ các mục và số liệu khớp. File chưa nộp được vì phần bao quanh bốn
chương còn là khung, và có hai lỗi định dạng. Chương 4 còn hai kết quả chưa có.

## 3. NHỮNG GÌ ĐÃ KIỂM VÀ ĐẠT

- Chương 4: 157 con số, tính lại từ dữ liệu và file dự đoán, khớp cả 157.
- Chương 3: 129 con số dẫn từ công trình khác đều tìm thấy trong văn bản bản gốc.
- Chương 1 và 2: 15 con số mà công cụ không tự tìm được trong bản gốc gồm số do chuyên đề tự đo,
  số nhắc lại từ Bảng 3.2 và một con số nằm trong câu bình luận được trích. Những số nhắc lại từ
  Chương 3 và 4 đã được đọc đối chiếu và trùng. Các số về hai từ điển có sẵn ở mục 2.4 đã được đo
  trong đợt rà sáng 13/10 và không được đo lại trong lần này.
- Trích dẫn: 60 tài liệu được dẫn, 60 mục trong danh sách, đánh số liên tục từ 1 tới 60 theo thứ tự
  xuất hiện, không mục nào thừa hay thiếu.
- 21 bảng có chú thích nằm trên bảng, 2 hình có chú thích nằm dưới hình, số bảng, hình và công
  thức theo số chương và liên tục.
- Lề 3,5 / 2 / 3 / 3,5 cm; thân bài Times New Roman cỡ 13, giãn dòng 1,5; số trang ở giữa lề dưới,
  số La Mã trước Chương 1, số Ả Rập từ Chương 1.
- Văn phong bốn chương: không có gạch ngang dài, dấu backtick, chữ in đậm hay mã bước của plan;
  số thập phân dùng dấu phẩy và có khoảng trắng trước dấu phần trăm ở mọi chỗ.

## 4. NHỮNG GÌ CÒN THIẾU

### Nhóm 1: phải xử lý trước khi nộp

| Mã | Thiếu gì | Ở đâu | Ai làm |
|---|---|---|---|
| N1 | Hai bản trong thư mục `Backup` cũ hơn bản trong repo. Bản `_bk_06.10.docx` (lưu 10:20 hôm nay) mang nội dung ngày 06/10: còn câu "SenticNet không có cho tiếng Việt", còn 3,70 %, mục 4.6 chưa có kết quả, bìa ghi "ĐỀ CƯƠNG THẠC SĨ". Bản `_BK_13.10.docx` chưa có Bảng 4.10 đến 4.16 | `ScientificPaper\Backup\` | Học viên: không nộp hai bản đó |
| N2 | 25 dòng `[TODO ...]` còn hiện trong file Word, 21 dòng có mã bước nội bộ, 2 dòng "(Ngân sách: khoảng ... trang)" | 3 dòng trong Chương 1 đến 4 (mục 1.8, 4.3, 4.5); 9 dòng ở các trang đầu; 8 dòng ở Chương 5, 6; 5 dòng ở Phụ lục | Claude, sau khi học viên chốt N5 và N6 |
| N3 | Các trang đầu chưa có nội dung: tháng trên bìa, tóm tắt, lời cảm ơn, danh sách các bảng, danh sách các hình. Lời cam đoan còn ghi "luận văn/đề án". Mục lục lưu trong file đã cũ (mục 4.6 và 4.7 cùng trang 53) | Phần trước Chương 1 của file Word | Claude viết tóm tắt và dựng hai danh sách; học viên cho tháng nộp, viết lời cảm ơn |
| N4 | Khổ giấy là Letter chứ không phải A4; ba cấp tiêu đề hiện bằng Calibri | Cả file | Claude (GAP-034) |
| N5 | Chương 4 thiếu hai kết quả thuộc mục tiêu 2 và 3 của chuyên đề: mốc tham chiếu bằng mô hình ngôn ngữ lớn (mục 4.3), thời gian suy luận và bộ nhớ GPU cùng Hình 4.2 (mục 4.5) | `Chuong4_ThucNghiem.md` dòng 116 và 210 | Học viên quyết: làm trước khi nộp, hay nộp và ghi rõ là chưa làm |
| N6 | Chương 5, Chương 6 và Phụ lục trong file là khung kèm ghi chú nội bộ. Bốn chương đầu nhắc tới Chương 5, Chương 6, mục 6.1 và mục 6.3 ở 13 chỗ | Sau Chương 4 của file Word | Học viên quyết: giữ tiêu đề với một câu "đang thực hiện", hay bỏ hẳn khỏi bản nộp |

### Nhóm 2: nên xử lý, hoặc cần hỏi giảng viên hướng dẫn

| Mã | Việc | Chi tiết |
|---|---|---|
| N7 | Độ dài | Quy định: cuốn chuyên đề "dày khoảng 30 trang". Bốn chương đầu hiện dài 58 trang ở khổ A4: Chương 1 dài 7 trang, Chương 2 dài 9, Chương 3 dài 18, Chương 4 dài 24. Phần lời không kể bảng khoảng 17.800 chữ. Dàn ý dự tính 24 trang cho bốn chương này |
| N8 | Học viên chưa đọc phần mới | Ba đoạn mới của mục 4.1.2, toàn bộ mục 4.6, đoạn "Phủ định và chuyển ý" ở mục 4.7; và chưa xem Bảng 4.10 đến 4.16 trong Word |
| N9 | Danh sách chữ viết tắt | 6 trong 10 mục không xuất hiện trong bốn chương (ABSA, ACSA, GNN, LLM, PLM, NEG/NEU/POS); các chữ có dùng mà chưa có: BiLSTM, LSTM, BERT, SVM, CRF, CPU, GPU, F1, BPE. Bảng còn dùng gạch ngang dài. Trang "Danh sách công thức" không có trong quy định |
| N10 | Tài liệu tham khảo | 43 trong 60 mục chưa có số trang, 11 mục ghi "và cộng sự" thay cho danh sách tác giả. Mẫu của trường: "Tác giả. Tên bài báo. Tên hội thảo, năm, trang." |
| N11 | Chỗ nhỏ trong lời văn | Mục 1.6 còn ghi "khoảng 800 mẫu" (nay là 799); Bảng 1.1 còn ghi "Xong bản nháp"; Bảng 4.2, 4.5, 4.11, 4.12 chưa được gọi tên trong lời văn; cả dòng chú thích bảng in đậm trong khi mẫu chỉ in đậm chữ "Bảng" và số |
| N12 | Trình bày tiêu đề chương | Mẫu (Phần I, Phụ lục 10): "Chương 1" cỡ 16 một dòng, tên chương cỡ 18 dòng dưới; tiêu đề các trang đầu cỡ 18. File đang gộp một dòng cỡ 16 |
| N13 | Phụ lục B | Mục 4.1.2 nói nhãn được gán "theo một bản hướng dẫn viết trước" nhưng bản đó chưa có trong file |

## 5. GIỚI HẠN CỦA LẦN KIỂM NÀY

- Chưa nhìn bảng trong Word bằng mắt: bảng có tràn lề hay không là việc N8 của học viên.
- Chưa có lượt soát chính tả bằng công cụ. Lần đọc lại này không thấy lỗi nào, nhưng đó không
  phải một lượt soát chính tả.
- Chưa biết giảng viên hướng dẫn đòi gì cho lần nộp tiến độ: hạn nộp, nộp Word hay PDF, có cần tóm
  tắt tiếng Anh không, có giữ mức 30 trang không.
- Hình `chuyende1/report/nhap/pictures/Hinh_4_2_Danh_doi_MacroF1_Chi_phi.png` không nằm trong file
  Word. Không nên dùng: hình so thời gian huấn luyện giữa các mô hình, trong khi mục 4.5 nói rõ các
  thời gian đó chưa so sánh được với nhau.

## 6. KIỂM CHỨNG

```
doi_chieu_chuong4.py --do-cat --do-mau-so : 157 chỗ, 157 khớp, 0 lệch
doi_chieu_ban_goc.py kiem, Chương 3      : 129 con số, thấy 120, thấy ở công trình khác cùng đoạn 9, cần xem tay 0
Word, khổ Letter (file hiện tại)          : 80 trang; Chương 1 đến 4 từ trang 1 tới 62
Word, khổ A4                              : 74 trang; Chương 1 đến 4 từ trang 1 tới 58
Word, font của đoạn Heading 1, 2, 3       : Calibri
w:pgSz của cả ba section                  : w=12240 h=15840 (Letter)
```

Bộ test không được chạy lại trong lần này vì không dòng mã nào đổi.

## 7. VIỆC CỦA BẠN

Ba quyết định, để Claude dọn file Word thành bản nộp trong một lượt:

1. N5: hai kết quả còn thiếu của Chương 4 làm trước khi nộp, hay nộp và ghi rõ là chưa làm.
2. N6: Chương 5, 6 và Phụ lục giữ tiêu đề kèm một câu "đang thực hiện", hay bỏ khỏi bản nộp.
3. N3: tháng ghi trên bìa.

Và một câu hỏi nên gửi giảng viên hướng dẫn: mức "khoảng 30 trang" có áp cho bản nộp này không (N7).
