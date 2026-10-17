# Phụ lục B và Phụ lục C của báo cáo Chuyên đề 1

Đề tài: A Neuro-Symbolic Multi-Graph Network with Explicit Modeling of Negation and Contrast for Vietnamese Aspect-Category Sentiment Analysis.

Học viên: Nguyễn Minh Trộng. Ngành Khoa học máy tính, Trường Đại học Công nghệ Kỹ thuật Thành phố Hồ Chí Minh. Giảng viên hướng dẫn: TS. Phan Thị Huyền Trang.

Phụ lục A in kèm báo cáo. Phụ lục B và Phụ lục C không in kèm mà được lưu ở file này. Số mục, số bảng được nhắc tới, như mục 4.1.2 hay Bảng 4.1, là số trong báo cáo.

## Phụ lục B. Tập chẩn đoán: quy trình chú thích và độ nhất quán

Phần này là bản đầy đủ của quy trình được tóm tắt ở mục 4.1.2 của báo cáo.

Bước đầu tiên là lọc ứng viên. Từ tập kiểm tra, 800 mẫu thuộc 604 bình luận được chọn theo từ khoá vào bốn kho: có từ phủ định (250 mẫu), có từ chuyển ý (200), có cả hai (150) và không có từ khoá nào, dùng làm đối chứng (200). Bước lọc ưu tiên bình luận dài từ 5 đến 40 từ; các mẫu được chọn dài từ 7 đến 42 từ. Trong mỗi kho, mẫu được rút sao cho ba nhãn cảm xúc gần bằng nhau, tổng cộng 268 tiêu cực, 267 trung tính và 265 tích cực. Từ khoá được so theo từng từ đã tách và gồm cả các dạng viết tắt như ko, k, kh.

Bước tiếp theo là chú thích. Có từ khoá trong câu chưa có nghĩa là hiện tượng tác động tới khía cạnh đang xét. Vì vậy mỗi mẫu được gán tay một nhãn hiện tượng theo một bản hướng dẫn viết trước: phủ định, chuyển ý, cả hai, hoặc thường. Nhãn được gán cho cặp câu và khía cạnh chứ không cho cả câu: cùng một câu có thể thuộc nhóm phủ định với khía cạnh này và thuộc nhóm thường với khía cạnh khác. Người chú thích cũng ghi lại những mẫu mà mình không đồng ý với nhãn cảm xúc gốc; khi chấm mô hình, nhãn gốc được giữ nguyên. Việc chú thích do một người thực hiện, là học viên.

Trong lúc chú thích, một mẫu bị loại. Còn lại 799 mẫu thuộc 603 bình luận: 415 mẫu thuộc nhóm thường, 119 mẫu thuộc nhóm phủ định, 181 mẫu thuộc nhóm chuyển ý và 84 mẫu thuộc nhóm cả hai. Số mẫu theo nhóm khác xa số mẫu theo kho ứng viên, vì có từ khoá chưa có nghĩa là có hiện tượng. Trong 250 mẫu của kho có từ phủ định, chỉ 115 mẫu, tức 46,0 %, được xếp vào nhóm phủ định hoặc nhóm cả hai. Ngược lại, 24 trong 200 mẫu của kho đối chứng được xếp vào một nhóm có hiện tượng, tức hiện tượng được diễn đạt bằng cách mà danh sách từ khoá không bắt được. Thành phần nhãn của từng nhóm được nêu ở Bảng C.5.

Chuyên đề chưa có người chú thích thứ hai. Độ tin cậy của nhãn hiện tượng vì vậy được ước lượng bằng độ nhất quán của chính người chú thích: 60 mẫu, rút 15 mẫu mỗi nhóm theo nhãn của lần gán đầu, được gán lại mà không xem nhãn cũ. Sau khi rút, một mẫu được chuyển nhóm khi rà lại quy tắc chú thích, nên theo nhãn lần đầu bốn nhóm có 14, 15, 15 và 16 mẫu. Hệ số kappa của Cohen [1] giữa hai lần gán là 0,733, với 48 trên 60 mẫu trùng nhau, tức 80,0 %. Con số này cần được đọc với ba lưu ý. Thứ nhất, hai lần gán cách nhau không quá 8 ngày, và ít nhất 28 trong 60 mẫu có nhãn lần đầu được ghi nhận trong vòng 3 ngày trước lần gán lại. Khoảng cách này ngắn hơn mức 14 ngày mà chuyên đề dự định. Người chú thích có thể còn nhớ nhãn cũ, nên 0,733 là cận trên của độ nhất quán thật. Thứ hai, đây là độ nhất quán của một người, không phải độ đồng thuận giữa hai người. Thứ ba, chỗ không nhất quán không rải đều: 7 trong 12 mẫu lệch là lệch giữa nhóm cả hai và nhóm phủ định, và nhóm cả hai chỉ giữ nguyên nhãn ở 9 trên 15 mẫu. Tách theo từng dấu hiệu, việc xét mẫu có phủ định hay không cho kappa 0,900, còn việc xét mẫu có chuyển ý hay không cho kappa 0,700. Vì vậy mục 4.6 trình bày kết quả theo bốn nhóm và cả theo từng dấu hiệu.

