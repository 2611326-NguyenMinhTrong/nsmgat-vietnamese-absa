Độ nhất quán của nhãn hiện tượng: kappa 0,733 trên 60 dòng gán lại. **Lần gán lại ngày 13/10/2026 cách lần gán đầu không quá 8 ngày, không đủ 14 ngày như quy ước; kappa này là cận trên.**

Accuracy theo nhóm hiện tượng, toàn bộ dòng. Mỗi ô: giá trị trung bình các seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (603 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 415) | Phủ định (n = 119) | Chuyển ý (n = 181) | Cả hai (n = 84) |
|---|---|---|---|---|
| Từ điển cảm xúc | 54,7 [49,8; 59,4] | 66,4 [57,8; 74,7]; +11,7, p 0,016 | 45,3 [38,1; 52,3]; -9,4, p 0,033 | 37,4 [27,9; 46,7]; -17,3, p 0,001 |
| BiLSTM với attention | 85,7 [82,7; 88,6] | 81,8 [75,6; 87,6]; -3,8, p 0,260 | 71,6 [65,9; 76,9]; -14,1, p < 0,001 | 70,7 [62,7; 78,6]; -15,0, p 0,001 |
| PhoBERT tinh chỉnh | 91,6 [89,2; 93,8] | 90,3 [85,4; 94,4]; -1,4, p 0,593 | 85,3 [80,7; 89,6]; -6,3, p 0,013 | 74,0 [65,5; 82,2]; -17,6, p < 0,001 |
| ASGCN | 90,4 [87,9; 92,7] | 88,7 [83,9; 93,2]; -1,6, p 0,551 | 83,6 [79,2; 87,7]; -6,7, p 0,004 | 74,3 [65,4; 82,5]; -16,1, p < 0,001 |
| ASGCN nối gốc | 91,2 [88,8; 93,5] | 89,4 [84,5; 94,0]; -1,8, p 0,526 | 85,2 [80,6; 89,4]; -6,0, p 0,013 | 74,5 [65,5; 82,9]; -16,7, p < 0,001 |
| Sentic-GCN | 92,3 [89,9; 94,5] | 92,8 [88,3; 96,5]; +0,5, p 0,810 | 87,1 [82,8; 91,0]; -5,2, p 0,028 | 75,2 [66,7; 83,3]; -17,1, p < 0,001 |

Macro-F1 theo nhóm hiện tượng, toàn bộ dòng. Mỗi ô: giá trị trung bình các seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (603 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 415) | Phủ định (n = 119) | Chuyển ý (n = 181) | Cả hai (n = 84) |
|---|---|---|---|---|
| Từ điển cảm xúc | 45,5 [42,2; 48,4] | 50,0 [44,9; 54,6]; +4,5, p 0,121 | 36,3 [31,2; 40,8]; -9,2, p < 0,001 | 30,5 [23,3; 36,9]; -14,9, p < 0,001 |
| BiLSTM với attention | 85,6 [82,6; 88,4] | 77,2 [69,4; 84,1]; -8,4, p 0,026 | 69,0 [63,4; 74,1]; -16,6, p < 0,001 | 68,7 [60,4; 76,1]; -16,9, p < 0,001 |
| PhoBERT tinh chỉnh | 91,8 [89,5; 94,0] | 88,4 [82,9; 93,0]; -3,4, p 0,201 | 84,3 [79,3; 88,7]; -7,5, p 0,003 | 72,7 [63,8; 80,8]; -19,1, p < 0,001 |
| ASGCN | 90,5 [88,1; 92,7] | 85,7 [80,0; 90,5]; -4,8, p 0,084 | 82,3 [77,9; 86,2]; -8,2, p < 0,001 | 73,1 [64,0; 81,0]; -17,4, p < 0,001 |
| ASGCN nối gốc | 91,4 [89,0; 93,6] | 87,0 [81,1; 92,0]; -4,4, p 0,127 | 84,2 [79,6; 88,3]; -7,2, p 0,003 | 72,9 [63,6; 80,9]; -18,5, p < 0,001 |
| Sentic-GCN | 92,6 [90,2; 94,6] | 91,8 [86,7; 95,9]; -0,8, p 0,782 | 86,4 [81,9; 90,4]; -6,1, p 0,008 | 74,7 [65,8; 82,4]; -17,9, p < 0,001 |

