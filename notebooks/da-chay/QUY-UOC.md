# Bản notebook đã chạy — hồ sơ để kiểm chứng

Thư mục này giữ **bản Colab đã chạy, còn nguyên output** của từng lần huấn luyện. Khác với
`notebooks/colab_train.ipynb`, vốn là bản nguồn sạch, không có output.

Mục đích: người đọc báo cáo muốn kiểm chứng một con số có thể mở đúng bản notebook đã sinh
ra con số đó và đọc lại toàn bộ nhật ký lần chạy, thay vì chỉ thấy kết quả cuối.

## Quy ước tên

Một file notebook ứng với **một phiên Colab**, không phải một seed. Thực tế một phiên
thường chạy được vài seed, còn một seed bị ngắt giữa chừng thì trải qua hai phiên.

```
notebooks/da-chay/<ten_thi_nghiem>/phien-<nam-thang-ngay>.ipynb
```

Phiên nào cũng giữ, kể cả phiên bị ngắt, vì nhật ký của nó là bằng chứng về chỗ đứt. Hai
phiên cùng ngày thì thêm hậu tố `-a`, `-b`.

Mỗi phiên ghi lại bao nhiêu seed thì đọc ở các dòng `=== BAT DAU <exp>/seed<N> ===` trong
output, không đoán theo tên file.

## Cách lấy file

Trên Colab, sau khi lần chạy kết thúc và **trước khi xoá output hay đóng tab**: File, Download,
Download .ipynb. Notebook mở từ GitHub không được Colab tự lưu, đóng tab là mất output.

## Thí nghiệm không có notebook

| Thí nghiệm | Vì sao thiếu | Bằng chứng còn lại |
|---|---|---|
| `senticgcn`, cả ba seed, chạy ngày 03/10/2026 | Không tải notebook về trước khi đóng phiên, xem [GAP-024](../../chuyende1/gaps/GAP-024_mat-notebook-phien-colab-senticgcn.md) | `logs/senticgcn/seed{42,1337,2024}.log` ghi từng epoch, và vân tay cấu hình trong `metrics.json` khớp giá trị tính lại từ `configs/senticgcn.yaml` |

Với các lần chạy này, mục "Mã commit in ra ở mục Lấy code" trong bảng dưới **không đối chiếu
được**. Thứ thay được một phần: giữa hai commit của kho trong ngày 03/10/2026 chỉ có
`notebooks/colab_train.ipynb` thay đổi, nên dù phiên nào kéo commit nào thì mã mô hình và file
cấu hình vẫn là một.

## Người kiểm chứng đối chiếu những gì

| Đọc trong notebook | So với |
|---|---|
| Mã commit in ra ở mục "Lấy code" | Lịch sử git của kho |
| Dòng `=== BAT DAU <exp>/seed<N> ===` | Tên thư mục kết quả |
| Vân tay cấu hình in ở cuối lần chạy | `config_hash` trong `results/<exp>/seed<N>/metrics.json` |
| accuracy và macro-F1 ở ô xem kết quả | Bảng số trong báo cáo |

## Hai điều dễ hiểu nhầm

**Vân tay cấu hình khác nhau giữa các seed là đúng, không phải dấu hiệu sai.** Số seed được
ghi vào cấu hình trước khi bấm vân tay, nên mỗi seed có một vân tay riêng. Tên mô hình truyền
ở `--model` cũng được ghi vào theo cùng cách. Muốn kiểm, tính lại vân tay từ chính file cấu
hình, tiêm **cả hai** giá trị đó rồi mới so:

```python
from nsmgat.utils.io import load_config, config_hash
cfg = load_config("configs/senticgcn.yaml")
cfg["seed"] = 1337                                   # so seed cua lan chay
cfg.setdefault("model", {})["name"] = "senticgcn"    # gia tri da truyen o --model
print(config_hash(cfg))
```

Bỏ dòng thứ tư thì `phobert`, `asgcn`, `asgcn_linked` vẫn ra đúng, vì tên trong file cấu hình
của chúng vốn trùng với `--model`. Riêng `senticgcn` sẽ lệch cả ba seed: `senticgcn.yaml` kế
thừa `asgcn.yaml` nên tên có sẵn trong file là `asgcn`. Xem
[GAP-023](../../chuyende1/gaps/GAP-023_doan-lenh-kiem-van-tay-thieu-ten-mo-hinh.md).

Giá trị `--model` của từng thí nghiệm: `phobert` cho `phobert`, `asgcn` cho cả `asgcn` lẫn
`asgcn_linked`, `senticgcn` cho `senticgcn`.

**Số epoch có thể khác nhau giữa các seed.** Cơ chế dừng sớm theo macro-F1 trên tập dev cắt
lần chạy ở những chỗ khác nhau tuỳ seed. Thời gian huấn luyện vì thế cũng chênh.

## Trước khi đưa lên kho công khai

Notebook tải từ Colab mang theo phần siêu dữ liệu của phiên. Mở file bằng trình soạn thảo
văn bản, kiểm khối `"metadata"` ở cuối, xoá những trường có địa chỉ thư điện tử hoặc mã
nhận dạng tệp trên Drive nếu có.
