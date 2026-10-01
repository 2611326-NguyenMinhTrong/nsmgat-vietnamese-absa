# PHIẾU BÀN GIAO — [CD1.6a] GCNLayer và ma trận kề

> Phiếu này phủ **phần hạ tầng** của CD1.6a: lớp `GCNLayer` dùng chung và hàm đổi danh sách
> cạnh thành ma trận kề. Phần còn lại của step (mô hình `ASGCNModel`, hai file config, chạy
> 3 seed) đang chờ học viên đọc bài ASGCN, sẽ có phiếu riêng.

**Ngày:** 23/09/2026 (GCNLayer) và 30/09/2026 (ma trận kề) · **Step:** CD1.6a (phần hạ tầng) · **Ánh xạ plan gốc:** S1.2 · **Thời gian thực tế:** ~1,5 giờ

---

## 1. ĐÃ LÀM GÌ — danh sách thay đổi

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `src/nsmgat/models/layers.py` | Sửa (từ khung rỗng 5 dòng) | Cài `GCNLayer`: nhận `(x, adj)` trả về `x'`, có chuẩn hoá đối xứng, nhận thêm `edge_weight` và `mask` tuỳ chọn |
| `tests/test_layers.py` | Tạo | 17 test cho lớp trên: công thức chuẩn hoá, bậc 0, gradient, mask, kiểm tra đầu vào sai |
| `src/nsmgat/graphs/adjacency.py` | Tạo | `edges_to_adj` và `edges_to_adj_batch`: đổi `List[TypedEdge]` thành ma trận kề dày, có lọc theo view, lấy trọng số theo `conf`, đệm và sinh mask |
| `tests/test_adjacency.py` | Tạo | 13 test: chiều cạnh, self-loop, lọc view, cạnh trùng, đệm, gộp batch, `link_roots`, ráp thẳng vào `GCNLayer` |

Ba lớp còn lại của `layers.py` (`EdgeAwareAttention`, `MultiGraphEncoder`, `CrossGraphFusion`)
vẫn chưa cài, đúng quy tắc số 6 của README: không viết logic của step chưa tới.

```bash
.venv/Scripts/python.exe -m pytest tests/ -q
```

---

## 2. ĐỂ LÀM GÌ — vấn đề mà phần này giải quyết

- **Vấn đề:** ba mô hình còn lại của thang bậc (`asgcn`, `senticgcn`, NS-MGAT) đều là mạng
  trên đồ thị, nhưng repo chưa có một phép toán đồ thị nào. `models/layers.py` mới là khung rỗng.
- **Sau step này:** đã có phép gộp tin từ hàng xóm theo ma trận kề, dùng được cho cả ba mô
  hình đó mà không phải sửa lại lớp.
- **Nếu bỏ step này thì hỏng ở đâu:** CD1.6a và CD1.6b không có gì để chạy. Xa hơn, cặp so
  sánh `asgcn` với `senticgcn` là thứ cô lập đúng phần "tri thức cảm xúc" trong báo cáo, và
  cặp `senticgcn` với NS-MGAT cô lập đóng góp của Chuyên đề 2. Mất lớp này là mất cả hai cặp.

---

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

**Ý tưởng cốt lõi.** Mỗi token lấy trung bình có trọng số biểu diễn của chính nó và của các
token nối với nó trong cây cú pháp, rồi nhân qua một ma trận trọng số học được. Lặp lại lớp
này hai lần thì mỗi token nhìn được hàng xóm của hàng xóm, tức xa hai bước trên cây.

**Ví dụ chạy xuyên suốt.** Câu "pin rất trâu", cây phụ thuộc: `pin` và `rất` cùng trỏ về
`trâu`, `trâu` là gốc. Cho `SyntacticGraphBuilder` dựng cạnh rồi đổ vào ma trận kề:

```
adj = [[1, 0, 1],      bậc = [2, 2, 3]
       [0, 1, 1],
       [1, 1, 1]]
```

Hàng 0 đọc là: `pin` nhận tin từ chính nó và từ `trâu`. `pin` và `rất` không nối nhau vì
trong cây chúng là anh em, không phải cha con.

Giả sử mỗi token là một số: `pin = 1`, `rất = 3`, `trâu = 5`, và ma trận trọng số bằng 1
để nhìn thẳng vào phép gộp. Chuẩn hoá đối xứng chia mỗi cạnh cho căn của tích hai bậc:

```
out[pin]  = 1/sqrt(2*2) * 1 + 1/sqrt(2*3) * 5 = 0,5000 + 2,0412 = 2,5412
out[rất]  = 1/sqrt(2*2) * 3 + 1/sqrt(2*3) * 5 = 1,5000 + 2,0412 = 3,5412
out[trâu] = 1/sqrt(3*2) * 1 + 1/sqrt(3*2) * 3 + 1/3 * 5 = 0,4082 + 1,2247 + 1,6667 = 3,2997
```

Số này lấy từ lần chạy thật, không tính nhẩm. Đổi sang `normalize="row"` thì ra
`[3,0 · 4,0 · 3,0]`, đúng bằng trung bình cộng thường của mỗi đỉnh với hàng xóm.

**Chỗ dễ hiểu sai nhất.** Hai chỗ.

Thứ nhất, chiều của cạnh trong ma trận kề. Quy ước ở đây là `adj[i][j] > 0` nghĩa là có
cạnh **j chảy sang i**, tức hàng i là danh sách những ai gửi tin cho token i. Viết ngược
lại thì phép nhân `adj @ x` vẫn chạy, không báo lỗi, chỉ ra kết quả sai âm thầm.

Thứ hai, self-loop. Bộ dựng đồ thị đã tự thêm self-loop cho mọi token, nên lớp này cố ý
không thêm nữa. Nếu sau này ai đó truyền vào một đồ thị không có self-loop thì token đó chỉ
nhận tin từ hàng xóm và đánh mất chính mình.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ — và phương án đã loại

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Ma trận kề dày hay thưa | Dày, `(B, N, N)` | Thưa kiểu `edge_index` | Câu trong UIT-ViSFD ngắn, ma trận dày đơn giản và đủ nhanh; `edge_index` chỉ đáng khi đồ thị lớn |
| Tự thêm self-loop | Không | Có, hoặc để cờ `add_self_loops` | Bộ dựng đồ thị đã thêm rồi, thêm nữa là đếm hai lần. Không để cờ vì một mặc định sai sớm muộn cũng có người bật nhầm |
| Hàm kích hoạt | Để bên ngoài gọi | Nhét ReLU vào trong lớp | Lớp cuối của một chồng GCN thường không kích hoạt, và Stage 4 cần chèn chuẩn hoá giữa các lớp |
| Vị trí cộng bias | Sau khi gộp | Dùng luôn bias của `nn.Linear`, tức cộng trước | Cộng trước làm bias bị nhân theo bậc của đỉnh, thành hàm của cấu trúc đồ thị chứ không còn là hằng số |
| Cách chuẩn hoá | Có ba chế độ, mặc định đối xứng | Chỉ đối xứng | ASGCN gốc dùng chia theo bậc đỉnh nhận, để sẵn `row` thì CD1.6a tái lập được bài gốc mà không phải sửa lớp |
| Xử lý bậc 0 | Kẹp bậc trước khi nghịch đảo | Lọc sau bằng `torch.where` | `torch.where` vẫn cho gradient đi qua nhánh không được chọn, nên vô cùng ở đó sẽ thành NaN khi `edge_weight` học được ở Stage 4 |
| Token đệm | Tham số `mask` tuỳ chọn | Mặc kệ, coi như vô hại | Có bias thì vị trí đệm ra giá trị khác 0, rồi rò vào bước gộp theo khía cạnh ở mô hình |
| Chỗ đặt hàm dựng ma trận kề | Module mới `graphs/adjacency.py` | Viết vào `graphs/base.py` hoặc `graphs/builder.py` | `base.py` đã đóng băng từ S0.2; `builder.py` là chỗ của S3.3, viết vào đó là lấn sang step chưa tới lượt |
| Cạnh trùng cặp (i, j) | Lấy max | Cộng dồn | Cộng dồn làm bậc của đỉnh phồng lên, kéo theo lệch cả phép chuẩn hoà. Xảy ra thật khi gộp nhiều view ở Stage 4 |
| Trọng số cạnh | Có chế độ `conf` lấy từ `TypedEdge.conf` | Chỉ nhị phân, ai cần trọng số thì tự nhân ngoài | Sentic-GCN và Stage 4 đều cần, để sẵn thì không phải sửa lại hàm. Mặc định vẫn nhị phân cho `asgcn` |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Step kế tiếp là: **CD1.6a phần 2 — `ASGCNModel` + `configs/asgcn.yaml` + `configs/asgcn_linked.yaml`**
- Nó sẽ dùng lại: `GCNLayer` xếp chồng hai lớp, giữa hai lớp gọi ReLU ở phía mô hình.
- Giao diện: `GCNLayer(in_dim, out_dim, dropout=…, bias=…, normalize=…)` và
  `forward(x, adj, edge_weight=None, mask=None) -> (B, N, out_dim)`.
