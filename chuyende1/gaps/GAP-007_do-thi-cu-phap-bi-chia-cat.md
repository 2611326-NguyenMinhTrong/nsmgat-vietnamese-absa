# GAP-007 — Hơn một nửa đồ thị cú pháp bị chia cắt thành nhiều thành phần

**Ngày phát hiện:** 02/09/2026 · **Phát hiện bởi:** Claude Code (khi làm CD1.3)
**Loại:** phương pháp · **Mức độ:** **nghiêm trọng** (ảnh hưởng trực tiếp 2 baseline) · **Trạng thái:** 🔴 Mở — cần học viên quyết

---

## 1. Phát hiện gì

Đo trên toàn bộ UIT-ViSFD bằng `scripts/diagnose_syntactic_graph.py`:

| Split | Example | Root/Example | Thành phần liên thông | **Bị chia cắt** |
|---|---|---|---|---|
| train | 23.872 | 2,37 | 2,37 (tối đa 32) | **12.450 (52,2 %)** |
| dev | 3.316 | 2,45 | 2,45 (tối đa 16) | **1.802 (54,3 %)** |
| test | 6.722 | 2,51 | 2,51 (tối đa 16) | **3.726 (55,4 %)** |

Hơn **một nửa** số Example có đồ thị cú pháp **không liên thông** — tách thành 2 đến 32 mảnh
rời nhau, không có cạnh nào nối giữa các mảnh.

Không có bất thường dữ liệu nào khác: 0 head ngoài phạm vi, 0 token tự trỏ vào mình.

## 2. Vì sao đây là vấn đề nghiêm trọng

GCN lan truyền thông tin **theo cạnh**. Nếu token khía cạnh nằm ở mảnh A còn từ cảm xúc
quyết định nhãn nằm ở mảnh B, thì **thêm bao nhiêu lớp GCN cũng không nối được chúng** —
thông tin không có đường đi.

Điều này đánh thẳng vào tiền đề của cả hai baseline đồ thị đã được GVHD duyệt:

| Baseline | Tiền đề | Bị đe doạ thế nào |
|---|---|---|
| `asgcn` | Cú pháp rút ngắn khoảng cách khía cạnh ↔ từ cảm xúc | Với 52 % dữ liệu, khoảng cách đó là **vô hạn** (không có đường đi) |
| `senticgcn` | Như trên, cộng tri thức cảm xúc | Như trên |
| NS-MGAT (CĐ2) | Đồ thị luật gắn lên nền đồ thị cú pháp | Nền bị chia cắt thì cạnh luật cũng khó phát huy |

