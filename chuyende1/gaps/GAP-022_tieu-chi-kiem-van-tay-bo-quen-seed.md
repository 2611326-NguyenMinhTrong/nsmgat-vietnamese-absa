# GAP-022 — Tiêu chí kiểm vân tay bỏ quên seed, suýt loại ba lần chạy đúng

**Ngày phát hiện:** 02/10/2026 · **Phát hiện bởi:** Claude (tự phát hiện khi đối chiếu lại)
**Loại:** phương pháp · **Mức độ:** trung bình (không hỏng dữ liệu, nhưng suýt loại kết quả đúng) · **Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

Khi hướng dẫn học viên kiểm các file tải từ Colab về, Claude đưa tiêu chí:

> Vân tay của `asgcn` phải là `d2d2aebdc30f`.

Tiêu chí này chỉ đúng với **seed 42**. `train.py` ghi `cfg["seed"] = seed` trước khi bấm vân
tay, nên mỗi seed sinh ra một vân tay riêng. Vân tay `d2d2aebdc30f` trùng với seed 42 chỉ vì
`base.yaml` đặt seed mặc định là 42, và Claude tính nó bằng cách nạp file cấu hình mà không
truyền seed nào.

Hậu quả nếu không phát hiện: seed 1337 và seed 2024 đều bị đánh dấu lệch, trong khi cả hai
lần chạy đều đúng. Mất hai lần chạy, mỗi lần gần một giờ GPU, và tệ hơn là mất lòng tin vào
một cơ chế kiểm vốn đang hoạt động đúng.

## 2. Nguyên nhân gốc

**Lấy giá trị kỳ vọng từ một đường khác với đường sinh ra giá trị thật.** Giá trị thật đi
qua `train.py`, nơi seed được tiêm vào cấu hình. Giá trị kỳ vọng được tính bằng một lệnh
riêng không đi qua bước đó. Hai đường khác nhau thì so với nhau không có nghĩa, dù cùng gọi
một hàm `config_hash`.

Dấu hiệu lẽ ra phải nhận ra ngay: **cả ba seed ra ba vân tay khác nhau.** Nếu học viên sửa
cấu hình giữa chừng thì hai lần chạy sau phải trùng vân tay với nhau. Ba giá trị khác nhau
đôi một chỉ hợp với một cách giải thích duy nhất là có thứ thay đổi theo từng lần chạy.

## 3. Đã sửa thế nào

Kiểm lại bằng đúng đường mà giá trị thật đi qua, tức nạp cấu hình rồi tiêm seed trước khi
bấm vân tay. Cả ba seed khớp tuyệt đối.

Đối chiếu chéo thêm: `lexicon`, `bilstm`, `phobert` cũng đều có ba vân tay khác nhau cho ba
seed, từ CĐ1.3 đến CĐ1.5. Đây là hành vi đã có từ lâu, không phải thứ mới xuất hiện ở
`asgcn`.

Ghi điều này vào `notebooks/da-chay/QUY-UOC.md`, chỗ người ngoài sẽ đọc khi kiểm chứng, kèm
đoạn lệnh tính vân tay đúng cách.

## 4. Bài học

**Một tiêu chí kiểm phải được rút ra từ đường sinh ra dữ liệu, không phải từ trí nhớ.** Khi
viết bất kỳ bước kiểm nào, hỏi một câu: giá trị thật được tạo ra ở dòng nào, và lệnh kiểm
này có đi qua đúng dòng đó không.

**Khi một phép kiểm báo sai, nghi ngờ phép kiểm trước khi nghi ngờ dữ liệu.** Nhất là khi
dữ liệu sai theo một dạng mà không giả thuyết hợp lý nào giải thích nổi.

## 5. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — không con số nào bị ảnh hưởng, không file nào bị sửa hay xoá. Giữ trong sổ
      vì bài học ở mục 4 áp dụng cho mọi bước kiểm còn lại của luận văn.
