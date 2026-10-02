# PHIẾU BÀN GIAO — [CD1.6a'] `asgcn_linked` và soi lỗi theo khía cạnh

> Tiếp sau [CD1.6a_chay-3-seed.md](CD1.6a_chay-3-seed.md). Phiếu đó nêu bốn cách đọc kết quả
> âm của `asgcn`; phiếu này kiểm cách giải thích số 2 và số 4.

**Ngày:** 02/10/2026 · **Step:** CD1.6a' · **Ánh xạ plan gốc:** S1.2 + GAP-007 phương án C · **Thời gian GPU:** 188 phút cho 3 seed

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `results/asgcn_linked/seed{42,1337,2024}/` | Tạo | Kết quả 3 lần chạy, mỗi seed `metrics.json` và `predictions.jsonl` |
| `logs/asgcn_linked/seed*.log` | Tạo | Nhật ký từng epoch |
| `scripts/soi_khia_canh.py` | Tạo | Soi `predictions.jsonl` theo khía cạnh, bốn bảng, chạy ở máy không cần GPU |
| `tests/test_soi_khia_canh.py` | Tạo | 21 test, trong đó có bước đối chiếu F1 tự tính với `f1_per_class` của cả 9 lần chạy |

Không sửa dòng mã nào. `asgcn_linked.yaml` kế thừa `asgcn.yaml` và chỉ ghi đè `link_roots`,
nên hai thí nghiệm khác nhau đúng một khoá.

---

## 2. ĐỂ LÀM GÌ

Hai câu hỏi, cả hai đều sinh ra từ kết quả âm của `asgcn`.

**Một.** 52,2 % Example có cây phụ thuộc vỡ thành nhiều mảnh rời. Nối các mảnh lại thì cứu
được bao nhiêu? Đây là cách giải thích số 2 của phiếu trước.

**Hai.** Phần sụt dồn 81 % vào lớp trung lập. Lớp đó hỏng ở những khía cạnh nào? Đây là cách
giải thích số 4.

---

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1 Nối các cây con rời nhau cứu được khoảng bảy phần mười

| Mô hình | accuracy | macro-F1 | F1 trung lập |
|---|---|---|---|
| lexicon | 0,7469 ± 0,0002 | 0,5240 ± 0,0002 | — |
| bilstm | 0,8642 ± 0,0062 | 0,7949 ± 0,0106 | — |
| phobert | 0,9186 ± 0,0011 | 0,8664 ± 0,0014 | 0,7131 ± 0,0037 |
| asgcn | 0,9133 ± 0,0038 | 0,8543 ± 0,0114 | 0,6836 ± 0,0278 |
| **asgcn_linked** | **0,9164 ± 0,0008** | **0,8626 ± 0,0029** | **0,7043 ± 0,0068** |

Khoảng cách với `phobert` thu hẹp lại:

| Chỉ số | `asgcn` thua | `asgcn_linked` thua | Lấy lại được |
|---|---|---|---|
| accuracy | 0,0053 | 0,0022 | 59 % |
| macro-F1 | 0,0121 | 0,0038 | **69 %** |
| F1 trung lập | 0,0295 | 0,0088 | **70 %** |

**Đây là bằng chứng trực tiếp cho cách giải thích số 2.** Đồ thị cú pháp bị vỡ đúng là một
nguyên nhân lớn, và nó giải thích được khoảng bảy phần mười phần thiệt.

Một điều nữa còn sạch hơn con số trung bình: **độ ổn định**. Độ lệch chuẩn giữa các seed giảm
gần bốn lần ở cả hai chỗ, macro-F1 từ 0,0114 xuống 0,0029 và F1 trung lập từ 0,0278 xuống
0,0068. `asgcn_linked` thậm chí ổn định hơn cả `phobert` ở accuracy.

Đọc được thành một câu: chạy GCN trên một đồ thị vỡ không chỉ làm kết quả kém hơn, nó còn làm
kết quả **phụ thuộc vào may rủi khởi tạo**, vì mỗi lần khởi tạo lại, mô hình phải tự xoay xở
với một cấu trúc không nối thông.

