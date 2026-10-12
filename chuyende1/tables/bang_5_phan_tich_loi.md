Bảng A. Lỗi theo cặp lớp, trung bình ba seed. Sáu cột giữa là phần trăm trên tổng số lỗi của mô hình; ba cột cuối là tỉ lệ tìm lại của từng lớp (%).

| Mô hình | Số lỗi | tiêu cực thành trung tính | tiêu cực thành tích cực | trung tính thành tiêu cực | trung tính thành tích cực | tích cực thành tiêu cực | tích cực thành trung tính | Tìm lại tiêu cực | Tìm lại trung tính | Tìm lại tích cực |
|---|---|---|---|---|---|---|---|---|---|---|
| Từ điển cảm xúc | 1701 | 0,0 | 30,4 | 12,9 | 35,1 | 21,5 | 0,0 | 76,6 | 0,0 | 90,1 |
| BiLSTM với attention | 913 | 10,6 | 15,7 | 19,8 | 20,2 | 18,5 | 15,3 | 89,2 | 55,3 | 91,7 |
| PhoBERT tinh chỉnh | 547 | 13,8 | 8,0 | 22,1 | 26,0 | 10,5 | 19,5 | 94,6 | 67,8 | 95,6 |
| ASGCN | 583 | 10,3 | 7,9 | 24,8 | 27,3 | 11,0 | 18,6 | 95,2 | 62,8 | 95,3 |
| ASGCN nối gốc | 562 | 9,5 | 7,2 | 23,7 | 26,1 | 12,6 | 20,9 | 95,8 | 65,7 | 94,9 |
| Sentic-GCN | 575 | 16,3 | 7,8 | 17,5 | 21,7 | 9,2 | 27,6 | 93,7 | 72,4 | 94,3 |

Bảng B. Macro-F1 theo khía cạnh (%), trung bình ba seed, xếp theo số mẫu huấn luyện giảm dần.

| Khía cạnh | Mẫu huấn luyện | Mẫu kiểm tra | Trung tính trong kiểm tra (%) | Từ điển cảm xúc | BiLSTM với attention | PhoBERT tinh chỉnh | ASGCN | ASGCN nối gốc | Sentic-GCN |
|---|---|---|---|---|---|---|---|---|---|
| GENERAL | 4.866 | 1.381 | 6,0 | 53,2 | 81,1 | 86,6 | 85,3 | 85,1 | 87,3 |
| PERFORMANCE | 4.140 | 1.172 | 9,9 | 55,9 | 71,8 | 80,3 | 80,2 | 81,3 | 81,9 |
| BATTERY | 3.604 | 1.014 | 9,1 | 49,0 | 73,0 | 84,4 | 82,9 | 83,1 | 83,2 |
| FEATURES | 2.642 | 711 | 7,3 | 52,2 | 63,6 | 78,1 | 76,9 | 78,9 | 80,4 |
| CAMERA | 2.146 | 588 | 12,1 | 51,6 | 81,9 | 86,9 | 85,2 | 87,7 | 87,3 |
| PRICE | 2.061 | 569 | 57,6 | 35,3 | 76,3 | 85,4 | 83,6 | 83,7 | 82,1 |
| SER&ACC | 1.995 | 593 | 4,6 | 56,6 | 61,4 | 76,5 | 68,9 | 71,1 | 75,8 |
| DESIGN | 1.378 | 398 | 7,0 | 47,6 | 58,6 | 76,2 | 75,0 | 74,1 | 77,7 |
| SCREEN | 949 | 269 | 6,3 | 53,5 | 67,2 | 74,7 | 72,9 | 78,4 | 78,7 |
| STORAGE | 91 | 27 | 11,1 | 52,6 | 48,2 | 81,6 | 76,2 | 77,7 | 76,2 |

Tương quan hạng Spearman giữa số mẫu huấn luyện của khía cạnh và macro-F1 trên khía cạnh đó (10 khía cạnh): Từ điển cảm xúc rho = 0,05, p = 0,881; BiLSTM với attention rho = 0,66, p = 0,038; PhoBERT tinh chỉnh rho = 0,52, p = 0,128; ASGCN rho = 0,70, p = 0,025; ASGCN nối gốc rho = 0,65, p = 0,043; Sentic-GCN rho = 0,76, p = 0,011.

