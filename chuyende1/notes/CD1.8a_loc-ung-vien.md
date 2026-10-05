# PHIẾU BÀN GIAO — [CD1.8a] Lọc ứng viên cho tập chẩn đoán

> Bước đầu của chuỗi dựng tập chẩn đoán: CD1.8a lọc ứng viên, CD1.8b viết hướng dẫn chú thích,
> CD1.8c chú thích tay, CD1.8d đo độ đồng thuận và chốt. Phiếu này là bước thứ nhất.

**Ngày:** 05/10/2026 · **Step:** CD1.8a · **Ánh xạ plan gốc:** S6.1 · **Không dùng GPU** · Trễ một tuần so với lịch

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `scripts/build_diagnostic_candidates.py` | Sửa | Trước là chỗ giữ tên 5 dòng, nay là công cụ lọc ứng viên |
| `tests/test_diagnostic_candidates.py` | Tạo | 26 test, trong đó 3 test chạy trên tập test thật |
| `data/diagnostic/candidates.csv` | Tạo | 800 Example ứng viên, ba cột cuối để trống cho bạn điền |
| `SO_TAY_LENH.md` | Sửa | Thêm mục 11c, gỡ tên script khỏi danh sách "chưa chạy được" |
| `chuyende1/MODULE.md` | Sửa | Thêm một dòng vào bảng công cụ ở mục 2.2 |

Lệnh đã chạy:

```bash
python scripts/build_diagnostic_candidates.py --chi-thong-ke
python scripts/build_diagnostic_candidates.py
python scripts/build_diagnostic_candidates.py --chi-thong-ke --so-doi-chung 300 --do-dai 5 30
python scripts/build_diagnostic_candidates.py --chi-thong-ke --khong-lay-ngoai-do-dai
```

---

## 2. ĐỂ LÀM GÌ

- **Vấn đề:** tập test có 6.722 Example. Chú thích tay hết là không thể, mà chọn bừa 300 thì
  phần lớn sẽ là câu khen chê thông thường, không có phủ định hay chuyển ý để mà chẩn đoán.
- **Sau step này:** có một danh sách 800 Example đã cô đặc hai hiện tượng cần đo, kèm một
  nhóm đối chứng, cân bằng ba nhãn. Bạn chỉ còn việc ngồi đọc và điền.
- **Nếu bỏ step này:** CD1.8c không có gì để chú thích, CD1.9 không có trục "theo hiện tượng",
  và mọi hạn chế ở Chương 5 mất con số đi kèm.

---

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1 Đơn vị là Example, không phải câu

Theo một câu thật của tập test, mã `visfd-test-01805`, 21 token:

> mới xài 3 ngày thấy tạm ổn..màn hình đẹp chơi game mượt..pin 4500 **nhưng** nhanh hết quá.

Câu này có bốn Example, mỗi khía cạnh một nhãn:

| Khía cạnh | Nhãn gốc | Có vào file ứng viên không |
|---|---|---|
| SCREEN | positive | không |
| BATTERY | negative | **có** |
| PERFORMANCE | positive | không |
| GENERAL | neutral | **có** |

Chữ "nhưng" tác động lên BATTERY: pin 4500 đáng lẽ phải trâu, nhưng lại nhanh hết. Nó không
dính gì tới SCREEN. Nếu gán "chuyển ý" cho cả câu thì bốn Example cùng mang một nhãn hiện
tượng, trong đó ba cái sai. Vì vậy mỗi dòng của file là một cặp câu và khía cạnh, và cột
`phenomenon` bạn điền là cho **đúng khía cạnh ở dòng đó**.

Hệ quả: 800 dòng của file đến từ 604 câu. 446 câu góp một dòng, 125 câu góp hai, 28 câu góp
ba, 5 câu góp bốn. File sắp theo nhóm rồi theo mã câu, nên các dòng cùng câu nằm liền nhau.

### 3.2 Câu đó đi qua bộ lọc thế nào

**Bước 1, khớp từ khoá theo token.** Bộ tách từ đã cắt câu thành 21 token. Công cụ so từng
token, viết thường, với ba tập từ khoá. Chỉ `nhưng` khớp, thuộc tập chuyển ý.

