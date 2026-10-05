# PHIẾU BÀN GIAO — [CD1.6b] Chạy `senticgcn` 3 seed và đọc kết quả

> Phần 2, phần cuối của CD1.6b. Phần trước: [CD1.6b_senticgcn.md](CD1.6b_senticgcn.md) (mô hình
> và cấu hình). Hai phiếu cần đọc kèm vì phiếu này đọc lại kết luận của chúng:
> [CD1.6a_chay-3-seed.md](CD1.6a_chay-3-seed.md) và
> [CD1.6a_asgcn-linked-va-soi-khia-canh.md](CD1.6a_asgcn-linked-va-soi-khia-canh.md).

**Ngày:** 04/10/2026 · **Step:** CD1.6b (phần 2/2) · **Ánh xạ plan gốc:** S1.3 · **Thời gian GPU thực tế:** 227 phút cho 3 seed

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `results/senticgcn/seed{42,1337,2024}/metrics.json` | Tạo | Kết quả 3 lần chạy trên Colab T4 |
| `results/senticgcn/seed{42,1337,2024}/predictions.jsonl` | Tạo | Dự đoán từng mẫu, 6.722 dòng mỗi seed, kèm xác suất 3 lớp |
| `logs/senticgcn/seed{42,1337,2024}.log` | Tạo | Nhật ký từng epoch |
| `tests/test_soi_khia_canh.py` | Sửa | Thêm `senticgcn` vào danh sách lần chạy được đối chiếu, từ 9 lên 12 |
| `notebooks/da-chay/QUY-UOC.md` | Sửa | Đoạn lệnh tính lại vân tay thiếu bước tiêm tên mô hình |
| `SO_TAY_LENH.md` | Sửa | Hai ô 8 và 9 còn ghi "cùng một vân tay"; thêm hai lệnh soi bốn mô hình ở §11b |
| `chuyende1/gaps/GAP-023_*.md` và `INDEX.md` | Tạo | Sai sót ở phép kiểm vân tay, đã sửa |
| `chuyende1/notes/CD1.6b_senticgcn.md` | Sửa | Thêm một dòng trỏ sang phiếu này |

Không đụng vào `configs/senticgcn.yaml`, `src/nsmgat/models/senticgcn.py` hay bất kỳ file nào
trong `src/` và `configs/` giữa ba lần chạy. Kho có hai commit trong ngày 03/10, và commit sau
(`91b4ad3`) chỉ đổi `notebooks/colab_train.ipynb`.

Lệnh đã chạy trên Colab, ba lần với ba seed:

```bash
python -m nsmgat.train --config configs/senticgcn.yaml --model senticgcn --seed 42
```

Lệnh phân tích ở máy, không cần GPU:

```bash
python scripts/soi_khia_canh.py f1   --exp phobert asgcn asgcn_linked senticgcn
python scripts/soi_khia_canh.py nham --exp phobert asgcn asgcn_linked senticgcn            # lớp 1
python scripts/soi_khia_canh.py nham --exp phobert asgcn asgcn_linked senticgcn --lop 0
python scripts/soi_khia_canh.py nham --exp phobert asgcn asgcn_linked senticgcn --lop 2
python scripts/soi_khia_canh.py loi  --exp phobert asgcn asgcn_linked senticgcn            # lớp 1
python scripts/soi_khia_canh.py loi  --exp phobert asgcn asgcn_linked senticgcn --lop 0
```

---

## 2. ĐỂ LÀM GÌ

- **Vấn đề:** `asgcn` đã đo phần cú pháp và ra kết quả âm. Chưa biết thêm tri thức cảm xúc vào
  trọng số cạnh thì được bao nhiêu điểm.
- **Sau step này:** thang baseline đủ sáu bậc, mỗi bậc 3 seed. Hiệu số `asgcn` sang `senticgcn`
  có số đo.
- **Nếu bỏ step này:** Bảng 4.5 thiếu dòng cuối, và CĐ2 mất mốc gần nhất để đo đóng góp của
  NS-MGAT.

`senticgcn` khác `asgcn` đúng một thứ là **giá trị trong ô ma trận kề**. Số tham số bằng nhau
tuyệt đối, 136.181.763, vì điểm cảm xúc đi vào bằng dữ liệu chứ không bằng tham số học được.