Cẩn trọng cần giữ: 0,0038 macro-F1 còn lại vẫn là `asgcn_linked` thua `phobert`, và chưa chạy
kiểm định ý nghĩa. Nối gốc **không** biến cú pháp thành có ích, nó chỉ gỡ gần hết phần hại.

### 3.2 Lớp trung lập, phần lớn, là chuyện của riêng giá tiền

| Khía cạnh | Tổng | Trung lập | Trung lập chiếm |
|---|---|---|---|
| **PRICE** | 569 | **328** | **57,6 %** |
| PERFORMANCE | 1.172 | 116 | 9,9 % |
| BATTERY | 1.014 | 92 | 9,1 % |
| GENERAL | 1.381 | 83 | 6,0 % |
| CAMERA | 588 | 71 | 12,1 % |
| FEATURES | 711 | 52 | 7,3 % |
| DESIGN | 398 | 28 | 7,0 % |
| SER&ACC | 593 | 27 | 4,6 % |
| SCREEN | 269 | 17 | 6,3 % |
| STORAGE | 27 | 3 | 11,1 % |
| Toàn tập test | 6.722 | 817 | 12,2 % |

**328 trong 817 câu trung lập, tức 40 %, thuộc về PRICE.** Và hơn một nửa số câu nói về giá
là trung lập.

Điều này hợp lý về mặt ngôn ngữ: câu nói về giá thường là một mệnh đề sự kiện, kiểu nêu con
số, không khen không chê. Các khía cạnh khác thì người dùng viết ra chủ yếu để khen hoặc chê.

Hệ quả cho cách đọc mọi con số macro-F1 từ nay: **macro-F1 đánh trọng số rất nặng cho một lớp
mà bản thân lớp đó lại nghiêng hẳn về một khía cạnh.** Cải thiện macro-F1 trên bộ dữ liệu này
phần lớn là cải thiện khả năng nhận ra câu nêu giá.

### 3.3 Hỏng nặng nhất ở nơi ít dữ liệu trung lập nhất

F1 lớp trung lập, tính riêng từng khía cạnh, trung bình 3 seed:

| Khía cạnh | n trung lập | phobert | asgcn | asgcn_linked |
|---|---|---|---|---|
| PRICE | 328 | 0,8953 ± 0,0045 | 0,8708 ± 0,0239 | 0,8786 ± 0,0123 |
| PERFORMANCE | 116 | 0,5318 ± 0,0159 | 0,5292 ± 0,0565 | 0,5595 ± 0,0059 |
| BATTERY | 92 | 0,6599 ± 0,0149 | 0,6156 ± 0,0128 | 0,6281 ± 0,0310 |
| GENERAL | 83 | 0,6664 ± 0,0180 | 0,6386 ± 0,0381 | 0,6362 ± 0,0375 |
| CAMERA | 71 | 0,7101 ± 0,0465 | 0,6648 ± 0,0763 | 0,7247 ± 0,0423 |
| FEATURES | 52 | 0,4815 ± 0,0221 | 0,4552 ± 0,1715 | 0,4980 ± 0,0704 |
| DESIGN | 28 | 0,4106 ± 0,0610 | 0,3869 ± 0,0884 | 0,3462 ± 0,0739 |
| SER&ACC | 27 | 0,4192 ± 0,0806 | **0,1953 ± 0,1857** | 0,2527 ± 0,1612 |
| SCREEN | 17 | 0,3258 ± 0,0266 | 0,2724 ± 0,1123 | 0,4310 ± 0,1099 |
| STORAGE | 3 | 0,5000 | 0,3778 | 0,4111 |

Hai điều đọc ra được.

**Thứ nhất, F1 đi theo lượng dữ liệu gần như đơn điệu.** PRICE có 328 câu trung lập và đạt
0,90; SCREEN có 17 câu và đạt 0,33. Không phải vì màn hình khó nói hơn giá tiền, mà vì mô
hình chưa từng thấy đủ ví dụ.

**Thứ hai, chỗ `asgcn` hỏng nặng nhất là SER&ACC**, từ 0,4192 xuống 0,1953, mất hơn một nửa,
với độ lệch chuẩn 0,1857. Độ lệch chuẩn lớn hơn cả nửa giá trị trung bình nghĩa là ở khía
cạnh này mô hình gần như **đoán**: có seed làm được, có seed không. FEATURES cũng vậy, độ
lệch chuẩn 0,1715.

