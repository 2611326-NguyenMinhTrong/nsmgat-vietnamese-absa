# PHIẾU BÀN GIAO — [CD1.6b] Sentic-GCN

> Bậc cuối của thang baseline trong CĐ1. Hai bậc trước:
> [CD1.6a_chay-3-seed.md](CD1.6a_chay-3-seed.md) và
> [CD1.6a_asgcn-linked-va-soi-khia-canh.md](CD1.6a_asgcn-linked-va-soi-khia-canh.md).
>
> Phiếu này là phần mã và cấu hình. Kết quả 3 seed nằm ở phiếu kế:
> [CD1.6b_chay-3-seed.md](CD1.6b_chay-3-seed.md).

**Ngày:** 03/10/2026 · **Step:** CD1.6b · **Ánh xạ plan gốc:** S1.3 · **Chưa chạy huấn luyện**

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `src/nsmgat/models/senticgcn.py` | Tạo | `SenticGCNModel` kế thừa `ASGCNModel`, ghi đè đúng hai hàm |
| `configs/senticgcn.yaml` | Tạo | Kế thừa `asgcn.yaml`, thêm đúng một khoá `lexicon_path` |
| `src/nsmgat/models/layers.py` | Sửa | Dây bẫy ở `row_plus1`, và sửa dòng chú thích vốn sai |
| `src/nsmgat/train.py` | Sửa | Đăng ký `senticgcn` vào registry |
| `tests/test_senticgcn.py` | Tạo | 12 test |
| `tests/test_layers.py` | Sửa | Thêm 4 test cho dây bẫy và cho mẫu số âm |
| `chuyende1/trac-nghiem/{de,dap-an,bai-lam}/04_Sentic-GCN.*` | Tạo | Đề 10 câu cho bài 🔴 vừa đọc được |
| `chuyende1/survey/doc_bat_buoc.md` | Sửa | Gỡ hộp cảnh báo chặn trả phí, ghi trạng thái mới |
| `SO_TAY_LENH.md` | Sửa | Lệnh chạy `senticgcn`, bảng vân tay theo từng seed |

---

## 2. ĐỂ LÀM GÌ

Bậc cuối của thang. `asgcn` đã đo xong phần cú pháp, và câu trả lời là âm: cú pháp thuần làm
kém đi 0,0121 macro-F1, nối gốc lấy lại được 69 % phần đó nhưng vẫn chưa bằng `phobert`.

`senticgcn` trả lời câu kế tiếp: **tri thức cảm xúc đáng bao nhiêu điểm?**

Bảng 4 của bài gốc đo được rằng bỏ SenticNet hại hơn bỏ cây phụ thuộc, trên cả bốn tập dữ
liệu của họ. Nếu điều đó còn đúng trên tiếng Việt thì đây là bậc đáng kỳ vọng nhất.

---

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1 Khác `asgcn` đúng một thứ: giá trị trong ô ma trận kề

Công thức (1) đến (4) và Thuật toán 1 của bài:

```
D_ij = 1 nếu w_i, w_j có quan hệ phụ thuộc, HOẶC i = j
S_ij = SenticNet(w_i) + SenticNet(w_j)
T_ij = 1 nếu w_i hoặc w_j là từ khía cạnh
A_ij = D_ij × (S_ij + T_ij + 1)
```

Mọi thứ khác giữ nguyên của `asgcn`: cùng bộ mã hoá PhoBERT, cùng `pair_mode`, cùng bước gộp
subword, cùng truy vấn attention, cùng 2 lớp GCN, cùng siêu tham số, cùng tập cạnh.

`SenticGCNModel` vì vậy kế thừa `ASGCNModel` và ghi đè **đúng hai hàm**: `_xay_chi_so` lấy
thêm điểm từng token, `_ma_tran_ke` nhân trọng số vào. Thừa số `D_ij` được giữ bằng cách lấy
ma trận nhị phân của lớp cha rồi nhân, nên mọi bước kiểm uid và cắt câu quá dài đi chung một
đường với `asgcn`, không có cách nào lệch.

### 3.2 Thừa số +1 là thứ làm cho thang baseline sạch

Đây là chi tiết đẹp nhất của công thức (4). Từ không có trong từ điển nhận điểm 0, nhưng số
hạng +1 làm nền nên cạnh vẫn mang trọng số `1 × (0 + 0 + 1) = 1`.

Hệ quả: **từ điển rỗng thì `A = D`, tức đúng ma trận kề nhị phân của `asgcn`.** `senticgcn`
là mở rộng ngặt của `asgcn`. Đây là tính chất được khoá bằng
`test_tu_dien_RONG_thi_giong_HET_asgcn`, test quan trọng nhất của step này.

### 3.3 Mã nguồn chính chủ lệch bài báo ở ba chỗ

Bản cài đặt này theo **bài báo**, không theo mã. Trước khi học viên tìm được toàn văn ngày
02/10, Claude Code đã đọc `github.com/BinLiang-NLP/Sentic-GCN` và suýt dựng sai theo mã.