---

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1 Con số

| Mô hình | accuracy | macro-F1 | F1 trung lập | Thời gian |
|---|---|---|---|---|
| lexicon | 0,7469 ± 0,0002 | 0,5240 ± 0,0002 | 0,0000 | 3,7 phút |
| bilstm | 0,8642 ± 0,0062 | 0,7949 ± 0,0106 | 0,6007 ± 0,0217 | 53,3 phút |
| phobert | 0,9186 ± 0,0011 | 0,8664 ± 0,0014 | 0,7131 ± 0,0037 | 23,7 phút |
| asgcn | 0,9133 ± 0,0038 | 0,8543 ± 0,0114 | 0,6836 ± 0,0278 | 62,1 phút |
| asgcn_linked | 0,9164 ± 0,0008 | 0,8626 ± 0,0029 | 0,7043 ± 0,0068 | 62,8 phút |
| **senticgcn** | **0,9145 ± 0,0033** | **0,8650 ± 0,0028** | **0,7125 ± 0,0048** | **75,7 phút** |

Từng seed của `senticgcn`:

| Seed | accuracy | macro-F1 | F1 trung lập | Epoch tốt nhất | Chạy tới epoch | Thời gian |
|---|---|---|---|---|---|---|
| 42 | 0,9119 | 0,8628 | 0,7077 | 5 | 8 | 79,3 phút |
| 1337 | 0,9133 | 0,8640 | 0,7127 | **8** | 8 | 70,2 phút |
| 2024 | 0,9182 | 0,8682 | 0,7172 | 7 | 8 | 77,6 phút |

Hiệu số trung bình của `senticgcn` với ba mô hình đứng trước:

| So với | accuracy | macro-F1 | F1 tiêu cực | F1 trung lập | F1 tích cực |
|---|---|---|---|---|---|
| asgcn | +0,0012 | **+0,0107** | +0,0039 | +0,0289 | −0,0009 |
| asgcn_linked | −0,0020 | +0,0024 | −0,0001 | +0,0082 | −0,0011 |
| phobert | **−0,0041** | −0,0014 | +0,0008 | −0,0005 | −0,0045 |

Đọc thẳng: `senticgcn` hơn `asgcn` 0,0107 macro-F1, lấy lại **88 %** khoảng `asgcn` thua
`phobert`, và về macro-F1 thì **ngang `phobert`**: thua 0,0014, đúng bằng một độ lệch chuẩn của
`phobert` và bằng nửa độ lệch chuẩn của chính nó. Về accuracy thì vẫn thua `phobert` 0,0041.

Không mô hình đồ thị nào trong thang vượt được `phobert`.

Thời gian mỗi epoch gần như bằng `asgcn`: 227 phút cho 24 epoch, tức 9,5 phút, so với 9,3 phút
của `asgcn`. Con số 75,7 phút cao hơn 62,1 phút là do cả ba seed chạy đủ 8 epoch, không phải
do mô hình nặng hơn.

### 3.2 Ba điều làm con số +0,0107 yếu hơn vẻ ngoài

**Một. Dấu của hiệu số không nhất quán giữa các seed.**

| Hiệu số macro-F1, cùng seed | seed 42 | seed 1337 | seed 2024 |
|---|---|---|---|
| senticgcn − asgcn | **−0,0041** | +0,0126 | +0,0235 |
| senticgcn − asgcn_linked | −0,0008 | +0,0046 | +0,0033 |
| senticgcn − phobert | −0,0021 | −0,0026 | +0,0005 |

Ở seed 42, `asgcn` **thắng** `senticgcn`. Phần hơn trung bình đến từ hai seed mà `asgcn` chạy
kém. Vậy câu đúng không phải "tri thức cảm xúc đáng 0,0107 điểm", mà là "`senticgcn` không có
seed nào chạy kém như hai seed của `asgcn`". Độ lệch chuẩn giảm từ 0,0114 xuống 0,0028, đúng
bằng mức của `asgcn_linked`.

**Hai. Accuracy hầu như đứng yên.** Macro-F1 tăng 0,0107 mà accuracy chỉ tăng 0,0012. Hai chỉ
số tách nhau xa thế nghĩa là số câu đúng gần như không đổi, chỉ có **cách phân bổ** câu đúng
giữa các lớp thay đổi. Mục 3.3 đếm cụ thể.