- Điều kiện tiên quyết ~~còn thiếu~~ **đã xong 30/09/2026**: `graphs/adjacency.py` cung cấp
  `edges_to_adj_batch(edges_per_sample, n_tokens_per_sample) -> (adj, mask)`, đưa thẳng được
  vào `GCNLayer(x, adj, mask=mask)`. `collate_fn` trong `data/dataset.py` vẫn trả `edge_index`
  rỗng — đó là phần của S3.3, không đụng tới.
- Điều kiện tiên quyết **còn thiếu thật sự**: học viên đọc bài ASGCN. Chưa trả lời được câu
  "neo khía cạnh vào đâu khi khía cạnh không xuất hiện trong câu" thì chưa cài được bước gộp
  theo khía cạnh của mô hình.

---

## 6. KIỂM CHỨNG — bằng chứng chạy thật

```
.venv/Scripts/python.exe -m pytest tests/ -q
........................................................................ [ 27%]
........................................................................ [ 54%]
........................................................................ [ 81%]
.................................................                        [100%]
265 passed in 43.46s
```

Sau khi thêm `graphs/adjacency.py` (30/09/2026):

```
278 passed in 70.74s (0:01:10)
```

Trước step này là 248 test, nay 278: 17 test của `tests/test_layers.py` và 13 test của
`tests/test_adjacency.py`.

Số liệu của ví dụ ở mục 3 lấy từ một lần chạy thật `SyntacticGraphBuilder` cộng `GCNLayer`,
không tính nhẩm.

**Sự cố gặp phải:** test về dropout hỏng ở lần chạy đầu. Nguyên nhân: đặt dropout 0,9 trên
vector chỉ 4 chiều nên cả hai lần chạy đều bị xoá sạch về 0, thành ra hai kết quả bằng nhau
và test tưởng là dropout không hoạt động. Sửa bằng cách dùng vector 32 chiều với dropout 0,5,
và ghi luôn lý do vào ngay trong test để lần sau không ai hạ số chiều xuống nữa.

---

## 7. DỪNG LẠI VÀ HỎI

**Câu hỏi mở gửi học viên:**

1. `asgcn` nên dùng chuẩn hoá nào? Đối xứng là cách chuẩn của Kipf và Welling, còn chia theo
   bậc đỉnh nhận mới đúng bài ASGCN gốc. Tôi nghiêng về chia theo bậc để tái lập trung thành,
   rồi nếu muốn thì so thêm một lần với đối xứng ở CD1.11. Bạn quyết.

**Những chỗ có thể bạn muốn hỏi thêm:**

- Vì sao hai lớp GCN chứ không phải ba hay bốn?
- Chuẩn hoá đối xứng khác chia theo bậc ở chỗ nào, và khác đó ảnh hưởng gì tới token gốc câu?
- Mô hình sẽ gộp biểu diễn theo khía cạnh ra sao khi khía cạnh không xuất hiện trong câu?

**Kết:**
> Bạn có câu hỏi phụ nào về phần này không, hay tôi đi tiếp sang phần 2 của CD1.6a, tức
> `ASGCNModel` và hai file config?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| Chọn cách chuẩn hoá nào cho `asgcn` | Học viên chốt 23/09/2026: **chia theo bậc đỉnh nhận** để tái lập trung thành ASGCN gốc; so với chuẩn hoá đối xứng để dành làm thăm dò P4 ở CD1.11, chỉ chạy nếu còn thời gian | Không. `GCNLayer` đã có sẵn `normalize="row"`; chỉ cần đặt trong hai file config ở phần 2 |
| Có bài báo nào cần đọc trước không | Có: `ASGCN` (Zhang, Li & Song, EMNLP-IJCNLP 2019), đang là 🔴 chưa đọc trong `doc_bat_buoc.md` và chính bảng đó ghi "đọc trước CD1.6a" | Không, nhưng **chặn phần 2**: câu hỏi neo khía cạnh với aspect-category chưa có lời giải thì chưa cài được bước gộp theo khía cạnh |
