# PHIẾU BÀN GIAO — [CD1.12i] Kiểm lại nhận định "PhoBERT tốt, thêm đồ thị chưa cải thiện rõ rệt" và tìm lý do

Ngày 16/10/2026. Học viên hỏi: có thật là PhoBERT tinh chỉnh đạt hiệu quả tốt còn việc bổ sung đồ thị chưa mang lại cải thiện
rõ rệt không; vì sao thêm đồ thị mà không có hiệu quả; nếu cần thì học viên chạy huấn luyện lại.

Không huấn luyện lại, không sửa bản nháp hay file Word. Mọi phép tính dùng `results/<mô hình>/seed<N>/predictions.jsonl`
đã có, nhật ký `logs/<mô hình>/seed<N>.log`, và hàm `do_do`, `kiem_dinh` của `scripts/compare_baselines.py` (bootstrap
ghép cặp theo bình luận, 10.000 lần, trung bình ba seed, giống Bảng 4.4).

## 1. ĐÃ LÀM GÌ

- Đọc `forward()` của `phobert.py`, `asgcn.py`, `senticgcn.py`, `layers.py`; đọc config bốn mô hình.
- Đọc đường cong dev của 12 lần chạy trong `logs/`.
- Viết một kịch bản phân tích tạm (thư mục scratchpad của phiên, chưa đưa vào repo) tính sáu phép ở mục 6.
- Thử `ASGCNModel` với `gcn_layers: 0` trên bộ mã hoá tí hon: chạy được, đổi ma trận kề không đổi đầu ra.
- Ghi GAP-040 và dòng trong `chuyende1/gaps/INDEX.md`.

## 2. KẾT LUẬN NGẮN

Nhận định **đúng về con số**, và sau phân tích còn chắc hơn: không có nhóm mẫu nào mà mô hình đồ thị hơn PhoBERT có ý nghĩa.
Nhưng nó **sai ở chỗ quy cho thành phần nào**: bậc PhoBERT lên ASGCN đổi hai thứ (cách đọc ra và GCN), nên chưa nói được
"cú pháp vô ích"; và diễn giải "đồ thị bị chia cắt là một nguyên nhân" ở mục 4.4 không đứng được khi tách nhóm (GAP-040).

## 3. BẰNG CHỨNG

**A. Mô hình đồ thị khác PhoBERT chừng nào PhoBERT khác chính nó.** Tỉ lệ mẫu có dự đoán khác nhau:

| Cặp | Tỉ lệ khác |
|---|---|
| PhoBERT với chính nó, ba cặp seed | 4,49 % |
| ASGCN với chính nó | 5,25 % |
| PhoBERT với ASGCN, chín cặp | 5,13 % |
| PhoBERT với ASGCN nối gốc | 4,86 % |
| PhoBERT với Sentic-GCN | 5,35 % |

Đổi sang mô hình đồ thị làm dự đoán dịch đi chỉ hơn đổi seed khoảng 0,4 đến 0,9 điểm phần trăm.

**B. Không có tập mẫu nào đồ thị sửa được một cách nhất quán.** Số mẫu mô hình X đúng ở cả ba seed mà PhoBERT sai ở cả ba,
so với chiều ngược lại: ASGCN 7 và 7, nối gốc 10 và 13, Sentic-GCN 13 và 17, trên 6.722 mẫu.

**C. Ở chỗ cú pháp lẽ ra giúp nhiều nhất, không mô hình đồ thị nào hơn.** Câu có nhiều khía cạnh trái cảm xúc (các khía
cạnh của cùng bình luận không cùng một nhãn) chiếm 53,4 % số mẫu kiểm tra. Đây là chỗ cần gắn đúng từ cảm xúc
với đúng khía cạnh, lý do ASGCN ra đời.

| Mô hình | Macro-F1 nhóm trái cảm xúc | Trừ PhoBERT | KTC 95 % | p |
|---|---|---|---|---|
| PhoBERT | 84,88 | | | |
| ASGCN | 83,05 | −1,83 | −2,49 đến −1,17 | < 0,001 |
| ASGCN nối gốc | 84,28 | −0,60 | −1,27 đến +0,06 | 0,075 |
| Sentic-GCN | 85,04 | +0,16 | −0,54 đến +0,88 | 0,642 |

Ở phần còn lại của tập kiểm tra, ASGCN không thua (+1,03, p 0,262). Tức phần ASGCN thua dồn đúng vào câu trái cảm xúc.

**D. Đồ thị bị chia cắt không phải chỗ ASGCN thua.** ASGCN trừ PhoBERT: −1,80 điểm macro-F1 ở mẫu một gốc (p < 0,001),
−0,77 ở mẫu từ hai gốc (p 0,043). Nối gốc trừ ASGCN: +1,06 ở mẫu mà nối gốc **không đổi** đồ thị (p 0,008), +0,66 ở mẫu có
đổi (p 0,024). Xem GAP-040.