| | Mã nguồn | Bài báo |
|---|---|---|
| Điểm của cạnh | Lấy của **một** token | **Tổng** điểm hai đầu cạnh, công thức (2) |
| Từ không có trong từ điển | Trọng số **0**, token rời khỏi đồ thị | Trọng số **1** nhờ số hạng +1 |
| Bonus khía cạnh | `sentic += 1` cộng dồn trong vòng lặp con, phụ thuộc thứ tự duyệt | `T_ij` độc lập với thứ tự |

Chỗ thứ hai nguy hiểm nhất: với từ điển tiếng Việt phủ 83 %, hiểu theo mã sẽ **cắt nhầm 17 %
token khỏi đồ thị mà không có gì báo lỗi**.

### 3.4 Mẫu số có thể âm, và ta chạy y hệt bài gốc

Công thức (7) chuẩn hoá `Ã_i = A_i/(E_i + 1)` với `E_i = Σ_j A_ij`.

Ở `asgcn`, `E_i` là **số hàng xóm**, nên mẫu số luôn ≥ 2. Ở `senticgcn`, `E_i` là **tổng có
dấu** của điểm cảm xúc vùng lân cận, nên mẫu số âm được, và khi âm thì cả hàng đổi dấu.

Đo thật trên UIT-ViSFD:

| | train | dev | test |
|---|---|---|---|
| Token có mẫu số ≤ 0 | 735 (0,079 %) | 86 | 251 |
| Example dính ít nhất một token như vậy | 884 (**3,70 %**) | 3,23 % | 3,93 % |
| \|mẫu số\| nhỏ nhất | 1,1 × 10⁻³ | 7,0 × 10⁻³ | 1,1 × 10⁻³ |
| Khuếch đại lớn nhất | 909 lần | 143 lần | 909 lần |
| Token có \|mẫu số\| < 10⁻³ | **0** | 0 | 0 |

Hai điều đọc ra. Thứ nhất, **không sinh NaN**: chia cho số âm hay số nhỏ đều ra số hữu hạn,
và không ca nào đủ gần 0. Thứ hai, 3,70 % Example nghĩa là với lô 32 mẫu thì khoảng **70 %
số lô** có ít nhất một token bị đổi dấu hoặc khuếch đại.

Học viên chốt 03/10/2026: **chạy y hệt bài gốc.** Đổi dấu là điều công thức quy định khi vùng
lân cận rất tiêu cực, không phải lỗi cài đặt. Sửa đi là sửa phương pháp.

Ba ca xấu nhất của ba tập là `Thất_vọng`, `tệ`, `nhảy`. Mất ổn định rơi đúng vào những từ mang
nhiều tín hiệu cảm xúc nhất. Đây đáng thành **một quan sát trong báo cáo**, giống phát hiện về
`link_roots`: một bộ chuẩn hoá thiết kế để **đếm** đem dùng cho **tổng có dấu** thì mất nghĩa.
Bài không bàn, dù với SenticNet tiếng Anh cũng xảy ra, vì Bảng 1 có `Bad −0,800` và
`Balefully −0,810`, cộng lại đã vượt −1.

### 3.5 Từ điển của ta khác bản chất với SenticNet

SenticNet là tri thức thường thức **bên ngoài**, không biết gì về bộ dữ liệu.
`data/lexicon_from_train.json` thì được quy nạp **từ nhãn của tập train** ở CĐ1.4a.

Không rò rỉ sang test nên hợp lệ về kỹ thuật. Nhưng về diễn giải thì khác hẳn: nếu `senticgcn`
thắng `asgcn`, một phần có thể đến từ thông tin nhãn của train đi vòng vào trọng số cạnh, chứ
không phải từ "tri thức cảm xúc" theo nghĩa của bài. **Phải nói rõ ở mục 4.3 của báo cáo.**

Độ phủ đo được: 83,3 % token tập train, 81,4 % tập test, không Example nào rỗng. Hình 3 của bài
cho thấy trên 60 % thì điểm số tăng đều, nên 83 % nằm trong vùng tốt theo chính đồ thị của tác
giả. [GAP-002](../gaps/GAP-002_senticgcn-can-tu-dien-cam-xuc.md) mở từ 27/08 nhờ vậy mà khép lại
được phần rủi ro "từ điển quá thưa nên tri thức cảm xúc bị vô hiệu hoá".

### 3.6 Hai chỗ lệch khỏi bài gốc, y hệt `asgcn`

`T_ij` **luôn bằng 0**, vì UIT-ViSFD là aspect-category và mười mã khía cạnh không bao giờ xuất
hiện trong câu. Masking theo khía cạnh ở công thức (9) và (10) cũng bỏ, truy vấn attention lấy
từ biểu diễn vế khía cạnh của cặp câu.