Nó cũng liên quan trực tiếp tới **thăm dò P3 của CD1.11** ("cú pháp rút ngắn khoảng cách từ
phủ định đến từ cảm xúc bao nhiêu"). Nếu 52 % ca không có đường đi, P3 phải xử lý riêng
nhóm này thay vì tính trung bình chung — nếu không con số sẽ vô nghĩa.


## 2b. Mức độ thiệt hại THẬT — nhẹ hơn con số 52 % gợi ra

*(đo bổ sung 02/09/2026 khi viết tài liệu giải thích cho học viên — REQ-007)*

Con số 52,2 % chỉ nói "đồ thị có vỡ không", chưa nói "vỡ có phá hỏng thứ ta cần không".
Ba chỉ số sát với đề tài hơn:

| Chỉ số | Con số | Diễn giải |
|---|---|---|
| Token bị cắt khỏi mệnh đề chính | **24,5 %** | Phần lớn nội dung vẫn cùng một khối |
| Câu có phủ định bị tách khỏi từ cảm xúc | **46,8 %** (4.926/10.518) | **Nhưng nhiều ca việc tách là ĐÚNG** — phủ định thuộc câu khác, không liên quan khía cạnh đang xét |
| **Câu chuyển ý bị đứt hai vế** | **12,5 %** (1.100/8.787) | **Nhẹ** — hiện tượng cốt lõi của luận văn phần lớn còn nguyên |

**Điều chỉnh kết luận:** chưa thể biết việc chia cắt gây hại hay có lợi — có lập luận cho cả
hai chiều. Với ACSA trên bình luận nhiều câu, mỗi câu thường nói về một khía cạnh khác nhau,
nên tách theo ranh giới câu **đôi khi là điều đúng nên làm**.

Điều này **không đổi khuyến nghị** (vẫn là phương án C), nhưng đổi **lý do**: không phải
"chia cắt gây hại nên phải sửa", mà là *"chưa biết hại hay lợi, nên phải đo"*.

Giải thích đầy đủ: `chuyende1/user-require/GiaiThich_DoThiCuPhap_va_GAP-007.md`

## 3. Nguyên nhân gốc — KHÔNG phải lỗi

Đã truy tới cùng: **đây là hành vi đúng của bộ phân tích, không phải bug.**

UIT-ViSFD gọi là "câu" nhưng thực chất là **bình luận nhiều câu**. VnCoreNLP tách câu trước
khi phân tích cú pháp, nên mỗi câu con có root riêng; bước S0.3 nối các câu con thành **một**
danh sách token → thành rừng.

Bằng chứng: token đứng ngay trước một root, thống kê trên 3.000 Example đầu:

```
'.'    1466      <- dấu chấm câu, tức ranh giới câu
'!'     269
'rất'   255
'Mới'   227
```

Ví dụ thật (`visfd-train-...`), 3 root ứng với đúng 3 câu:

> "Mình mới xài được 7 tháng xuống 7% pin**.** Chả hiểu máy mới kiểu gì nữa**.** Dùng cơ bản
> lướt web cơ bản game ko chơi"

Root ở token 2 (`xài`), 10 (`Chả`), 18 (`Dùng`) — hai cái sau đều đứng ngay sau dấu chấm.

## 4. Đã làm gì

`SyntacticGraphBuilder` **cài đúng đặc tả S3.1**, không tự ý nối các mảnh lại. Lý do: nối
mảnh là một **can thiệp làm thay đổi kết quả thí nghiệm**, không nằm trong đặc tả, và không
phải quyết định của tôi. Thay vào đó tôi biến vấn đề thành con số đo được để học viên quyết
trên bằng chứng.

## 5. Ba phương án — cần học viên chọn

| | Phương án | Nội dung | Được gì | Mất gì |
|---|---|---|---|---|
| **A** | **Giữ nguyên (mặc định hiện tại)** | Đồ thị đúng như parser trả về | Trung thực với phương pháp gốc của ASGCN/Sentic-GCN; so sánh được với công bố quốc tế | 52 % dữ liệu có đồ thị chia cắt → hai baseline đồ thị có thể yếu đi vì lý do ngoài phương pháp |
| **B** | **Nối các root với nhau** | Thêm cạnh giữa root của các câu con liền kề, `etype="DEP:root_link"` | Đồ thị luôn liên thông; thông tin chảy được giữa các câu | Lệch khỏi ASGCN gốc → phải nói rõ trong báo cáo; cạnh này không có cơ sở ngôn ngữ học |
| **C** | **Chạy cả A và B** | Thêm một biến thể `asgcn_linked` | **Đo được chính xác** việc chia cắt gây thiệt hại bao nhiêu điểm — một kết quả có giá trị riêng | Thêm ~1 ngày GPU |
| ~~**D**~~ | ~~**Ép parser đọc cả bình luận một lần**~~ | Bỏ dấu chấm câu → parser coi cả bình luận là một câu | Đồ thị liền mạch hoàn toàn, không cần cạnh nhân tạo | ❌ **ĐÃ LOẠI** — làm đổi head của **24,8 %** token, sinh ra cạnh SAI nguỵ trang thành cú pháp thật (`nhiệt_tình --nmod--> lỗi`). Xem mục 5b |

**Tôi nghiêng về C**, và không phải vì "làm cho chắc". Lý do: hiệu số giữa A và B **chính là
một phát hiện của Chuyên đề 1** — nó trả lời được câu *"cú pháp có thật sự giúp không, hay
chỉ giúp khi đồ thị liền mạch?"*. Đó là đúng loại hạn chế định lượng mà nhiệm vụ 4 của đề bài
yêu cầu, và nó rẻ vì `asgcn_linked` dùng chung toàn bộ hạ tầng với `asgcn`.

Nếu chọn A hoặc B thì vẫn **bắt buộc** báo cáo con số 52 % trong mục 4.1 và mục 6.2.


## 5b. Phương án D đã thử và loại — ép parser đọc cả bình luận một lần

*(học viên đề xuất 02/09/2026; đã kiểm chứng thực nghiệm, không suy đoán)*

**Làm được không: CÓ.** `py_vncorenlp` không có tuỳ chọn tắt tách câu, nhưng bỏ dấu chấm câu
thì bộ tách câu hết ranh giới để cắt → 1 câu, 1 root, đồ thị liền mạch hoàn toàn.

**Nên làm không: KHÔNG.** Đo bằng `scripts/probe_force_single_parse.py` trên 150 bình luận
nhiều câu:

```
Token so sánh được : 2.743
Giữ nguyên head    : 2.063  (75,2 %)
>> BỊ ĐỔI head     :   680  (24,8 %)
```

Ép parse một lần **viết lại một phần tư cấu trúc**. Phần bị đổi gần như chắc chắn xấu đi:
bản parse từng câu là parser chạy **đúng miền dữ liệu nó được huấn luyện**, bản ép một câu
là chạy **ngoài miền đó**.

Cạnh sai điển hình quan sát được: `Nv --nmod--> lỗi` và `nhiệt_tình --nmod--> lỗi` — câu
*"Nv nhiệt tình"* (tích cực, khía cạnh SER&ACC) bị gắn thẳng vào *"lỗi"* (tiêu cực, câu
khác). GCN sẽ lan cảm xúc tiêu cực vào đúng chỗ tích cực.

**Điểm phân biệt cốt lõi giữa các phương án:**

| | Cạnh **thiếu** | Cạnh **sai** |
|---|---|---|
| A — giữ nguyên | Có | **Không** |
| B — nối root | Không | Có, nhưng **đánh dấu rõ** là `DEP:root_link` |
| D — ép parse | Không | **Có, và nguỵ trang thành cú pháp thật** |

Với GCN, **cạnh sai nguy hiểm hơn cạnh thiếu**: cạnh thiếu làm thông tin không tới nơi, cạnh
sai làm thông tin **chảy nhầm chỗ**.

**Còn "tách theo mỗi bình luận chứ không tách câu"?** Dữ liệu đã làm sẵn — mỗi `Example`
tương ứng một bình luận. Giới hạn nằm ở **bộ phân tích cú pháp chỉ biết làm việc ở mức câu**,
không phải ở đơn vị dữ liệu. Muốn có cấu trúc đúng ở mức nhiều câu phải dùng **phân tích diễn
ngôn** (discourse parsing) — tiếng Việt chưa có công cụ đủ tốt. Đây là một khoảng trống đáng
nêu ở mục 6.3 (hướng phát triển).

**Giá trị của việc đã thử:** con số 24,8 % chứng minh giữ nguyên ranh giới câu là đúng, và
biến câu hỏi *"sao không cho parser đọc cả bình luận?"* thành một đoạn có bằng chứng trong
mục 4.3 của báo cáo.

## 6. Bài học

**Đo chất lượng đầu vào của một phương pháp TRƯỚC khi chạy phương pháp đó.** Nếu để đến lúc
`senticgcn` cho kết quả thấp mới đi tìm nguyên nhân, sẽ không phân biệt được "phương pháp
không hợp" với "dữ liệu đầu vào kém" — đúng rủi ro **R3** mà plan đã cảnh báo. Việc chẩn
đoán tốn 1 giờ và loại trừ vĩnh viễn một cách giải thích cạnh tranh.

## 7. Có cần đưa vào báo cáo không

- [x] **Có — bắt buộc**, ở ba chỗ:
  - **mục 4.1** (mô tả dữ liệu): nêu con số 52,2 / 54,3 / 55,4 % và giải thích nguyên nhân
  - **mục 4.3** (mô tả mô hình): nói rõ đã chọn phương án nào và vì sao
  - **mục 6.2** (hạn chế): đây là hạn chế của dữ liệu, không phải của phương pháp
