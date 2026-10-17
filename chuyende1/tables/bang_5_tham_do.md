Sinh bởi scripts/probe_oracle_rules.py. Mô hình: PhoBERT tinh chỉnh, trung bình 5 seed (42, 1337, 2024, 7, 123).

Bảng P1a. Luật lật cực lý tưởng trên tập chẩn đoán: phạm vi là các dòng người chú thích gán nhóm đó. Số lỗi là trung bình mỗi seed; macro-F1 tính trong nhóm (%).

| Nhóm | Số dòng | Lỗi | Lỗi ngược cực | Lỗi có nhãn gốc trung tính | Lỗi ở dòng không đồng ý nhãn gốc | Macro-F1 | Sau khi lật | Tăng (điểm) |
|---|---|---|---|---|---|---|---|---|
| Phủ định | 119 | 11,6 | 1,2 | 8,8 | 6,0 | 88,4 | 89,3 | 0,88 |
| Chuyển ý | 181 | 26,6 | 1,4 | 21,0 | 15,2 | 84,3 | 85,0 | 0,71 |
| Cả hai | 84 | 21,8 | 0,6 | 15,8 | 13,0 | 72,7 | 73,3 | 0,64 |
| Thường | 415 | 34,8 | 2,8 | 23,8 | 18,6 | 91,8 | 92,5 | 0,71 |

Bảng P1b. Cận trên trên toàn tập kiểm tra (6722 mẫu; macro-F1 86,70 %, 551,8 lỗi mỗi seed, trong đó 96,8 lỗi ngược cực). 3676 mẫu thuộc câu có từ khoá phủ định, 4268 mẫu thuộc câu có từ khoá phủ định hoặc chuyển ý.

| Luật lý tưởng sửa | Số lỗi sửa mỗi seed | Macro-F1 tăng (điểm) | Accuracy tăng (điểm) |
|---|---|---|---|
| Lỗi ngược cực ở câu có từ khoá phủ định | 59,4 | 0,71 | 0,88 |
| Lỗi ngược cực ở mọi chỗ | 96,8 | 1,16 | 1,44 |
| Mọi lỗi ở câu có từ khoá phủ định hoặc chuyển ý | 420,0 | 10,23 | 6,25 |

Bảng P2. Luật từ khoá so với nhãn hiện tượng của người chú thích. Ước lượng theo ô (nhóm từ khoá, nhãn gốc) cho 4071 mẫu của tập kiểm tra thuộc câu 5 đến 40 từ và không chỉ chứa từ ngờ (ngoài quần thể: 2077 mẫu ở câu ngoài độ dài, 574 mẫu ở câu chỉ có từ ngờ). Dùng 794 dòng của tập chẩn đoán (5 dòng ngoài quần thể). Khoảng tin cậy 95 % bằng bootstrap trong từng ô.

Hai cột cuối đếm trên cả tập chẩn đoán: dòng có hiện tượng mà câu không có từ khoá của luật, và trong đó bao nhiêu dòng có từ ngờ.

| Luật | Độ chính xác (%) | KTC 95 % | Độ phủ (%) | KTC 95 % | Dòng luật bắt | Trong đó đúng | Dòng bị bỏ sót | Có từ ngờ |
|---|---|---|---|---|---|---|---|---|
| Câu có từ khoá phủ định | 49,5 | 43,8 – 55,2 | 94,7 | 90,2 – 98,1 | 399 | 191 | 12 | 2 |
| Câu có từ nối chuyển ý | 58,2 | 52,6 – 63,8 | 59,9 | 52,1 – 68,8 | 345 | 211 | 52 | 19 |

Bảng P3. Từ khoá phủ định và từ đứng ngay sau nó trên cây VnCoreNLP, 2187 câu của tập kiểm tra. Ba cột tỉ lệ và khoảng cách tính trên các lượt có từ đứng sau thuộc cùng câu; khoảng cách tuyến tính luôn là 1.

| Dạng | Lượt | Có từ đứng sau | Gán nhãn phó từ (%) | Kề nhau trên cây (%) | Cách từ 3 cạnh (%) | Khoảng cách trên cây trung bình |
|---|---|---|---|---|---|---|
| Dạng chuẩn | 1010 | 969 | 99,7 | 94,4 | 1,3 | 1,08 |
| Dạng viết tắt | 1009 | 961 | 0,0 | 72,5 | 12,2 | 1,51 |