Người chú thích không đồng ý với nhãn cảm xúc gốc ở 144 trên 799 mẫu, tức 18,0 %, gồm 1 mẫu người chú thích không quyết được. Tỉ lệ này không đều: 12,5 % ở nhóm thường, 11,8 % ở nhóm phủ định, 27,1 % ở nhóm chuyển ý và 34,5 % ở nhóm cả hai. Nhận định này cũng kém ổn định giữa hai lần gán. Trên nhãn cảm xúc mà người chú thích cho là đúng, kappa giữa hai lần gán là 0,753. Trong 60 mẫu gán lại, lần đầu người chú thích không đồng ý với nhãn gốc ở 12 mẫu, lần hai ở 7 mẫu, và chỉ 5 mẫu ở cả hai lần. Chuyên đề vì vậy không sửa nhãn gốc. Nhận định này chỉ được dùng để tách ra 655 mẫu mà người chú thích đồng ý với nhãn gốc, làm phép kiểm tra độ vững ở mục 4.6.

## Phụ lục C. Các bảng bổ sung của Chương 4

Phụ lục này gồm các bảng chi tiết của Chương 4; trong chương chỉ nêu ý chính của từng bảng. Các bảng được đánh số theo thứ tự được nhắc tới trong chương.

Bảng C.1: Quy mô và phân bố nhãn của UIT-ViSFD sau khi chuyển về dạng mẫu

| | Train | Dev | Test | Tổng |
|---|---|---|---|---|
| Số bình luận gốc | 7.786 | 1.112 | 2.224 | 11.122 |
| Số bình luận sinh ra ít nhất một mẫu | 7.671 | 1.094 | 2.187 | 10.952 |
| Số mẫu | 23.872 | 3.316 | 6.722 | 33.910 |
| Số khía cạnh trung bình mỗi bình luận | 3,11 | 3,03 | 3,07 | |
| Tiêu cực | 7.464 (31,27 %) | 1.011 (30,49 %) | 2.210 (32,88 %) | 10.685 |
| Trung tính | 2.903 (12,16 %) | 381 (11,49 %) | 817 (12,15 %) | 4.101 |
| Tích cực | 13.505 (56,57 %) | 1.924 (58,02 %) | 3.695 (54,97 %) | 19.124 |

Bảng C.2: Cách viết mười khía cạnh khi đưa vào mô hình

| Mã trong dữ liệu | Viết thành | Mã trong dữ liệu | Viết thành |
|---|---|---|---|
| BATTERY | pin | STORAGE | bộ_nhớ |
| SCREEN | màn_hình | DESIGN | thiết_kế |
| CAMERA | camera | PRICE | giá |
| FEATURES | tính_năng | GENERAL | tổng_thể |
| PERFORMANCE | hiệu_năng | SER&ACC | dịch_vụ và phụ_kiện |

Bảng C.3: Macro-F1 từng seed của bốn mô hình dùng PhoBERT (%)

| Mô hình | Seed 42 | Seed 1337 | Seed 2024 | Seed 7 | Seed 123 |
|---|---|---|---|---|---|
| PhoBERT tinh chỉnh | 86,49 | 86,65 | 86,77 | 86,48 | 87,10 |
| ASGCN | 86,69 | 85,14 | 84,47 | 86,87 | 85,93 |
| ASGCN nối gốc | 86,36 | 85,94 | 86,49 | 86,83 | 86,42 |
| Sentic-GCN | 86,28 | 86,40 | 86,82 | 86,96 | 87,05 |

Bảng C.4: Hành vi trên lớp trung tính, trung bình 5 seed (tập kiểm tra có 817 mẫu trung tính trong 6.722 mẫu)

| Mô hình | Số lần đoán trung tính | Precision (%) | Recall (%) | Tổng số mẫu đoán sai |
|---|---|---|---|---|
| Từ điển cảm xúc | 0 |  | 0,00 | 1.702,0 |
| BiLSTM với attention | 693,8 | 65,38 | 55,52 | 915,8 |
| PhoBERT tinh chỉnh | 779,6 | 73,40 | 69,87 | 551,8 |
| ASGCN | 711,4 | 74,87 | 64,94 | 573,8 |
| ASGCN nối gốc | 719,8 | 75,63 | 66,56 | 558,0 |
| Sentic-GCN | 845,6 | 70,54 | 72,90 | 565,4 |