**Ba. Từ điển của ta không phải SenticNet.** `data/lexicon_from_train.json` quy nạp từ nhãn
của tập train. Không rò rỉ sang test, nhưng phần hơn `asgcn`, nếu có thật, có thể đến từ
thông tin nhãn đi vòng vào trọng số cạnh chứ không phải từ tri thức cảm xúc theo nghĩa của bài
gốc. Thí nghiệm này **không tách được** hai nguồn đó. Phải nói rõ ở mục 4.3 của báo cáo.

### 3.3 `senticgcn` không nhận ra câu trung lập giỏi hơn, nó đoán trung lập nhiều hơn

Đây là phần đáng học nhất của phiếu. F1 lớp trung lập của `senticgcn` và `phobert` gần như
trùng nhau, 0,7125 và 0,7131. Nhưng hai con số đó được làm ra theo hai cách khác hẳn:

| Lớp trung lập | precision | recall | Số câu mô hình đoán là trung lập |
|---|---|---|---|
| phobert | 0,7526 ± 0,0157 | 0,6777 ± 0,0062 | 736,0 (759, 734, 715) |
| asgcn | 0,7556 ± 0,0295 | 0,6283 ± 0,0694 | 682,0 (801, 633, 612) |
| asgcn_linked | 0,7591 ± 0,0093 | 0,6573 ± 0,0177 | 707,7 (711, 679, 733) |
| **senticgcn** | **0,7026 ± 0,0314** | **0,7242 ± 0,0233** | **844,0 (907, 847, 778)** |

Tập test có 817 câu trung lập thật. Ba mô hình trước đều đoán **ít hơn** con số đó.
`senticgcn` là mô hình đầu tiên đoán **nhiều hơn**.

Đi qua bằng số đếm, trung bình 3 seed, `senticgcn` so với `phobert`:

| Nhãn thật | phobert đoán đúng | senticgcn đoán đúng | Chênh |
|---|---|---|---|
| Trung lập, 817 câu | 553,7 | 591,7 | **+38,0** |
| Tiêu cực, 2.210 câu | 2.090,3 | 2.071,7 | −18,6 |
| Tích cực, 3.695 câu | 3.530,7 | 3.483,7 | −47,0 |
| **Cộng** | 6.174,7 | 6.147,1 | **−27,6** |

Tìm thêm được 38 câu trung lập, đổi lại mất 65,6 câu ở hai lớp kia. Tính ra 27,6 câu sai thêm
trên 6.722, đúng bằng 0,0041 accuracy ở mục 3.1.

Phần mất đi đâu thì bảng nhầm lẫn nói rõ:

| Bị đoán nhầm **thành trung lập** | phobert | asgcn | asgcn_linked | senticgcn |
|---|---|---|---|---|
| Câu tiêu cực | 75,7 (3,4 %) | 60,3 | 53,3 | 93,7 (4,2 %) |
| Câu tích cực | 106,7 (2,9 %) | 108,3 | 117,3 | **158,7 (4,3 %)** |

Báo động giả tăng từ 182,4 lên 252,4, tức thêm 70 câu, để đổi lấy 38 câu trung lập đúng.

**Chỗ dễ hiểu sai nhất:** macro-F1 coi ba lớp ngang nhau, nên 38 câu ở lớp chỉ có 817 câu nặng
gần bằng 47 câu ở lớp có 3.695 câu. Vì vậy macro-F1 gần như không thấy cuộc đổi chác này, còn
accuracy thì thấy. Một mô hình nâng macro-F1 bằng cách dịch ranh giới về phía lớp thiểu số
**không** phải là một mô hình phân biệt giỏi hơn. Muốn biết thì phải nhìn precision và recall
riêng, không nhìn F1.

**Vì sao `senticgcn` dịch ranh giới về phía trung lập thì chưa biết.** `[CẦN KIỂM: so phân bố
xác suất lớp trung lập trong predictions.jsonl giữa senticgcn và asgcn, và tách theo câu có
hay không có token mang mẫu số âm]`. Chưa kiểm thì không viết cơ chế nào vào báo cáo.

### 3.4 Phần được nằm ngoài PRICE, phần mất nằm ở PRICE

