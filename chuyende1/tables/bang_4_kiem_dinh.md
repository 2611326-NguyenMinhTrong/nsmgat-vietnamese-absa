Kiểm định bootstrap ghép cặp: 10.000 lần lấy mẫu theo câu (2.187 câu), trên trung bình các seed. Hiệu số tính bằng điểm phần trăm, A trừ B.

| A | B | Hiệu số macro-F1 | Khoảng tin cậy 95 % | p | Hiệu số accuracy | Khoảng tin cậy 95 % | p |
|---|---|---|---|---|---|---|---|
| BiLSTM với attention | Từ điển cảm xúc | +27,08 | +25,85 đến +28,28 | < 0,001 | +11,70 | +10,61 đến +12,80 | < 0,001 |
| PhoBERT tinh chỉnh | BiLSTM với attention | +7,23 | +6,32 đến +8,13 | < 0,001 | +5,42 | +4,82 đến +6,01 | < 0,001 |
| ASGCN | PhoBERT tinh chỉnh | -0,88 | -1,34 đến -0,44 | < 0,001 | -0,33 | -0,59 đến -0,07 | 0,013 |
| ASGCN nối gốc | ASGCN | +0,59 | +0,25 đến +0,93 | < 0,001 | +0,24 | +0,04 đến +0,43 | 0,018 |
| Sentic-GCN | ASGCN | +0,88 | +0,40 đến +1,38 | < 0,001 | +0,12 | -0,15 đến +0,41 | 0,400 |
| ASGCN nối gốc | PhoBERT tinh chỉnh | -0,29 | -0,76 đến +0,17 | 0,222 | -0,09 | -0,36 đến +0,18 | 0,522 |
| Sentic-GCN | PhoBERT tinh chỉnh | +0,00 | -0,45 đến +0,46 | 0,987 | -0,20 | -0,48 đến +0,07 | 0,158 |
