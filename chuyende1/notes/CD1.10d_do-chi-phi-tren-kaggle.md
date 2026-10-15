# PHIẾU BÀN GIAO — [CD1.10d] Đo chi phí suy luận trên Kaggle thay cho Colab

Ngày 16/10/2026. Học viên hỏi: "tôi muốn chạy trên Kaggle thay vì Colab được không? nếu được thì hướng dẫn tôi
từng bước". Được. Phép đo không phụ thuộc nền tảng; điều cần giữ là sáu mô hình đo trong một phiên, trên cùng một
loại GPU, và loại đó là T4 như lúc huấn luyện.

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `notebooks/kaggle_do_chi_phi.ipynb` | Tạo | 14 ô (6 ô mã): kiểm GPU là T4, kéo mã, cài, nối dữ liệu và bộ trọng số từ dataset, đo, kiểm và tải kết quả |
| `scripts/profile_cost.py` | Sửa | `--kiem` không chặn oan BiLSTM: với mô hình có dự đoán đổi theo kích thước lô (GAP-035) chỉ chặn khi lệch hơn 2 % số mẫu |
| `tests/test_profile_cost.py` | Sửa | Thêm 1 test cho trường hợp đó |
| `data/cache/kaggle_upload/` | Tạo, không lên GitHub | Năm file có ở máy để tải lên Kaggle: ba file dữ liệu, `bilstm_best.pt`, `lexicon_best.pt` (mã băm khớp bản gốc) |

## 2. VÌ SAO LÀM VẬY

- Notebook riêng thay vì sửa notebook Colab: Kaggle không gắn Google Drive, dữ liệu vào qua dataset (chỉ đọc, ở
  `/kaggle/input`), và đường dẫn khác. Notebook Colab giữ nguyên để còn chạy được.
- Bộ trọng số đổi tên thành `<tên mô hình>_best.pt`: sáu file cùng tên `best.pt` thì không phân biệt được trong
  dataset. Notebook tìm file theo tên ở mọi tầng thư mục của dataset, nên tải lên thế nào cũng được.
- Ba file dữ liệu bị kiểm số dòng và SHA-256: BiLSTM dựng bảng từ vựng từ tập huấn luyện ngay khi tạo mô hình, nên
  một file huấn luyện khác bản đã dùng sẽ làm sai mô hình mà không báo lỗi.
- Ô 1 dừng nếu GPU không phải T4: Kaggle có cả P100. Đo trên P100 vẫn so được sáu mô hình với nhau, nhưng báo cáo
  sẽ có hai loại GPU (huấn luyện trên T4, đo trên P100).
- `CUDA_VISIBLE_DEVICES=0`: lựa chọn "GPU T4 x2" cho hai GPU; phép đo chỉ dùng một.
- Thư mục mã đặt tên `nsmgat-repo`, không đặt `nsmgat`: trùng tên gói Python thì `import nsmgat` có thể nhầm sang
  thư mục (notebook Colab đã gặp và ghi lại).
- Lỗi của `--kiem` tìm thấy khi viết notebook: BiLSTM trên CPU khác 10 dự đoán ở lô 32, đúng ngưỡng chặn; trên GPU
  có thể vượt ngưỡng và bị báo LỖI dù bộ trọng số đúng. Nay BiLSTM chỉ bị chặn khi lệch hơn 2 % (134 mẫu); một bộ
  trọng số sai lệch hàng trăm mẫu.

## 3. CÁC BƯỚC CHẠY TRÊN KAGGLE

Tên nút dưới đây lấy theo tài liệu hướng dẫn Kaggle tra được ngày 16/10/2026; giao diện có thể khác vài chữ.