F1 lớp trung lập theo từng khía cạnh, trung bình 3 seed:

| Khía cạnh | n trung lập | phobert | asgcn | asgcn_linked | senticgcn |
|---|---|---|---|---|---|
| PRICE | 328 | **0,8953 ± 0,0045** | 0,8708 ± 0,0239 | 0,8786 ± 0,0123 | 0,8754 ± 0,0032 |
| PERFORMANCE | 116 | 0,5318 ± 0,0159 | 0,5292 ± 0,0565 | 0,5595 ± 0,0059 | **0,5727 ± 0,0173** |
| BATTERY | 92 | **0,6599 ± 0,0149** | 0,6156 ± 0,0128 | 0,6281 ± 0,0310 | 0,6294 ± 0,0233 |
| GENERAL | 83 | 0,6664 ± 0,0180 | 0,6386 ± 0,0381 | 0,6362 ± 0,0375 | **0,6974 ± 0,0046** |
| CAMERA | 71 | 0,7101 ± 0,0465 | 0,6648 ± 0,0763 | 0,7247 ± 0,0423 | **0,7275 ± 0,0266** |
| FEATURES | 52 | 0,4815 ± 0,0221 | 0,4552 ± 0,1715 | 0,4980 ± 0,0704 | **0,5426 ± 0,0205** |
| DESIGN | 28 | 0,4106 ± 0,0610 | 0,3869 ± 0,0884 | 0,3462 ± 0,0739 | **0,4628 ± 0,0657** |
| SER&ACC | 27 | **0,4192 ± 0,0806** | 0,1953 ± 0,1857 | 0,2527 ± 0,1612 | 0,4020 ± 0,0786 |
| SCREEN | 17 | 0,3258 ± 0,0266 | 0,2724 ± 0,1123 | 0,4310 ± 0,1099 | **0,4395 ± 0,0684** |
| STORAGE | 3 | **0,5000** | 0,3778 | 0,4111 | 0,3778 |

`senticgcn` cao nhất ở 6 trong 10 khía cạnh, `phobert` ở 4 khía cạnh còn lại. Với n dưới 30
thì chỉ mang tính gợi ý, như phiếu trước đã dặn.

Số câu trung lập bị sai, `senticgcn` trừ `phobert`: PERFORMANCE −10,0, GENERAL −10,0, CAMERA
−6,0, FEATURES −5,3, DESIGN −3,7, SCREEN −1,7, PRICE −0,7, SER&ACC −0,7, BATTERY 0, STORAGE 0.
Cộng lại −38. **PRICE, nơi chứa 40 % câu trung lập, gần như không đóng góp gì.**

Còn phần mất thì dồn về PRICE. Ma trận nhầm lẫn của riêng khía cạnh này, trung bình 3 seed:

| PRICE, nhãn thật | phobert: tiêu cực / trung lập / tích cực | senticgcn: tiêu cực / trung lập / tích cực |
|---|---|---|
| Tiêu cực, 79 câu | 66,3 / 8,7 / 4,0 | 59,0 / **16,7** / 3,3 |
| Trung lập, 328 câu | 15,3 / 285,0 / 27,7 | 16,7 / 285,7 / 25,7 |
| Tích cực, 162 câu | 2,7 / 15,0 / 144,3 | 2,3 / **22,3** / 137,3 |

Số câu trung lập đoán đúng không đổi, 285,7 so với 285,0. Báo động giả tăng từ 23,7 lên 39,0.
F1 lớp tiêu cực của PRICE tụt từ 0,8124 xuống 0,7512, mức thấp nhất trong bốn mô hình.

Khớp với dự đoán ở mục 3.5 của phiếu trước: trần cải thiện nằm ở các khía cạnh mỏng dữ liệu,
không nằm ở PRICE.

### 3.5 Ổn định trở lại, dù đồ thị vẫn vỡ

`senticgcn` chạy với `link_roots: false`, tức **đúng tập cạnh bị chia cắt** của `asgcn`. Vậy
mà hai chỗ `asgcn` gần như đoán mò thì nay trở về mức của `phobert`:

| F1 trung lập | phobert | asgcn | senticgcn |
|---|---|---|---|
| SER&ACC, 27 câu | 0,4192 ± 0,0806 | 0,1953 ± 0,1857 | 0,4020 ± 0,0786 |
| FEATURES, 52 câu | 0,4815 ± 0,0221 | 0,4552 ± 0,1715 | 0,5426 ± 0,0205 |

Phiếu trước kết luận đồ thị vỡ là nguyên nhân lớn của mất ổn định, dựa trên việc nối gốc làm
độ lệch chuẩn giảm gần bốn lần. Nay có một mô hình **không nối gốc** mà độ lệch chuẩn cũng
giảm đúng bằng ấy, 0,0028 so với 0,0029. Kết luận cũ vì thế phải viết lại cho hẹp hơn: nối
gốc là **một** cách làm `asgcn` ổn định, không phải bằng chứng rằng đồ thị vỡ là nguyên nhân.

### 3.6 Một quan sát xuyên suốt 12 lần chạy: epoch được chọn

Xếp 12 lần chạy của bốn mô hình dùng PhoBERT theo macro-F1 trên tập test:

| Mô hình | Seed | Epoch tốt nhất trên dev | Dừng ở epoch | train_loss tại epoch đó | macro-F1 test | Số câu đoán trung lập |
|---|---|---|---|---|---|---|
| asgcn | 2024 | **3** | 6 | 0,2243 | 0,8447 | 612 |
| asgcn | 1337 | **3** | 6 | 0,2303 | 0,8514 | 633 |
| asgcn_linked | 1337 | **3** | 6 | 0,2318 | 0,8594 | 679 |
| senticgcn | 42 | 5 | 8 | 0,1386 | 0,8628 | 907 |
| asgcn_linked | 42 | 4 | 7 | 0,1720 | 0,8636 | 711 |
| senticgcn | 1337 | 8 | 8 | 0,0666 | 0,8640 | 847 |
| phobert | 42 | 4 | 7 | 0,1727 | 0,8649 | 759 |
| asgcn_linked | 2024 | 4 | 7 | 0,1696 | 0,8649 | 733 |
| phobert | 1337 | 5 | 8 | 0,1356 | 0,8665 | 734 |
| asgcn | 42 | 5 | 8 | 0,1360 | 0,8669 | 801 |
| phobert | 2024 | 4 | 7 | 0,1672 | 0,8677 | 715 |
| senticgcn | 2024 | 7 | 8 | 0,0824 | 0,8682 | 778 |

**Ba lần chạy thấp nhất là đúng ba lần mà dừng sớm giữ lại trọng số của epoch 3.** Chín lần
còn lại, thuộc cả bốn mô hình, nằm gọn trong dải 0,8628 đến 0,8682, rộng 0,0054. Ba lần đó
cũng là ba lần đoán trung lập ít nhất.

Một cách đọc khớp với cả hai cột cuối và với mục 3.3: trọng số ở epoch 3 chưa học xong lớp
thiểu số nên đoán trung lập ít, recall lớp trung lập thấp, kéo macro-F1 xuống. Nếu đúng, đó
cũng là lý do 81 % phần sụt của `asgcn` nằm ở lớp trung lập. Đây là giả thuyết, chưa kiểm.

Hệ quả cho cách đọc cả thang: phiếu CD1.6a nêu bốn cách giải thích kết quả âm của `asgcn`, và
xếp cách số 3, dừng sớm cắt quá tay, vào loại "chỉ làm nếu GVHD yêu cầu". Bảng trên là bằng
chứng mạnh nhất hiện có, và nó nghiêng về **cách số 3**. Nếu đúng thì hai câu đã viết phải
sửa: "thêm cú pháp làm kém đi" và "nối gốc lấy lại 69 %" đều có thể chỉ là "mô hình này có mấy
seed bị chọn nhầm epoch 3".

Ba điều giữ cho quan sát này đúng mực:

- Đây là quan sát **sau khi đã nhìn số liệu**, trên 12 lần chạy, không phải kiểm định. Nếu 12
  lần chạy hoán đổi được cho nhau thì xác suất ba lần thấp nhất trùng đúng ba lần chọn epoch 3
  là 1 trên 220. Nhưng chúng thuộc bốn mô hình khác nhau nên không hoán đổi được, con số đó chỉ
  để hình dung.
