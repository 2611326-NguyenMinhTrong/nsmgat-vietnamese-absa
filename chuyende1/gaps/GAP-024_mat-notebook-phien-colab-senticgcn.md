# GAP-024 — Mất notebook phiên Colab của `senticgcn`, vì hướng dẫn mang kết quả về không nhắc tới nó

**Ngày phát hiện:** 04/10/2026 · **Phát hiện bởi:** Claude Code (khi kiểm file tải về), học viên xác nhận đã mất ngày 05/10/2026
**Loại:** tài liệu · **Mức độ:** nhẹ (không số liệu nào đổi, mất một lớp bằng chứng) · **Trạng thái:** ⚪ Chấp nhận sống chung, phần tài liệu ✅ đã sửa

---

## 1. Sai ở đâu

`notebooks/da-chay/QUY-UOC.md` quy định mỗi phiên Colab giữ lại một bản notebook còn nguyên
output. `asgcn` và `asgcn_linked` đều có. `senticgcn` thì không: cả ba seed chạy ngày
03/10/2026, kết quả và nhật ký đã về máy, nhưng notebook không được tải về và nay không còn.

## 2. Phát hiện thế nào

Ngày 04/10, khi kiểm chín file `senticgcn` tải về, thư mục `notebooks/da-chay/senticgcn/`
không tồn tại. Ngày 05/10 học viên xác nhận đã mất.

## 3. Nguyên nhân gốc

**Hai tài liệu nói hai điều khác nhau, và tài liệu được đọc lúc chạy là tài liệu thiếu.**

- `QUY-UOC.md` đòi giữ notebook, nhưng đó là file đọc khi **kiểm chứng**, không phải khi chạy.
- Mục 10 của `notebooks/colab_train.ipynb` và ô 10 trong `SO_TAY_LENH.md` là hai chỗ đọc
  **lúc chạy**. Cả hai ghi nguyên văn "chỉ cần `metrics.json` và `predictions.jsonl`", không
  nhắc notebook, cũng không nhắc file nhật ký.

Làm đúng theo hướng dẫn lúc chạy thì notebook không được tải về. Hai phiên trước giữ được là
nhờ Claude nhắc riêng trong phiên làm việc, không phải nhờ hướng dẫn.

Thêm một điều làm sai sót này không cứu được: notebook mở từ GitHub không được Colab tự lưu
vào Drive. Ba thứ kia nằm trên Drive nên lấy lúc nào cũng được; notebook thì đóng tab là mất.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `results/senticgcn/`, `logs/senticgcn/` | Không. Số liệu nguyên vẹn |
| Bảng đối chiếu trong `QUY-UOC.md` | Có. Với `senticgcn`, không đối chiếu được mã commit mà phiên chạy đã kéo về |
| Mục 10 của `notebooks/colab_train.ipynb`, ô 10 của `SO_TAY_LENH.md` | Có, đã sửa |

**Số liệu `senticgcn` vẫn dùng được.** Bằng chứng còn lại:

- Nhật ký từng epoch của cả ba seed, có dấu thời gian, trong `logs/senticgcn/`.
- Vân tay cấu hình trong `metrics.json` khớp giá trị tính lại từ `configs/senticgcn.yaml`.
- Số tham số 136.181.763, bằng `asgcn`, đúng với mô hình không thêm tham số học được.
- Giữa hai commit của kho trong ngày 03/10 chỉ có `notebooks/colab_train.ipynb` thay đổi, nên
  phiên nào kéo commit nào thì mã mô hình và file cấu hình vẫn là một.

Thứ mất: người kiểm chứng không tự đọc được output của phiên chạy, phải tin vào nhật ký.

## 5. Đã sửa thế nào

Học viên quyết ngày 05/10/2026: **không chạy lại, ghi nhận là mất.** Chạy lại ba seed tốn
khoảng 227 phút GPU để lấy lại một lớp bằng chứng mà nhật ký đã thay được phần lớn.

Phần tài liệu đã sửa để không lặp lại:

- `notebooks/colab_train.ipynb` mục 10: bảng bốn thứ phải mang về, nói rõ notebook phải tải
  **trước khi đóng tab** và vì sao.
- `SO_TAY_LENH.md` ô 10: cùng nội dung.
- `notebooks/da-chay/QUY-UOC.md`: thêm mục "Thí nghiệm không có notebook" để người kiểm chứng
  biết thiếu gì và dùng gì thay.

**Hệ quả phải nói ra trong báo cáo:** nếu có phụ lục về khả năng tái lập, ghi rõ `senticgcn`
chỉ có nhật ký huấn luyện, không có bản notebook đã chạy.

## 6. Bài học — phòng lần sau bằng cách nào

**Một yêu cầu về việc phải làm lúc chạy thì phải nằm trong tài liệu được đọc lúc chạy.** Viết
nó ở file quy ước dành cho người kiểm chứng là viết cho sai người đọc.

Cùng mặt trái đã ghi ở GAP-011: yêu cầu có ở tài liệu tổng nhưng mất hút ở từng bước thực
hiện.

## 7. Có cần đưa vào báo cáo không

- [x] **Có**, một câu ở mục 6.2 "Hạn chế của Chuyên đề 1" hoặc ở phụ lục tái lập: lần chạy
      `senticgcn` thiếu bản notebook đã chạy, bằng chứng thay thế là nhật ký từng epoch.
- [ ] Không