Khớp theo **nguyên token** chứ không theo chuỗi con là có chủ ý. Câu `visfd-test-01586` có
đoạn "sóng yếu không tưởng luôn". Bộ tách từ gộp thành một token `không_tưởng`, và token đó
không nằm trong tập phủ định, nên câu không bị coi là có phủ định. Tìm chuỗi "không" trong văn
bản thô thì sẽ dính.

**Bước 2, xếp nhóm cho câu.**

| Câu chứa | Nhóm |
|---|---|
| Từ phủ định và từ chuyển ý | `ca_hai` |
| Chỉ từ phủ định | `phu_dinh` |
| Chỉ từ chuyển ý | `chuyen_y` |
| Không từ nào trong cả ba tập | `doi_chung` |
| Chỉ từ thuộc tập "ngờ" | **bị loại**, không vào nhóm nào |

Câu ví dụ vào `chuyen_y`. Cả bốn Example của nó vào kho của nhóm này.

**Bước 3, chia chỉ tiêu cho ba nhãn.** Nhóm `chuyen_y` có chỉ tiêu 200. Kho của nó:

| | negative | neutral | positive |
|---|---|---|---|
| Trong khoảng 5–40 token | 122 | 62 | 233 |
| Ngoài khoảng | 35 | 33 | 107 |

Chia đều thì mỗi nhãn 67, 67, 66. Lớp neutral chỉ có 62 câu trong khoảng, thiếu 5.

**Bước 4, hai yêu cầu của đặc tả va nhau.** Đặc tả đòi cân bằng nhãn, và đòi ưu tiên câu ngắn
vừa. Ở đây không thoả được cả hai. Công cụ chọn **cân bằng nhãn thắng**: lấy thêm 5 câu
neutral ngoài khoảng, câu lệch ít nhất trước. Câu dài nhất được lấy có 42 token. Cả file chỉ
có 5 dòng như vậy.

**Bước 5, rút ngẫu nhiên có hạt giống.** Trong 122 Example negative của nhóm, rút 67. Example
BATTERY của câu ví dụ trúng. Hạt giống mặc định 42; chạy lại ra đúng file cũ từng byte.

### 3.3 Ba bậc từ khoá, và vì sao cần bậc "ngờ"

Số **câu** của tập test chứa từng từ, trên tổng 2.187 câu:

| Bậc | Từ khoá và số câu |
|---|---|
| Phủ định, chắc | không 529, ko 381, k 255, chưa 208, chẳng 18, chả 17, không_thể 13, kg 13, kh 12, không_thể_nào 4, khong 4, hok 4, éo 3, kô 1, không_nổi 1 |
| Chuyển ý, chắc | nhưng 410, dù 51, mặc_dù 38, có_điều 36, trừ 28, tuy_nhiên 22, tuy 16, mỗi_tội 16, nhưng_mà 11, được_cái 9, vậy_mà 6, ngoại_trừ 4, nhưg 2, cơ_mà 2, và năm từ chỉ có 1 câu |
| Ngờ | mà 411, còn 292, chứ 53, đâu 49, khỏi 47, tiếc 36, đừng 27, riêng 19, hông 6, nhung 3, dù_sao 2, chẳng_lẽ 1 |

Từ "mà" có mặt ở 411 câu. Khi thì nó chuyển ý: "pin 4500 mà hao quá nhanh". Khi thì không:
"nghĩ mà chán". Có hai cách xử lý sai:

- Coi "mà" là từ khoá chắc: nhóm chuyển ý ngập ca sai, bạn tốn giờ đọc những câu vô ích.
- Bỏ hẳn "mà": câu "pin 4500 mà hao quá nhanh" rơi vào nhóm đối chứng, và nhóm đối chứng,
  thứ lẽ ra phải sạch hiện tượng, lại lẫn câu chuyển ý.

Bậc "ngờ" là lối thứ ba: câu chỉ chứa từ ngờ bị cho ra khỏi **cả hai phía**. 192 câu bị loại
theo cách này. Ví dụ `visfd-test-00275` có "cảm biến vân tay bên hông": chữ `hông` ở đây là
cạnh máy, nhưng ở câu khác "hông có chơi game" nó là "không". Cùng mặt chữ, không phân biệt
được bằng từ khoá, nên loại.