- Chưa biết đỉnh dev ở epoch 3 là **may rủi** hay là **tính chất của mô hình**. `asgcn` dính 2
  trong 3 seed, `asgcn_linked` 1 trong 3, `phobert` và `senticgcn` không seed nào. Nếu là tính
  chất của mô hình thì thang vẫn đọc được, chỉ đổi cơ chế: không phải "cú pháp thêm thông tin
  sai" mà là "cú pháp làm đường cong dev phẳng sớm".
- Không được lấy trung bình riêng chín lần "chọn đúng epoch" rồi báo cáo. Đó là chọn mẫu theo
  kết quả.

Seed 1337 của `senticgcn` còn cho thấy mặt kia của cùng vấn đề: epoch tốt nhất là epoch 8,
cũng là epoch cuối, dev vẫn đang lên (0,8464, 0,8481, 0,8507). Lần chạy này bị trần 8 epoch
cắt chứ không phải tự dừng.

### 3.7 Lo ngại về hội tụ không xảy ra

Phiếu trước đo được khoảng 70 % số lô có ít nhất một token mang mẫu số âm, và để ngỏ câu hỏi
chuyện đó có phá hội tụ không. Ba seed trả lời là không:

| | epoch 1, train_loss | epoch 1, dev macro-F1 | epoch 8, train_loss |
|---|---|---|---|
| senticgcn, seed 42 / 1337 / 2024 | 0,5921 / 0,5893 / 0,5813 | 0,7820 / 0,8044 / 0,7729 | 0,0686 / 0,0666 / 0,0659 |
| asgcn, seed 42 / 1337 / 2024 | 0,5754 / 0,5823 / 0,5672 | 0,7836 / 0,8097 / 0,7712 | 0,0599 / — / — |

Hai đường cong đi sát nhau từ đầu tới cuối. Không lần nào sinh NaN, dây bẫy ở ngưỡng 10⁻⁶
không kích hoạt.

### 3.8 Ý nghĩa cho CĐ2

**Một.** Mốc để NS-MGAT vượt là dải 0,863 đến 0,868 macro-F1, không phải một con số. Cả bốn
mô hình dùng PhoBERT đều rơi vào dải đó khi không bị chọn nhầm epoch 3.

**Hai.** Báo cáo macro-F1 của NS-MGAT phải kèm precision, recall và số câu đoán vào từng lớp.
Nếu không, một cú dịch ranh giới như ở mục 3.3 sẽ trông giống một tiến bộ.

**Ba.** Trong cùng một mô hình, seed bị chọn epoch 3 thấp hơn các seed còn lại từ 0,004 đến
0,022 macro-F1. Các hiệu số trung bình giữa bốn mô hình thì nằm trong khoảng 0,001 đến 0,012.
Hai cỡ này ngang nhau, nên chừng nào chưa rõ chuyện chọn epoch thì chưa đọc được hiệu số giữa
các mô hình. Nên quyết xong trước khi đo NS-MGAT.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Phiếu cho phần chạy | Phiếu riêng, cùng cách CD1.6a đã tách ba phần | Viết tiếp vào `CD1.6b_senticgcn.md` | Phiếu cũ ghi "chưa chạy huấn luyện" và đúng tại ngày viết. Sửa vào đó thì mất mốc thời gian |
| Kết luận về tri thức cảm xúc | **Không** kết luận nó có ích | Viết "tri thức cảm xúc đáng 0,0107 macro-F1" | Dấu hiệu số đổi theo seed, accuracy không tăng, và từ điển sinh từ nhãn train. Ba lý do độc lập |
| Precision và recall tính bằng gì | Tính tại chỗ từ `predictions.jsonl`, ghi công thức ở mục 6 | Thêm lệnh con vào `scripts/soi_khia_canh.py` | Số câu đoán trung lập cộng lại được từ ba lần chạy `nham` có sẵn. Thêm lệnh con là mở rộng công cụ, chưa ai yêu cầu |
| Thêm `senticgcn` vào test đối chiếu | Có, từ 9 lên 12 lần chạy | Kiểm một lần bằng tay rồi thôi | Mọi con số trong phiếu này đọc từ `predictions.jsonl` của `senticgcn`. Phiếu trước đã đặt lệ khoá bằng test |
| Kiểm định ý nghĩa thống kê | Chưa chạy | Chạy McNemar hoặc bootstrap ngay | Thuộc CD1.10, và câu hỏi thứ tư gửi GVHD về chính chuyện này chưa gửi |
| Quan sát ở mục 3.6 | Ghi là quan sát, kèm ba điều cẩn trọng | Sửa lại hai kết luận cũ ngay | Chưa có thí nghiệm tách bạch. Sửa kết luận dựa trên tương quan 12 điểm là lặp lại đúng lỗi đang chỉ ra |
| Commit khi chưa có notebook | Commit kết quả và nhật ký trước | Chờ đủ notebook | Nhật ký từng epoch đã là bằng chứng. Notebook bổ sung sau bằng một commit riêng |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Bảng ở mục 3.1 là Bảng 4.5 của cuốn chuyên đề, **đủ sáu dòng**.
- Mục 3.3 và 3.6 là nội dung mới cho phần bàn luận ở Chương 4, và mục 3.2 điều thứ ba là câu
  bắt buộc phải có ở mục 4.3.