Accuracy theo nhóm hiện tượng, chỉ các dòng người chú thích đồng ý với nhãn gốc. Mỗi ô: giá trị trung bình các seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (526 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 363) | Phủ định (n = 105) | Chuyển ý (n = 132) | Cả hai (n = 55) |
|---|---|---|---|---|
| Từ điển cảm xúc | 59,6 [54,3; 64,8] | 74,3 [65,8; 82,3]; +14,7, p 0,004 | 56,1 [47,4; 64,6]; -3,6, p 0,489 | 49,8 [36,8; 62,7]; -9,8, p 0,161 |
| BiLSTM với attention | 90,6 [87,9; 93,1] | 87,0 [81,5; 92,2]; -3,6, p 0,223 | 80,0 [74,0; 85,7]; -10,6, p < 0,001 | 82,9 [74,2; 90,8]; -7,7, p 0,066 |
| PhoBERT tinh chỉnh | 95,5 [93,6; 97,3] | 94,7 [90,9; 97,9]; -0,9, p 0,695 | 91,4 [87,0; 95,3]; -4,2, p 0,072 | 84,0 [74,7; 92,1]; -11,5, p 0,004 |
| ASGCN | 94,5 [92,5; 96,3] | 93,5 [89,5; 96,9]; -1,0, p 0,683 | 89,7 [85,4; 93,6]; -4,8, p 0,035 | 82,5 [72,7; 91,3]; -11,9, p 0,006 |
| ASGCN nối gốc | 95,0 [93,1; 96,9] | 94,1 [89,8; 97,6]; -0,9, p 0,693 | 91,4 [87,1; 95,0]; -3,7, p 0,085 | 82,5 [72,5; 91,5]; -12,5, p 0,007 |
| Sentic-GCN | 96,0 [94,1; 97,7] | 95,8 [92,3; 98,6]; -0,2, p 0,970 | 91,5 [87,1; 95,5]; -4,5, p 0,048 | 81,8 [71,9; 90,6]; -14,2, p < 0,001 |

Macro-F1 theo nhóm hiện tượng, chỉ các dòng người chú thích đồng ý với nhãn gốc. Mỗi ô: giá trị trung bình các seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (526 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 363) | Phủ định (n = 105) | Chuyển ý (n = 132) | Cả hai (n = 55) |
|---|---|---|---|---|
| Từ điển cảm xúc | 48,4 [45,0; 51,4] | 53,7 [48,6; 58,0]; +5,3, p 0,074 | 42,2 [36,3; 47,5]; -6,2, p 0,054 | 37,4 [28,1; 45,5]; -10,9, p 0,014 |
| BiLSTM với attention | 90,5 [87,8; 93,0] | 82,4 [74,3; 89,0]; -8,2, p 0,024 | 75,3 [68,7; 81,3]; -15,2, p < 0,001 | 77,1 [65,6; 86,4]; -13,4, p 0,006 |
| PhoBERT tinh chỉnh | 95,5 [93,6; 97,2] | 92,9 [87,8; 97,0]; -2,6, p 0,265 | 88,5 [82,6; 93,6]; -7,0, p 0,010 | 78,5 [66,3; 88,3]; -17,0, p < 0,001 |
| ASGCN | 94,5 [92,5; 96,3] | 90,5 [84,6; 95,1]; -4,0, p 0,122 | 86,2 [81,0; 90,7]; -8,3, p 0,001 | 77,2 [64,8; 87,6]; -17,3, p 0,002 |
| ASGCN nối gốc | 95,1 [93,1; 96,8] | 91,9 [86,0; 96,4]; -3,2, p 0,232 | 88,7 [83,3; 93,1]; -6,4, p 0,010 | 76,0 [63,8; 86,5]; -19,1, p < 0,001 |
| Sentic-GCN | 96,1 [94,2; 97,7] | 94,5 [89,9; 98,1]; -1,5, p 0,489 | 89,1 [83,3; 93,9]; -7,0, p 0,006 | 76,4 [63,5; 86,9]; -19,7, p < 0,001 |

