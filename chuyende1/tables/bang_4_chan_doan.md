Độ nhất quán của nhãn hiện tượng: kappa 0,733 trên 60 dòng gán lại. **Lần gán lại ngày 13/10/2026 cách lần gán đầu không quá 8 ngày, không đủ 14 ngày như quy ước; kappa này là cận trên.**

Accuracy theo nhóm hiện tượng, toàn bộ dòng. Mỗi ô: giá trị trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (603 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 415) | Phủ định (n = 119) | Chuyển ý (n = 181) | Cả hai (n = 84) |
|---|---|---|---|---|
| Từ điển cảm xúc | 54,8 [49,9; 59,5] | 66,4 [57,8; 74,7]; +11,6, p 0,016 | 45,3 [38,1; 52,3]; -9,5, p 0,031 | 37,3 [27,8; 46,6]; -17,5, p 0,001 |
| BiLSTM với attention | 86,2 [83,1; 89,1] | 81,8 [75,4; 87,7]; -4,4, p 0,199 | 71,8 [65,9; 77,4]; -14,4, p < 0,001 | 69,8 [61,5; 77,9]; -16,3, p < 0,001 |
| PhoBERT tinh chỉnh | 91,4 [89,0; 93,7] | 90,5 [85,6; 94,8]; -0,9, p 0,726 | 84,2 [79,3; 88,7]; -7,2, p 0,008 | 71,8 [62,7; 80,5]; -19,6, p < 0,001 |
| ASGCN | 89,6 [87,0; 92,2] | 86,6 [81,0; 91,7]; -3,1, p 0,298 | 83,1 [78,2; 87,4]; -6,6, p 0,012 | 73,8 [64,8; 82,1]; -15,8, p < 0,001 |
| ASGCN nối gốc | 91,2 [88,7; 93,4] | 88,0 [82,4; 93,1]; -3,2, p 0,285 | 84,0 [79,1; 88,5]; -7,2, p 0,005 | 74,6 [65,4; 83,2]; -16,6, p < 0,001 |
| Sentic-GCN | 92,0 [89,6; 94,3] | 93,0 [88,6; 96,8]; +0,9, p 0,673 | 86,7 [82,2; 90,9]; -5,3, p 0,034 | 74,6 [66,2; 82,6]; -17,4, p < 0,001 |

Macro-F1 theo nhóm hiện tượng, toàn bộ dòng. Mỗi ô: giá trị trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (603 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 415) | Phủ định (n = 119) | Chuyển ý (n = 181) | Cả hai (n = 84) |
|---|---|---|---|---|
| Từ điển cảm xúc | 45,5 [42,3; 48,5] | 50,0 [44,9; 54,6]; +4,4, p 0,128 | 36,3 [31,2; 40,8]; -9,3, p < 0,001 | 30,5 [23,2; 36,8]; -15,1, p < 0,001 |
| BiLSTM với attention | 86,0 [83,0; 88,9] | 77,7 [69,9; 84,5]; -8,4, p 0,027 | 69,1 [63,1; 74,4]; -17,0, p < 0,001 | 67,6 [59,2; 75,2]; -18,4, p < 0,001 |
| PhoBERT tinh chỉnh | 91,7 [89,3; 93,8] | 88,5 [82,6; 93,4]; -3,1, p 0,254 | 83,0 [77,8; 87,6]; -8,6, p 0,001 | 69,9 [60,6; 78,5]; -21,7, p < 0,001 |
| ASGCN | 89,7 [87,1; 92,2] | 82,3 [75,9; 87,8]; -7,5, p 0,019 | 81,6 [76,7; 86,0]; -8,1, p 0,001 | 72,7 [63,4; 80,7]; -17,0, p < 0,001 |
| ASGCN nối gốc | 91,4 [88,9; 93,6] | 84,8 [78,0; 90,8]; -6,5, p 0,044 | 82,9 [78,0; 87,4]; -8,4, p < 0,001 | 73,0 [63,4; 81,3]; -18,3, p < 0,001 |
| Sentic-GCN | 92,3 [89,9; 94,5] | 92,1 [87,0; 96,2]; -0,2, p 0,942 | 86,1 [81,3; 90,3]; -6,3, p 0,011 | 73,9 [65,1; 81,8]; -18,4, p < 0,001 |

