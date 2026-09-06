# PHIẾU BÀN GIAO — [CD1.3b] Phương án C cho GAP-007: tham số `link_roots`

**Ngày:** 06/09/2026 · **Step:** CD1.3b (bổ sung cho CD1.3) · **Thời gian:** ~1 giờ

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `src/nsmgat/graphs/syntactic.py` | Sửa | Thêm tham số `link_roots` (mặc định `False`) + hàm `_build_root_links()` |
| `tests/test_graphs.py` | Sửa | +9 test cho biến thể nối root (33 test tổng) |
| `scripts/diagnose_syntactic_graph.py` | Sửa | Báo luôn chi phí của biến thể nối root |
| `pLan/chuyende1/PLAN_CHUYENDE1.md` | Sửa | Thêm `asgcn_linked` vào bảng baseline, lịch Tuần 5, ràng buộc config |
| `chuyende1/gaps/GAP-007` | Sửa | Mục 5c — quyết định cuối và 5 lý do thiết kế |
| `chuyende1/user-require/GiaiThich_...md` | Sửa | Viết lại: Phần 4 đổi tên, thêm Phần 5 "đã cài gì" |

```bash
python -m pytest tests/ -q                       # 107 passed
python scripts/diagnose_syntactic_graph.py        # +2,4% cạnh cho biến thể
```

## 2. ĐỂ LÀM GÌ

- **Trước:** GAP-007 mở, chặn CD1.6a và CD1.6b. Biết 52,2 % đồ thị bị chia cắt nhưng
  không có cách nào đo tác động của nó.
- **Sau:** có thể chạy hai biến thể khác **đúng một biến**, nên hiệu số đo trực tiếp tác động
  của việc chia cắt.
- **Nếu bỏ:** khi `asgcn` cho kết quả thấp, không phân biệt được "phương pháp đồ thị không
  hợp" với "đồ thị bị chia cắt" — đúng rủi ro R3.

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

### 3.1. Nối theo CHUỖI, không phải hình sao

Câu có 3 root ở vị trí 0, 2, 4:

```
CHUỖI (đã chọn)                    HÌNH SAO (đã loại)
  root₀ ↔ root₂ ↔ root₄              root₀ ↔ root₂
                                     root₀ ↔ root₄
  Khoảng cách 0→4 = 2 bước           Khoảng cách 0→4 = 1 bước
```

Chuỗi giữ được **trật tự tuyến tính của diễn ngôn**: hai câu liền kề liên quan nhau hơn hai
câu cách xa. Hình sao làm mọi câu cách câu đầu đúng 1 bước — sai bản chất, và biến câu đầu
thành một nút trung tâm giả tạo.

### 3.2. Vì sao `conf = 1.0` chứ không phải 0,5 hay 0,7

Đây là chỗ dễ sai nhất. Cạnh `root_link` **là nhân tạo**, nên phản xạ đầu tiên là cho nó
`conf` thấp hơn cạnh cú pháp thật.

Nhưng: **lấy con số ở đâu ra?** Không có cơ sở nào biện minh cho 0,5 thay vì 0,6. Đó chính
là cái bẫy mà `PLAN_NSMGAT.md` cảnh báo ngay từ đầu — *"confidence = 0,92 ở đâu ra? Sao không
phải 0,8?"*. Bịa một con số là tự tạo ra một câu hỏi phản biện không trả lời được.

Cách xử lý đúng: giữ `conf = 1.0` như mọi cạnh view `syn`, và **phân biệt bằng `etype`** riêng
`DEP:root_link`. Nhờ đó:

- **CĐ1**: ASGCN đối xử mọi cạnh như nhau (nó không dùng `conf`), ta chỉ đo có/không
- **CĐ2**: NS-MGAT **học được trọng số riêng** cho etype này từ dữ liệu — đúng tinh thần
  "confidence phải đo được, không phải gán tay"

### 3.3. Một bất biến toán học đẹp

Với `link_roots=True`, số cạnh **luôn** bằng `3n − 2`, bất kể câu có bao nhiêu root:

```
2·(n − r)  cạnh cú pháp
+   n      self-loop
+ 2·(r − 1) cạnh nối root
─────────────────────────
= 2n − 2r + n + 2r − 2  =  3n − 2      ← r triệt tiêu!
```

Kiểm bằng số thật: câu 3 token 1 root → 7 cạnh; câu 4 token 2 root → 10 cạnh; câu 3 token
3 root → 7 cạnh. Đều khớp `3n − 2`.

Có test canh bất biến này, nên nếu sau này ai sửa builder làm hỏng công thức thì test đỏ ngay.

### 3.4. Vì sao mặc định phải là `False`

