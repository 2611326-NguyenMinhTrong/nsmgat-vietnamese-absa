# PHIẾU BÀN GIAO — [CD1.11] Ba phép thăm dò trần cải tiến (P1, P2, P3)

**Ngày:** 18/10/2026 · **Step:** CD1.11 · **Ánh xạ plan gốc:** `[MỚI]` · **Thời gian thực tế:** khoảng 2 giờ

Học viên: "phần GPT-4o tạm thời sẽ làm sau cùng, giờ làm tiếp bước tiếp theo". Bước tiếp theo trong
`PLAN_CHUYENDE1.md` (bỏ qua E9 GPT-4o) là CD1.11, cũng là việc phiếu CD1.12h gọi là "bằng chứng còn thiếu quan
trọng nhất" cho hướng đề tài.

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `scripts/probe_oracle_rules.py` | Tạo | Ba phép thăm dò P1, P2, P3; chỉ đọc dữ liệu đã có, không huấn luyện, chạy khoảng 2 giây |
| `tests/test_probe_oracle_rules.py` | Tạo | 12 test: luật lý tưởng, ước lượng theo ô, khoảng cách trên cây, chặn dữ liệu lệch, khớp kết quả đã công bố |
| `results/probe_results.json` | Tạo | Toàn bộ số của ba phép thăm dò (file plan đã đặt tên sẵn) |
| `chuyende1/tables/bang_5_tham_do.md` | Tạo | Bốn bảng P1a, P1b, P2, P3 |
| `chuyende1/MODULE.md` | Sửa | Thêm dòng công cụ; đánh dấu xong mục "probe_results.json có đủ 3 con số" |
| `SO_TAY_LENH.md` (chỉ ở máy) | Sửa | Mục 11n và một dòng ở bảng tra nhanh |

```powershell
.\.venv\Scripts\python.exe scripts\probe_oracle_rules.py
.\.venv\Scripts\python.exe scripts\probe_oracle_rules.py --mo-hinh asgcn --chi-in   # và asgcn_linked, senticgcn: kiểm độ vững của P1
```

Chưa sửa gì trong báo cáo (bản nháp và file Word không đổi).

---

## 2. ĐỂ LÀM GÌ

- **Vấn đề:** đề tài đặt cược vào việc xử lý tường minh phủ định và chuyển ý, nhưng tới nay chưa có con số nào nói
  hướng đó đáng giá bao nhiêu trên UIT-ViSFD. Chương 4 đã cho thấy thêm cây cú pháp lên PhoBERT chưa có lợi đo được.
- **Sau step này:** có ba con số để mục 5.4 lập luận, và để Chương 6 chọn hướng cho Chuyên đề 2 bằng số đo thay vì
  bằng lời hứa.
- **Nếu bỏ:** mục 5.4 và 5.5 không có chỗ dựa; câu hỏi phản biện "vì sao chọn luật mà không chọn cách khác" và
  "độ tin cậy 0,92 của luật ở đâu ra" (PLAN_CHUYENDE1 mục 8) không có câu trả lời.

---

## 3. CƠ CHẾ VÀ KẾT QUẢ

### P1. Trần của luật lật cực

Ý tưởng: cách xử lý phủ định quen thuộc nhất là lật cực ý kiến (tích cực thành tiêu cực và ngược lại). Một luật như
vậy, kể cả khi hoàn hảo, chỉ sửa được lỗi mô hình đoán NGƯỢC CỰC. Lỗi có lớp trung tính ở một đầu thì lật không sửa
được. Phép thăm dò cho một luật "biết trước nhãn thật": lật đúng mọi lỗi ngược cực trong phạm vi, không lật nhầm chỗ
nào, rồi đo macro-F1 tăng bao nhiêu. Đó là trần: không luật lật cực thật nào vượt được.

