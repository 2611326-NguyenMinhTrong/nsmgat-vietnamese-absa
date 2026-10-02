# PHIẾU BÀN GIAO — [CD1.6a] Chạy `asgcn` 3 seed và đọc kết quả âm

> Phần 3, phần cuối của CD1.6a. Hai phần trước:
> [CD1.6a_gcn-layer.md](CD1.6a_gcn-layer.md) (hạ tầng) và
> [CD1.6a_asgcn-model.md](CD1.6a_asgcn-model.md) (mô hình và config).

**Ngày:** 02/10/2026 · **Step:** CD1.6a (phần 3/3) · **Ánh xạ plan gốc:** S1.2 · **Thời gian GPU thực tế:** 186 phút cho 3 seed

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `results/asgcn/seed{42,1337,2024}/metrics.json` | Tạo | Kết quả 3 lần chạy trên Colab T4 |
| `results/asgcn/seed{42,1337,2024}/predictions.jsonl` | Tạo | Dự đoán từng mẫu, 6.722 dòng mỗi seed, kèm xác suất 3 lớp |
| `logs/asgcn/seed{42,1337,2024}.log` | Tạo | Nhật ký từng epoch, nay được đưa vào kho để kiểm chứng |
| `src/nsmgat/trainer.py` | Sửa | Vá GAP-021: đưa trạng thái ngẫu nhiên về ByteTensor trên CPU trước khi khôi phục |
| `tests/test_resume.py` | Sửa | Thêm 2 test giả lập GPU cho nhánh vừa vá |
| `.gitignore` | Sửa | Mở ngoại lệ cho `logs/asgcn/*.log`, đặt ở cuối file |
| `notebooks/da-chay/` | Tạo | Chỗ giữ bản Colab đã chạy, kèm `QUY-UOC.md` cho người kiểm chứng |
| `notebooks/da-chay/asgcn/phien-2026-10-02.ipynb` | Tạo | Phiên Colab chạy tiếp seed 42 rồi chạy seed 1337 và 2024 |
| `chuyende1/gaps/GAP-021`, `GAP-022` | Tạo | Hai lỗi phát sinh trong lúc chạy, đều đã sửa |

Không đụng vào `configs/asgcn.yaml` và `src/nsmgat/models/asgcn.py` trong suốt ba lần chạy.

---

## 2. ĐỂ LÀM GÌ

Trả lời đúng một câu hỏi: **cây phụ thuộc cú pháp đáng bao nhiêu điểm trên UIT-ViSFD?**

`asgcn` khác `phobert` đúng một biến. Bằng chứng kiểm được: số tham số chênh nhau 1.181.184,
đúng bằng hai lớp GCN 768×768 cộng hai vector bias, không dư một tham số nào. Mọi thứ khác,
từ bộ mã hoá, cách khía cạnh đi vào, số epoch, learning rate, đến seed, đều giống hệt.

Vì vậy hiệu số giữa hai mô hình **là** phần đóng góp của cú pháp, không phải thứ gì khác.

---

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1 Con số

| Mô hình | accuracy | macro-F1 | Thời gian |
|---|---|---|---|
| lexicon | 0,7469 ± 0,0002 | 0,5240 ± 0,0002 | — |
| bilstm | 0,8642 ± 0,0062 | 0,7949 ± 0,0106 | — |
| phobert | 0,9186 ± 0,0011 | 0,8664 ± 0,0014 | 23,7 phút |
| **asgcn** | **0,9133 ± 0,0038** | **0,8543 ± 0,0114** | **62,1 phút** |
| **Hiệu số** | **−0,0053** | **−0,0121** | **2,6 lần chậm hơn** |

Từng seed:

| Seed | accuracy | macro-F1 | Epoch tốt nhất | Dừng ở epoch | Thời gian |
|---|---|---|---|---|---|
| 42 | 0,9173 | 0,8669 | 5 | 8 | 72,5 phút |
| 1337 | 0,9127 | 0,8514 | 3 | 6, dừng sớm | 56,4 phút |
| 2024 | 0,9098 | 0,8447 | 3 | 6, dừng sớm | 57,6 phút |

**Thêm cú pháp vào làm kết quả kém đi.** Đây là kết quả âm, và nó thật.

Hai điều nữa đáng chú ý ngang con số chính. Thứ nhất, độ lệch chuẩn giữa các seed rộng gấp
3,5 lần ở accuracy và gấp 8 lần ở macro-F1, tức mô hình còn kém ổn định hơn. Thứ hai, chi phí
tính toán gấp 2,6 lần.