`asgcn` đã được định nghĩa là "ASGCN chuẩn". Nếu mặc định là `True`, thì việc thêm một tham
số mới sẽ **âm thầm đổi hành vi** của một baseline đã có — và mọi kết quả trước đó thành
không so sánh được. Nguyên tắc: *tham số mới không bao giờ được đổi hành vi mặc định của thứ
đã tồn tại.*

Có test riêng canh điều này (`test_mac_dinh_la_khong_noi_root`).

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Chọn | Loại | Vì sao loại |
|---|---|---|---|
| Mặc định | `False` | `True` | Đổi ngầm hành vi baseline đã có |
| Cách nối | Chuỗi | Hình sao | Sai bản chất trật tự diễn ngôn |
| Hướng | Hai chiều | Một chiều | GCN cần cả hai chiều (xem CD1.3 mục 3.2) |
| `conf` | 1,0 | 0,5 hoặc số khác | **Không có cơ sở biện minh** — bẫy "0,92 ở đâu ra" |
| Phân biệt | `etype` riêng | Trộn chung `DEP:*` | Cạnh nhân tạo phải tách bạch được — khác biệt cốt lõi so với phương án D |
| Tạo `configs/asgcn*.yaml` | **Chưa** | Tạo luôn | `asgcn` chưa tồn tại → vi phạm quy tắc 6 ("không viết logic của step chưa tới"). Thuộc CD1.6a |

## 5. ĐIỂM NỐI VỚI STEP SAU

- **CD1.6a (Tuần 5)** phải tạo **cả hai** config: `configs/asgcn.yaml` (`link_roots: false`)
  và `configs/asgcn_linked.yaml` (`link_roots: true`).
- ⚠️ Hai file phải **giống hệt nhau ở MỌI tham số khác**. Lệch một siêu tham số nào thì hiệu
  số không còn đo tác động của việc chia cắt nữa mà đo lẫn cả siêu tham số — cả thí nghiệm
  thành vô dụng.
- Mô hình `asgcn` đọc `link_roots` từ config rồi truyền vào
  `SyntacticGraphBuilder(link_roots=...)`.
- Kết quả sẽ vào mục 4.1, 4.3 và 6.2 của báo cáo.

## 6. KIỂM CHỨNG

```
.venv/Scripts/python.exe -m pytest tests/ -q
........................................................................ [ 67%]
...................................                                      [100%]
107 passed in 22.64s
```

Trước CD1.3b là 98 test, giờ 107 (+9).

**Chi phí thật của biến thể, đo trên dữ liệu thật:**

| Split | Cạnh TB `asgcn` | Cạnh TB `asgcn_linked` | Tăng |
|---|---|---|---|
| train | 112,57 | 115,32 | **+2,4 %** |
| dev | 107,73 | 110,62 | +2,7 % |
| test | 113,07 | 116,09 | +2,7 % |

Rẻ hơn dự tính ban đầu (~1 ngày GPU vẫn giữ nguyên vì thời gian huấn luyện chi phối bởi số
Example chứ không phải số cạnh).

Chín test mới đáng chú ý:

- `test_mac_dinh_la_khong_noi_root` — canh `asgcn` không bị đổi ngầm
- `test_cay_mot_root_thi_hai_bien_the_giong_het_nhau` — chứng minh hiệu số **chỉ** đến từ câu
  nhiều root, đúng thiết kế thí nghiệm
- `test_noi_root_lam_do_thi_lien_thong` — cốt lõi: biến thể xoá được sự chia cắt
- `test_noi_theo_CHUOI_khong_phai_hinh_sao` — canh đúng cách nối
- `test_cong_thuc_so_canh_khi_noi_root` — canh bất biến `3n − 2`
- `test_canh_noi_root_phan_biet_duoc_bang_etype` — canh khác biệt cốt lõi so với phương án D

## 7. DỪNG LẠI VÀ HỎI

**Không có câu hỏi chặn.** GAP-007 đã chốt, CD1.6a không còn bị chặn.

**Những chỗ bạn có thể muốn hỏi thêm:**

- Vì sao `conf = 1.0` cho một cạnh nhân tạo — nghe có vẻ không trung thực?
- Bất biến `3n − 2` có ý nghĩa gì ngoài việc đẹp?
- Nếu kết quả `asgcn_linked` chênh lệch rất nhỏ (dưới 0,5 điểm) thì có kết luận được không?

**Step kế tiếp theo lịch:** **CD1.4a `lexicon`** (Tuần 3) — sàn tuyệt đối, đồng thời đo độ phủ
từ điển cảm xúc tiếng Việt để trả lời GAP-002. Không phụ thuộc GAP-007.

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi code không |
|---|---|---|
| | | |