Gộp hai điều lại: cú pháp vỡ không làm hỏng đều. Nó biến những khía cạnh vốn đã mỏng dữ liệu
thành ra ngẫu nhiên. Đây đúng là cách giải thích số 4 của phiếu trước, nay có số liệu.

### 3.4 Câu trung lập bị đoán nhầm thành gì

| Mô hình | Đoán đúng | Nhầm thành tiêu cực | Nhầm thành tích cực |
|---|---|---|---|
| phobert | 553,7 (67,8 %) | 121,0 (14,8 %) | 142,3 (17,4 %) |
| asgcn | 513,3 (62,8 %) | 144,3 (17,7 %) | 159,3 (19,5 %) |
| asgcn_linked | 537,0 (65,7 %) | 133,3 (16,3 %) | 146,7 (18,0 %) |

Lỗi chia khá đều về hai phía, nghiêng nhẹ sang tích cực ở cả ba mô hình. Không có hiện tượng
mô hình đẩy câu trung lập về một cực nhất định.

`asgcn` mất 40 câu trung lập so với `phobert`; `asgcn_linked` lấy lại 24 trong số đó.

### 3.5 Ý nghĩa cho CĐ2

**Một.** Trần có thể cải thiện nằm ở các khía cạnh mỏng dữ liệu, không nằm ở PRICE. PRICE đã
0,88 đến 0,90, khó nâng. SCREEN, SER&ACC, DESIGN đang 0,25 đến 0,43 với tổng cộng 72 câu
trung lập. NS-MGAT muốn hơn `phobert` về macro-F1 thì phải thắng ở đúng vùng mỏng đó.

**Hai.** Đây là một luận cứ cho hướng neo ký hiệu. Khi dữ liệu mỏng, học thuần từ ví dụ không
đủ, và luật phủ định hay tương phản viết tay có chỗ đứng chính đáng, không phải thêm vào cho
đẹp kiến trúc.

**Ba.** Cần cẩn thận khi báo cáo: độ lệch chuẩn ở các khía cạnh mỏng rất lớn, nên mọi so sánh
theo từng khía cạnh phải kèm độ lệch chuẩn, và với n dưới 30 thì nên nói rõ là chỉ mang tính
gợi ý.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Phân tích theo khía cạnh làm ở đâu | `scripts/soi_khia_canh.py`, một công cụ riêng, có kèm test | Viết luôn vào `scripts/error_analysis.py` | File đó thuộc S5.4 và còn phải làm ca minh hoạ khả năng giải thích, chưa tới lượt. Quy tắc 6 của README: không viết logic của step sau. Học viên chốt 02/10/2026: đưa vào kho để mọi con số trong phiếu này tính lại được, tới S5.4 xem lại có gộp không |
| Tin vào công thức F1 tự viết kiểu gì | Đối chiếu với `f1_per_class` mà đường huấn luyện thật đã ghi, cả 9 lần chạy | Tin vì đọc lại thấy đúng | Hai con số đi qua hai đường độc lập: một bên `nsmgat.evaluate`, một bên đếm tay trên `predictions.jsonl`. Trùng khớp cả 9 thì mới tin được cả hai. Đã khoá bằng test |
| Gộp 3 seed kiểu gì | Tính chỉ số trên từng seed rồi lấy trung bình và độ lệch chuẩn | Gộp dự đoán 3 seed rồi tính một lần | Gộp trước thì mất thông tin về dao động, mà dao động chính là phát hiện đáng giá nhất ở mục 3.3 |
| Thứ tự làm | Soi khía cạnh trước, `senticgcn` sau | Chạy `senticgcn` ngay | Hạn mức GPU đang cạn, việc này không tốn GPU. Kết quả của nó còn giúp đọc `senticgcn` sắc hơn |
| Có kết luận cú pháp vô dụng không | **Không**, chỉ kết luận đồ thị vỡ gây hại | Kết luận cú pháp không giúp gì | `asgcn_linked` vẫn thua `phobert` 0,0038 macro-F1, nhưng chưa kiểm định, và còn hai cách giải thích chưa kiểm |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Bảng ở mục 3.1 là Bảng 4.5 của cuốn chuyên đề, đã đủ năm dòng của thang baseline.
- Mục 3.2 và 3.3 là nội dung mới cho mục 4.1 mô tả dữ liệu: con số 40 % câu trung lập thuộc
  PRICE chưa từng xuất hiện ở đâu trong báo cáo.