### 3.4 Phát hiện đáng giá nhất của step: phủ định viết tắt

Trong 2.187 câu test, **1.223 câu có từ phủ định, tức 56 %**. Chia theo dạng viết:

| Câu chứa | Số câu |
|---|---|
| Chỉ dạng chuẩn: không, chưa, chẳng, chả | 560 |
| **Chỉ dạng viết tắt: ko, k, kh, kg, hok** | **500** |
| Cả hai dạng | 163 |

Và đây là từ loại mà bộ tách từ gán cho chúng, đếm trên cả tập test:

| Từ | Số lần | Được gán là phó từ (R) | Được gán nhầm thành |
|---|---|---|---|
| không | 727 | 727 | — |
| chưa | 230 | 230 | — |
| **ko** | 570 | **0** | động từ 327, danh từ 217, còn lại 26 |
| **k** | 384 | **0** | danh từ 229, động từ 139, còn lại 16 |

`không` được gán đúng 727 trên 727 lần. `ko` và `k` cộng lại 954 lần, **không lần nào** được
nhận ra là phó từ phủ định.

Ba hệ quả, mỗi cái chạm một phần khác của luận văn:

1. **Bộ luật của Chuyên đề 2.** Luật phủ định mà dựa vào từ loại, kiểu "phó từ phủ định đứng
   trước tính từ", sẽ bỏ sót 500 trong 1.223 câu, tức 41 %. Phải khớp theo mặt chữ hoặc chuẩn
   hoá văn bản trước.
2. **Đồ thị cú pháp.** `ko` bị gán là động từ thì cây phụ thuộc quanh nó cũng sai theo. Đây có
   thể là một nguồn nhiễu của `asgcn` mà GAP-007 chưa tính tới. Chưa đo.
3. **Từ điển cảm xúc.** `data/lexicon_from_train.json` học điểm theo token, nên ba cách viết
   là ba mục riêng: `không` −0,1702, `ko` −0,1975, `k` −0,2489. Cùng dấu, nhưng lệch nhau tới
   0,08 dù là một từ. Với `senticgcn`, cạnh nối tới `k` vì thế nặng hơn cạnh nối tới `không`
   mà không có lý do ngôn ngữ nào.

Chữ `k` có một chỗ phải cẩn thận. Tôi đọc 24 ngữ cảnh ngẫu nhiên: khoảng 19 là phủ định, 4 là
tiểu từ hỏi kiểu "máy có bị gì k ạ", 1 là đơn vị tiền "100 k". Đây là ước lượng bằng mắt trên
24 mẫu, không phải phép đo. Nó đủ để giữ `k` ở bậc chắc, và cũng là lý do cột `phenomenon`
phải do người quyết.

### 3.5 File đầu ra trông thế nào

| Cột | Ai điền | Nội dung |
|---|---|---|
| `uid` | công cụ | Mã Example, khoá để ghép lại với tập test |
| `text` | công cụ | Câu gốc, đã gộp xuống dòng thành dấu cách cho dễ đọc |
| `aspect` | công cụ | Khía cạnh của dòng này |
| `nhan_goc` | công cụ | Nhãn của UIT-ViSFD: negative, neutral, positive |
| `nhom_ung_vien` | công cụ | Nhóm theo từ khoá. **Không phải** nhãn hiện tượng |
| `tu_khoa_kich_hoat` | công cụ | Từ khoá chắc đã khớp, ví dụ `ko; nhưng` |
| `so_token` | công cụ | Độ dài câu |
| `phenomenon` | **bạn** | Hiện tượng thật, cho đúng khía cạnh ở dòng này |
| `nhan_kiem_tra` | **bạn** | Nhãn cảm xúc bạn cho là đúng, nếu nghi nhãn gốc sai |
| `ghi_chu` | **bạn** | Tự do |

Kết quả chọn, cân bằng trong từng nhóm:

| Nhóm | Chỉ tiêu | negative | neutral | positive | Số câu | Ngoài khoảng |
|---|---|---|---|---|---|---|
| phu_dinh | 250 | 84 | 83 | 83 | 203 | 0 |
| chuyen_y | 200 | 67 | 67 | 66 | 120 | 5 |
| ca_hai | 150 | 50 | 50 | 50 | 106 | 0 |
| doi_chung | 200 | 67 | 67 | 66 | 175 | 0 |
| **Tổng** | **800** | **268** | **267** | **265** | **604** | **5** |