1. **Ở máy, gom file.** Năm file đã có ở `data\cache\kaggle_upload\`. Từ Google Drive tải
   `nsmgat/checkpoints/asgcn_linked/seed42/best.pt` và `nsmgat/checkpoints/senticgcn/seed42/best.pt` (mỗi file
   khoảng 540 MB), đổi tên thành `asgcn_linked_best.pt` và `senticgcn_best.pt`, đặt vào cùng thư mục. Nếu Drive còn
   `best.pt` của `phobert` hay `asgcn` thì thêm luôn, đổi tên theo cùng cách.
2. **Tài khoản Kaggle.** Đăng nhập, xác minh số điện thoại trong phần cài đặt tài khoản. Không xác minh thì không
   bật được GPU và Internet.
3. **Tạo dataset.** *Create* (dấu cộng) > *New Dataset*, kéo cả bảy file vào, đặt tên (ví dụ `nsmgat-do-chi-phi`),
   để **Private**, bấm *Create*. Chờ tải lên xong (khoảng 1,1 GB).
4. **Tạo notebook.** *Create* > *New Notebook*, rồi *File* > *Import Notebook*, chọn
   `notebooks\kaggle_do_chi_phi.ipynb` ở máy.
5. **Gắn dataset và chọn máy.** Khung bên phải: *Add Input* > dataset vừa tạo. *Settings*: *Accelerator* =
   **GPU T4 x2**, *Internet* = **On**.
6. **Chạy từng ô từ trên xuống.** Ô 1 phải in `OK: Tesla T4`. Ô 4 phải in ba dòng "khop file o may" và `CO` cho
   các mô hình có file. Ô 5 chạy 15 đến 25 phút; xem cột `khác` của `asgcn_linked` và `senticgcn` ở lô 32, lớn hơn
   vài mẫu thì dừng và báo Claude.
7. **Ô 6** chép kết quả, chạy lệnh kiểm và in đường tải `cost_profile.json`. Nếu mã trên GitHub chưa có lệnh `--kiem`
   (commit ngày 16/10 chưa push), ô in một dòng nói Claude sẽ kiểm ở máy.
8. **Mang về và tắt phiên.** Tải `cost_profile.json` vào `results\cost_profile.json`. *File* > *Download notebook*,
   lưu vào `notebooks\da-chay\cost\phien-<năm-tháng-ngày>-kaggle.ipynb`. Tắt phiên (*Stop session*) để không tốn giờ
   GPU. Báo Claude.

## 4. QUYẾT ĐỊNH THIẾT KẾ VÀ PHƯƠNG ÁN ĐÃ LOẠI

- Lấy bộ trọng số từ Drive bằng đường chia sẻ công khai rồi tải trong notebook: loại, vì phải mở quyền xem file
  cho bất kỳ ai có đường dẫn.
- Dùng công cụ dòng lệnh của Kaggle để tải dataset lên: loại cho lần này, vì phải cài và tạo khoá API Kaggle; tải
  qua trình duyệt đủ cho bảy file.
- Đặt bộ trọng số theo đúng cây thư mục `checkpoints/<tên>/seed42/` trong dataset: loại, vì giao diện tải lên của
  Kaggle có thể làm phẳng thư mục; tìm theo tên file không phụ thuộc chuyện đó.

## 5. ĐIỂM NỐI VỚI STEP SAU

Như mục 5 của phiếu CD1.10c. Khi điền tên GPU vào mục 4.5, ghi đo trên Tesla T4 của Kaggle; tên GPU, phiên bản
PyTorch và Transformers lấy từ `moi_truong` trong `cost_profile.json`.

## 6. KIỂM CHỨNG

```
notebook                    6 ô mã biên dịch được (bỏ các dòng % và !)
ô 4 chạy thử ở máy           trên thư mục giả lập /kaggle/input có thư mục con: tìm đủ ba file dữ liệu và hai bộ
                            trọng số, dựng đúng data/processed/ và checkpoints/<tên>/seed42/best.pt; sửa một file
                            dữ liệu thì ô dừng với "KHAC FILE O MAY"
                            (ở máy dùng chép file thay cho liên kết vì Windows không cho tạo liên kết; Kaggle là Linux)
pytest tests/test_profile_cost.py   11 passed, 1 skipped; cả bộ 514 passed, 1 skipped
data/cache/kaggle_upload/   năm file, SHA-256 khớp bản gốc
kho GitHub                  công khai (API GitHub trả "visibility": "public"), Kaggle kéo được không cần khoá
```

Chưa chạy được trên Kaggle thật: cần tài khoản của học viên. Phần chưa thử: cài gói trên Kaggle, tải PhoBERT, tải
file về qua `FileLink`.

## 7. DỪNG LẠI VÀ HỎI

1. Có push hai commit ngày 16/10 không? Không push thì phép đo vẫn chạy được (mã đo đã ở GitHub từ 13/10), chỉ ô 6
   không kiểm được trên Kaggle; Claude kiểm ở máy khi bạn mang file về.
2. Drive còn `best.pt` của `phobert` hay `asgcn` không?