Accuracy theo dấu hiệu, toàn bộ dòng. Dòng thuộc nhóm cả hai được tính vào cả hai cột sau. Mỗi ô: giá trị trung bình các seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (603 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 415) | Có phủ định (n = 203) | Có chuyển ý (n = 265) |
|---|---|---|---|
| Từ điển cảm xúc | 54,7 [49,9; 59,5] | 54,4 [47,8; 60,9]; -0,3, p 0,945 | 42,8 [37,2; 48,4]; -11,9, p 0,002 |
| BiLSTM với attention | 85,7 [82,7; 88,6] | 77,2 [72,3; 82,2]; -8,4, p 0,003 | 71,3 [66,7; 75,8]; -14,4, p < 0,001 |
| PhoBERT tinh chỉnh | 91,6 [89,2; 93,8] | 83,5 [79,0; 87,9]; -8,1, p 0,002 | 81,7 [77,5; 85,7]; -9,9, p < 0,001 |
| ASGCN | 90,4 [88,0; 92,6] | 82,8 [78,0; 87,2]; -7,6, p 0,004 | 80,7 [76,5; 84,5]; -9,7, p < 0,001 |
| ASGCN nối gốc | 91,2 [88,8; 93,5] | 83,3 [78,5; 87,6]; -8,0, p 0,003 | 81,8 [77,6; 85,7]; -9,4, p < 0,001 |
| Sentic-GCN | 92,3 [89,9; 94,5] | 85,5 [81,0; 89,6]; -6,8, p 0,007 | 83,3 [79,3; 87,0]; -9,0, p < 0,001 |

Macro-F1 theo dấu hiệu, toàn bộ dòng. Dòng thuộc nhóm cả hai được tính vào cả hai cột sau. Mỗi ô: giá trị trung bình các seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (603 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 415) | Có phủ định (n = 203) | Có chuyển ý (n = 265) |
|---|---|---|---|
| Từ điển cảm xúc | 45,5 [42,2; 48,4] | 42,3 [38,0; 46,3]; -3,2, p 0,224 | 34,5 [30,5; 38,2]; -11,0, p < 0,001 |
| BiLSTM với attention | 85,6 [82,5; 88,4] | 73,5 [68,0; 78,6]; -12,1, p < 0,001 | 68,9 [64,4; 73,2]; -16,7, p < 0,001 |
| PhoBERT tinh chỉnh | 91,8 [89,4; 94,0] | 81,5 [76,5; 85,9]; -10,4, p < 0,001 | 80,6 [76,2; 84,5]; -11,2, p < 0,001 |
| ASGCN | 90,5 [88,1; 92,7] | 80,2 [75,2; 84,8]; -10,3, p < 0,001 | 79,4 [75,2; 83,1]; -11,1, p < 0,001 |
| ASGCN nối gốc | 91,4 [89,0; 93,6] | 80,8 [75,7; 85,3]; -10,6, p < 0,001 | 80,6 [76,3; 84,5]; -10,8, p < 0,001 |
| Sentic-GCN | 92,6 [90,3; 94,6] | 84,2 [79,2; 88,4]; -8,4, p 0,001 | 82,7 [78,5; 86,3]; -9,9, p < 0,001 |

Accuracy theo dấu hiệu, chỉ các dòng người chú thích đồng ý với nhãn gốc. Dòng thuộc nhóm cả hai được tính vào cả hai cột sau. Mỗi ô: giá trị trung bình các seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (526 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 363) | Có phủ định (n = 160) | Có chuyển ý (n = 187) |
|---|---|---|---|
| Từ điển cảm xúc | 59,6 [54,6; 64,7] | 65,9 [58,6; 73,1]; +6,3, p 0,158 | 54,2 [47,1; 61,4]; -5,4, p 0,220 |
| BiLSTM với attention | 90,6 [87,9; 93,1] | 85,6 [81,0; 89,9]; -5,0, p 0,046 | 80,9 [75,9; 85,5]; -9,8, p < 0,001 |
| PhoBERT tinh chỉnh | 95,5 [93,7; 97,2] | 91,0 [86,9; 94,6]; -4,5, p 0,027 | 89,2 [85,1; 92,9]; -6,3, p 0,002 |
| ASGCN | 94,5 [92,5; 96,3] | 89,8 [85,6; 93,7]; -4,7, p 0,035 | 87,6 [83,4; 91,4]; -6,9, p 0,001 |
| ASGCN nối gốc | 95,0 [93,0; 96,9] | 90,1 [85,8; 94,1]; -4,9, p 0,031 | 88,8 [84,6; 92,6]; -6,3, p 0,004 |
| Sentic-GCN | 96,0 [94,1; 97,7] | 91,0 [86,9; 94,7]; -5,0, p 0,018 | 88,7 [84,5; 92,5]; -7,3, p < 0,001 |