### 3.6 Chỗ dễ hiểu sai nhất, và một điều chưa giải quyết

**`nhom_ung_vien` không phải nhãn.** Nó chỉ nói câu chứa từ khoá gì. Câu "Có ai bị như mình k"
nằm trong nhóm `phu_dinh` vì có `k`, nhưng đó là câu hỏi. Ngược lại một Example trong nhóm
`doi_chung` vẫn có thể mang phủ định bằng một từ ngoài danh sách. Nhãn thật là cột bạn điền.

**Lớp neutral của file nghiêng hẳn về PRICE.** Trong 267 Example neutral, 110 cái thuộc khía
cạnh PRICE, tức 41 %. Công cụ không làm ra điều này: nó phản ánh đúng tập test, nơi 40 % câu
trung lập thuộc PRICE. Nhưng hệ quả với tập chẩn đoán thì phải nghĩ: phần lớn Example PRICE
neutral trong câu có phủ định là câu kiểu "pin ko trâu ... giá 5 triệu", phủ định chẳng dính
gì tới giá. Chúng sẽ được chú thích là không có hiện tượng. Nhóm phủ định sau khi chú thích vì
thế nhiều khả năng **thiếu Example neutral thật sự**. Đặc tả chỉ đòi cân bằng nhãn nên tôi
không tự thêm trần theo khía cạnh. Đây là câu hỏi số 1 ở mục 7.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Lọc bằng gì | **Từ khoá** | Luật được kích hoạt, như đặc tả gốc S6.1 | Bộ luật thuộc S2.2 của Chuyên đề 2, chưa tồn tại. `PLAN_CHUYENDE1.md` đã đổi sang từ khoá. Cột `luật_kích_hoạt` thành `tu_khoa_kich_hoat` |
| Danh sách từ khoá để ở đâu | Trong chính script | `src/nsmgat/rules/` | Thư mục đó thuộc Chuyên đề 2, `MODULE.md` mục 2.3 cấm động vào |
| Đơn vị ứng viên | Example | Câu | Hiện tượng gắn với khía cạnh, xem mục 3.1. Schema của tập chẩn đoán cũng là schema Example |
| Khớp từ khoá | Theo nguyên token, viết thường | Tìm chuỗi con trong văn bản thô | `không_tưởng`, `không_khí`, `mượt_mà` sẽ khớp nhầm |
| Dựa vào từ loại không | **Không** | Chỉ lấy token mang nhãn phó từ | 954 lần `ko` và `k` không lần nào được gán là phó từ, mục 3.4 |
| Từ đa nghĩa | Bậc "ngờ", loại câu khỏi mọi nhóm | Đưa vào bậc chắc, hoặc bỏ qua | Cách thứ nhất làm bẩn nhóm hiện tượng, cách thứ hai làm bẩn nhóm đối chứng |
| Số nhóm | Bốn, tách riêng `ca_hai` | Ba nhóm như bảng `diagnostic` của `metrics.json` | Nhóm là theo từ khoá, chưa phải nhãn. Gộp `ca_hai` vào đâu là việc của hướng dẫn chú thích ở CD1.8b, không quyết ở đây |
| Chỉ tiêu | 250, 200, 150, 200 | 300, 300, 200 theo đúng tỉ lệ của đặc tả gốc | Kho `chuyen_y` chỉ có 417 Example trong khoảng độ dài, lấy 300 thì gần cạn lớp negative. 150 dòng `ca_hai` bù lại vì chúng chứa cả hai loại từ khoá |
| Cân bằng nhãn va với ưu tiên câu ngắn | Cân bằng thắng | Chấp nhận lệch nhãn | Đặc tả viết "cân bằng" như yêu cầu, viết "ưu tiên" cho độ dài. Có cờ `--khong-lay-ngoai-do-dai` cho ai muốn ngược lại: khi đó neutral của `chuyen_y` còn 62 |
| Trần theo khía cạnh | **Không đặt** | Giới hạn số Example PRICE | Đặc tả không yêu cầu. Chờ bạn quyết, mục 7 |
| Chạy lại khi file đã điền dở | **Dừng**, không đổi gì | Ghi đè, hoặc luôn sao lưu rồi ghi đè | File này là 20 đến 25 giờ làm tay. Đúng mẫu hỏng của GAP-017. Chỉ `--ghi-de` mới qua, và khi đó tự sao lưu |
| Tên file sao lưu | `candidates.<ngày-giờ>.csv.bak` | `candidates.csv.bak` | Tên cố định thì lần ghi đè thứ hai xoá mất bản sao của lần thứ nhất. Đuôi `.csv.bak` khớp quy tắc có sẵn trong `.gitignore` |
| Nhãn trong file | `negative`, `neutral`, `positive` | 0, 1, 2 | Người đọc không phải nhớ bảng mã. Có test canh khớp `schema.LABEL_NAMES` |
| Kiểm chống rò rỉ đặt ở đâu | Ở hàm đọc file, kiểm cả `split` lẫn tiền tố `uid` | Một test chạy sau | Đặt ở cửa vào thì không thể quên. Hai dấu hiệu độc lập, trật một là dừng |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Step kế tiếp là: **CD1.8b, viết hướng dẫn chú thích**, file `docs/annotation_guideline.md`.
  Theo lịch đây là việc của tuần 6, tức tuần này.