Accuracy theo nhóm hiện tượng, chỉ các dòng người chú thích đồng ý với nhãn gốc. Mỗi ô: giá trị trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (526 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 363) | Phủ định (n = 105) | Chuyển ý (n = 132) | Cả hai (n = 55) |
|---|---|---|---|---|
| Từ điển cảm xúc | 59,7 [54,4; 64,8] | 74,3 [65,8; 82,3]; +14,6, p 0,004 | 56,1 [47,4; 64,6]; -3,6, p 0,478 | 49,7 [36,7; 62,6]; -10,0, p 0,154 |
| BiLSTM với attention | 91,2 [88,5; 93,6] | 87,0 [81,3; 92,3]; -4,2, p 0,163 | 80,3 [73,9; 86,2]; -10,9, p < 0,001 | 81,2 [72,0; 89,6]; -10,0, p 0,023 |
| PhoBERT tinh chỉnh | 95,6 [93,6; 97,3] | 95,2 [91,5; 98,3]; -0,4, p 0,885 | 90,9 [86,1; 95,2]; -4,7, p 0,054 | 83,0 [73,2; 91,5]; -12,6, p 0,002 |
| ASGCN | 93,8 [91,5; 95,8] | 92,1 [87,4; 96,1]; -1,7, p 0,510 | 90,2 [85,7; 94,3]; -3,6, p 0,146 | 83,6 [74,0; 92,2]; -10,1, p 0,025 |
| ASGCN nối gốc | 95,0 [93,0; 96,9] | 93,7 [89,2; 97,4]; -1,4, p 0,564 | 90,9 [86,4; 94,7]; -4,1, p 0,063 | 83,0 [72,8; 92,0]; -12,0, p 0,009 |
| Sentic-GCN | 95,8 [93,8; 97,6] | 95,9 [92,4; 98,8]; +0,1, p 0,919 | 91,2 [86,4; 95,3]; -4,6, p 0,050 | 81,8 [72,1; 90,5]; -14,0, p < 0,001 |

Macro-F1 theo nhóm hiện tượng, chỉ các dòng người chú thích đồng ý với nhãn gốc. Mỗi ô: giá trị trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (526 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 363) | Phủ định (n = 105) | Chuyển ý (n = 132) | Cả hai (n = 55) |
|---|---|---|---|---|
| Từ điển cảm xúc | 48,4 [45,0; 51,5] | 53,7 [48,6; 58,0]; +5,3, p 0,078 | 42,2 [36,3; 47,5]; -6,3, p 0,052 | 37,3 [28,1; 45,5]; -11,1, p 0,013 |
| BiLSTM với attention | 91,1 [88,4; 93,5] | 83,3 [75,2; 89,8]; -7,8, p 0,028 | 75,1 [67,9; 81,3]; -16,0, p < 0,001 | 74,8 [63,0; 84,3]; -16,2, p < 0,001 |
| PhoBERT tinh chỉnh | 95,6 [93,7; 97,3] | 93,7 [88,5; 97,6]; -2,0, p 0,412 | 87,9 [81,4; 93,3]; -7,7, p 0,008 | 76,8 [63,8; 87,2]; -18,9, p < 0,001 |
| ASGCN | 93,7 [91,4; 95,8] | 87,6 [80,8; 93,2]; -6,1, p 0,047 | 86,6 [81,0; 91,5]; -7,1, p 0,010 | 78,8 [66,5; 89,0]; -14,9, p 0,004 |
| ASGCN nối gốc | 95,1 [93,0; 96,9] | 90,9 [84,3; 96,0]; -4,2, p 0,152 | 88,1 [82,5; 92,7]; -7,0, p 0,007 | 76,8 [63,7; 87,6]; -18,3, p 0,001 |
| Sentic-GCN | 95,8 [93,9; 97,6] | 94,8 [90,0; 98,4]; -1,1, p 0,647 | 88,7 [82,5; 93,7]; -7,2, p 0,008 | 76,6 [63,9; 87,2]; -19,2, p < 0,001 |

Accuracy theo dấu hiệu, toàn bộ dòng. Dòng thuộc nhóm cả hai được tính vào cả hai cột sau. Mỗi ô: giá trị trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (603 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 415) | Có phủ định (n = 203) | Có chuyển ý (n = 265) |
|---|---|---|---|
| Từ điển cảm xúc | 54,8 [50,0; 59,6] | 54,4 [47,8; 60,8]; -0,4, p 0,922 | 42,8 [37,2; 48,4]; -12,0, p 0,002 |
| BiLSTM với attention | 86,2 [83,1; 89,0] | 76,8 [71,7; 81,8]; -9,3, p 0,001 | 71,2 [66,4; 75,9]; -15,0, p < 0,001 |
| PhoBERT tinh chỉnh | 91,4 [88,9; 93,7] | 82,8 [78,1; 87,3]; -8,6, p 0,001 | 80,3 [75,8; 84,4]; -11,2, p < 0,001 |
| ASGCN | 89,6 [87,0; 92,2] | 81,3 [76,3; 86,0]; -8,4, p 0,004 | 80,1 [75,8; 84,2]; -9,5, p < 0,001 |
| ASGCN nối gốc | 91,2 [88,7; 93,5] | 82,4 [77,5; 87,0]; -8,7, p 0,002 | 81,0 [76,6; 85,1]; -10,2, p < 0,001 |
| Sentic-GCN | 92,0 [89,6; 94,3] | 85,4 [80,9; 89,5]; -6,7, p 0,008 | 82,9 [78,7; 86,8]; -9,2, p < 0,001 |

