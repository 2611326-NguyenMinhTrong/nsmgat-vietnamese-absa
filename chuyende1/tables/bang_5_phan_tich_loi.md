Bảng A. Lỗi theo cặp lớp, trung bình các seed. Sáu cột giữa là phần trăm trên tổng số lỗi của mô hình; ba cột cuối là tỉ lệ tìm lại của từng lớp (%).

| Mô hình | Số lỗi | tiêu cực thành trung tính | tiêu cực thành tích cực | trung tính thành tiêu cực | trung tính thành tích cực | tích cực thành tiêu cực | tích cực thành trung tính | Tìm lại tiêu cực | Tìm lại trung tính | Tìm lại tích cực |
|---|---|---|---|---|---|---|---|---|---|---|
| Từ điển cảm xúc | 1702 | 0,0 | 30,5 | 12,9 | 35,1 | 21,5 | 0,0 | 76,5 | 0,0 | 90,1 |
| BiLSTM với attention | 916 | 10,7 | 15,2 | 19,5 | 20,2 | 18,9 | 15,6 | 89,3 | 55,5 | 91,5 |
| PhoBERT tinh chỉnh | 552 | 15,9 | 8,0 | 19,7 | 24,9 | 9,6 | 21,9 | 94,0 | 69,9 | 95,3 |
| ASGCN | 574 | 12,1 | 8,0 | 22,8 | 27,1 | 10,6 | 19,4 | 94,8 | 64,9 | 95,3 |
| ASGCN nối câu | 558 | 10,0 | 7,3 | 23,0 | 25,9 | 12,2 | 21,5 | 95,6 | 66,6 | 94,9 |
| Sentic-GCN | 565 | 16,9 | 7,5 | 17,4 | 21,8 | 9,2 | 27,3 | 93,8 | 72,9 | 94,4 |

Bảng B. Macro-F1 theo khía cạnh (%), trung bình các seed, xếp theo số mẫu huấn luyện giảm dần.

| Khía cạnh | Mẫu huấn luyện | Mẫu kiểm tra | Trung tính trong kiểm tra (%) | Từ điển cảm xúc | BiLSTM với attention | PhoBERT tinh chỉnh | ASGCN | ASGCN nối câu | Sentic-GCN |
|---|---|---|---|---|---|---|---|---|---|
| GENERAL | 4.866 | 1.381 | 6,0 | 53,2 | 81,2 | 86,0 | 85,3 | 85,3 | 87,4 |
| PERFORMANCE | 4.140 | 1.172 | 9,9 | 55,9 | 71,7 | 81,3 | 81,1 | 81,1 | 82,4 |
| BATTERY | 3.604 | 1.014 | 9,1 | 48,9 | 72,8 | 83,8 | 83,3 | 84,0 | 83,6 |
| FEATURES | 2.642 | 711 | 7,3 | 52,2 | 64,2 | 79,1 | 76,5 | 78,8 | 81,1 |
| CAMERA | 2.146 | 588 | 12,1 | 51,5 | 82,3 | 87,1 | 85,8 | 87,5 | 87,0 |
| PRICE | 2.061 | 569 | 57,6 | 35,3 | 75,9 | 85,3 | 83,7 | 84,1 | 82,7 |
| SER&ACC | 1.995 | 593 | 4,6 | 56,6 | 62,6 | 77,7 | 71,9 | 73,4 | 76,3 |
| DESIGN | 1.378 | 398 | 7,0 | 47,7 | 59,2 | 76,5 | 76,4 | 76,1 | 77,3 |
| SCREEN | 949 | 269 | 6,3 | 53,4 | 67,1 | 76,8 | 73,9 | 76,0 | 78,7 |
| STORAGE | 91 | 27 | 11,1 | 52,6 | 48,6 | 80,7 | 77,5 | 76,9 | 76,7 |

Tương quan hạng Spearman giữa số mẫu huấn luyện của khía cạnh và macro-F1 trên khía cạnh đó (10 khía cạnh): Từ điển cảm xúc rho = 0,05, p = 0,881; BiLSTM với attention rho = 0,66, p = 0,038; PhoBERT tinh chỉnh rho = 0,60, p = 0,067; ASGCN rho = 0,58, p = 0,082; ASGCN nối câu rho = 0,65, p = 0,043; Sentic-GCN rho = 0,76, p = 0,011.