### 3.2 Hiệu số nằm gần hết ở lớp trung lập

| F1 từng lớp | phobert | asgcn | Hiệu số |
|---|---|---|---|
| Tiêu cực | 0,9334 ± 0,0009 | 0,9303 ± 0,0053 | −0,0031 |
| **Trung lập** | **0,7131 ± 0,0037** | **0,6836 ± 0,0278** | **−0,0295** |
| Tích cực | 0,9527 ± 0,0009 | 0,9490 ± 0,0015 | −0,0037 |

Lớp trung lập chiếm **81 %** toàn bộ phần sụt của macro-F1. Hai lớp còn lại gần như không
đổi, chênh lệch của chúng nằm trong khoảng dao động giữa các seed.

Lớp trung lập cũng là lớp thiểu số: 817 trong 6.722 mẫu của tập test, tức 12,2 %. Và độ lệch
chuẩn của nó ở `asgcn` là 0,0278, gấp 7,5 lần `phobert`.

Đây là **một dữ kiện quan trọng hơn con số tổng**: nếu cú pháp làm hỏng đều khắp, ta sẽ nghĩ
về kiến trúc. Nhưng nó chỉ làm hỏng ở chỗ ít dữ liệu nhất và khó nhất, điều đó nghiêng về
cách giải thích "thêm nhiễu" hơn là "thêm thông tin sai".

### 3.3 Bốn cách đọc kết quả âm này

Bốn cách không loại trừ nhau. Xếp theo mức độ ảnh hưởng tới CĐ2.

**Cách 1. Cơ chế mà ASGCN dựa vào không tồn tại trong bài toán của ta.**

ASGCN gốc làm aspect-term: cụm khía cạnh là một đoạn **nằm trong câu**, và cây phụ thuộc có
việc để làm là nối cụm đó tới từ ý kiến ở xa. Hai cơ chế cốt lõi của bài, trọng số theo vị
trí (công thức 5) và masking theo khía cạnh (công thức 7), đều cần cụm khía cạnh có mặt
trong câu.

UIT-ViSFD là aspect-category: mười mã cố định, không mã nào xuất hiện trong câu. Ta đã phải
bỏ cả hai cơ chế đó (mục 4 của phiếu trước). Thứ còn lại là một GCN chạy trên cây phụ thuộc
mà **không biết nó đang được hỏi về khía cạnh nào**. Khía cạnh chỉ đi vào ở bước attention
cuối cùng, sau khi GCN đã làm xong việc.

Nói cách khác, ta đã cài đúng ASGCN, nhưng phần làm nên sức mạnh của ASGCN đã bị bài toán
tước mất từ đầu. Kết quả âm ở đây không chứng minh "cú pháp vô dụng", nó chứng minh **"cú
pháp không gắn với khía cạnh thì vô dụng"**.

Đây chính là lý do tồn tại của NS-MGAT: luận văn phải nối khía cạnh vào **đồ thị**, chứ
không chỉ vào bước attention cuối.

**Cách 2. Đồ thị bị vỡ ở hơn một nửa dữ liệu.**

Theo [GAP-007](../gaps/GAP-007_do-thi-cu-phap-bi-chia-cat.md), **52,2 %** Example của tập train
có cây phụ thuộc tách thành nhiều mảnh rời, không cạnh nào nối giữa các mảnh. Cấu hình
`link_roots: false` giữ nguyên tình trạng đó vì đó là hành vi của bài gốc.

GCN hai lớp trên một đồ thị vỡ thì với hơn một nửa dữ liệu, thông tin không đi qua được giữa
các mảnh. Phần lan truyền trên đồ thị coi như không chạy.

Cách này kiểm được trực tiếp, và đó đúng là việc của `asgcn_linked`.

**Cách 3. Quy tắc dừng sớm có thể đã cắt hai seed quá tay.**

Nhìn lại đường cong dev của hai seed dừng sớm:

| Seed | Đỉnh, ở epoch 3 | Epoch 6 | Kém đỉnh bao nhiêu |
|---|---|---|---|
| 1337 | 0,844810 | 0,843038 | 0,001772 |
| 2024 | 0,841377 | 0,841309 | **0,000068** |

Đường cong gần như **phẳng**, không đi xuống. Nhưng kiên nhẫn 3 chỉ hỏi "có vượt đỉnh không",
không hỏi "có tệ đi không", nên ba epoch đi ngang vẫn bị tính là ba lần không cải thiện. Hai
seed đó kết thúc bằng trọng số của epoch 3, trong khi seed 42 được chạy tới epoch 5 và cho
kết quả tốt nhất trong ba.

