# CD1.8d (phần một) — Sửa 73 dòng PRICE, viết lại K2, rút 60 dòng để tự gán lại

**Ngày:** 13/10/2026 · **Trạng thái:** 🟡 phần một xong; phần chốt tập chờ ngày 27/10 · **Step kế:** lệnh chốt tập và chấm mô hình

---

## 1. ĐÃ LÀM GÌ

Theo bốn trả lời của học viên ngày 13/10:

| Trả lời của học viên | Việc đã làm |
|---|---|
| Đồng ý sửa các dòng PRICE về `dong_y` | Sửa 73 dòng trong `candidates.csv` (có sao lưu), mỗi dòng thêm ghi chú ngày sửa; sinh lại file `.xlsx`. Giữ nguyên 6 dòng có ý kiến về chính cái giá để học viên xem lại |
| Chưa hiểu K2 | Viết lại K2 trong `docs/annotation_guideline.md` mục 6 bằng một câu hỏi và năm ví dụ thật. Lập danh sách 14 dòng đề xuất đổi, chưa đổi |
| Dùng hết các dòng đã gán | Ghi vào Sổ quyết định. Không đổi `configs/base.yaml` |
| Chưa có người thứ hai | Tạo `scripts/finalize_diagnostic.py` (+ 5 test), rút 60 dòng ra `data/diagnostic/gan_lai_60.xlsx` |

Hướng dẫn chú thích lên phiên bản 2.

## 2. ĐỂ LÀM GÌ

Tập chẩn đoán chỉ dùng được làm bằng chứng khi biết nhãn hiện tượng có lặp lại được không. Không
có người thứ hai thì cách còn lại là chính người gán làm lại một mẫu sau khi đã quên nhãn cũ.

## 3. CƠ CHẾ — phần để học

### 3.1. K2 bằng một câu

Hỏi: **từ phủ định hay từ nối này nói về chính khía cạnh của dòng, hay về cái máy?**

"Khá mượt, không có gì phải phàn nàn trong tầm giá này cả", dòng PRICE: thứ không bị phàn nàn
là cái máy. Bỏ chữ "không" đi thì nhãn PRICE vẫn trung tính. Vậy với PRICE đây không phải phủ
định, gán `regular`. Cùng câu đó ở dòng GENERAL thì là `negation`.

Vì sao cần: nhóm phủ định đo việc mô hình có hiểu từ phủ định không. Dòng PRICE kiểu này mô hình
đoán đúng mà không cần hiểu chữ "không", nên để nó trong nhóm phủ định là làm nhóm dễ lên giả tạo.

### 3.2. Mẫu gán lại

- 60 dòng, phân tầng 15 dòng mỗi nhóm `negation`, `contrast`, `both`, `regular`. Rút theo tỉ lệ
  thật thì `both` chỉ được khoảng 6 dòng.
- File gán lại không có nhãn cũ và không có cột nhóm ứng viên.
- Lệnh `kappa` từ chối chạy trước ngày 27/10/2026, trừ khi người gán là người thứ hai.
- Kappa so lần gán lại với nhãn **đang có trong CSV lúc tính**, nên sửa 14 dòng K2 trước ngày đó
  vẫn được tính đúng.

### 3.3. Vì sao không đổi tên file trong `base.yaml`

`base.yaml` ghi `diagnostic_300.jsonl`. Tập thật sẽ có 799 dòng. Đổi tên trong `base.yaml` là
đổi `config_hash` của cả 18 lần chạy đã có, đúng lỗi GAP-014. Giữ tên file, ghi số dòng thật trong báo cáo.

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao |
|---|---|---|---|
| Ai sửa 73 dòng | Claude sửa trong CSV, có ghi chú từng dòng | Học viên sửa tay | Việc cơ học, học viên đã đồng ý; ghi chú giữ dấu vết |
| 6 dòng có ý kiến về giá | Giữ, chờ học viên | Sửa luôn | "vừa rẻ", "xứng đáng với giá tiền" là ý kiến về giá; quy ước của bộ dữ liệu cho các dòng này là tích cực |
| 14 dòng K2 | Chỉ đề xuất | Sửa luôn | Học viên chưa hiểu quy tắc thì chưa thể coi là đã đồng ý |
| Rút mẫu | Phân tầng đều | Ngẫu nhiên đơn | Cần đủ dòng `both` |
| Rút ngay hôm nay | Có | Chờ sửa xong K2 | Đồng hồ 14 ngày chạy sớm; kappa đọc nhãn mới nhất nên không phụ thuộc |

## 5. ĐIỂM NỐI

- Step kế: lệnh chốt file tập chẩn đoán và chấm sáu mô hình theo bốn nhóm, có khoảng tin cậy
  bootstrap theo câu như `compare_baselines.py`. Không cần huấn luyện lại. Kết quả là số sơ bộ
  cho tới khi kappa đạt.
- Sau 27/10: kappa. Đạt 0,70 thì điền mục 4.1.2 và 4.6. Không đạt thì xem cặp nhãn lệch nhiều
  nhất, sửa quy tắc, gán lại nhóm đó.

## 6. KIỂM CHỨNG

```
414 passed
```

- Hàm kappa khớp `sklearn.metrics.cohen_kappa_score`.
- Đã chạy `rut-mau` thật: 60 dòng, 15 mỗi nhóm; nhãn gốc 17 tiêu cực, 24 trung tính, 19 tích cực.
- Đã chạy `kappa` thật: lệnh dừng đúng với thông báo chưa tới 27/10.
- Sau khi sửa: `dong_y` 656, lệch nhãn gốc 143 trên 800 (17,9 %), trước đó 216 (27,0 %).
- **Chưa kiểm:** file `gan_lai_60.xlsx` chưa mở bằng Excel thật.

## 7. VIỆC CỦA BẠN

Đầy đủ ở `pLan/chuyende1/VIEC_CAN_LAM.md`. Ba việc mới:

1. Đọc lại K2, rồi xem 14 dòng PRICE ở các stt 9, 27, 34, 229, 369, 392, 495, 537, 643, 680, 772,
   777, 786, 787 của `candidates_chu_thich.xlsx`.
2. Xem 6 dòng PRICE giữ `positive` ở stt 190, 410, 464, 494, 614, 630.
3. Từ 27/10: gán lại `gan_lai_60.xlsx`, không mở trước ngày đó.