Bảng C.5: Thành phần của tập chẩn đoán theo nhóm hiện tượng và nhãn cảm xúc gốc

| Nhóm | Số mẫu | Tiêu cực | Trung tính | Tích cực | Không đồng ý với nhãn gốc |
|---|---|---|---|---|---|
| Thường | 415 | 107 | 148 | 160 | 52 (12,5 %) |
| Phủ định | 119 | 54 | 28 | 37 | 14 (11,8 %) |
| Chuyển ý | 181 | 74 | 60 | 47 | 49 (27,1 %) |
| Cả hai | 84 | 33 | 30 | 21 | 29 (34,5 %) |
| Tổng | 799 | 268 | 266 | 265 | 144 (18,0 %) |

Bảng C.6: Hiệu số so với nhóm thường của cùng mô hình (điểm phần trăm, giá trị p trong ngoặc)

| Mô hình | Accuracy, phủ định | Accuracy, chuyển ý | Accuracy, cả hai | Macro-F1, phủ định | Macro-F1, chuyển ý | Macro-F1, cả hai |
|---|---|---|---|---|---|---|
| Từ điển cảm xúc | +11,7 (0,016) | -9,4 (0,033) | -17,3 (0,001) | +4,5 (0,121) | -9,2 (< 0,001) | -14,9 (< 0,001) |
| BiLSTM với attention | -3,8 (0,260) | -14,1 (< 0,001) | -15,0 (0,001) | -8,4 (0,026) | -16,6 (< 0,001) | -16,9 (< 0,001) |
| PhoBERT tinh chỉnh | -1,4 (0,593) | -6,3 (0,013) | -17,6 (< 0,001) | -3,4 (0,201) | -7,5 (0,003) | -19,1 (< 0,001) |
| ASGCN | -1,6 (0,551) | -6,7 (0,004) | -16,1 (< 0,001) | -4,8 (0,084) | -8,2 (< 0,001) | -17,4 (< 0,001) |
| ASGCN nối gốc | -1,8 (0,526) | -6,0 (0,013) | -16,7 (< 0,001) | -4,4 (0,127) | -7,2 (0,003) | -18,5 (< 0,001) |
| Sentic-GCN | +0,5 (0,810) | -5,2 (0,028) | -17,1 (< 0,001) | -0,8 (0,782) | -6,1 (0,008) | -17,9 (< 0,001) |

Bảng C.7: Macro-F1 trên bốn nhóm của tập chẩn đoán (%, khoảng tin cậy 95 % trong ngoặc)

| Mô hình | Thường (415 mẫu) | Phủ định (119) | Chuyển ý (181) | Cả hai (84) |
|---|---|---|---|---|
| Từ điển cảm xúc | 45,5 (42,2 đến 48,4) | 50,0 (44,9 đến 54,6) | 36,3 (31,2 đến 40,8) | 30,5 (23,3 đến 36,9) |
| BiLSTM với attention | 85,6 (82,6 đến 88,4) | 77,2 (69,4 đến 84,1) | 69,0 (63,4 đến 74,1) | 68,7 (60,4 đến 76,1) |
| PhoBERT tinh chỉnh | 91,8 (89,5 đến 94,0) | 88,4 (82,9 đến 93,0) | 84,3 (79,3 đến 88,7) | 72,7 (63,8 đến 80,8) |
| ASGCN | 90,5 (88,1 đến 92,7) | 85,7 (80,0 đến 90,5) | 82,3 (77,9 đến 86,2) | 73,1 (64,0 đến 81,0) |
| ASGCN nối gốc | 91,4 (89,0 đến 93,6) | 87,0 (81,1 đến 92,0) | 84,2 (79,6 đến 88,3) | 72,9 (63,6 đến 80,9) |
| Sentic-GCN | 92,6 (90,2 đến 94,6) | 91,8 (86,7 đến 95,9) | 86,4 (81,9 đến 90,4) | 74,7 (65,8 đến 82,4) |

Bảng C.8: Accuracy theo từng dấu hiệu (%, khoảng tin cậy 95 % trong ngoặc) và hiệu số so với nhóm thường (điểm phần trăm, giá trị p trong ngoặc)