Ví dụ: mẫu 01975, khía cạnh PRICE. Câu chê số tiền bỏ ra không xứng với chất lượng, có từ "không". Nhãn gốc là
trung tính, PhoBERT đoán tiêu cực ở cả 5 seed. Lỗi này có trung tính ở một đầu, nên luật lật cực không sửa được. Người
chú thích cũng không đồng ý với nhãn gốc ở dòng này (ghi tiêu cực), tức mô hình có thể mới là bên đúng.

Kết quả với PhoBERT, trung bình 5 seed (Bảng P1a, P1b):

| Phạm vi | Lỗi mỗi seed | Lỗi ngược cực | Macro-F1 tăng khi lật đúng hết |
|---|---|---|---|
| Tập chẩn đoán, nhóm phủ định (119 dòng) | 11,6 | 1,2 | 0,88 điểm (trong nhóm) |
| Tập chẩn đoán, nhóm thường (415 dòng) | 34,8 | 2,8 | 0,71 điểm (trong nhóm) |
| Toàn tập kiểm tra, câu có từ khoá phủ định | 551,8 (cả tập) | 59,4 | 0,71 điểm |
| Toàn tập kiểm tra, mọi chỗ | 551,8 | 96,8 | 1,16 điểm |

Ba điều đọc ra:

1. PhoBERT gần như không nhầm cực ở câu phủ định: 1,2 trong 11,6 lỗi mỗi seed. Phần lớn lỗi (8,8 trên 11,6) là nhãn
   gốc trung tính mà mô hình đoán có cực. Ba mô hình đồ thị cho kết quả giống vậy: lật đúng hết ở nhóm phủ định tăng
   0,89 đến 1,16 điểm, trên toàn tập 0,69 đến 0,77 điểm.
2. Luật lật cực không có lợi riêng cho câu phủ định: nhóm thường cũng tăng 0,71 điểm khi lật đúng hết.
3. Hơn một nửa số lỗi ở ba nhóm hiện tượng nằm ở dòng người chú thích không đồng ý với nhãn gốc (6,0 trên 11,6;
   15,2 trên 26,6; 13,0 trên 21,8). Phần lỗi đó chưa chắc là lỗi của mô hình.

Plan (mục CD1.11) đặt ngưỡng: "Nếu P1 cho trần rất thấp (ví dụ < +1,5 điểm): đó là kết quả có giá trị... Chuyên đề
2 phải đổi hướng. Báo GVHD ngay". Trần đo được là 0,88 điểm ở nhóm phủ định và 0,71 điểm trên toàn tập, tức dưới ngưỡng.

Cận trên lỏng ở dòng cuối Bảng P1b (sửa mọi lỗi ở câu có từ khoá phủ định hoặc chuyển ý: tăng 10,23 điểm) không dùng
được để lập luận: 4.268 trên 6.722 mẫu thuộc câu có từ khoá, nên phạm vi đó chứa 420 trên 552 lỗi, gần như cả tập.

### P2. Độ chính xác và độ phủ của luật từ khoá

Luật tối giản: mẫu (câu, khía cạnh) có phủ định nếu câu có từ khoá phủ định; có chuyển ý nếu câu có từ nối chuyển ý.
Đúng hai danh sách từ khoá đã dùng để lọc ứng viên. Đối chiếu với nhãn hiện tượng của người chú thích.

Vì sao phải ước lượng theo ô: tập chẩn đoán rút cân bằng nhãn trong từng nhóm từ khoá, nên tỉ lệ thô không đại diện
cho tập kiểm tra. Ví dụ hai ô:

- ô (có từ phủ định, nhãn tiêu cực): tập kiểm tra có 719 mẫu, tập chẩn đoán rút 84 dòng, 46 dòng có phủ định thật.
  Ước lượng cho cả ô: 719 × 46 / 84 ≈ 394 mẫu;
- ô (không từ khoá nào, nhãn tích cực): 1.316 mẫu, rút 66 dòng, 1 dòng có phủ định. Ước lượng: 1.316 / 66 ≈ 20 mẫu.
  Mỗi dòng ở ô này đại diện cho khoảng 20 mẫu, còn ở ô trên chỉ khoảng 9.

