# CD1.8f — Chốt tập chẩn đoán và đưa kết quả vào báo cáo

Ngày 13/10/2026. Tiếp theo `CD1.8d_rut-mau-gan-lai.md` (mục 9) và `CD1.8e_cham-theo-nhom.md`.

## 1. ĐÃ LÀM GÌ

Học viên chọn dùng luôn lần gán lại ngày 13/10 và ghi đúng khoảng cách thật (phương án 1 của GAP-032).
Theo đó:

- `finalize_diagnostic.py kappa` có thêm cờ `--gan-som`. File `data/diagnostic/kappa.json` ghi
  `gan_som: true`, ngày gán lại 13/10/2026 và khoảng cách tối đa 8 ngày.
- Đã chạy `chot`: `data/diagnostic/diagnostic_300.jsonl` có 799 dòng (file chỉ nằm trên máy).
- Đã chạy lại `cham`. Kết quả không còn mang dấu sơ bộ; đầu bảng có câu nói rõ lần gán lại không đủ 14 ngày.
- `cham` in thêm hai loại bảng: theo dấu hiệu (có phủ định, có chuyển ý) và so từng mô hình với
  PhoBERT trong từng nhóm.
- Báo cáo: viết xong phần còn thiếu của mục 4.1.2, toàn bộ mục 4.6 (Bảng 4.10 đến 4.16), thêm một
  đoạn ở mục 4.7, sửa một ô ở Bảng 1.1. Đã ghép vào file Word.
- `doi_chieu_chuong4.py` nay kiểm cả phần tập chẩn đoán: 156 chỗ, khớp cả 156.

## 2. VÌ SAO LÀM VẬY

- Cờ riêng thay cho `--bo-qua-ngay`: cờ cũ dành cho người chú thích thứ hai và ghi loại kết quả là
  "cần ghi rõ ai gán lần hai". Dùng nó cho trường hợp này là ghi sai sự việc.
- Bảng theo dấu hiệu: 7 trong 12 dòng lệch giữa hai lần gán là lệch giữa `both` và `negation`. Gộp
  `negation` với `both` thành "có phủ định" thì tập mẫu đó không đổi khi một dòng chuyển giữa hai
  nhóm, nên kết luận trên nhóm gộp không phụ thuộc vào ranh giới kém ổn định.
- Bảng so với PhoBERT trong từng nhóm: phiếu CD1.8e ghi "chưa kiểm định cặp mô hình trong từng nhóm".
  Đây là phép so trả lời câu hỏi của đề tài: mô hình đồ thị có hơn PhoBERT trên câu khó không.
- Bảng 4.10 đến 4.16 đánh số nối tiếp sau Bảng 4.9, nên không bảng cũ nào phải đổi số.

## 3. ĐỌC KẾT QUẢ THẾ NÀO

- Bảng 4.11, 4.12: giá trị và khoảng tin cậy 95 % của từng nhóm.
- Bảng 4.13: hiệu số của mỗi nhóm so với nhóm thường của cùng mô hình; số trong ngoặc là p.
- Bảng 4.14: như trên nhưng chia theo dấu hiệu. Dòng `both` được tính vào cả hai cột.
- Bảng 4.15: mô hình trừ PhoBERT, trong cùng một nhóm. 20 phép so, không hiệu chỉnh.
- Bảng 4.16: chấm lại trên 655 dòng bạn ghi `dong_y`.

## 4. KẾT QUẢ

Độ nhất quán (60 dòng): kappa 0,733, trùng 48 dòng. Có phủ định hay không: kappa 0,900. Có chuyển ý
hay không: kappa 0,700. Nhãn cảm xúc sau kiểm tra: kappa 0,753.

Accuracy của PhoBERT (%), hiệu so với nhóm thường trong ngoặc:

| Cách chia | Thường | Phủ định | Chuyển ý | Cả hai |
|---|---|---|---|---|
| Bốn nhóm, 799 dòng | 91,4 | 90,5 (-0,9; p 0,726) | 84,2 (-7,2; p 0,008) | 71,8 (-19,6; p < 0,001) |
| Bốn nhóm, 655 dòng `dong_y` | 95,6 | 95,2 (-0,4; p 0,885) | 90,9 (-4,7; p 0,054) | 83,0 (-12,6; p 0,002) |

| Theo dấu hiệu, 799 dòng | Thường | Có phủ định (203) | Có chuyển ý (265) |
|---|---|---|---|
| PhoBERT | 91,4 | 82,8 (-8,6; p 0,001) | 80,3 (-11,2; p < 0,001) |

Năm điều báo cáo nêu:

1. Nhóm cả hai thấp hơn nhóm thường 15,8 đến 19,6 điểm ở cả sáu mô hình; không mô hình nào đạt 75 %.
2. Nhóm chuyển ý thấp hơn 5,3 đến 14,4 điểm.
3. Theo bốn nhóm thì nhóm phủ định không khác nhóm thường về accuracy. Theo dấu hiệu thì mẫu có phủ
   định thấp hơn 6,7 đến 9,3 điểm ở năm mô hình học. Báo cáo vì vậy không kết luận rằng phủ định
   đứng một mình là dễ.
4. Không mô hình đồ thị nào hơn PhoBERT có ý nghĩa ở nhóm nào. Sentic-GCN hơn 2,5 đến 2,8 điểm ở ba
   nhóm có hiện tượng nhưng khoảng tin cậy chứa 0, và trên 655 dòng `dong_y` thì còn +0,6, +0,3, -1,2.
5. Người chú thích không đồng ý với nhãn gốc ở 27,1 % số dòng nhóm chuyển ý và 34,5 % nhóm cả hai,
   so với 12,5 % ở nhóm thường. Một phần khoảng cách đến từ đó.

Điểm lạ ghi ở phiếu CD1.8e nay đã có lời giải: mô hình từ điển không đoán lớp trung tính ở dòng nào
của tập, nên accuracy của nó bị chặn bởi tỉ lệ dòng không trung tính, là 64,3 % ở nhóm thường và
76,5 % ở nhóm phủ định. Hiệu số +11,6 điểm là do thành phần nhãn.

## 5. GIỚI HẠN ĐÃ GHI TRONG BÁO CÁO

- Kappa là cận trên: hai lần gán cách nhau không quá 8 ngày, ít nhất 28 dòng dưới 3 ngày.
- Một người gán. Chưa có người thứ hai.
- Ranh giới `both` với `negation` kém ổn định: nhóm `both` giữ nguyên 9 trên 15 dòng.
- Nhóm cả hai có 84 dòng, khoảng tin cậy rộng khoảng 18 điểm.
- Tập không phải mẫu ngẫu nhiên của tập kiểm tra, và là một lát cắt của chính tập kiểm tra.
- Nhận định "nhãn gốc sai" cũng kém ổn định: lần 1 có 12 dòng, lần 2 có 7 dòng, trùng 5 dòng.

## 6. KIỂM CHỨNG

```
440 passed   (cả bộ; tests/test_finalize_diagnostic.py có 14 test, thêm 4)
doi_chieu_chuong4.py --do-cat: 156 chỗ, 156 khớp, 0 lệch
```

- Giá trị accuracy và macro-F1 của mọi ô (sáu mô hình, bốn nhóm và hai nhóm gộp, hai tập) được
  `doi_chieu_chuong4.py` tính lại từ `predictions.jsonl` bằng một đoạn mã độc lập và khớp
  `results/diagnostic_eval.json` tới 9 chữ số.
- Bảng bốn nhóm giống hệt bản sơ bộ ở phiếu CD1.8e (cùng hạt giống, cùng thứ tự rút).
- File Word: 22 bảng, 2 hình, không còn khoá trích dẫn chưa đánh số.
- **Chưa kiểm:** chưa ai mở bảy bảng mới bằng Word. Bảng 4.13 có 7 cột, Bảng 4.15 có ô dài.
- **Chưa làm:** trường `diagnostic` trong 18 file `metrics.json` vẫn bằng 0. Plan ghi đây là sản phẩm
  của bước này; báo cáo không dùng tới nó. Con số "28 dòng dưới 3 ngày" lấy từ giờ sửa của các bản
  sao lưu CSV (bảng ở GAP-032), công cụ đối chiếu không kiểm được.

## 7. VIỆC CỦA BẠN

Đầy đủ ở `pLan/chuyende1/VIEC_CAN_LAM.md`.

1. Đọc ba đoạn mới của mục 4.1.2, toàn bộ mục 4.6 và đoạn "Phủ định và chuyển ý" ở mục 4.7 trong
   `chuyende1/report/nhap/Chuong4_ThucNghiem.md`. Đây là kết quả chính của nhiệm vụ 4, bạn cần
   hiểu và đồng ý với từng câu.
2. Mở file Word, bấm Ctrl+A rồi F9, xem Bảng 4.10 đến 4.16 có tràn lề không.
3. Quyết định có điền trường `diagnostic` vào 18 file `metrics.json` không (việc C8).
4. Vẫn còn: xác nhận máy đã huấn luyện mô hình từ điển và BiLSTM; câu hỏi Sentic-GCN với từ điển có sẵn.
