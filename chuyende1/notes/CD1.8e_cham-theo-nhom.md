# CD1.8e — Chấm sáu mô hình theo nhóm hiện tượng (số sơ bộ)

Ngày 13/10/2026. Tiếp theo `CD1.8d_rut-mau-gan-lai.md`.

## 1. ĐÃ LÀM GÌ

Thêm hai lệnh vào `scripts/finalize_diagnostic.py`:

- `cham`: tính accuracy và macro-F1 của sáu mô hình trên từng nhóm thường, phủ định, chuyển ý,
  cả hai; kèm khoảng tin cậy 95 % và phép so mỗi nhóm với nhóm thường.
- `chot`: ghi tập chẩn đoán thành `data/diagnostic/diagnostic_300.jsonl`. Lệnh từ chối chạy
  cho tới khi có kappa đạt 0,70, nên hôm nay chưa ghi file nào.

Đã chạy `cham` thật. Kết quả ở `chuyende1/tables/bang_4_chan_doan.md` và
`results/diagnostic_eval.json`, cả hai mang dấu sơ bộ.

## 2. VÌ SAO LÀM VẬY

- Không chạy lại mô hình. Mỗi dòng của tập chẩn đoán là một mẫu của tập kiểm tra, và dự đoán của
  18 lần chạy cho mọi mẫu kiểm tra đã nằm trong `predictions.jsonl`. Ghép hai thứ lại là đủ, và
  bảo đảm số ở đây đến từ đúng các mô hình của bảng kết quả chính.
- Bootstrap theo câu. Một câu có thể góp dòng PRICE vào nhóm thường và dòng GENERAL vào nhóm
  phủ định. Rút theo câu thì hai nhóm được rút cùng nhau, nên phép so giữa hai nhóm tính đúng
  phần phụ thuộc đó.
- Chấm theo nhãn gốc của bộ dữ liệu, vì mô hình học theo nhãn đó và bảng kết quả chính cũng chấm
  theo nó. Chấm thêm một lần trên riêng 655 dòng bạn ghi `dong_y`, để xem kết luận có đổi không
  khi bỏ các dòng nhãn gốc bị nghi.
- Chưa đụng `metrics.json`. Trường `diagnostic` trong 18 file vẫn bằng 0. Chỉ điền sau khi tập
  được chốt, để không phải ghi hai lần vào file kết quả.

## 3. ĐỌC KẾT QUẢ THẾ NÀO

Mỗi ô của bảng có dạng `84,2 [79,3; 88,7]; -7,2, p 0,008`:

- 84,2 là giá trị trung bình ba seed, tính bằng phần trăm.
- Hai số trong ngoặc vuông là khoảng tin cậy 95 %.
- -7,2 là hiệu so với nhóm thường của cùng mô hình, tính bằng điểm phần trăm.
- p là xác suất thấy hiệu lớn cỡ đó nếu thật ra hai nhóm bằng nhau. Dưới 0,05 thì tin được.

## 4. KẾT QUẢ SƠ BỘ (chưa dùng cho báo cáo)

Accuracy (%), toàn bộ 799 dòng, hiệu so với nhóm thường trong ngoặc:

| Mô hình | Thường (415) | Phủ định (119) | Chuyển ý (181) | Cả hai (84) |
|---|---|---|---|---|
| Từ điển cảm xúc | 54,8 | 66,4 (+11,6) | 45,3 (-9,5) | 37,3 (-17,5) |
| BiLSTM | 86,2 | 81,8 (-4,4) | 71,8 (-14,4) | 69,8 (-16,3) |
| PhoBERT | 91,4 | 90,5 (-0,9) | 84,2 (-7,2) | 71,8 (-19,6) |
| ASGCN | 89,6 | 86,6 (-3,1) | 83,1 (-6,6) | 73,8 (-15,8) |
| ASGCN nối gốc | 91,2 | 88,0 (-3,2) | 84,0 (-7,2) | 74,6 (-16,6) |
| Sentic-GCN | 92,0 | 93,0 (+0,9) | 86,7 (-5,3) | 74,6 (-17,4) |

Ba điều thấy được, đều cần kappa trước khi viết vào báo cáo:

1. Nhóm cả hai là chỗ mọi mô hình mạnh đều rơi 16 đến 20 điểm, p dưới 0,001. Không mô hình nào
   vượt 75 %.
2. Phủ định đứng một mình không làm PhoBERT và Sentic-GCN kém đi về accuracy (p 0,73 và 0,67).
   Giả thuyết "mô hình kém ở câu phủ định" không được số liệu này ủng hộ ở dạng đơn giản đó.
3. Ba mô hình đồ thị không hơn PhoBERT ở nhóm cả hai: 73,8 đến 74,6 so với 71,8, các khoảng tin
   cậy trùng nhau gần hết. Chưa kiểm định cặp mô hình trong từng nhóm.

Khi chỉ giữ 655 dòng `dong_y`, mọi con số tăng (PhoBERT nhóm thường 95,6; cả hai 83,0) nhưng thứ
tự và hai kết luận đầu giữ nguyên. Hiệu ở nhóm chuyển ý về accuracy yếu đi, p quanh 0,05.

Có một điểm trái dự đoán: mô hình từ điển làm nhóm phủ định tốt hơn nhóm thường 11,6 điểm. Chưa
tìm nguyên nhân. `[CẦN KIỂM: phân bố nhãn gốc của nhóm phủ định so với nhóm thường, và luật đảo
dấu của mô hình từ điển.]`

## 5. GIỚI HẠN PHẢI NÓI TRONG BÁO CÁO

- Tập chẩn đoán không phải mẫu ngẫu nhiên của tập kiểm tra: ứng viên được lọc bằng từ khoá, ưu tiên
  câu dài 5 đến 40 từ (thực tế các dòng được chọn dài 7 đến 42 từ). Nhóm thường ở đây không đại diện cho toàn tập kiểm tra.
- Nhãn hiện tượng do một người gán. Độ nhất quán chưa đo.
- Mô hình đã được chọn và báo cáo trên tập kiểm tra; tập chẩn đoán là một lát cắt của chính tập
  đó, không phải dữ liệu mới.
- Nhóm cả hai chỉ có 84 dòng, khoảng tin cậy rộng gần 18 điểm.

## 6. KIỂM CHỨNG

```
10 passed   (tests/test_finalize_diagnostic.py)
```

- Trên dữ liệu thật, accuracy và macro-F1 của PhoBERT ở nhóm thường và chuyển ý khớp
  `sklearn` tới 12 chữ số.
- Lệnh dừng nếu nhãn thật trong file dự đoán khác `nhan_goc` của CSV, hoặc thiếu dự đoán.
- `chot` chạy thật: dừng đúng với thông báo chưa có kappa.
- Chưa kiểm: `chot` chưa từng ghi file thật; `train.py` chưa từng đọc file đó.

## 7. VIỆC CỦA BẠN

Không có việc mới. Hai việc cũ còn nguyên: sao lưu `data/diagnostic/`, và từ 27/10 gán lại
`data/diagnostic/gan_lai_60.xlsx`. Sau khi kappa đạt, báo để chạy `chot` rồi `cham` lại.

## 8. BỔ SUNG 13/10 (trưa)

Các số ở mục 4 không còn là sơ bộ: tập đã chốt và kết quả đã vào mục 4.6 của báo cáo, kèm bảng theo
dấu hiệu và bảng so với PhoBERT trong từng nhóm. Điểm lạ về mô hình từ điển ở cuối mục 4 đã có lời
giải. Xem `CD1.8f_chot-tap-va-ket-qua-chan-doan.md`.