Macro-F1 theo dấu hiệu, toàn bộ dòng. Dòng thuộc nhóm cả hai được tính vào cả hai cột sau. Mỗi ô: giá trị trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (603 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 415) | Có phủ định (n = 203) | Có chuyển ý (n = 265) |
|---|---|---|---|
| Từ điển cảm xúc | 45,5 [42,3; 48,5] | 42,3 [38,0; 46,3]; -3,3, p 0,208 | 34,4 [30,4; 38,2]; -11,1, p < 0,001 |
| BiLSTM với attention | 86,0 [82,9; 88,9] | 73,2 [67,6; 78,4]; -12,9, p < 0,001 | 68,6 [63,8; 73,0]; -17,5, p < 0,001 |
| PhoBERT tinh chỉnh | 91,7 [89,2; 93,8] | 80,3 [74,9; 85,1]; -11,4, p < 0,001 | 78,9 [74,2; 83,0]; -12,8, p < 0,001 |
| ASGCN | 89,7 [87,1; 92,2] | 78,2 [73,0; 83,1]; -11,5, p < 0,001 | 78,8 [74,4; 82,8]; -11,0, p < 0,001 |
| ASGCN nối gốc | 91,4 [88,9; 93,6] | 79,6 [74,3; 84,6]; -11,7, p < 0,001 | 79,8 [75,3; 83,8]; -11,6, p < 0,001 |
| Sentic-GCN | 92,3 [89,9; 94,5] | 84,0 [79,0; 88,3]; -8,3, p 0,001 | 82,2 [77,9; 86,0]; -10,1, p < 0,001 |

Accuracy theo dấu hiệu, chỉ các dòng người chú thích đồng ý với nhãn gốc. Dòng thuộc nhóm cả hai được tính vào cả hai cột sau. Mỗi ô: giá trị trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (526 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 363) | Có phủ định (n = 160) | Có chuyển ý (n = 187) |
|---|---|---|---|
| Từ điển cảm xúc | 59,7 [54,6; 64,8] | 65,8 [58,5; 73,0]; +6,1, p 0,166 | 54,2 [47,1; 61,4]; -5,5, p 0,212 |
| BiLSTM với attention | 91,2 [88,6; 93,6] | 85,0 [80,2; 89,5]; -6,2, p 0,014 | 80,6 [75,4; 85,5]; -10,6, p < 0,001 |
| PhoBERT tinh chỉnh | 95,6 [93,7; 97,3] | 91,0 [86,8; 94,7]; -4,6, p 0,027 | 88,6 [84,2; 92,5]; -7,0, p 0,001 |
| ASGCN | 93,8 [91,5; 95,8] | 89,2 [84,8; 93,3]; -4,6, p 0,058 | 88,2 [84,0; 92,1]; -5,5, p 0,017 |
| ASGCN nối gốc | 95,0 [93,0; 96,9] | 90,0 [85,5; 94,1]; -5,0, p 0,030 | 88,6 [84,3; 92,5]; -6,4, p 0,004 |
| Sentic-GCN | 95,8 [93,8; 97,5] | 91,0 [86,9; 94,7]; -4,7, p 0,027 | 88,4 [84,2; 92,4]; -7,4, p < 0,001 |

Macro-F1 theo dấu hiệu, chỉ các dòng người chú thích đồng ý với nhãn gốc. Dòng thuộc nhóm cả hai được tính vào cả hai cột sau. Mỗi ô: giá trị trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; với nhóm khác nhóm thường có thêm hiệu so với nhóm thường (điểm phần trăm) và p hai phía. Bootstrap 10.000 lần theo câu (526 câu). Nhãn chấm là nhãn gốc của bộ dữ liệu.