Bảng C. Accuracy theo độ dài câu. Mỗi ô: trung bình các seed (%), khoảng tin cậy 95 % trong ngoặc vuông; nhóm khác nhóm đầu có thêm hiệu so với nhóm đầu (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (2.187 câu).

| Mô hình | Đến 20 từ (n = 990) | 21 đến 40 từ (n = 3476) | 41 đến 80 từ (n = 1822) | Trên 80 từ (n = 434) |
|---|---|---|---|---|
| Từ điển cảm xúc | 80,4 [77,5; 83,1] | 76,2 [74,5; 77,8]; -4,3, p 0,009 | 70,0 [67,3; 72,8]; -10,4, p < 0,001 | 69,1 [63,6; 74,7]; -11,3, p < 0,001 |
| BiLSTM với attention | 92,1 [90,4; 93,7] | 88,2 [87,2; 89,2]; -3,8, p < 0,001 | 82,4 [80,7; 84,1]; -9,6, p < 0,001 | 75,2 [71,2; 79,1]; -16,9, p < 0,001 |
| PhoBERT tinh chỉnh | 95,0 [93,6; 96,3] | 92,8 [92,0; 93,6]; -2,2, p 0,006 | 89,9 [88,5; 91,2]; -5,1, p < 0,001 | 84,5 [80,8; 87,9]; -10,5, p < 0,001 |
| ASGCN | 94,8 [93,6; 96,0] | 92,3 [91,5; 93,1]; -2,5, p < 0,001 | 89,7 [88,3; 91,0]; -5,2, p < 0,001 | 84,4 [80,6; 87,8]; -10,5, p < 0,001 |
| ASGCN nối câu | 94,9 [93,6; 96,1] | 92,5 [91,7; 93,3]; -2,4, p 0,002 | 89,9 [88,6; 91,3]; -5,0, p < 0,001 | 85,2 [81,5; 88,6]; -9,7, p < 0,001 |
| Sentic-GCN | 95,2 [93,8; 96,5] | 92,5 [91,7; 93,3]; -2,7, p 0,002 | 89,5 [88,1; 90,9]; -5,7, p < 0,001 | 84,7 [81,0; 88,0]; -10,6, p < 0,001 |

Bảng D. Accuracy theo loại câu. Mỗi ô: trung bình các seed (%), khoảng tin cậy 95 % trong ngoặc vuông; nhóm khác nhóm đầu có thêm hiệu so với nhóm đầu (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (2.187 câu).

| Mô hình | Nhiều khía cạnh, cùng nhãn (n = 2840) | Một khía cạnh (n = 290) | Nhiều khía cạnh, trái nhãn (n = 3592) |
|---|---|---|---|
| Từ điển cảm xúc | 94,6 [93,1; 96,0] | 83,8 [79,5; 87,9]; -10,8, p < 0,001 | 58,2 [56,8; 59,6]; -36,4, p < 0,001 |
| BiLSTM với attention | 94,5 [93,6; 95,2] | 88,0 [84,8; 91,1]; -6,5, p < 0,001 | 79,9 [78,7; 81,0]; -14,6, p < 0,001 |
| PhoBERT tinh chỉnh | 96,9 [96,3; 97,5] | 91,8 [88,9; 94,4]; -5,1, p < 0,001 | 87,8 [86,7; 88,8]; -9,1, p < 0,001 |
| ASGCN | 97,3 [96,7; 97,8] | 92,6 [89,8; 95,1]; -4,7, p < 0,001 | 86,8 [85,8; 87,8]; -10,5, p < 0,001 |
| ASGCN nối câu | 97,1 [96,5; 97,6] | 92,9 [90,1; 95,5]; -4,2, p 0,001 | 87,3 [86,3; 88,3]; -9,8, p < 0,001 |
| Sentic-GCN | 96,4 [95,7; 97,0] | 93,0 [90,4; 95,4]; -3,4, p 0,008 | 87,7 [86,6; 88,7]; -8,7, p < 0,001 |

Bảng E. Câu trái nhãn (986 câu). Sụp nhãn: câu bị đoán cùng một nhãn cho mọi khía cạnh. Hai cột cuối chỉ tính trên 836 câu có đúng hai nhãn khác nhau: trong các lỗi ở đó, bao nhiêu phần trăm rơi vào nhãn còn lại đang có trong câu chứ không phải nhãn thứ ba.

| Mô hình | Câu sụp nhãn (%) | Số lỗi ở câu hai nhãn | Lỗi rơi vào nhãn kia của câu (%) |
|---|---|---|---|
| Từ điển cảm xúc | 100,0 | 1119 | 87,4 |
| BiLSTM với attention | 18,9 | 561 | 64,5 |
| PhoBERT tinh chỉnh | 11,3 | 340 | 63,4 |
| ASGCN | 13,9 | 370 | 66,8 |
| ASGCN nối câu | 12,9 | 356 | 65,0 |
| Sentic-GCN | 10,2 | 345 | 60,3 |

Bảng F. Số mẫu sai trên 6.722 mẫu kiểm tra. Luôn sai: sai ở mọi seed.

| Mô hình | Luôn sai | Sai ở ít nhất một seed |
|---|---|---|
| Từ điển cảm xúc | 1.683 (25,0 %) | 1.720 (25,6 %) |
| BiLSTM với attention | 419 (6,2 %) | 1.577 (23,5 %) |
| PhoBERT tinh chỉnh | 307 (4,6 %) | 854 (12,7 %) |
| ASGCN | 291 (4,3 %) | 946 (14,1 %) |
| ASGCN nối câu | 301 (4,5 %) | 876 (13,0 %) |
| Sentic-GCN | 322 (4,8 %) | 855 (12,7 %) |

Bảng G. Giao lỗi của bốn mô hình dùng PhoBERT (PhoBERT tinh chỉnh, ASGCN, ASGCN nối câu, Sentic-GCN).

| Số mô hình luôn sai trên mẫu | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Số mẫu | 6.272 | 126 | 68 | 65 | 191 |

Cả bốn mô hình luôn sai trên 191 mẫu (2,8 % tập kiểm tra). Không lần chạy nào trong 12 lần sai trên 5.520 mẫu (82,1 %).

Bảng H. Đặc điểm của 191 mẫu cả bốn mô hình luôn sai, so với toàn tập kiểm tra.

| Đặc điểm | Trong nhóm cùng sai | Tỉ lệ trong nhóm (%) | Tỉ lệ trong toàn tập (%) |
|---|---|---|---|
| Nhãn thật tiêu cực | 31 | 16,2 | 32,9 |
| Nhãn thật trung tính | 103 | 53,9 | 12,2 |
| Nhãn thật tích cực | 57 | 29,8 | 55,0 |
| Thuộc câu trái nhãn | 166 | 86,9 | 53,4 |
| Khía cạnh GENERAL | 21 | 11,0 | 20,5 |
| Khía cạnh PERFORMANCE | 34 | 17,8 | 17,4 |
| Khía cạnh BATTERY | 34 | 17,8 | 15,1 |
| Khía cạnh FEATURES | 27 | 14,1 | 10,6 |
| Khía cạnh SER&ACC | 8 | 4,2 | 8,8 |
| Khía cạnh CAMERA | 18 | 9,4 | 8,7 |
| Khía cạnh PRICE | 29 | 15,2 | 8,5 |
| Khía cạnh DESIGN | 11 | 5,8 | 5,9 |
| Khía cạnh SCREEN | 7 | 3,7 | 4,0 |
| Khía cạnh STORAGE | 2 | 1,0 | 0,4 |

Bảng I. Trong 191 mẫu đó, nhãn thật bị đoán thành nhãn nào (nhãn được đoán nhiều nhất trong 12 lần chạy).

| Nhãn thật thành nhãn đoán | Số mẫu | Tỉ lệ (%) |
|---|---|---|
| trung tính thành tích cực | 57 | 29,8 |
| trung tính thành tiêu cực | 46 | 24,1 |
| tích cực thành tiêu cực | 30 | 15,7 |
| tích cực thành trung tính | 27 | 14,1 |
| tiêu cực thành tích cực | 17 | 8,9 |
| tiêu cực thành trung tính | 14 | 7,3 |