Nghĩa là một phần hiệu số có thể là **tạo tác của quy tắc dừng**, không phải của mô hình.

Cẩn trọng: chuyện này không tự động có lợi cho `asgcn`. Muốn kiểm thì phải đổi quy tắc dừng
cho **cả hai** mô hình rồi chạy lại cả sáu lần, vì đổi quy tắc là đổi vân tay cấu hình. Ghi
nhận, chưa sửa.

**Cách 4. Một triệu tham số khởi tạo ngẫu nhiên thêm nhiễu, lớp thiểu số chịu nặng nhất.**

`asgcn` thêm 1.181.184 tham số khởi tạo ngẫu nhiên, học ở learning rate 1e-3, tức gấp 50 lần
learning rate của bộ mã hoá. Lớp trung lập chỉ có 12,2 % dữ liệu nên nhạy nhất với nhiễu, và
đúng là nó gánh 81 % phần sụt, với độ lệch chuẩn gấp 7,5 lần.

Cách này không cạnh tranh với ba cách trên. Nó giải thích **vì sao hiệu số dồn vào một lớp**,
chứ không giải thích vì sao có hiệu số.

### 3.4 Cách nào kiểm bằng thí nghiệm nào

| Cách giải thích | Kiểm bằng | Đã có kế hoạch chưa |
|---|---|---|
| 2. Đồ thị vỡ | `asgcn_linked`, 3 seed, khác đúng một khoá `link_roots` | Có, chạy ngay sau |
| 1. Cú pháp không gắn khía cạnh | So với `senticgcn` ở CĐ1.6b rồi với NS-MGAT ở CĐ2 | Có, là trục chính của luận văn |
| 4. Nhiễu ở lớp thiểu số | Soi `predictions.jsonl` theo lớp và theo khía cạnh | Chưa, làm được ngay, không tốn GPU |
| 3. Dừng sớm cắt quá tay | Đổi quy tắc dừng, chạy lại cả `phobert` lẫn `asgcn` | Chưa, tốn 6 lần chạy, chỉ làm nếu GVHD yêu cầu |

Thứ tự này có chủ ý: `asgcn_linked` rẻ nhất và tách bạch nhất, nên chạy trước.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Sửa code giữa ba seed | **Không**, kể cả khi thấy chỗ chậm | Tối ưu bước gộp subword ngay | Ba seed chạy trên hai bản mã khác nhau thì không gộp được thành một trung bình |
| `save_last_every` | Giữ 1, chấp nhận mất khoảng 3,4 phút mỗi epoch để ghi 1,6 GB lên Drive | Đặt 2 cho nhanh | Nó không nằm trong vân tay nên đổi được, nhưng bị ngắt sẽ mất tới 2 epoch. Phiên Colab đã đứt một lần rồi |
| Khi Drive đầy | Xoá `last.pt` của những lần chạy **đã có `metrics.json`** | Xoá hết `*.pt`, hoặc đặt `save_last: false` | Điều kiện đã có `metrics.json` là bằng chứng lần chạy kết thúc. Không có điều kiện đó thì có ngày xoá nhầm lần đang chạy |
| Giữ `best.pt` của `asgcn` | Có, tới khi xong cả 3 seed | Xoá luôn cho nhẹ | `predictions.jsonl` đủ để tính lại mọi chỉ số, nhưng còn một bước soi lỗi chưa làm |
| Nhật ký vào kho | Mở ngoại lệ riêng cho `logs/asgcn/*.log` | Giữ nguyên `/logs/` chặn hết | Nhật ký từng epoch là bằng chứng mạnh hơn cả notebook. Ba file cộng lại 20 KB |
| Chỗ đặt ngoại lệ | Cuối `.gitignore` | Cạnh dòng `/logs/` | Dòng `*.log` của mục LaTeX nằm sau sẽ chặn lại. Trong `.gitignore`, quy tắc sau thắng quy tắc trước. Đã kiểm bằng `git check-ignore -v` |
| Báo GVHD kết quả âm | Có, nhưng cùng với `asgcn_linked` | Báo ngay | Một kết quả âm kèm một thí nghiệm giải thích nó thì thuyết phục hơn một kết quả âm đứng trơ |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- **Ngay kế tiếp:** `asgcn_linked`, 3 seed, bắt buộc `--exp-name asgcn_linked`, nếu không sẽ
  ghi đè lên `results/asgcn/`. Vân tay mong đợi tính theo từng seed từ `configs/asgcn_linked.yaml`.