- **Việc của học viên ngay kế tiếp:** trắc nghiệm 04, file
  `chuyende1/trac-nghiem/de/04_Sentic-GCN.md`. Đạt rồi mới tick ô "Đã đọc kỹ" trong
  `chuyende1/survey/doc_bat_buoc.md` và đổi dòng Sentic-GCN trong `survey_matrix.csv` khỏi
  `chua_kiem`.
- Step kế tiếp theo plan: **CD1.2b** khảo sát đợt 2 và nháp Chương 3, hoặc **CD1.8a** lọc ứng
  viên tập chẩn đoán.
- Bốn câu hỏi gửi GVHD vẫn chưa gửi. Kết quả âm của `asgcn` cùng `asgcn_linked` cũng chưa gửi,
  nay nên gửi kèm `senticgcn` và quan sát ở mục 3.6.
- Điều kiện tiên quyết còn thiếu: không. Notebook phiên Colab của `senticgcn` đã mất và được
  ghi nhận ở GAP-024, xem mục 6 và mục 8.

---

## 6. KIỂM CHỨNG — bằng chứng chạy thật

```
357 passed in 63.64s (0:01:03)
```

Trước step này 354, nay 357. Tăng đúng 3, là ba seed `senticgcn` thêm vào
`test_f1_khop_voi_f1_per_class_trong_metrics`.

Kiểm chín file tải từ Colab về:

| Mục kiểm | Kết quả |
|---|---|
| Vân tay seed 42 | `bb0bb11d2ede`, khớp giá trị tính lại |
| Vân tay seed 1337 | `0caf4ff9183f`, khớp |
| Vân tay seed 2024 | `9f2b79e52833`, khớp |
| `n_params` | 136.181.763 cả ba seed, bằng `asgcn` |
| Số dòng `predictions.jsonl` | 6.722 mỗi file |
| `exp_name` và `seed` trong file so với tên thư mục | `senticgcn`, khớp cả ba |
| F1 tự đếm từ `predictions.jsonl` so với `f1_per_class` | Lệch 0 ở cả ba seed, cả ba lớp |
| Bộ ba `uid`, `aspect`, `y_true` so với `phobert` seed 42 | Trùng từng dòng, cả ba seed |

**Một sai sót trong lúc kiểm, đã sửa:**
[GAP-023](../gaps/GAP-023_doan-lenh-kiem-van-tay-thieu-ten-mo-hinh.md). Lần tính lại vân tay
đầu tiên ra ba giá trị lệch, vì đoạn lệnh trong `notebooks/da-chay/QUY-UOC.md` chỉ tiêm seed
mà bỏ bước tiêm tên mô hình. Dữ liệu đúng, phép kiểm sai. Cùng bài học với GAP-022.

**Nguồn của từng nhóm số:**

| Số liệu | Tính bằng |
|---|---|
| Mục 3.1, 3.2 | `metrics.json` của 18 lần chạy, trung bình và độ lệch chuẩn mẫu |
| Bảng F1 theo khía cạnh, bảng nhầm lẫn, số câu sai | `scripts/soi_khia_canh.py`, sáu lệnh ở mục 1 |
| Số câu đoán trung lập | Cộng ba ô của ba lần chạy `nham`: đoán đúng trung lập, tiêu cực thành trung lập, tích cực thành trung lập |
| Precision, recall lớp trung lập, ma trận của riêng PRICE | Đếm tại chỗ từ `predictions.jsonl`, trên từng seed rồi lấy trung bình |
| Epoch tốt nhất, train_loss | `logs/<exp>/seed<N>.log`, epoch có dev macro-F1 cao nhất |