| Mô hình | Thường (415 mẫu) | Có phủ định (203) | Hiệu số | Có chuyển ý (265) | Hiệu số |
|---|---|---|---|---|---|
| Từ điển cảm xúc | 54,7 (49,9 đến 59,5) | 54,4 (47,8 đến 60,9) | -0,3 (0,945) | 42,8 (37,2 đến 48,4) | -11,9 (0,002) |
| BiLSTM với attention | 85,7 (82,7 đến 88,6) | 77,2 (72,3 đến 82,2) | -8,4 (0,003) | 71,3 (66,7 đến 75,8) | -14,4 (< 0,001) |
| PhoBERT tinh chỉnh | 91,6 (89,2 đến 93,8) | 83,5 (79,0 đến 87,9) | -8,1 (0,002) | 81,7 (77,5 đến 85,7) | -9,9 (< 0,001) |
| ASGCN | 90,4 (88,0 đến 92,6) | 82,8 (78,0 đến 87,2) | -7,6 (0,004) | 80,7 (76,5 đến 84,5) | -9,7 (< 0,001) |
| ASGCN nối gốc | 91,2 (88,8 đến 93,5) | 83,3 (78,5 đến 87,6) | -8,0 (0,003) | 81,8 (77,6 đến 85,7) | -9,4 (< 0,001) |
| Sentic-GCN | 92,3 (89,9 đến 94,5) | 85,5 (81,0 đến 89,6) | -6,8 (0,007) | 83,3 (79,3 đến 87,0) | -9,0 (< 0,001) |

Bảng C.9: Hiệu số accuracy so với PhoBERT tinh chỉnh trong từng nhóm (điểm phần trăm, mô hình trừ PhoBERT; khoảng tin cậy 95 % trong ngoặc)

| Mô hình | Thường | Phủ định | Chuyển ý | Cả hai |
|---|---|---|---|---|
| Từ điển cảm xúc | -36,9 (-41,7 đến -32,3); p < 0,001 | -23,9 (-31,7 đến -16,3); p < 0,001 | -40,0 (-47,1 đến -33,0); p < 0,001 | -36,7 (-46,6 đến -26,7); p < 0,001 |
| BiLSTM với attention | -5,9 (-8,3 đến -3,6); p < 0,001 | -8,4 (-13,3 đến -3,7); p < 0,001 | -13,7 (-18,9 đến -8,7); p < 0,001 | -3,3 (-9,4 đến +2,9); p 0,303 |
| ASGCN | -1,3 (-2,5 đến -0,0); p 0,048 | -1,5 (-4,0 đến +1,1); p 0,258 | -1,7 (-3,7 đến +0,3); p 0,109 | +0,2 (-3,7 đến +4,2); p 0,949 |
| ASGCN nối gốc | -0,4 (-1,5 đến +0,8); p 0,532 | -0,8 (-3,5 đến +1,9); p 0,561 | -0,1 (-2,4 đến +2,2); p 0,933 | +0,5 (-3,6 đến +4,8); p 0,869 |
| Sentic-GCN | +0,7 (-0,4 đến +1,8); p 0,240 | +2,5 (+0,0 đến +5,4); p 0,063 | +1,8 (-0,5 đến +4,1); p 0,146 | +1,2 (-2,2 đến +5,1); p 0,564 |

ASGCN thấp hơn PhoBERT 1,3 điểm ở nhóm thường (p bằng 0,048); ở nhóm phủ định, khoảng cách 1,5 điểm không có ý nghĩa (p bằng 0,258). Ở nhóm cả hai, BiLSTM chỉ thấp hơn PhoBERT 3,3 điểm (p bằng 0,303), tức với 84 mẫu của nhóm này, lợi thế của mô hình tiền huấn luyện không còn đo được.

Bảng C.10: Accuracy trên 655 mẫu mà người chú thích đồng ý với nhãn gốc (%; trong ngoặc là hiệu số so với nhóm thường và giá trị p)

| Mô hình | Thường (363 mẫu) | Phủ định (105) | Chuyển ý (132) | Cả hai (55) |
|---|---|---|---|---|
| Từ điển cảm xúc | 59,6 | 74,3 (+14,7; p 0,004) | 56,1 (-3,6; p 0,489) | 49,8 (-9,8; p 0,161) |
| BiLSTM với attention | 90,6 | 87,0 (-3,6; p 0,223) | 80,0 (-10,6; p < 0,001) | 82,9 (-7,7; p 0,066) |
| PhoBERT tinh chỉnh | 95,5 | 94,7 (-0,9; p 0,695) | 91,4 (-4,2; p 0,072) | 84,0 (-11,5; p 0,004) |
| ASGCN | 94,5 | 93,5 (-1,0; p 0,683) | 89,7 (-4,8; p 0,035) | 82,5 (-11,9; p 0,006) |
| ASGCN nối gốc | 95,0 | 94,1 (-0,9; p 0,693) | 91,4 (-3,7; p 0,085) | 82,5 (-12,5; p 0,007) |
| Sentic-GCN | 96,0 | 95,8 (-0,2; p 0,970) | 91,5 (-4,5; p 0,048) | 81,8 (-14,2; p < 0,001) |

## Tài liệu tham khảo

[1] Jacob Cohen. A Coefficient of Agreement for Nominal Scales. Educational and Psychological Measurement, vol. 20, no. 1, tr. 37–46, 1960.