- Hiệu số `asgcn` với `asgcn_linked` trả lời trực tiếp cách giải thích số 2.
- Sau đó CĐ1.6b `senticgcn`, dùng lại `GCNLayer`, `edges_to_adj`, bước gộp subword và bước
  attention, chỉ khác phần trọng số cạnh.
- Ba con số của `asgcn` là một cột trong Bảng 4.5 của cuốn chuyên đề, và mục 3.3 của phiếu
  này là bản nháp có sẵn cho phần bàn luận.
- Kiểm định ý nghĩa thống kê **chưa chạy**. Với 3 seed thì kiểm định t ghép cặp có lực rất
  thấp, cần nói rõ điều đó trong báo cáo thay vì đưa một trị số p trông như bằng chứng.

---

## 6. KIỂM CHỨNG — bằng chứng chạy thật

```
312 passed in 67.05s
```

Trước step này 310 test, nay 312, thêm đúng 2 test của GAP-021.

Kiểm tính toàn vẹn của 9 file tải từ Colab về:

| Mục kiểm | Kết quả |
|---|---|
| Vân tay seed 42 | `d2d2aebdc30f`, khớp giá trị tính lại |
| Vân tay seed 1337 | `e90c6f78af62`, khớp |
| Vân tay seed 2024 | `d666cd85a10c`, khớp |
| Số dòng `predictions.jsonl` | 6.722 mỗi file, bằng cỡ tập test |
| `seed` trong file so với tên thư mục | Khớp cả ba |
| `n_params` | 136.181.763 cả ba seed, hơn `phobert` đúng 1.181.184 |

**Hai lỗi phát sinh trong lúc chạy, đều đã sửa:**

[GAP-021](../gaps/GAP-021_map-location-day-trang-thai-ngau-nhien-len-gpu.md) — `torch.load`
với `map_location="cuda"` đẩy cả trạng thái sinh số ngẫu nhiên lên GPU, làm cơ chế chạy tiếp
ném `TypeError`. Dòng ngay trên đã phòng đúng chuyện này cho trạng thái CPU rồi bỏ sót chỗ
anh em cách hai dòng. Test không bắt được vì máy học viên không có GPU.

[GAP-022](../gaps/GAP-022_tieu-chi-kiem-van-tay-bo-quen-seed.md) — tiêu chí kiểm do Claude đưa
ra bỏ quên việc `train.py` ghi số seed vào cấu hình trước khi bấm vân tay, nên suýt loại hai
lần chạy đúng. Bài học: khi một phép kiểm báo sai, nghi ngờ phép kiểm trước khi nghi ngờ dữ liệu.

**Khối `diagnostic` trong cả ba file đều bằng 0 với `n = 0`.** Không phải lỗi: `phobert` cả
ba seed cũng vậy. Tập chẩn đoán phủ định và tương phản chưa dựng, đó là việc của CĐ1.11.

**Bằng chứng cho người ngoài kiểm chứng:** `notebooks/da-chay/asgcn/phien-2026-10-02.ipynb`
giữ nguyên output của phiên Colab, trong đó đọc được cả lần chạy seed 42 thất bại, lần chạy
tiếp thành công, rồi seed 1337 và seed 2024. Kèm ba file nhật ký trong `logs/asgcn/`.

---

## 7. DỪNG LẠI VÀ HỎI

**Những chỗ có thể bạn muốn hỏi thêm:**

- Kết quả âm thì viết vào báo cáo thế nào cho đúng mực, không biện hộ mà cũng không tự hạ?
- Có nên chạy thêm seed thứ tư thứ năm để thu hẹp khoảng dao động không?
- Cách giải thích số 3 về dừng sớm có đáng bỏ 6 lần chạy để kiểm không?
- `asgcn_linked` mà cũng thua `phobert` thì kết luận là gì?

**Ba câu hỏi gửi GVHD vẫn chưa gửi**, nay thêm một câu thứ tư: chuyên đề có cần kiểm định ý
nghĩa thống kê giữa các baseline không, hay nêu trung bình kèm độ lệch chuẩn là đủ.

**Kết:**
> Bạn muốn chạy `asgcn_linked` ngay, hay dừng lại soi `predictions.jsonl` theo khía cạnh
> trước để hiểu rõ hơn lớp trung lập hỏng ở đâu?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