Bảng C. Accuracy theo độ dài câu. Mỗi ô: trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; nhóm khác nhóm đầu có thêm hiệu so với nhóm đầu (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (2.187 câu).

| Mô hình | Đến 20 từ (n = 990) | 21 đến 40 từ (n = 3476) | 41 đến 80 từ (n = 1822) | Trên 80 từ (n = 434) |
|---|---|---|---|---|
| Từ điển cảm xúc | 80,5 [77,6; 83,1] | 76,2 [74,5; 77,8]; -4,3, p 0,008 | 70,1 [67,3; 72,8]; -10,4, p < 0,001 | 69,1 [63,6; 74,7]; -11,3, p < 0,001 |
| BiLSTM với attention | 92,1 [90,4; 93,7] | 88,2 [87,2; 89,2]; -3,9, p < 0,001 | 82,5 [80,7; 84,3]; -9,5, p < 0,001 | 75,2 [71,0; 79,2]; -16,9, p < 0,001 |
| PhoBERT tinh chỉnh | 94,9 [93,5; 96,2] | 92,8 [92,0; 93,6]; -2,1, p 0,014 | 90,1 [88,7; 91,5]; -4,8, p < 0,001 | 84,6 [80,8; 88,1]; -10,3, p < 0,001 |
| ASGCN | 94,6 [93,2; 95,9] | 92,1 [91,3; 92,9]; -2,5, p 0,002 | 89,7 [88,3; 91,1]; -4,9, p < 0,001 | 84,5 [80,7; 87,9]; -10,1, p < 0,001 |
| ASGCN nối gốc | 94,7 [93,4; 96,0] | 92,5 [91,7; 93,3]; -2,2, p 0,006 | 89,8 [88,4; 91,2]; -4,9, p < 0,001 | 85,3 [81,6; 88,7]; -9,4, p < 0,001 |
| Sentic-GCN | 95,3 [93,9; 96,6] | 92,4 [91,6; 93,2]; -2,9, p < 0,001 | 89,2 [87,8; 90,6]; -6,1, p < 0,001 | 84,3 [80,5; 87,7]; -11,1, p < 0,001 |

Bảng D. Accuracy theo loại câu. Mỗi ô: trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; nhóm khác nhóm đầu có thêm hiệu so với nhóm đầu (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (2.187 câu).

| Mô hình | Nhiều khía cạnh, cùng nhãn (n = 2840) | Một khía cạnh (n = 290) | Nhiều khía cạnh, trái nhãn (n = 3592) |
|---|---|---|---|
| Từ điển cảm xúc | 94,6 [93,1; 96,0] | 83,9 [79,7; 88,0]; -10,7, p < 0,001 | 58,2 [56,8; 59,6]; -36,4, p < 0,001 |
| BiLSTM với attention | 94,5 [93,7; 95,3] | 88,3 [85,0; 91,4]; -6,2, p < 0,001 | 79,9 [78,7; 81,1]; -14,6, p < 0,001 |
| PhoBERT tinh chỉnh | 97,1 [96,5; 97,7] | 92,3 [89,4; 94,9]; -4,8, p < 0,001 | 87,7 [86,6; 88,7]; -9,4, p < 0,001 |
| ASGCN | 97,5 [97,0; 98,0] | 92,6 [89,8; 95,2]; -4,9, p < 0,001 | 86,3 [85,3; 87,4]; -11,2, p < 0,001 |
| ASGCN nối gốc | 97,2 [96,6; 97,7] | 93,1 [90,4; 95,7]; -4,1, p 0,002 | 87,2 [86,1; 88,2]; -10,0, p < 0,001 |
| Sentic-GCN | 96,3 [95,6; 96,9] | 93,1 [90,4; 95,6]; -3,2, p 0,013 | 87,5 [86,4; 88,5]; -8,9, p < 0,001 |

Bảng E. Câu trái nhãn (986 câu). Sụp nhãn: câu bị đoán cùng một nhãn cho mọi khía cạnh. Hai cột cuối chỉ tính trên 836 câu có đúng hai nhãn khác nhau: trong các lỗi ở đó, bao nhiêu phần trăm rơi vào nhãn còn lại đang có trong câu chứ không phải nhãn thứ ba.

| Mô hình | Câu sụp nhãn (%) | Số lỗi ở câu hai nhãn | Lỗi rơi vào nhãn kia của câu (%) |
|---|---|---|---|
| Từ điển cảm xúc | 100,0 | 1119 | 87,4 |
| BiLSTM với attention | 19,1 | 559 | 64,1 |
| PhoBERT tinh chỉnh | 12,0 | 339 | 64,7 |
| ASGCN | 15,0 | 383 | 67,6 |
| ASGCN nối gốc | 13,2 | 362 | 65,5 |
| Sentic-GCN | 10,3 | 350 | 59,9 |

Bảng F. Số mẫu sai trên 6.722 mẫu kiểm tra. Luôn sai: sai ở cả ba seed.

| Mô hình | Luôn sai | Sai ở ít nhất một seed |
|---|---|---|
| Từ điển cảm xúc | 1.684 (25,1 %) | 1.717 (25,5 %) |
| BiLSTM với attention | 524 (7,8 %) | 1.371 (20,4 %) |
| PhoBERT tinh chỉnh | 351 (5,2 %) | 761 (11,3 %) |
| ASGCN | 355 (5,3 %) | 832 (12,4 %) |
| ASGCN nối gốc | 369 (5,5 %) | 766 (11,4 %) |
| Sentic-GCN | 374 (5,6 %) | 787 (11,7 %) |

Bảng G. Giao lỗi của bốn mô hình dùng PhoBERT (PhoBERT tinh chỉnh, ASGCN, ASGCN nối gốc, Sentic-GCN).

| Số mô hình luôn sai trên mẫu | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Số mẫu | 6.175 | 159 | 86 | 90 | 212 |

Cả bốn mô hình luôn sai trên 212 mẫu (3,2 % tập kiểm tra). Không lần chạy nào trong 12 lần sai trên 5.636 mẫu (83,8 %).

Bảng H. Đặc điểm của 212 mẫu cả bốn mô hình luôn sai, so với toàn tập kiểm tra.

| Đặc điểm | Trong nhóm cùng sai | Tỉ lệ trong nhóm (%) | Tỉ lệ trong toàn tập (%) |
|---|---|---|---|
| Nhãn thật tiêu cực | 35 | 16,5 | 32,9 |
| Nhãn thật trung tính | 114 | 53,8 | 12,2 |
| Nhãn thật tích cực | 63 | 29,7 | 55,0 |
| Thuộc câu trái nhãn | 185 | 87,3 | 53,4 |
| Khía cạnh GENERAL | 27 | 12,7 | 20,5 |
| Khía cạnh PERFORMANCE | 37 | 17,5 | 17,4 |
| Khía cạnh BATTERY | 36 | 17,0 | 15,1 |
| Khía cạnh FEATURES | 31 | 14,6 | 10,6 |
| Khía cạnh SER&ACC | 9 | 4,2 | 8,8 |
| Khía cạnh CAMERA | 20 | 9,4 | 8,7 |
| Khía cạnh PRICE | 30 | 14,2 | 8,5 |
| Khía cạnh DESIGN | 12 | 5,7 | 5,9 |
| Khía cạnh SCREEN | 8 | 3,8 | 4,0 |
| Khía cạnh STORAGE | 2 | 0,9 | 0,4 |

Bảng I. Trong 212 mẫu đó, nhãn thật bị đoán thành nhãn nào (nhãn được đoán nhiều nhất trong 12 lần chạy).

| Nhãn thật thành nhãn đoán | Số mẫu | Tỉ lệ (%) |
|---|---|---|
| trung tính thành tích cực | 60 | 28,3 |
| trung tính thành tiêu cực | 54 | 25,5 |
| tích cực thành tiêu cực | 33 | 15,6 |
| tích cực thành trung tính | 30 | 14,2 |
| tiêu cực thành tích cực | 18 | 8,5 |
| tiêu cực thành trung tính | 17 | 8,0 |
