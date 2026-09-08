# GAP-011 — Tiêu chí hoàn thành đòi `predictions.jsonl` nhưng không có code nào ghi ra

**Ngày phát hiện:** 08/09/2026 · **Phát hiện bởi:** Claude Code (khi học viên hỏi "CD1.4b đủ số liệu chưa?")
**Loại:** code
**Mức độ:** nghiêm trọng (chặn CD1.9, và làm hỏng phần so sánh có ý nghĩa thống kê)
**Trạng thái:** 🔴 Mở

---

## 1. Sai ở đâu

`chuyende1/MODULE.md` mục 5 (Tiêu chí hoàn thành module) yêu cầu:

> 12 thư mục `results/{4 exp}/seed{42,1337,2024}/` có `metrics.json` + **`predictions.jsonl`** hợp lệ

Nhưng tìm khắp mã nguồn, **không có dòng nào ghi `predictions.jsonl`**:

```
$ grep -rn "predictions" src/nsmgat/*.py
(không có kết quả)
```

Thực tế trên đĩa sau hai baseline đã chạy xong:

```
results/lexicon/seed42/   -> chỉ có metrics.json
results/bilstm/seed42/    -> chỉ có metrics.json
```

## 2. Phát hiện thế nào

Học viên hỏi *"CD1.4b đủ số liệu chưa?"*. Để trả lời cho chắc, thay vì chỉ đếm số seed,
đi đối chiếu với danh sách tiêu chí hoàn thành trong `MODULE.md` — và phát hiện một
tiêu chí chưa từng có ai làm.

**Cách phát hiện này đáng nhớ:** câu hỏi "đủ chưa?" chỉ trả lời được nếu có một danh sách
"đủ nghĩa là gì" viết sẵn từ trước. Nếu lúc đó mới ngồi nghĩ ra tiêu chí thì sẽ tự nghĩ ra
đúng những tiêu chí mà mình đã làm được.

## 3. Nguyên nhân gốc

**Giả định ngầm không được viết ra, cộng với ranh giới đặt sai mức.**

`MODULE.md` liệt kê `predictions.jsonl` như một *sản phẩm bàn giao của module*, nhưng
không step nào (CD1.4a, CD1.4b…) ghi nó vào phần "Output" của step đó. Mỗi step chỉ ghi
`results/<exp>/seed<N>/metrics.json`. Nên từng step làm xong đều thấy mình đủ, còn cái
thiếu chỉ lộ ra ở mức module — nơi không ai đọc lại cho tới lúc tổng kết.

Đây là **mặt trái của cùng cơ chế** đã gây GAP-004/005/006/009: một yêu cầu nằm ở nhiều
nơi, sửa/làm một nơi rồi quên nơi còn lại. Bốn lần trước là *giá trị sai lan ra*; lần này
là *yêu cầu có ở chỗ tổng, mất ở chỗ chi tiết*.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `results/lexicon/seed42/` (CD1.4a — đã đóng) | Có, phải chạy lại để sinh file |
| `results/bilstm/seed*/` (CD1.4b — đang chạy) | Có |
| **CD1.9 Phân tích lỗi** | **Chặn.** Không có dự đoán từng mẫu thì không lập được ma trận nhầm lẫn, không lấy được ca sai làm ví dụ cho mục 5.3 |
| **CD1.10 So sánh baseline** | Chặn phần kiểm định ý nghĩa thống kê: McNemar / bootstrap đều cần dự đoán **từng mẫu** của hai mô hình, `macro_f1` gộp không đủ |
| Số liệu đã có trong `metrics.json` | **Vẫn dùng được.** Đây là thiếu sản phẩm phụ, không phải sai số liệu |

Điểm nhẹ nhõm: `scripts/try_bilstm.py --sai` và `try_lexicon.py --sai` đang tính lại dự đoán
tại chỗ mỗi lần chạy, nên vẫn xem được ca sai — chỉ là chậm và không lưu lại được để đối chiếu.

## 5. Đã sửa thế nào

Chưa sửa. Ba việc phải quyết trước khi làm, **hỏi học viên**:

1. **Lược đồ file** — mỗi dòng cần gì? Đề xuất tối thiểu: `uid`, `aspect`, `y_true`,
   `y_pred`, `probs` (3 số). Có `probs` thì về sau đo được cả độ hiệu chuẩn (calibration),
   không phải chạy lại.
2. **Chạy lại hay ghi bù?** Chạy lại `lexicon` mất ~3 phút, `bilstm` mất ~57 phút/seed.
   Rẻ hơn: thêm cờ `--no-train` chạy trên `best.pt` đã có để chỉ sinh file dự đoán —
   không phải huấn luyện lại. Cách này cho ra **đúng** dự đoán cũ vì `best.pt` không đổi.
3. **`metrics.json` có đổi không?** Lược đồ này đã đóng băng ở S0.4 — nên **không đổi**,
   `predictions.jsonl` là file riêng bên cạnh.

## 6. Bài học — phòng lần sau bằng cách nào

**Trước khi đóng một step, mở `MODULE.md` mục 5 và đối chiếu từng dòng tiêu chí, không chỉ
đối chiếu phần "Output" viết trong step đó.** Phần "Output" của step do chính người làm step
viết ra, nên nó phản ánh cái người đó nhớ — còn mục 5 mới là hợp đồng với module.

## 7. Có cần đưa vào báo cáo không

- [ ] Có — đưa vào mục 6.2 "Hạn chế của Chuyên đề 1"
- [x] Không — sai sót nội bộ về quy trình; sửa xong thì số liệu cuối cùng không khác gì.
      Nhưng nếu tới Tuần 13 vẫn chưa sinh được `predictions.jsonl` thì **phải** ghi vào 6.2,
      vì lúc đó mục 5.3 (phân tích lỗi) sẽ mỏng đi thấy rõ.