- CĐ1.6b `senticgcn` nên chạy với `link_roots: true`, vì nay đã có bằng chứng rằng để đồ thị
  vỡ làm hỏng kết quả và làm mất ổn định. Cần một quyết định rõ ràng về chuyện này.
- S5.4 `scripts/error_analysis.py` sẽ làm lại phân tích này cho đàng hoàng, kèm ca minh hoạ.
- Ba câu hỏi gửi GVHD vẫn chưa gửi, nay đủ số liệu để gửi cùng kết quả `asgcn` và `asgcn_linked`.

---

## 6. KIỂM CHỨNG — bằng chứng chạy thật

```
333 passed in 69.97s
```

Trước step này 312 test, nay 333, thêm đúng 21 test của `tests/test_soi_khia_canh.py`.

Test đáng giá nhất là `test_f1_khop_voi_f1_per_class_trong_metrics`: nó chạy trên cả 9 lần
chạy và đòi F1 do `scripts/soi_khia_canh.py` tự đếm phải trùng tới 6 chữ số với
`f1_per_class` mà `nsmgat.evaluate` đã ghi vào `metrics.json`. Hai con số đi qua hai đường
độc lập, nên trùng khớp là bằng chứng cho cả hai, không phải chỉ cho một.

Test thứ hai đáng nói là `test_nhan_that_giong_nhau_o_MOI_mo_hinh_va_seed`. Bảng ở mục 3.2
dựa trên một câu chưa ai kiểm: nhãn thật thì mô hình nào cũng như nhau. Test này khoá câu đó
lại bằng cách so từng bộ ba `uid`, `aspect`, `y_true` của cả 9 lần chạy.

Chín file của `asgcn_linked` tải từ Colab về, kiểm đủ:

| Seed | Vân tay | Khớp giá trị tính lại | Số dòng | Thời gian |
|---|---|---|---|---|
| 42 | `91c68e846232` | có | 6.722 | 62,3 phút |
| 1337 | `3ee7d4f267b3` | có | 6.722 | 57,9 phút |
| 2024 | `ffb7f8f134cb` | có | 6.722 | 68,2 phút |

`exp_name` cả ba đều là `asgcn_linked`, không ghi đè lên `results/asgcn/`.

Mọi con số trong phiếu này tính trực tiếp từ `predictions.jsonl` và `metrics.json` trong kho,
không chép tay từ đâu.

**Chưa chạy kiểm định ý nghĩa thống kê.** Với 3 seed thì kiểm định t ghép cặp có lực rất
thấp, và điều đó phải nói rõ trong báo cáo.

---

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi cần bạn quyết:**

1. ~~Script soi khía cạnh để ở thư mục nháp hay đưa vào kho?~~ **Học viên chốt 02/10/2026:
   đưa vào kho thành `scripts/soi_khia_canh.py`**, kèm 21 test, để mọi con số trong phiếu này
   tính lại được. Tới S5.4 xem lại có gộp vào `error_analysis.py` không.
2. `senticgcn` ở CĐ1.6b chạy với `link_roots: true` hay `false`? **Chưa trả lời.**

**Những chỗ có thể bạn muốn hỏi thêm:**

- `asgcn_linked` vẫn thua `phobert`, vậy viết vào báo cáo là cú pháp có ích hay vô ích?
- Có nên thêm một thí nghiệm chỉ dùng PRICE để kiểm giả thuyết ở mục 3.2 không?
- Khía cạnh chỉ có 3 câu trung lập như STORAGE thì có nên đưa vào bảng không?

**Kết:**
> Bạn muốn sang CĐ1.6b `senticgcn`, hay viết báo cáo gửi GVHD trước vì giờ đã đủ số liệu?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