Macro-F1 theo dấu hiệu, chỉ các dòng người chú thích đồng ý với nhãn gốc. Dòng thuộc nhóm cả hai được tính vào cả hai cột sau. Mỗi ô: giá trị trung bình các seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (526 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 363) | Có phủ định (n = 160) | Có chuyển ý (n = 187) |
|---|---|---|---|
| Từ điển cảm xúc | 48,4 [45,0; 51,4] | 48,2 [43,6; 52,5]; -0,1, p 0,962 | 40,8 [36,0; 45,4]; -7,6, p 0,009 |
| BiLSTM với attention | 90,5 [87,8; 93,0] | 80,6 [74,4; 85,9]; -10,0, p < 0,001 | 76,0 [70,3; 81,0]; -14,6, p < 0,001 |
| PhoBERT tinh chỉnh | 95,5 [93,7; 97,2] | 87,8 [82,1; 92,4]; -7,7, p 0,002 | 85,7 [80,3; 90,3]; -9,9, p < 0,001 |
| ASGCN | 94,5 [92,5; 96,3] | 85,5 [79,7; 90,5]; -9,0, p < 0,001 | 83,5 [78,5; 88,0]; -11,0, p < 0,001 |
| ASGCN nối gốc | 95,1 [93,0; 96,8] | 86,1 [80,2; 91,2]; -9,0, p 0,001 | 85,1 [79,9; 89,6]; -9,9, p < 0,001 |
| Sentic-GCN | 96,1 [94,2; 97,7] | 87,9 [82,2; 92,7]; -8,2, p < 0,001 | 85,5 [80,0; 90,1]; -10,6, p < 0,001 |

Accuracy: từng mô hình so với PhoBERT tinh chỉnh trong từng nhóm, toàn bộ dòng. Mỗi ô: hiệu số so với PhoBERT tinh chỉnh trong chính nhóm đó (điểm phần trăm, mô hình trừ PhoBERT tinh chỉnh), khoảng tin cậy 95 % và p hai phía. Bootstrap ghép cặp 10.000 lần theo câu (603 câu). Không hiệu chỉnh cho việc so nhiều lần.

| Mô hình | Thường | Phủ định | Chuyển ý | Cả hai |
|---|---|---|---|---|
| Từ điển cảm xúc | -36,9 [-41,7; -32,3], p < 0,001 | -23,9 [-31,7; -16,3], p < 0,001 | -40,0 [-47,1; -33,0], p < 0,001 | -36,7 [-46,6; -26,7], p < 0,001 |
| BiLSTM với attention | -5,9 [-8,3; -3,6], p < 0,001 | -8,4 [-13,3; -3,7], p < 0,001 | -13,7 [-18,9; -8,7], p < 0,001 | -3,3 [-9,4; +2,9], p 0,303 |
| ASGCN | -1,3 [-2,5; -0,0], p 0,048 | -1,5 [-4,0; +1,1], p 0,258 | -1,7 [-3,7; +0,3], p 0,109 | +0,2 [-3,7; +4,2], p 0,949 |
| ASGCN nối gốc | -0,4 [-1,5; +0,8], p 0,532 | -0,8 [-3,5; +1,9], p 0,561 | -0,1 [-2,4; +2,2], p 0,933 | +0,5 [-3,6; +4,8], p 0,869 |
| Sentic-GCN | +0,7 [-0,4; +1,8], p 0,240 | +2,5 [+0,0; +5,4], p 0,063 | +1,8 [-0,5; +4,1], p 0,146 | +1,2 [-2,2; +5,1], p 0,564 |

Macro-F1: từng mô hình so với PhoBERT tinh chỉnh trong từng nhóm, toàn bộ dòng. Mỗi ô: hiệu số so với PhoBERT tinh chỉnh trong chính nhóm đó (điểm phần trăm, mô hình trừ PhoBERT tinh chỉnh), khoảng tin cậy 95 % và p hai phía. Bootstrap ghép cặp 10.000 lần theo câu (603 câu). Không hiệu chỉnh cho việc so nhiều lần.

| Mô hình | Thường | Phủ định | Chuyển ý | Cả hai |
|---|---|---|---|---|
| Từ điển cảm xúc | -46,3 [-49,7; -43,1], p < 0,001 | -38,5 [-44,8; -31,9], p < 0,001 | -48,0 [-54,1; -42,0], p < 0,001 | -42,1 [-51,5; -32,5], p < 0,001 |
| BiLSTM với attention | -6,2 [-8,7; -3,9], p < 0,001 | -11,3 [-18,1; -4,9], p < 0,001 | -15,3 [-20,9; -9,8], p < 0,001 | -4,0 [-10,9; +2,9], p 0,250 |
| ASGCN | -1,3 [-2,6; -0,1], p 0,038 | -2,8 [-6,1; +0,5], p 0,094 | -2,0 [-4,2; +0,2], p 0,081 | +0,5 [-4,0; +5,1], p 0,859 |
| ASGCN nối gốc | -0,4 [-1,6; +0,8], p 0,519 | -1,4 [-5,1; +2,2], p 0,429 | -0,1 [-2,6; +2,5], p 0,911 | +0,2 [-4,2; +5,1], p 0,946 |
| Sentic-GCN | +0,7 [-0,4; +1,9], p 0,191 | +3,3 [+0,1; +7,0], p 0,043 | +2,1 [-0,5; +4,8], p 0,111 | +2,0 [-1,9; +6,5], p 0,336 |