Khác lần trước ở một điểm: nay ta **trích được con số của chính tác giả** cho chỗ lệch thứ nhất.
Bảng 4 dòng `w/o a`: bỏ T làm Rest14 tụt từ 84,03 xuống 82,92, Lap14 từ 77,90 xuống 76,35, tức
**1,1 đến 1,8 điểm**. Viết vào Chương 4 được bằng số thay vì nói chung chung.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Theo bài báo hay theo mã nguồn | **Bài báo** | Mã nguồn trên GitHub | Bài là bản công bố và là thứ hội đồng đối chiếu. Mã lệch ba chỗ, trong đó một chỗ sẽ cắt nhầm 17 % token |
| Mẫu số âm | **Giữ nguyên**, không kẹp | Kẹp về dương, hoặc dịch thang điểm sang [0, 1] | Cả hai đều đổi công thức của bài. Đo được là không sinh NaN nên không có lý do kỹ thuật nào buộc phải đổi |
| Dây bẫy ở `row_plus1` | **Có**, ngưỡng 10⁻⁶ | Không thêm gì | Không bao giờ kích hoạt trên dữ liệu này nên không đổi một chữ số nào, nhưng nếu đổi từ điển mà trúng số 0 thì nhận thông báo thay vì bảng kết quả toàn NaN |
| Chỗ đặt phần tính trọng số | Trong **mô hình** | `graphs/affective.py` | File đó thuộc S3.2, chưa tới lượt (quy tắc 6). Cùng cách `ASGCNModel` đã làm với đồ thị cú pháp |
| Từ điển | Dùng lại `lexicon_from_train.json` của CĐ1.4a | Dựng từ điển mới, hoặc tìm VietSentiWordNet | `build_affective_lexicon.py` thuộc S3.2. Từ điển cũ đã có, phủ 83 %, và đã dùng cho baseline `lexicon` |
| `link_roots` | **false**, giữ bài gốc | true, vì đã biết nối gốc giúp | Đổi một mình `senticgcn` sang true thì hiệu số `asgcn → senticgcn` lẫn hai biến. Học viên chốt 02/10/2026 |
| Lấy điểm token từ đâu | Tách ngược từ **khoá câu** | Đọc lại ba file dữ liệu lần nữa | Khoá câu đã chứa đúng bộ token mà chỉ mục cạnh đang dùng, nên không thể lệch nhau, và không tốn thêm một lượt đọc 34.000 bản ghi |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- **Ngay kế tiếp:** chạy 3 seed trên Colab. Lệnh và vân tay ở mục 6.
- Hiệu số `asgcn → senticgcn` là dòng cuối của Bảng 4.5, và là luận cứ cho câu "cú pháp một
  mình chưa đủ" ở Chương 5.
- CĐ2 NS-MGAT: `senticgcn` là mốc gần nhất. Hiệu số `NS-MGAT − senticgcn` chính là phép đo
  đóng góp của luận văn, nên con số này phải sạch.
- Đề trắc nghiệm 04 đã sẵn sàng, ô "Đã đọc kỹ" của `Sentic-GCN` còn trống.
- Dòng `Sentic-GCN` trong `survey_matrix.csv` vẫn `chua_kiem`, cập nhật sau khi đạt bài.

---

## 6. KIỂM CHỨNG — bằng chứng chạy thật

```
354 passed in 78.19s
```

Trước step này 333, nay 354. Tăng 21, gồm 4 test dây bẫy, 12 test `senticgcn`, và 5 ca bộ chấm
trắc nghiệm sinh thêm do có đề 04.

**Duyệt toàn bộ tập train ở máy bằng encoder tí hon**, đúng quy tắc rút ra từ GAP-020:

```
khoi tao: 4.2s, 10,941 cau trong chi muc
so Example: 23,872 | so batch: 746
da duyet 23,872 Example trong 43s | batch loi: 0 | batch co NaN: 0
```

Không lô nào lỗi, không lô nào sinh NaN, dây bẫy không kích hoạt lần nào. Khớp với con số đo
được ở mục 3.4.

**Config khác `asgcn` đúng một khoá:**

```
{'model.lexicon_path': (None, 'data/lexicon_from_train.json')}
```

**Vân tay theo từng seed**, dùng để đối chiếu khi tải kết quả về:

| seed 42 | seed 1337 | seed 2024 |
|---|---|---|
| `bb0bb11d2ede` | `0caf4ff9183f` | `9f2b79e52833` |

**Lệnh chạy:**

```
python -m nsmgat.train --config configs/senticgcn.yaml --model senticgcn --seed 42
```

Không cần `--exp-name`, vì tên thí nghiệm mặc định lấy theo `--model`.

**Chưa chạy huấn luyện.** Không con số nào về chất lượng mô hình trong phiếu này là kết quả
thực nghiệm.

---

## 7. DỪNG LẠI VÀ HỎI

**Những chỗ có thể bạn muốn hỏi thêm:**

- Vì sao lấy ma trận nhị phân của lớp cha rồi nhân, thay vì tự dựng lại từ đầu?
- 70 % số lô có token đổi dấu, chuyện đó có làm huấn luyện khó hội tụ không?
- Nếu `senticgcn` thắng `asgcn` thì làm sao tách được phần do tri thức cảm xúc với phần do
  thông tin nhãn của train đi vòng vào trọng số cạnh?
- Có nên chạy thêm biến thể dùng từ điển ngoài để trả lời câu trên không?

**Kết:**
> Bạn làm trắc nghiệm 04 trước, hay chạy 3 seed trên Colab trước rồi làm đề trong lúc chờ?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