- Nó dùng lại từ step này: `data/diagnostic/candidates.csv` làm nguồn ví dụ thật. Hướng dẫn
  cần 10 câu mẫu đã gán nhãn và các ca khó; lấy thẳng từ 800 dòng này thì ví dụ nào cũng là
  câu bạn sẽ gặp lại khi chú thích.
- Giao diện giữa hai step: mười cột ở mục 3.5. CD1.8d sẽ đọc lại file theo **tên cột**, và
  ghép với tập test theo `uid`.
- Ba việc CD1.8b phải quyết, tôi cố ý không quyết ở đây:
  1. Tập giá trị của cột `phenomenon`. Plan gốc có bốn nhãn kể cả `both`; plan Chuyên đề 1 và
     `metrics.json` chỉ có ba.
  2. Phủ định không tác động tới khía cạnh đang xét thì gán gì.
  3. Chú thích bằng công cụ nào. CSV mở thẳng bằng Excel trên máy tiếng Việt sẽ dính cột.
- Điều kiện tiên quyết còn thiếu cho CD1.8d: người gán nhãn thứ hai. Câu hỏi số 4 gửi GVHD
  vẫn chưa gửi.
- Mục 3.4 là nguyên liệu cho Chương 5 và cho thiết kế bộ luật của Chuyên đề 2.

---

## 6. KIỂM CHỨNG — bằng chứng chạy thật

```
383 passed in 62.19s (0:01:02)
```

Trước step này 357, nay 383. Tăng đúng 26, là số test của `tests/test_diagnostic_candidates.py`.

| Điều được khoá | Test |
|---|---|
| Dòng của tập train bị chặn ở cửa vào | `test_dong_cua_tap_TRAIN_bi_chan_o_cua_vao` |
| `uid` và `split` là hai dấu hiệu độc lập | `test_uid_va_split_la_HAI_dau_hieu_doc_lap` |
| `không_khí`, `không_tưởng` không bị coi là phủ định | `test_khop_theo_TOKEN_khong_theo_chuoi_con` |
| Câu chỉ có từ ngờ không lọt vào nhóm đối chứng | `test_cau_chi_co_tu_NGO_bi_loai_chu_KHONG_vao_doi_chung` |
| Ba tập từ khoá không giao nhau | `test_ba_tap_tu_khoa_khong_giao_nhau` |
| Cân bằng nhãn thắng ưu tiên câu ngắn, lấy câu lệch ít nhất | `test_CAN_BANG_NHAN_thang_uu_tien_cau_ngan` |
| Cùng hạt giống ra cùng kết quả, không phụ thuộc thứ tự đầu vào | `test_cung_seed_thi_ra_dung_cung_ket_qua` |
| File đã chú thích thì từ chối, và không đổi một byte | `test_DA_CHU_THICH_thi_tu_choi_ghi_de_va_KHONG_dong_vao_file` |
| Trên dữ liệu thật: đủ 800 dòng, không dòng nào ngoài test, không trùng `uid` | `test_tren_tap_test_that_ra_du_800_va_khong_dong_nao_ngoai_test` |
| Nhóm đối chứng thật sự không chứa từ khoá nào, đối chiếu lại với token gốc | `test_nhom_doi_chung_that_su_khong_co_tu_khoa_nao` |
| File trong kho sinh lại được từ mã nguồn hiện tại | `test_file_ung_vien_trong_kho_khop_voi_lan_sinh_lai` |

