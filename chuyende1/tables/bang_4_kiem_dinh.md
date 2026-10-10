Kiểm định bootstrap ghép cặp: 10.000 lần lấy mẫu theo câu (2.187 câu), trên trung bình ba seed. Hiệu số tính bằng điểm phần trăm, A trừ B.

| A | B | Hiệu số macro-F1 | Khoảng tin cậy 95 % | p | Hiệu số accuracy | Khoảng tin cậy 95 % | p |
|---|---|---|---|---|---|---|---|
| BiLSTM với attention | Từ điển cảm xúc | +27,09 | +25,84 đến +28,34 | < 0,001 | +11,73 | +10,62 đến +12,85 | < 0,001 |
| PhoBERT tinh chỉnh | BiLSTM với attention | +7,15 | +6,18 đến +8,11 | < 0,001 | +5,44 | +4,82 đến +6,07 | < 0,001 |
| ASGCN | PhoBERT tinh chỉnh | -1,21 | -1,78 đến -0,64 | < 0,001 | -0,53 | -0,85 đến -0,22 | 0,001 |
| ASGCN nối gốc | ASGCN | +0,83 | +0,35 đến +1,30 | < 0,001 | +0,32 | +0,05 đến +0,58 | 0,021 |
| Sentic-GCN | ASGCN | +1,07 | +0,47 đến +1,67 | < 0,001 | +0,12 | -0,23 đến +0,46 | 0,504 |
| ASGCN nối gốc | PhoBERT tinh chỉnh | -0,38 | -0,94 đến +0,20 | 0,205 | -0,21 | -0,53 đến +0,11 | 0,200 |
| Sentic-GCN | PhoBERT tinh chỉnh | -0,14 | -0,72 đến +0,44 | 0,630 | -0,41 | -0,76 đến -0,07 | 0,021 |