| Mô hình | Thường (n = 363) | Có phủ định (n = 160) | Có chuyển ý (n = 187) |
|---|---|---|---|
| Từ điển cảm xúc | 48,4 [45,1; 51,5] | 48,2 [43,6; 52,4]; -0,2, p 0,933 | 40,8 [36,0; 45,4]; -7,6, p 0,009 |
| BiLSTM với attention | 91,1 [88,4; 93,5] | 80,1 [73,8; 85,5]; -11,0, p < 0,001 | 75,1 [69,2; 80,4]; -16,0, p < 0,001 |
| PhoBERT tinh chỉnh | 95,6 [93,8; 97,3] | 87,6 [81,7; 92,5]; -8,0, p < 0,001 | 84,7 [78,9; 89,7]; -10,9, p < 0,001 |
| ASGCN | 93,7 [91,4; 95,8] | 84,3 [78,2; 89,7]; -9,4, p < 0,001 | 84,3 [79,0; 88,9]; -9,4, p < 0,001 |
| ASGCN nối gốc | 95,1 [93,0; 96,9] | 85,8 [79,5; 91,1]; -9,3, p 0,002 | 84,9 [79,5; 89,6]; -10,2, p < 0,001 |
| Sentic-GCN | 95,8 [93,9; 97,5] | 88,1 [82,3; 92,8]; -7,8, p 0,002 | 85,2 [79,7; 89,9]; -10,7, p < 0,001 |

Accuracy: từng mô hình so với PhoBERT tinh chỉnh trong từng nhóm, toàn bộ dòng. Mỗi ô: hiệu số so với PhoBERT tinh chỉnh trong chính nhóm đó (điểm phần trăm, mô hình trừ PhoBERT tinh chỉnh), khoảng tin cậy 95 % và p hai phía. Bootstrap ghép cặp 10.000 lần theo câu (603 câu). Không hiệu chỉnh cho việc so nhiều lần.

| Mô hình | Thường | Phủ định | Chuyển ý | Cả hai |
|---|---|---|---|---|
| Từ điển cảm xúc | -36,6 [-41,4; -32,0], p < 0,001 | -24,1 [-31,7; -16,7], p < 0,001 | -38,9 [-46,0; -32,0], p < 0,001 | -34,5 [-44,3; -24,7], p < 0,001 |
| BiLSTM với attention | -5,2 [-7,6; -2,9], p < 0,001 | -8,7 [-13,8; -3,7], p < 0,001 | -12,3 [-17,8; -7,2], p < 0,001 | -2,0 [-7,8; +4,1], p 0,550 |
| ASGCN | -1,8 [-3,3; -0,2], p 0,027 | -3,9 [-6,9; -1,0], p 0,010 | -1,1 [-3,8; +1,6], p 0,441 | +2,0 [-1,5; +5,9], p 0,345 |
| ASGCN nối gốc | -0,2 [-1,5; +1,1], p 0,753 | -2,5 [-6,1; +1,1], p 0,184 | -0,2 [-2,8; +2,3], p 0,922 | +2,8 [-1,4; +7,2], p 0,225 |
| Sentic-GCN | +0,6 [-0,6; +1,9], p 0,334 | +2,5 [-0,8; +6,3], p 0,172 | +2,6 [-0,4; +5,6], p 0,099 | +2,8 [-1,4; +7,6], p 0,237 |

Macro-F1: từng mô hình so với PhoBERT tinh chỉnh trong từng nhóm, toàn bộ dòng. Mỗi ô: hiệu số so với PhoBERT tinh chỉnh trong chính nhóm đó (điểm phần trăm, mô hình trừ PhoBERT tinh chỉnh), khoảng tin cậy 95 % và p hai phía. Bootstrap ghép cặp 10.000 lần theo câu (603 câu). Không hiệu chỉnh cho việc so nhiều lần.

| Mô hình | Thường | Phủ định | Chuyển ý | Cả hai |
|---|---|---|---|---|
| Từ điển cảm xúc | -46,1 [-49,6; -42,8], p < 0,001 | -38,6 [-44,9; -31,9], p < 0,001 | -46,7 [-52,9; -40,6], p < 0,001 | -39,5 [-49,0; -29,7], p < 0,001 |
| BiLSTM với attention | -5,6 [-8,1; -3,2], p < 0,001 | -10,9 [-17,9; -4,2], p < 0,001 | -13,9 [-20,0; -8,1], p < 0,001 | -2,3 [-9,1; +4,7], p 0,497 |
| ASGCN | -1,9 [-3,5; -0,4], p 0,018 | -6,3 [-10,4; -2,4], p 0,001 | -1,4 [-4,4; +1,5], p 0,337 | +2,8 [-1,5; +7,7], p 0,229 |
| ASGCN nối gốc | -0,3 [-1,5; +1,0], p 0,670 | -3,7 [-9,1; +1,5], p 0,157 | -0,1 [-3,1; +2,8], p 0,937 | +3,1 [-1,8; +8,4], p 0,225 |
| Sentic-GCN | +0,7 [-0,6; +1,9], p 0,290 | +3,6 [-0,8; +8,4], p 0,108 | +3,0 [-0,3; +6,4], p 0,073 | +4,0 [-0,8; +9,6], p 0,113 |