**E. ASGCN thua chủ yếu ở hai seed chọn checkpoint epoch 3.** Epoch có dev macro-F1 tốt nhất:

| Mô hình | seed 42 | seed 1337 | seed 2024 |
|---|---|---|---|
| PhoBERT | 4 (0,8495) | 5 (0,8466) | 4 (0,8543) |
| ASGCN | 5 (0,8553) | 3 (0,8448) | 3 (0,8414) |
| ASGCN nối gốc | 4 (0,8492) | 3 (0,8543) | 4 (0,8544) |
| Sentic-GCN | 5 (0,8509) | 8 (0,8507), vẫn đang tăng | 7 (0,8442) |

ASGCN seed 42 hơn PhoBERT; hai seed còn lại dừng ở epoch 6 với điểm dev thấp hơn và test cũng thấp hơn. Sentic-GCN seed
1337 chạm trần 8 epoch khi dev còn tăng.

## 4. VÌ SAO THÊM ĐỒ THỊ MÀ KHÔNG HIỆU QUẢ — xếp theo độ chắc của bằng chứng

1. **Bài toán nhóm khía cạnh làm đồ thị mất điểm neo** (bằng chứng C, mạnh). ASGCN và Sentic-GCN thiết kế cho khía cạnh
   là một cụm từ trong câu: GCN chuyển thông tin từ từ cảm xúc tới nút khía cạnh theo đường cú pháp ngắn, rồi bước che
   chỉ giữ nút khía cạnh, cộng trọng số theo khoảng cách. UIT-ViSFD là nhóm khía cạnh, không có nút khía cạnh trong câu, nên
   cả ba cơ chế bị bỏ (mục 4.3). Đồ thị vì thế **giống hệt nhau cho cả khoảng ba khía cạnh của cùng một bình luận**; khía
   cạnh chỉ đi vào qua truy vấn attention. Đồ thị không giúp phân biệt "pin trâu" thuộc khía cạnh nào, đúng việc nó được
   kỳ vọng làm. Bài Sentic-GCN tự đo: bỏ thành phần T (khía cạnh) mất 1,11 đến 1,55 điểm accuracy.