**Khối `diagnostic` trong cả ba file bằng 0 với `n = 0`.** Không phải lỗi, tập chẩn đoán phủ
định và tương phản chưa dựng.

**Không có và sẽ không có:** notebook phiên Colab của `senticgcn`. Học viên xác nhận ngày
05/10/2026 là đã mất, và quyết không chạy lại. Ghi ở
[GAP-024](../gaps/GAP-024_mat-notebook-phien-colab-senticgcn.md). Theo nhật ký, ba lần chạy
bắt đầu lúc 08:26, 12:45 và 19:05 ngày 03/10 theo giờ của Colab. Thiếu notebook thì không đối
chiếu được mã commit mà từng lần chạy đã kéo về; thứ thay được một phần là giữa hai commit của
kho trong ngày đó chỉ có `notebooks/colab_train.ipynb` thay đổi.

**Chưa chạy kiểm định ý nghĩa thống kê.**

---

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi cần bạn quyết:**

1. Notebook của các phiên Colab chạy `senticgcn` còn không? Nếu còn: tải bản còn nguyên output,
   đặt vào `notebooks/da-chay/senticgcn/`, tên `phien-2026-10-03.ipynb`, nhiều phiên cùng ngày
   thì thêm `-a`, `-b`. Nếu đã mất thì ghi nhận là mất, không dựng lại.
2. Quan sát ở mục 3.6 có đáng kiểm bằng thí nghiệm không? Rẻ nhất: nếu trên Drive còn
   `last.pt` của `asgcn` seed 1337 hoặc 2024, đó là trọng số epoch 6, chấm được trên tập test
   mà không cần huấn luyện lại. Đắt hơn: một biến thể chẩn đoán kiểu `asgcn_linked`, chỉ đổi
   quy tắc dừng.
3. Có gom hai dòng tiêm seed và tên mô hình trong `train.py` thành một hàm dùng chung không?
   Đây là cách sửa tận gốc của GAP-023.

**Những chỗ có thể bạn muốn hỏi thêm:**

- Vì sao F1 bằng nhau mà precision và recall lại khác nhau được?
- Dịch ranh giới về phía lớp thiểu số thì tốt hay xấu cho bài toán này?
- Viết kết quả `senticgcn` vào báo cáo thế nào khi từ điển sinh từ nhãn train?
- Mục 3.6 có làm hỏng những gì đã viết về `asgcn` và `asgcn_linked` không?

**Kết:**
> Bạn có câu hỏi phụ nào về phần này không, hay bạn làm trắc nghiệm 04 rồi ta đi tiếp sang
> **CD1.2b** hoặc **CD1.8a**?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

Học viên trả lời ngày 05/10/2026:

| Câu hỏi ở mục 7 | Trả lời của học viên | Có dẫn tới thay đổi không |
|---|---|---|
| 1. Notebook phiên Colab còn không | **Đã mất, bỏ qua.** Không chạy lại | Có. Ghi GAP-024; sửa mục 10 của `notebooks/colab_train.ipynb`, ô 10 của `SO_TAY_LENH.md` và `notebooks/da-chay/QUY-UOC.md` để lần sau không mất |
| 2. Có kiểm quan sát về epoch 3 bằng thí nghiệm không | Chưa trả lời | Không. Mục 3.6 vẫn là quan sát, hai kết luận cũ chưa sửa |
| 3. Có gom hai dòng tiêm trong `train.py` thành một hàm không | Chưa trả lời | Không. `train.py` giữ nguyên |
| Trắc nghiệm 04 | **Đạt 10/10**, đúng cả 4 câu trọng yếu | Có. Tick `doc_bat_buoc.md`; dòng Sentic-GCN trong `survey_matrix.csv` sang `da_doc_toan_van`, đọc lại toàn văn từ bản tác giả tự lưu ở sentic.net vì PDF ngày 02/10 không nằm trong kho |
