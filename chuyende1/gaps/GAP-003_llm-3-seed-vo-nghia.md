# GAP-003 — Chạy `llm_zs` 3 seed ở temperature 0 cho độ lệch chuẩn giả tạo

**Ngày phát hiện:** 27/08/2026 · **Phát hiện bởi:** Claude Code (khi rà lại giao thức thực nghiệm)
**Loại:** phương pháp · **Mức độ:** **nghiêm trọng** (ảnh hưởng kết luận) · **Trạng thái:** 🔴 Mở

---

## 1. Sai ở đâu

Giao thức thực nghiệm chuẩn (`PLAN_CHUYENDE1.md` mục 6.1) bắt **mọi mô hình** chạy 3 seed
(42, 1337, 2024) và báo cáo `mean ± std`. Bảng nhật ký trong `progress_cd1.md` cũng có sẵn
3 dòng cho `llm_zs`.

Với 3 mô hình huấn luyện được, seed điều khiển khởi tạo trọng số, thứ tự shuffle, dropout →
3 lần chạy cho 3 kết quả khác nhau, `std` phản ánh **độ ổn định thật** của mô hình.

Với LLM gọi qua API ở `temperature = 0`, **seed không điều khiển gì cả**. Ba lần chạy cho ra
kết quả gần như giống hệt → `std ≈ 0`.

## 2. Vì sao đây là sai sót nghiêm trọng chứ không phải chuyện nhỏ

Bảng kết quả sẽ trông như thế này:

```
phobert     72,4 ± 0,8
senticgcn   73,1 ± 1,1
llm_zs      65,3 ± 0,0     ← trông như mô hình ổn định nhất trong cả bảng
```

Người đọc sẽ hiểu là **LLM ổn định vượt trội**. Thực tế ta chỉ đơn giản là *không thay đổi gì
giữa ba lần chạy*. Đây là con số **đúng về mặt tính toán nhưng sai về mặt diễn giải** — loại
sai nguy hiểm nhất, vì nó không lộ ra khi kiểm tra code.

Nếu hội đồng hỏi *"vì sao std của LLM bằng 0?"* mà không trả lời được thì mất tin cậy cho cả
bảng, không riêng dòng đó.

## 3. Nguyên nhân gốc

**Áp một giao thức đồng nhất lên các mô hình có bản chất khác nhau.** Ý định của quy tắc
"3 seed cho mọi mô hình" là *đối xử công bằng*. Nhưng công bằng không có nghĩa là làm giống
hệt nhau — mà là **đo cùng một đại lượng**. Đại lượng cần đo là *độ biến thiên do những lựa
chọn tuỳ ý trong quy trình*. Với mô hình huấn luyện, lựa chọn tuỳ ý là seed. Với LLM,
lựa chọn tuỳ ý là **bộ ví dụ few-shot và cách diễn đạt prompt**.

## 4. Phương án xử lý — đề xuất

| Chế độ | Cách làm | Báo cáo |
|---|---|---|
| **Zero-shot** | Chạy **1 lần**, `temperature = 0` | Báo 1 con số, ghi rõ *"tất định, không có độ lệch chuẩn"* — **không** ghi `± 0,0` |
| **Few-shot** | Chạy **3 lần với 3 bộ ví dụ k-shot khác nhau** (rút ngẫu nhiên từ train, dùng seed 42/1337/2024 để **chọn ví dụ**) | `mean ± std` — std này đo *độ nhạy với việc chọn ví dụ*, một đại lượng có ý nghĩa thật |

Bổ sung vào mục 6.1 của plan một dòng: *"Với baseline không huấn luyện, 'seed' được định
nghĩa lại là seed của việc chọn ví dụ few-shot; zero-shot báo cáo đơn trị."*

Cách này còn cho thêm một kết quả đáng giá cho Chương 4: **LLM nhạy thế nào với việc chọn
ví dụ** — thường là rất nhạy, và đó là một hạn chế đo được của họ phương pháp prompting.

## 5. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Phải sửa |
|---|---|
| `PLAN_CHUYENDE1.md` mục 6.1 (giao thức seed) | Chưa sửa — chờ học viên chốt |
| `progress_cd1.md` nhật ký thí nghiệm, 3 dòng `llm_zs` | Chưa sửa |
| `configs/llm_zs.yaml` (chưa tạo) | Sẽ tạo ở CD1.7 theo phương án đã chốt |
| Chương 4 mục 4.2, 4.4 | Phải nói rõ cách hiểu "seed" cho từng loại mô hình |

Chưa chạy thí nghiệm nào nên chưa có số liệu phải huỷ.

## 6. Bài học

**Trước khi áp một quy tắc đồng nhất lên mọi mô hình, hỏi: quy tắc này đang đo đại lượng gì,
và đại lượng đó có tồn tại ở mọi mô hình không?** Quy tắc giống nhau ≠ so sánh công bằng.

## 7. Có cần đưa vào báo cáo không

- [x] **Có** — mục 4.2 phải định nghĩa "seed" riêng cho baseline không huấn luyện; nếu không,
      cột `± std` trong bảng kết quả chính sẽ bị hiểu sai.