Accuracy: từng mô hình so với PhoBERT tinh chỉnh trong từng nhóm, chỉ các dòng người chú thích đồng ý với nhãn gốc. Mỗi ô: hiệu số so với PhoBERT tinh chỉnh trong chính nhóm đó (điểm phần trăm, mô hình trừ PhoBERT tinh chỉnh), khoảng tin cậy 95 % và p hai phía. Bootstrap ghép cặp 10.000 lần theo câu (526 câu). Không hiệu chỉnh cho việc so nhiều lần.

| Mô hình | Thường | Phủ định | Chuyển ý | Cả hai |
|---|---|---|---|---|
| Từ điển cảm xúc | -35,9 [-41,0; -30,7], p < 0,001 | -21,0 [-29,2; -13,0], p < 0,001 | -34,8 [-43,3; -26,6], p < 0,001 | -33,3 [-46,4; -20,2], p < 0,001 |
| BiLSTM với attention | -4,4 [-6,5; -2,4], p < 0,001 | -8,3 [-13,6; -3,5], p < 0,001 | -10,6 [-16,7; -4,8], p < 0,001 | -1,8 [-8,7; +5,3], p 0,650 |
| ASGCN | -1,8 [-3,3; -0,4], p 0,013 | -3,2 [-5,8; -0,6], p 0,021 | -0,8 [-3,6; +2,1], p 0,632 | +0,6 [-2,3; +4,0], p 0,868 |
| ASGCN nối gốc | -0,6 [-1,6; +0,6], p 0,356 | -1,6 [-4,2; +0,9], p 0,245 | +0,0 [-2,7; +2,8], p 1,000 | -0,0 [-2,9; +3,0], p 1,000 |
| Sentic-GCN | +0,2 [-0,8; +1,3], p 0,790 | +0,6 [-1,9; +3,4], p 0,718 | +0,3 [-3,1; +3,6], p 0,932 | -1,2 [-4,8; +2,8], p 0,588 |

Macro-F1: từng mô hình so với PhoBERT tinh chỉnh trong từng nhóm, chỉ các dòng người chú thích đồng ý với nhãn gốc. Mỗi ô: hiệu số so với PhoBERT tinh chỉnh trong chính nhóm đó (điểm phần trăm, mô hình trừ PhoBERT tinh chỉnh), khoảng tin cậy 95 % và p hai phía. Bootstrap ghép cặp 10.000 lần theo câu (526 câu). Không hiệu chỉnh cho việc so nhiều lần.

| Mô hình | Thường | Phủ định | Chuyển ý | Cả hai |
|---|---|---|---|---|
| Từ điển cảm xúc | -47,2 [-50,7; -43,8], p < 0,001 | -40,0 [-45,9; -33,5], p < 0,001 | -45,7 [-53,0; -38,1], p < 0,001 | -39,4 [-52,0; -25,7], p < 0,001 |
| BiLSTM với attention | -4,6 [-6,7; -2,5], p < 0,001 | -10,4 [-18,3; -3,5], p 0,004 | -12,8 [-20,9; -5,0], p 0,002 | -1,9 [-12,1; +8,9], p 0,694 |
| ASGCN | -1,9 [-3,4; -0,5], p 0,010 | -6,0 [-10,0; -2,4], p 0,002 | -1,3 [-4,7; +2,3], p 0,460 | +2,0 [-2,6; +8,0], p 0,448 |
| ASGCN nối gốc | -0,6 [-1,7; +0,6], p 0,329 | -2,8 [-6,9; +0,8], p 0,135 | +0,2 [-3,6; +4,2], p 0,927 | +0,0 [-4,6; +4,5], p 0,987 |
| Sentic-GCN | +0,2 [-0,8; +1,3], p 0,711 | +1,1 [-2,5; +5,2], p 0,564 | +0,8 [-4,0; +5,6], p 0,741 | -0,2 [-5,1; +6,0], p 0,905 |