Cộng các ô lại ra số mẫu có phủ định mà luật bắt và luật bỏ sót. Quần thể là 4.071 mẫu thuộc câu 5 đến 40 từ và không
chỉ chứa từ ngờ; 2.651 mẫu còn lại không ước lượng được vì không được rút (Bảng P2 ghi rõ).

| Luật | Độ chính xác | Độ phủ |
|---|---|---|
| Câu có từ khoá phủ định | 49,5 % (KTC 95 %: 43,8 đến 55,2) | 94,7 % (90,2 đến 98,1) |
| Câu có từ nối chuyển ý | 58,2 % (52,6 đến 63,8) | 59,9 % (52,1 đến 68,8) |

Đọc ra:

1. Danh sách từ phủ định bắt gần hết phủ định, nhưng chỉ khoảng một nửa số mẫu nó bắt là có phủ định tác động lên
   đúng khía cạnh đó. Lý do chính: một câu có nhiều khía cạnh, từ "không" thường chỉ tác động lên một (quy tắc K1 của
   hướng dẫn), hoặc không mang nghĩa phủ định ý kiến (K3). Ở mức khía cạnh, độ tin cậy của luật thô khoảng 0,5, xa
   con số 0,92 mà bản kế hoạch NS-MGAT nêu làm ví dụ.
2. Luật chuyển ý bỏ sót khoảng 40 %. Trên tập chẩn đoán có 52 dòng chuyển ý hoặc cả hai mà câu không có từ nối nào
   trong danh sách; 19 dòng trong số đó có từ ngờ, 33 dòng không có từ nào của cả hai danh sách (Bảng P2, hai cột
   cuối). Đếm tạm thì từ ngờ ở 19 dòng chủ yếu là "mà" và "còn". Xem tay vài dòng thì thấy cả cách tách từ ("có điều"
   bị tách thành hai từ, không khớp "có_điều") lẫn cách nói không có trong danh sách.
3. Cái khó không nằm ở việc nhận ra từ phủ định, mà ở việc gắn nó vào đúng khía cạnh. Muốn có "cửa sổ quanh khía cạnh"
   như plan ghi thì cần từ điển cụm từ của từng khía cạnh, vì khía cạnh của UIT-ViSFD không có vị trí trong câu.

### P3. Cây cú pháp và từ phủ định

Lấy mọi lượt từ khoá phủ định trong 2.187 câu của tập kiểm tra mà ngay sau là một từ cùng câu (không phải dấu câu).
Trong tiếng Việt từ phủ định đứng ngay trước vị từ nó phủ định, nên khoảng cách tuyến tính là 1. Đo trên cây VnCoreNLP:

| Dạng | Lượt có từ đứng sau | Gán nhãn phó từ | Kề nhau trên cây | Cách từ 3 cạnh | Khoảng cách trung bình |
|---|---|---|---|---|---|
| Chuẩn (không, chưa, chẳng, chả...) | 969 | 99,7 % | 94,4 % | 1,3 % | 1,08 |
| Viết tắt (ko, k, kh...) | 961 | 0,0 % | 72,5 % | 12,2 % | 1,51 |

Ví dụ (dựng tay trong test): "pin ko trâu". VnCoreNLP gán "ko" là động từ và làm gốc câu, "trâu" lại gắn vào "pin".
Đường đi trên cây từ "ko" tới "trâu" là ko, pin, trâu: 2 cạnh, trong khi hai từ đứng liền nhau.

Đọc ra:

1. Cây cú pháp không đưa từ phủ định lại gần hơn: với dạng chuẩn hai từ đã kề nhau sẵn; với dạng viết tắt cây còn làm
   xa hơn ở hơn một phần tư số lượt (27,5 % không kề nhau).
2. Một nửa số lượt từ phủ định trong tập kiểm tra là dạng viết tắt (1.009 trên 2.019), và VnCoreNLP không gán nhãn phó
   từ cho lượt nào trong 961 lượt đo được. Một cạnh "phủ định" dựa vào nhãn từ loại sẽ bỏ sót cả nửa này.