2. **PhoBERT đã nắm phần lớn thông tin cú pháp** (bằng chứng A, B; có tài liệu). Mười hai lớp tự chú ý đã cho mọi cặp từ
   nhìn nhau; cây phụ thuộc chỉ là một tập con các cặp đó. Ở đây GCN còn chỉ tạo trọng số attention, vector cuối vẫn là
   biểu diễn PhoBERT. Dai và cộng sự (NAACL 2021, "Does syntax matter? A strong baseline for Aspect-based Sentiment
   Analysis with RoBERTa", trang 1816–1829) thấy RoBERTa tinh chỉnh đơn thuần đạt ngang hoặc hơn kết quả tốt nhất đã công
   bố trên sáu tập dữ liệu thuộc bốn ngôn ngữ, và cây suy từ RoBERTa tốt hơn cây của bộ phân tích cú pháp khi đưa vào các
   mô hình đồ thị. Bài này chưa có trong danh mục tài liệu.
3. **Cạnh không có loại, phép gộp không có dấu** (lập luận, khớp với Bảng C.6). GCN coi "không" và "rất" là láng giềng
   như nhau và lấy trung bình; nó không biểu diễn được phủ định lật cực hay "nhưng" làm vế sau thắng. Lỗi còn lại của PhoBERT
   dồn vào chính các hiện tượng đó (mục 4.6), nên một đồ thị cú pháp không loại khó chạm tới chúng.
4. **Huấn luyện thêm dao động** (bằng chứng E, trung bình). Hai lớp GCN 768 chiều khởi tạo ngẫu nhiên, tốc độ học 1e-3, tối
   đa 8 epoch, kiên nhẫn 3: hai seed ASGCN chọn checkpoint sớm, một seed Sentic-GCN chưa hội tụ. Ba seed không đủ tách.
5. **Trần do nhãn** (đã có ở mục 4.6 và phiếu CD1.12h). 212 mẫu sai ở cả 12 lần chạy của bốn mô hình dùng PhoBERT; ở hai
   nhóm khó, 27 đến 35 % nhãn gốc bị người chú thích không đồng ý. Khoảng trống cho bất kỳ thay đổi kiến trúc nào là nhỏ.
6. **Hai biến bị lẫn** (GAP-040). Bậc 3 lên 4 đổi cả cách đọc ra; PhoBERT dùng độ chính xác hỗn hợp còn ba mô hình đồ thị
   thì không.

Không ủng hộ: "đồ thị bị chia cắt là nguyên nhân" (bằng chứng D).

## 5. Ý NGHĨA CHO HƯỚNG ĐỀ TÀI

Kết quả này không bác hướng NS-MGAT, nhưng đặt điều kiện rõ hơn: đồ thị chỉ đáng thêm khi mang thông tin PhoBERT chưa có.
Cụ thể là (a) cạnh có loại cho phủ định và chuyển ý, gộp có tính toán tử chứ không chỉ lấy trung bình; (b) có điểm neo cho
nhóm khía cạnh, nếu không đồ thị giống nhau cho mọi khía cạnh; (c) mọi phần hơn phải được so với "PhoBERT cùng đầu gộp,
không đồ thị", không chỉ so với PhoBERT đọc `<s>`; (d) nhiều seed hơn và cùng thiết lập độ chính xác. Rủi ro cần nói thẳng:
đồ thị cú pháp trong NS-MGAT có thể cũng không đóng góp gì, và phép loại bỏ ở CĐ2 phải đo được điều đó.

## 6. KIỂM CHỨNG

- Kịch bản tạm đọc cả 12 file dự đoán, kiểm cùng thứ tự uid và nhãn thật với `data/processed/visfd_test.jsonl` (assert).
- Phép tách theo số gốc: tập mẫu mà `SyntacticGraphBuilder(link_roots=True)` sinh số cạnh khác `link_roots=False` trùng
  khít tập mẫu có từ hai gốc (3.726 mẫu), nên nhóm "một gốc" đúng là nhóm nối gốc không chạm tới.
- Số của nhóm trái cảm xúc khớp `results/error_analysis.json` (khoá `loai_cau`, `da_trai`): PhoBERT 87,68 % accuracy,
  84,88 % macro-F1.
- `gcn_layers: 0`: `len(model.gcn) == 0`, đầu ra (4, 3) hữu hạn, thay ma trận kề bằng toàn 0 cho đúng cùng đầu ra.
- Tài liệu Dai và cộng sự 2021: tra trên ACL Anthology (2021.naacl-main.146).

## 7. DỪNG LẠI VÀ HỎI

Đề xuất huấn luyện lại, theo thứ tự đáng làm (thời gian theo Bảng 4.6, Tesla T4):

| | Thí nghiệm | Trả lời câu hỏi | Chi phí |
|---|---|---|---|
| R1 | Đối chứng "PhoBERT cộng gộp attention theo khía cạnh, không GCN": file config mới kế thừa `asgcn.yaml`, chỉ ghi `gcn_layers: 0`; ba seed | Phần thua là do cách đọc ra hay do GCN | khoảng 3 giờ |
| R2 | Thêm hai seed cho PhoBERT, ASGCN và R1 | ASGCN thua thật hay do seed; nối gốc hơn thật hay do seed | khoảng 5 giờ |
| R3 | PhoBERT không dùng độ chính xác hỗn hợp, ba seed | Gỡ biến lẫn thứ hai | khoảng 2,5 giờ (ước tính, chưa đo PhoBERT không dùng độ chính xác hỗn hợp) |

Lưu ý khi chạy R1: phải truyền `--exp-name` (ví dụ `asgcn_khong_gcn`), vì mặc định tên thí nghiệm bằng `--model`, chạy
`--model asgcn` mà quên cờ này sẽ ghi đè `results/asgcn/`.

Câu hỏi cho học viên:

1. Chạy R1 (và R2, R3) hay chỉ sửa lời văn theo GAP-040 mục 5 hướng 2?
2. Có đưa kịch bản phân tích tạm vào repo thành `scripts/` (kèm test và sổ tay lệnh) để con số ở phiếu này tái lập được không?
3. Có thêm Dai và cộng sự 2021 vào danh mục tài liệu để dẫn ở mục 4.4 và 4.7 không?

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

**16/10/2026, học viên quyết:** chạy R1, R2, R3 trên Kaggle, chạy ngầm bằng Save Version, một lần bấm; muốn chắc chắn đồ
thị không giúp, hoặc tốt hơn là khảo sát xem có cách nào đồ thị đóng góp được.

Đã chuẩn bị (chưa chạy):

- `configs/asgcn_khong_gcn.yaml` (R1) và `configs/phobert_fp32.yaml` (R3), mỗi file khác file cha đúng một khoá; bốn test
  mới (khác đúng một khoá ×2, `gcn_layers: 0` thì đồ thị không còn ảnh hưởng, số tham số bằng PhoBERT).
- `notebooks/kaggle_doi_chung_do_thi.ipynb`: 17 lần chạy trên hai GPU của T4 x2, khoảng 8 đến 9 giờ, chốt nhận việc ở mốc
  11 giờ, chạy nốt được từ output version trước. Đã chạy thử ở máy với lệnh huấn luyện giả (xong, lỗi, bỏ qua vì hết giờ,
  giữ đúng best.pt, chạy nốt).
- Mở rộng so với bảng ở mục 7, vì mục tiêu là "chắc chắn": R2 thêm hai seed cho cả `asgcn_linked` và `senticgcn` (để ba
  mô hình đồ thị đều có 5 seed), và thêm `phobert_kaggle` (PhoBERT seed 42 chạy lại trên Kaggle) để đo lệch do đổi nền
  tảng, vì các lần chạy mới ở Kaggle còn ba seed cũ ở Colab. Seed mới: 7 và 123.
