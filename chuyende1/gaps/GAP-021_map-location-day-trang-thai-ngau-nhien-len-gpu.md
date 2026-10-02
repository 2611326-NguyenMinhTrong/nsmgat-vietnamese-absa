# GAP-021 — map_location đẩy trạng thái ngẫu nhiên lên GPU, chạy tiếp thì hỏng

**Ngày phát hiện:** 02/10/2026 · **Phát hiện bởi:** học viên (chạy tiếp seed 42 trên Colab)
**Loại:** code · **Mức độ:** **nghiêm trọng** (chặn hẳn cơ chế chạy tiếp trên GPU) · **Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

`Trainer._tiep_tuc` nạp checkpoint bằng:

```python
goi = torch.load(self.last_path, map_location=self.device, weights_only=False)
```

Trên Colab `self.device` là `cuda`, nên `map_location` đổi chỗ **mọi** tensor trong gói lên
GPU, kể cả hai trạng thái sinh số ngẫu nhiên nằm trong `goi["ngau_nhien"]`.

`torch.cuda.set_rng_state_all` kiểm `isinstance(t, torch.ByteTensor)` trước khi nhận. Kiểu
`torch.ByteTensor` chỉ dành cho CPU, nên tensor đã lên GPU không thoả, và torch ném:

```
TypeError: RNG state must be a torch.ByteTensor
```

Lỗi xảy ra **ngay đầu lần chạy tiếp**, trước khi huấn luyện được epoch nào.

## 2. Vì sao vết hỏng này đáng chú ý hơn vẻ ngoài của nó

Dòng ngay phía trên đã phòng đúng chuyện này cho trạng thái CPU:

```python
torch.set_rng_state(tt["torch"].cpu().to(torch.uint8))   # dòng 107, đã phòng
torch.cuda.set_rng_state_all(tt["torch_cuda"])           # dòng 109, bỏ sót
```

Nghĩa là nguyên nhân đã từng được nhìn thấy và xử lý một lần, rồi bỏ sót chỗ anh em của nó
cách đó hai dòng. Hỏng kiểu này không đến từ việc không biết, mà từ việc sửa một ca cụ thể
thay vì sửa cái chung.

## 3. Vì sao test không bắt được

`tests/test_resume.py` có test trung tâm `test_tiep_tuc_cho_ket_qua_GIONG_HET_chay_lien_mach`,
đúng là test quan trọng nhất của cơ chế này. Nhưng nó chạy ở máy học viên, **không có GPU**.
Khi đó `_trang_thai_ngau_nhien()` ghi `torch_cuda = None` và cả nhánh lỗi không bao giờ được
chạy tới.

Đây là **cùng một mẫu hỏng với GAP-020**, lần này ở biến khác: GAP-020 là nhánh chỉ chạm tới
khi câu dài hơn `max_seq_len`, GAP-021 là nhánh chỉ chạm tới khi có GPU. Cả hai lần, test
xanh chỉ chứng minh "đúng trong môi trường tôi đang ngồi".

## 4. Đã sửa thế nào

Tách phần chuẩn hoá thành một hàm dùng chung cho cả hai đường, thay vì viết lặp:

```python
def _ve_byte_cpu(t: torch.Tensor) -> torch.Tensor:
    return t.detach().cpu().to(torch.uint8)
```

Thêm một chốt chặn: nếu số GPU lúc chạy tiếp khác số GPU lúc lưu thì dừng hẳn và nói rõ lý
do, vì khi đó một phần trạng thái ngẫu nhiên không được khôi phục và lần chạy tiếp rẽ sang
một nhánh khác với lần chạy liền mạch.

Thêm 2 test vào `tests/test_resume.py`:

- `test_trang_thai_cuda_duoc_dua_ve_byte_tensor_tren_cpu`
- `test_bao_ro_khi_so_GPU_khac_luc_luu`

**Giới hạn của hai test này, ghi rõ ngay trong file test:** máy không có GPU thì không tạo
được tensor cuda thật, nên chúng ép **sai kiểu** thay vì **sai thiết bị**. Chúng khoá được
bước chuẩn hoá, nhưng không thay thế được một lần chạy tiếp thật trên GPU. Bằng chứng cuối
cùng là lần chạy tiếp seed 42 trên Colab sau khi vá.

## 5. Bài học

Hai điều, điều thứ hai mới là điều mới.

**Một.** Trùng với bài học GAP-020 và vì vậy nâng thành quy tắc: mỗi nhánh code chỉ chạy
trong một môi trường nhất định phải được viết test có giả lập môi trường đó, bằng
`monkeypatch` nếu không có phần cứng. Không chạm được nhánh thì nhánh đó coi như chưa viết.

**Hai, riêng của lần này.** `map_location` tác động lên *toàn bộ* gói, không chỉ trọng số.
Mọi thứ không phải tham số mô hình mà được nhét chung vào checkpoint — trạng thái ngẫu
nhiên, bộ đếm, siêu dữ liệu dạng tensor — đều bị nó đổi chỗ theo. Chỗ nào đọc ra khỏi gói mà
đòi một kiểu cụ thể thì phải tự chuẩn hoá lại, không được tin vào kiểu lúc lưu.

## 6. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — lỗi cài đặt của công cụ chạy tiếp, phát hiện trước khi có bất kỳ số liệu
      nào, và không đụng tới con số nào trong `metrics.json`. `last.pt` và `best.pt` sinh ra
      trước lúc vá vẫn dùng được nguyên vẹn: chỗ hỏng nằm ở đường đọc, không ở đường ghi.