3. Điều này khớp với Chương 4: GCN trên cây cú pháp không cho lợi đo được.

Chỗ dễ hiểu sai nhất:

- P1 là trần của luật LẬT CỰC, không phải trần của mọi cách xử lý phủ định. Một mô hình học được từ cạnh phủ định vẫn
  có thể sửa lỗi có lớp trung tính. P1 chỉ nói: lợi ích, nếu có, không đến từ việc lật cực.
- Độ chính xác ở P2 tính theo cặp (câu, khía cạnh), không theo câu. Theo câu thì luật từ khoá gần như luôn đúng là câu
  có từ phủ định.
- Ở P3, "từ đứng sau" chỉ là xấp xỉ của từ bị phủ định; có thể sai ở câu như "không phải máy này tệ".

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Luật lý tưởng của P1 | Chỉ sửa lỗi ngược cực | Sửa mọi lỗi trong nhóm | Cho 100 % ở nhóm, không nói gì; plan cũng ghi "lật dự đoán" |
| Phạm vi P1 | Cả bốn nhóm, thêm toàn tập kiểm tra | Chỉ nhóm phủ định như plan | Không có nhóm thường để so thì không biết lỗi ngược cực có tập trung ở câu phủ định không |
| Mô hình của P1 | PhoBERT, cờ `--mo-hinh` cho mô hình khác | Cả sáu mô hình trong một bảng | PhoBERT là mốc chính và là xương sống dự kiến của mô hình đề xuất; ba mô hình đồ thị đã chạy để kiểm độ vững (mục 3) |
| Số dòng của P2 | Cả 794 dòng trong quần thể | 150 câu như plan | Dùng hết dữ liệu đã gán thì khoảng tin cậy hẹp hơn |
| Cách ước lượng P2 | Theo ô (nhóm từ khoá, nhãn gốc), trọng số số mẫu chia số dòng rút | Tỉ lệ thô trên tập chẩn đoán | Tập rút cân bằng nhãn, ô không từ khoá bị rút thưa: độ phủ thô sẽ sai |
| Khoảng tin cậy P2 | Bootstrap trong từng ô (rút nhị thức) | Theo câu | Ô được rút độc lập; các dòng cùng câu có thể nằm ở các ô khác nhau. Hệ quả: khoảng tin cậy có thể hơi hẹp |
| Cửa sổ quanh khía cạnh | Không làm | Từ điển cụm từ khía cạnh | Là việc của Chuyên đề 2 (S2.2); khía cạnh không có vị trí trong câu |
| Tập của P3 | Mọi câu của tập kiểm tra | Các mẫu cả bốn mô hình cùng sai, như plan | Cách bộ phân tích xử lý từ phủ định không phụ thuộc mô hình nào sai; tập cùng sai quá nhỏ cho một tỉ lệ |
| Đích của P3 | Từ đứng ngay sau | Từ cảm xúc gần nhất theo từ điển | Phải đặt ngưỡng điểm từ điển tuỳ ý; dạng chuẩn kề từ đứng sau trên cây ở 94,4 % số lượt nên xấp xỉ này hợp dữ liệu |
| Danh sách từ khoá | Import từ `build_diagnostic_candidates.py` | Chép sang file mới | Hai bản sẽ lệch nhau |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Step kế tiếp trong plan: **viết Chương 5** (cùng tuần với CD1.11). Dùng `chuyende1/tables/bang_5_phan_tich_loi.md`
  (đã là 5 seed) cho mục 5.1, 5.2 và `bang_5_tham_do.md` cho mục 5.4.
- Mục 5.3 (ca điển hình) cần việc A14 của học viên: đọc 10 ca cả bốn mô hình cùng sai. Danh sách ca hiện ở
  `chuyende1/report/nhap/ca_cung_sai.md` làm theo 3 seed; với 5 seed phải rút lại.
- Khi viết Chương 5 phải thêm chỗ kiểm cho số của chương (công cụ đối chiếu hiện chỉ có cho Chương 4).
- Kết quả P1 dưới ngưỡng của plan, nên trước khi viết mục 5.5 cần học viên chọn cách đặt hướng (mục 7).