Accuracy: từng mô hình so với PhoBERT tinh chỉnh trong từng nhóm, chỉ các dòng người chú thích đồng ý với nhãn gốc. Mỗi ô: hiệu số so với PhoBERT tinh chỉnh trong chính nhóm đó (điểm phần trăm, mô hình trừ PhoBERT tinh chỉnh), khoảng tin cậy 95 % và p hai phía. Bootstrap ghép cặp 10.000 lần theo câu (526 câu). Không hiệu chỉnh cho việc so nhiều lần.

| Mô hình | Thường | Phủ định | Chuyển ý | Cả hai |
|---|---|---|---|---|
| Từ điển cảm xúc | -35,9 [-41,0; -30,7], p < 0,001 | -20,4 [-28,8; -12,3], p < 0,001 | -35,3 [-43,8; -27,0], p < 0,001 | -34,2 [-47,4; -20,9], p < 0,001 |
| BiLSTM với attention | -4,9 [-7,0; -2,9], p < 0,001 | -7,6 [-12,5; -3,3], p < 0,001 | -11,4 [-16,9; -6,0], p < 0,001 | -1,1 [-8,1; +6,2], p 0,779 |
| ASGCN | -1,0 [-2,2; +0,0], p 0,059 | -1,1 [-3,3; +1,2], p 0,339 | -1,7 [-3,8; +0,4], p 0,132 | -1,5 [-4,6; +1,7], p 0,400 |
| ASGCN nối gốc | -0,5 [-1,5; +0,6], p 0,357 | -0,6 [-2,8; +1,8], p 0,658 | +0,0 [-2,4; +2,5], p 1,000 | -1,5 [-4,2; +1,2], p 0,329 |
| Sentic-GCN | +0,4 [-0,5; +1,4], p 0,392 | +1,1 [-0,6; +3,3], p 0,272 | +0,2 [-2,3; +2,8], p 0,963 | -2,2 [-4,5; -0,0], p 0,047 |

Macro-F1: từng mô hình so với PhoBERT tinh chỉnh trong từng nhóm, chỉ các dòng người chú thích đồng ý với nhãn gốc. Mỗi ô: hiệu số so với PhoBERT tinh chỉnh trong chính nhóm đó (điểm phần trăm, mô hình trừ PhoBERT tinh chỉnh), khoảng tin cậy 95 % và p hai phía. Bootstrap ghép cặp 10.000 lần theo câu (526 câu). Không hiệu chỉnh cho việc so nhiều lần.

| Mô hình | Thường | Phủ định | Chuyển ý | Cả hai |
|---|---|---|---|---|
| Từ điển cảm xúc | -47,2 [-50,6; -43,9], p < 0,001 | -39,2 [-45,4; -32,5], p < 0,001 | -46,4 [-53,4; -39,0], p < 0,001 | -41,1 [-53,4; -27,8], p < 0,001 |
| BiLSTM với attention | -5,0 [-7,1; -3,0], p < 0,001 | -10,5 [-18,1; -4,1], p < 0,001 | -13,2 [-20,5; -6,2], p < 0,001 | -1,4 [-11,2; +9,1], p 0,768 |
| ASGCN | -1,1 [-2,2; +0,0], p 0,054 | -2,4 [-5,5; +0,7], p 0,125 | -2,4 [-5,2; +0,5], p 0,104 | -1,4 [-6,3; +3,7], p 0,580 |
| ASGCN nối gốc | -0,5 [-1,6; +0,7], p 0,381 | -1,0 [-4,4; +2,3], p 0,516 | +0,2 [-3,1; +3,7], p 0,963 | -2,5 [-6,2; +1,0], p 0,151 |
| Sentic-GCN | +0,5 [-0,4; +1,6], p 0,306 | +1,6 [-0,7; +4,5], p 0,188 | +0,6 [-3,0; +4,3], p 0,774 | -2,1 [-5,5; +0,9], p 0,167 |