Kiểm thêm bằng tay, ngoài test:

- Không câu nào của tập test trùng nguyên văn với một câu của train hay dev: 0 trên 2.187.
- Đọc 6 dòng ngẫu nhiên mỗi nhóm. Thấy đúng một ca từ khoá khớp nhầm: "Có ai bị như mình k".
- Hai lệnh ví dụ trong sổ tay đã chạy thật.

**Nguồn của từng nhóm số:**

| Số liệu | Tính bằng |
|---|---|
| Bảng từ khoá, bảng kho, bảng kết quả chọn, 1.223 câu có phủ định và ba dạng của nó | `python scripts/build_diagnostic_candidates.py --chi-thong-ke` |
| 604 câu, phân bố số dòng mỗi câu, 110 trên 267 Example neutral thuộc PRICE | Đếm tại chỗ từ `data/diagnostic/candidates.csv` |
| Bảng từ loại của `không`, `chưa`, `ko`, `k` | Đếm tại chỗ từ trường `pos` của `visfd_test.jsonl`, mỗi câu đếm một lần |
| Điểm của `không`, `ko`, `k` trong từ điển | Đọc thẳng từ `data/lexicon_from_train.json` |
| Ước lượng 19 trên 24 cho chữ `k` | Đọc bằng mắt 24 ngữ cảnh ngẫu nhiên, **không phải phép đo** |

**Một con số trong tài liệu cũ cần đọc cho đúng.** Sổ tiến độ ghi tập test có 2.224 câu. Số
câu có ít nhất một Example là 2.187. 37 câu còn lại không sinh ra Example nào. Hai con số đều
đúng, chỉ khác thứ được đếm.

**Chưa làm:** chưa đo tỉ lệ từ khoá khớp đúng hiện tượng trên một mẫu đủ lớn. Con số đó sẽ tự
có sau CD1.8c, khi cột `phenomenon` được điền, và chính là số liệu của thăm dò P2 ở CD1.11.

---

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi cần bạn quyết:**

1. **Lớp neutral nghiêng về PRICE**, 110 trên 267. Giữ nguyên như dữ liệu thật, hay đặt trần
   cho PRICE để neutral trải sang khía cạnh khác? Quyết trước khi bắt đầu chú thích, vì đổi
   sau là đổi file.
2. Chỉ tiêu 250, 200, 150, 200 có ổn không? Mục tiêu là sau khi chú thích còn đủ 100 Example
   cho mỗi hiện tượng. Tỉ lệ từ khoá trúng hiện tượng thì chưa ai biết, nên 800 là ước lượng.
3. `candidates.csv` có đưa lên GitHub không? Nó chứa 800 câu của UIT-ViSFD. Thư mục
   `data/diagnostic/` hiện không bị `.gitignore` chặn, còn `data/processed/` thì bị.

**Những chỗ có thể bạn muốn hỏi thêm:**

- Vì sao không lấy hết Example của một câu đã chọn, cho đỡ phải đọc lại câu?
- Một Example trong nhóm `ca_hai` thì sau này tính vào nhóm phủ định hay chuyển ý?
- 41 % câu phủ định chỉ dùng dạng viết tắt, vậy PhoBERT có hiểu `ko` là `không` không?
- Nhóm đối chứng lấy 200, sao không lấy luôn 100 cho đủ dùng?

**Còn treo từ các step trước:** phương án A hay B cho GAP-026; có kiểm quan sát về epoch 3
không; có gom hai dòng tiêm trong `train.py` không; bốn câu hỏi gửi GVHD.

**Kết:**
> Bạn có câu hỏi phụ nào về phần này không, hay tôi đi tiếp sang **CD1.8b, viết hướng dẫn chú
> thích**?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
