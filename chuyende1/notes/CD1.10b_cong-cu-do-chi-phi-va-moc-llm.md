# CD1.10b và CD1.7 — Công cụ cho hai phần còn thiếu của Chương 4, và phương án rút gọn báo cáo

Ngày 13/10/2026. Học viên cần hoàn thành mục 4.3 (mốc tham chiếu bằng mô hình ngôn ngữ lớn) và mục
4.5 (chi phí suy luận), và hỏi cắt báo cáo xuống khoảng 30 trang thế nào. Phiếu này ghi hai công cụ
đã viết và chạy thử; **chưa có con số nào của hai mục đó**, vì cả hai cần học viên chạy.

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `scripts/profile_cost.py` | Tạo | Đo thời gian suy luận và bộ nhớ GPU đỉnh của sáu mô hình trong cùng một điều kiện |
| `tests/test_profile_cost.py` | Tạo | 7 test (1 test chỉ chạy khi có GPU) |
| `notebooks/colab_train.ipynb` | Sửa | Thêm mục 12 gồm 4 ô; 25 ô cũ không đổi |
| `scripts/eval_llm.py` | Viết lại | Thay file giữ chỗ 5 dòng: rút tập con, dựng câu lệnh, gọi API có bộ nhớ đệm, bảng so sánh |
| `configs/llm.yaml` | Tạo | Tên mô hình, tham số, câu lệnh, cách gọi tên mười khía cạnh |
| `tests/test_eval_llm.py` | Tạo | 23 test, không test nào gọi mạng |
| `results/llm_subset_uids.json` | Tạo | 500 mẫu của tập con, chỉ gồm mã mẫu |
| `chuyende1/gaps/GAP-035_...md` | Tạo | Dự đoán của BiLSTM đổi theo kích thước lô |

Lệnh đã chạy ở máy:

```
python scripts/profile_cost.py --exp lexicon bilstm --chi-in
python scripts/profile_cost.py --exp phobert asgcn asgcn_linked senticgcn --so-mau 64 --lap 1 --chi-in
python scripts/eval_llm.py chon
python scripts/eval_llm.py xem
```

## 2. VÌ SAO LÀM VẬY

- Đo chi phí trong một lệnh, một phiên, một GPU: Bảng 4.9 hiện chỉ có thời gian huấn luyện, và chính
  mục 4.5 nói các thời gian đó chưa so được với nhau. Phép đo mới giữ mọi thứ như nhau cho sáu mô hình.
- Đối chiếu dự đoán của lần đo với file đã công bố: để chắc rằng bộ trọng số đang đo là bộ đã cho
  số trong báo cáo, không chỉ là một file cùng tên.
- Mô hình ngôn ngữ lớn chỉ chạy trên 500 mẫu, và sáu mô hình kia được chấm lại trên đúng 500 mẫu đó:
  so một mô hình trên 500 mẫu với mô hình khác trên 6.722 mẫu là so hai tập khác nhau.
- Zero-shot một lần, few-shot ba bộ ví dụ: theo phương án ở GAP-003.

## 3. ĐỌC KẾT QUẢ THẾ NÀO

`profile_cost.py` in mỗi mô hình một dòng, hai nhóm cột cho lô 1 và lô 32:

- `ms/mẫu`: mili giây cho một mẫu, trung vị của 3 lần lặp. Thời gian tách subword không nằm trong đó.
  Với ba mô hình đồ thị, con số gồm cả việc dựng ma trận kề cho từng lô nhưng không gồm thời gian
  phân tích cú pháp bằng VnCoreNLP.
- `đỉnh MB`: bộ nhớ GPU đỉnh, gồm cả trọng số của mô hình.
- `khác`: số mẫu có nhãn dự đoán khác file `predictions.jsonl` đã công bố.
- `trọng số`: `best.pt` hoặc `khoi_tao` (không tìm thấy `best.pt`).

`eval_llm.py chay` in accuracy, macro-F1, số câu trả lời không đọc được và số token thật.

## 4. KẾT QUẢ CỦA LẦN CHẠY THỬ

Không con số nào dưới đây là số để đưa vào Bảng 4.9: máy không có GPU.
*(Đính chính 16/10/2026: máy có card GTX 1650 4 GB nhưng PyTorch trong `.venv` là bản chỉ chạy CPU, nên PyTorch không thấy
GPU. Kết luận đo trên Colab không đổi. Xem GAP-039.)*

- Mô hình từ điển và BiLSTM, với `best.pt` thật, trên cả tập kiểm tra: phép đo chạy xong. Mô hình từ
  điển cho 0 dự đoán khác ở cả hai kích thước lô.
- BiLSTM cho 0 dự đoán khác ở lô 64 (kích thước lúc đánh giá), 10 ở lô 32 và 59 ở lô 1. Đây là phát
  hiện mới, ghi ở GAP-035.
- Bốn mô hình dùng PhoBERT: dựng được từ file cấu hình và chạy được trên 64 mẫu với trọng số lúc
  khởi tạo. `best.pt` của chúng không có ở máy.
- Tập con: 500 mẫu thuộc 455 bình luận, 164 tiêu cực, 61 trung tính, 275 tích cực.
- Độ dài câu lệnh: zero-shot khoảng 252 nghìn ký tự đầu vào cho 500 lần gọi; few-shot khoảng 750 đến
  775 nghìn ký tự cho mỗi bộ ví dụ. Cả bốn lần chạy: 2.000 lần gọi, khoảng 2,5 triệu ký tự.

## 5. GIỚI HẠN

