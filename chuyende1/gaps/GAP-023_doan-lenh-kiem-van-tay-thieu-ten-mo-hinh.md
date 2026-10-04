# GAP-023 — Đoạn lệnh kiểm vân tay thiếu bước tiêm tên mô hình, báo lệch cả ba seed `senticgcn`

**Ngày phát hiện:** 04/10/2026 · **Phát hiện bởi:** Claude Code (tự phát hiện khi kiểm file tải về)
**Loại:** phương pháp · **Mức độ:** nhẹ (không hỏng dữ liệu, không con số nào đổi) · **Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

`notebooks/da-chay/QUY-UOC.md` là chỗ người ngoài đọc để kiểm chứng. Đoạn lệnh tính lại vân
tay ở đó chỉ tiêm số seed:

```python
cfg = load_config("configs/asgcn.yaml"); cfg["seed"] = 1337
print(config_hash(cfg))
```

Nhưng `src/nsmgat/train.py` tiêm **hai** giá trị trước khi bấm vân tay, ở hai dòng liền nhau:

```python
cfg["seed"] = seed
cfg.setdefault("model", {})["name"] = args.model
```

Khi kiểm ba seed `senticgcn` tải về ngày 04/10, Claude tính giá trị kỳ vọng theo đúng đoạn
lệnh thiếu đó và nhận ba vân tay lệch:

| Seed | Chỉ tiêm seed | Tiêm cả tên mô hình | Trong `metrics.json` |
|---|---|---|---|
| 42 | `88cffb5a75fa` | `bb0bb11d2ede` | `bb0bb11d2ede` |
| 1337 | `4850ab1db8a4` | `0caf4ff9183f` | `0caf4ff9183f` |
| 2024 | `794a6ff5a05f` | `9f2b79e52833` | `9f2b79e52833` |

Kèm theo, `SO_TAY_LENH.md` còn hai ô trong bảng các bước chạy Colab ghi "mỗi seed phải cùng
vân tay với seed đầu" và "ba seed, cùng một vân tay". Hai ô đó nói ngược lại đoạn văn ngay
bên dưới chính chúng, là phần còn sót từ trước GAP-022.

## 2. Phát hiện thế nào

Ba giá trị trong file khớp tuyệt đối với bảng vân tay đã ghi trong phiếu bàn giao ngày 03/10,
còn ba giá trị tính lại thì lệch cả ba. Dữ liệu khớp một nguồn độc lập mà phép kiểm thì
không, nên nghi phép kiểm trước. Đúng bài học của GAP-022, và lần này mất vài phút thay vì
suýt loại hai lần chạy.

Đối chiếu xong mới thấy `SO_TAY_LENH.md` và ô Mục 6 của `notebooks/colab_train.ipynb` đều đã
có đủ cả hai bước tiêm. Chỉ `QUY-UOC.md` còn bản cũ.

## 3. Nguyên nhân gốc

**Sửa GAP-022 mới vá đúng chỗ đang hỏng lúc đó, chưa hỏi "train.py còn tiêm gì nữa".**

Đoạn lệnh trong `QUY-UOC.md` viết ngày 02/10, khi chỉ có `phobert`, `asgcn`, `asgcn_linked`.
Với ba thí nghiệm đó, tên mô hình ghi sẵn trong file cấu hình trùng với giá trị `--model`,
nên bỏ bước tiêm tên vẫn ra đúng. Thiếu sót **vô hình** suốt chín lần chạy.

`senticgcn.yaml` kế thừa `asgcn.yaml`, nên tên có sẵn trong file là `asgcn`, còn `--model` là
`senticgcn`. Đây là thí nghiệm đầu tiên mà hai giá trị khác nhau. Đo lại ngày 04/10:

| Thí nghiệm | Tên trong file cấu hình | `--model` | Đoạn lệnh cũ ra đúng không |
|---|---|---|---|
| phobert | `phobert` | `phobert` | có |
| asgcn | `asgcn` | `asgcn` | có |
| asgcn_linked | `asgcn` | `asgcn` | có |
| senticgcn | `asgcn` | `senticgcn` | **không** |

Nguyên nhân sâu hơn: **công thức "chuẩn bị cấu hình trước khi bấm vân tay" đang tồn tại
thành bốn bản chép tay**, ở `train.py`, ở ô Mục 6 của notebook, ở `SO_TAY_LENH.md` và ở
`QUY-UOC.md`. Ngày 03/10 hai bản được cập nhật, một bản bị quên. Cùng mẫu hỏng thứ nhất của
sổ này: một giá trị xuất hiện ở nhiều chỗ mà không chỗ nào là nguồn.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `notebooks/da-chay/QUY-UOC.md`, đoạn lệnh tính vân tay | Có, đã sửa |
| `SO_TAY_LENH.md`, hai ô 8 và 9 của bảng các bước Colab | Có, đã sửa |
| `results/senticgcn/seed*/metrics.json` | Không. Cả ba file đúng ngay từ đầu |
| Vân tay của 9 lần chạy `phobert`, `asgcn`, `asgcn_linked` | Không. Đo lại, đoạn lệnh cũ và mới cho cùng giá trị |

Không số liệu nào sinh ra từ sai sót này. Thứ bị ảnh hưởng là **người kiểm chứng bên ngoài**:
làm đúng theo `QUY-UOC.md` cho `senticgcn` thì sẽ kết luận nhầm rằng ba lần chạy dùng cấu
hình khác với file trong kho.

## 5. Đã sửa thế nào

- `notebooks/da-chay/QUY-UOC.md`: đoạn lệnh nay tiêm cả seed lẫn tên mô hình, kèm một đoạn
  nói rõ vì sao bỏ dòng thứ hai thì ba thí nghiệm cũ vẫn đúng còn `senticgcn` lệch, và bảng
  giá trị `--model` của từng thí nghiệm.
- `SO_TAY_LENH.md`: ô 8 và ô 9 nay ghi mỗi seed một vân tay riêng, khớp bảng bên dưới.
- Kiểm lại ba seed `senticgcn` bằng đúng đường của `train.py`: khớp cả ba.

**Chưa làm, chờ học viên quyết:** gom hai dòng tiêm trong `train.py` thành một hàm ở
`nsmgat.utils.io`, để `train.py`, notebook và mọi đoạn lệnh kiểm cùng gọi một chỗ. Đó mới là
cách sửa tận gốc, nhưng đụng vào `train.py` nên không tự ý làm.

## 6. Bài học — phòng lần sau bằng cách nào

**Phép kiểm phải gọi đúng hàm đã sinh ra giá trị thật, không chép lại các bước của hàm đó.**
Chép lại thì đúng tại thời điểm chép, rồi lệch dần mỗi khi bên gốc thêm một bước.

Khi chưa gom được thành hàm: **mỗi lần thêm một thí nghiệm mới, chạy đoạn lệnh kiểm trong
tài liệu trên chính thí nghiệm đó trước khi chạy GPU**, không chỉ trên thí nghiệm cũ. Chín
lần chạy xanh không nói được gì về lần thứ mười nếu lần thứ mười khác ở đúng chỗ đoạn lệnh
bỏ qua.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — sai sót nội bộ ở tài liệu kiểm chứng, đã sửa, không ảnh hưởng kết quả. Giữ
      trong sổ vì đây là lần thứ hai cùng một bài học, sau GAP-022.
