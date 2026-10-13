# GAP-035 — Dự đoán của BiLSTM đổi theo kích thước lô lúc suy luận

**Ngày phát hiện:** 13/10/2026 · **Phát hiện bởi:** cột `khác` của `scripts/profile_cost.py`, khi chạy thử phép đo chi phí ở máy
**Loại:** phương pháp · code
**Mức độ:** nhẹ (số đã công bố tái lập đúng; mức đổi nhỏ hơn dao động giữa các hạt giống)
**Trạng thái:** 🔴 Mở: chờ học viên quyết có ghi vào báo cáo không

---

## 1. Sai ở đâu

Một mô hình đã huấn luyện xong thì cùng một mẫu phải cho cùng một dự đoán, bất kể mẫu đó được đưa
vào chung lô với những mẫu nào. BiLSTM của chuyên đề không có tính chất này. Nạp lại ba bộ trọng số
đã lưu và chạy lại tập kiểm tra (6.722 mẫu) trên chính máy đã huấn luyện:

| Hạt giống | Lô 64 (lúc đánh giá) | Lô 32 | Lô 1 |
|---|---|---|---|
| 42 | 0 dự đoán khác; accuracy 85,82 % | 10 khác; 85,82 % | 59 khác; 85,76 % |
| 1337 | 0 khác; 86,37 % | chưa đo | 43 khác; 86,27 % |
| 2024 | 0 khác; 87,06 % | chưa đo | 47 khác; 87,07 % |

"Khác" là so với `results/bilstm/seed<N>/predictions.jsonl`. Ở lô 64 cả ba hạt giống cho lại đúng
từng dự đoán đã công bố.

## 2. Phát hiện thế nào

`profile_cost.py` đo thời gian suy luận ở lô 1 và lô 32, và đối chiếu nhãn dự đoán của lần đo với
file dự đoán đã công bố để chắc rằng đang đo đúng mô hình. Mô hình từ điển cho 0 dự đoán khác ở cả
hai kích thước lô; BiLSTM thì không.

## 3. Nguyên nhân gốc

Trong `src/nsmgat/models/bilstm.py`, hàm `ma_hoa` đưa cả tensor đã đệm vào LSTM mà không đóng gói
chuỗi theo độ dài thật. Vector khía cạnh được nối vào mọi vị trí, kể cả vị trí đệm. LSTM chiều
ngược vì vậy đọc hết phần đệm rồi mới tới từ thật, và trạng thái của nó tại các từ thật phụ thuộc
vào số vị trí đệm. Số vị trí đệm của một mẫu lại do mẫu dài nhất trong lô quyết định. Lớp attention
có che phần đệm, nhưng các trạng thái được gộp đã mang ảnh hưởng đó.

Các mô hình dùng PhoBERT không dựng theo cách này: bộ mã hoá dùng mặt nạ chú ý. Chúng sẽ được kiểm
bằng cùng cột `khác` khi phép đo chạy trên Colab.

## 4. Ảnh hưởng lan tới đâu

- Bảng 4.5 và mọi phân tích dùng dự đoán của BiLSTM: không đổi. Các con số đó ứng với một quy trình
  xác định (lô 64, theo thứ tự file) và tái lập đúng.
- Điều cần biết khi đọc: accuracy của BiLSTM xê dịch tới 0,10 điểm khi đổi kích thước lô, nhỏ hơn độ
  lệch chuẩn 0,62 điểm giữa ba hạt giống. Bậc này cách bậc trên và bậc dưới hơn 5 điểm, nên không
  kết luận nào của Chương 4 phụ thuộc vào nó.
- Mô hình cũng được huấn luyện với phần đệm như vậy, nên đây là một đặc điểm của mô hình đã huấn
  luyện chứ không chỉ của lúc suy luận.

## 5. Phương án

1. **Giữ nguyên, ghi một câu vào phần mô tả BiLSTM ở mục 4.3** (Claude đề nghị): kết quả ứng với
   kích thước lô 64 lúc đánh giá; ở kích thước lô 1 có 43 đến 59 trong 6.722 dự đoán đổi. Không tốn
   thời gian chạy.
2. Sửa mô hình cho đóng gói chuỗi rồi huấn luyện lại ba hạt giống (khoảng 53 phút mỗi lần trên CPU),
   cập nhật Bảng 4.5 đến 4.8, các bảng của mục 4.6 và phân tích lỗi. Đây là đổi mô hình của một bậc
   đã công bố; làm thì mọi con số có BiLSTM đều đổi.

## 6. Bài học

Đối chiếu dự đoán của một lần chạy lại với file đã công bố bắt được điều mà so accuracy không bắt
được: ở lô 32 accuracy trùng tới sáu chữ số trong khi 10 dự đoán đã đổi. Và test của mô hình nên có
phép kiểm "một mẫu, hai cách ghép lô, cùng đầu ra".