- Đường chạy trên GPU chưa được thử: máy không có GPU. Mô hình từ điển và BiLSTM chưa từng chạy trên
  GPU. Nếu một mô hình lỗi ở một kích thước lô, công cụ ghi lỗi rồi đo tiếp các mô hình khác.
- Chưa có lần gọi API nào. Phần gọi mạng của `eval_llm.py` chưa được chạy thật; test dùng hàm gọi giả.
- Chưa kiểm được tên mô hình `gpt-4o` còn dùng được trên API hay không. Lệnh `kiem` trả lời câu này
  khi có khoá.
- Câu lệnh không định nghĩa ba mức cảm xúc, chỉ nêu tên nhãn. Đây là một lựa chọn; đổi câu lệnh có
  thể đổi kết quả.
- Số token và chi phí chưa biết. Bản plan gốc ước 1 đến 2 USD cho 500 câu; phương án bốn lần chạy
  dài hơn mức đó. Lệnh `chay --thu 5` cho số token thật trước khi chạy đủ.

## 6. KIỂM CHỨNG

```
474 passed, 1 skipped   (cả bộ; trước đó 445)
profile_cost.py, bilstm seed 42, lô 64: accuracy 0,858227, 0 dự đoán khác; metrics.json ghi 0,858227
profile_cost.py, bilstm seed 1337 và 2024, lô 64: 0 dự đoán khác
notebook: 25 ô cũ giữ nguyên từng ký tự, thêm 4 ô
```

## 7. VIỆC CỦA BẠN

1. **Mục 4.5.** Xem trên Drive còn `best.pt` của bốn mô hình dùng PhoBERT không, tải `best.pt` của
   BiLSTM và mô hình từ điển lên, rồi chạy mục 12 của notebook trên Colab. Cần push trước để Colab
   lấy được mã mới.
2. **Mục 4.3.** Có khoá API của OpenAI thì đặt vào biến môi trường và chạy theo §11k của sổ tay lệnh.
   Trước đó xác nhận hai điều: dùng `gpt-4o`, và phương án zero-shot một lần cùng few-shot ba bộ ví dụ.
3. **GAP-035.** Chọn: ghi một câu vào mục 4.3 về việc dự đoán của BiLSTM đổi theo kích thước lô, hay
   sửa mô hình và huấn luyện lại.

## 8. PHƯƠNG ÁN RÚT GỌN VỀ KHOẢNG 30 TRANG

Số đo bằng Word ở khổ A4: bốn chương đầu dài 58 trang (7, 9, 18, 24). Trong đó bảng chiếm khoảng 12
trang và hình khoảng 1 trang; lời văn khoảng 45 trang. Các con số tiết kiệm dưới đây là ước lượng.

Quy định ghi luận văn dày 50 đến 70 trang "không kể hình vẽ, bảng biểu, đồ thị và phụ lục", và chuyên
đề "dày khoảng 30 trang", trình bày "tương tự như cuốn luận văn". Cách đếm cho chuyên đề vì vậy cần
hỏi giảng viên hướng dẫn.

**Mức 1: chuyển sang phụ lục, không viết lại.** Tiết kiệm khoảng 8 trang, không mất nội dung.

| Chuyển gì | Từ đâu | Khoảng |
|---|---|---|
| Bảng 3.4 (48 công trình) | mục 3.9, sang Phụ lục A | 3,5 trang |
| Bảng 4.12, 4.14, 4.15, 4.16 và phần diễn giải chi tiết | mục 4.6 | 2,6 trang |
| Quy trình chú thích và phân tích độ nhất quán, giữ lại một đoạn tóm tắt | mục 4.1.2, sang Phụ lục B | 1,3 trang |
| Hình 2.1 và đoạn mô tả | mục 2.2 | 0,6 trang |
| Bảng 4.3, Bảng 4.7 | mục 4.2, 4.4 | 0,4 trang |

**Mức 2: rút lời văn từng chương.** Sau cả hai mức, bốn chương còn khoảng 32 trang, trong đó lời văn
khoảng 26 trang.

| Chương | Hiện tại | Sau mức 1 và 2 | Rút ở đâu |
|---|---|---|---|
| 1 | 7 | 4,5 | Gộp mục 1.5 vào 1.4; mục 1.2 còn nửa trang và trỏ sang 3.10; rút 1.3, 1.6, 1.7 |
| 2 | 9 | 5,5 | Bỏ công thức GAT và đoạn về BERT, RoBERTa; phần hai từ điển có sẵn chỉ giữ ở mục 4.3; mô tả bootstrap chỉ giữ ở mục 4.2 |
| 3 | 18 | 8,5 | Mỗi nhóm từ 3.2 đến 3.7 còn nửa trang tới hai phần ba trang; mục 3.1 còn nửa trang; số liệu từng bài nằm ở Phụ lục A |
| 4 | 24 | 14 | Mục 4.1 còn 2,5 trang; 4.2 còn 1,8; 4.3 còn 2; 4.4 còn 3; 4.6 còn 2,5; 4.7 còn 1,2 |

Cộng Chương 5 (4 trang) và Chương 6 (2 trang) theo dàn ý, toàn cuốn khoảng 38 trang kể cả bảng, lời
văn khoảng 32 trang.

**Mức 3: đúng 30 trang kể cả bảng.** Phải bỏ nội dung thật, ví dụ phần đọc theo từng dấu hiệu ở mục
4.6 hoặc biến thể nối gốc. Không nên làm trước khi hỏi giảng viên hướng dẫn.

Nên rút gọn sau khi mục 4.3 và 4.5 có số, vì hai mục đó sẽ thêm khoảng một trang.