---

## 6. KIỂM CHỨNG

```
pytest tests/test_probe_oracle_rules.py -q      12 passed
pytest tests -q                                   558 passed, 1 skipped in 121.26s
```

- Macro-F1 gốc của P1 theo từng nhóm khớp `results/diagnostic_eval.json`; trên toàn tập khớp trung bình 5 file
  `results/phobert/seed*/metrics.json` (test `test_khop_ket_qua_da_cong_bo`).
- Số lỗi ngược cực của PhoBERT (96,8 trên 551,8 mỗi seed, tức 17,6 %) khớp Bảng A của `bang_5_phan_tich_loi.md`
  (8,0 % tiêu cực thành tích cực cộng 9,6 % tích cực thành tiêu cực).
- 794 dòng trong quần thể cộng 5 dòng ngoài quần thể bằng 799 dòng của tập chẩn đoán; 4.071 + 2.077 + 574 = 6.722.
- Lệnh dừng nếu file dự đoán lệch uid hay nhãn thật, một dòng của tập chẩn đoán khác nhãn gốc, hoặc một ô của P2 không
  có dòng nào.
- Sự cố: khi thêm mục 11n vào `SO_TAY_LENH.md` bằng heredoc, một đường dẫn có `\t`, `\b` thành ký tự điều khiển; đã
  sửa và quét lại cả bốn file vừa ghi, không còn ký tự điều khiển.

---

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi cần bạn quyết:**

1. P1 dưới ngưỡng của plan. Plan ghi khi đó "Chuyên đề 2 phải đổi hướng, báo GVHD ngay". Đề nghị của tôi: không bỏ phủ
   định và chuyển ý, mà dời trọng tâm của mô hình đề xuất từ "luật lật cực" sang hai việc mà số đo chỉ ra:
   (a) quyết định một khía cạnh trong câu có hiện tượng là trung tính hay có cực (phần lớn lỗi nằm ở đây);
   (b) gắn hiện tượng vào đúng khía cạnh (luật từ khoá chỉ đúng khoảng một nửa ở mức khía cạnh).
   Bạn đồng ý viết Chương 5 theo hướng này không, hay muốn hỏi cô trước?
2. Có viết Chương 5 ngay không? Dàn ý dự kiến khoảng 4 trang, trong khi file Word đang 58 trang.

**Những chỗ tôi đoán bạn có thể muốn hỏi thêm:**

- Vì sao lỗi ngược cực ít như vậy mà accuracy của câu phủ định vẫn không thấp hơn câu thường?
- Nếu bỏ các dòng không đồng ý nhãn gốc thì P1 đổi thế nào?
- Có nên chuẩn hoá "ko", "k" thành "không" trước khi phân tích cú pháp không?

**Kết:**
> Bạn có câu hỏi phụ nào về phần này không, hay tôi đi tiếp sang **viết Chương 5**?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| Luật từ khoá: 94,7 % và 49,5 % nghĩa là gì? | Độ phủ: trong 100 mẫu thật có phủ định, luật bắt khoảng 95. Độ chính xác: trong 100 mẫu luật gắn "có phủ định", khoảng 50 mẫu đúng; sai chủ yếu vì câu nhiều khía cạnh mà "không" chỉ tác động lên một | Không |
| "Gắn hiện tượng vào đúng khía cạnh" NLP đã giải quyết chưa? | Không phải bài toán mới: gắn ý kiến vào khía cạnh là cốt lõi của ABSA (attention, đồ thị cú pháp, AC-MIMLLN cho nhóm khía cạnh, tập MAMS), phủ định theo đối tượng có Moore và Barnes 2021 (trong ma trận). Đề xuất ở mục 7 được rút từ số đo, CHƯA đối chiếu tài liệu: rút lại đề xuất đó làm hướng Chuyên đề 2 cho tới khi tìm tài liệu có chủ đích. Số đo P1 đến P3 không đổi | Không |
