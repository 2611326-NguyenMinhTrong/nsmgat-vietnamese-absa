# GAP-014 — Thêm một dòng sổ sách vào `base.yaml` làm đổi `config_hash` của mọi kết quả cũ

**Ngày phát hiện:** 08/09/2026 · **Phát hiện bởi:** Claude Code (đọc `git diff` trước khi commit)
**Loại:** code
**Mức độ:** nghiêm trọng (làm hỏng chính thứ dùng để truy nguồn kết quả)
**Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

Ở CD1.4b tôi thêm ba dòng vào `configs/base.yaml` mục `output`:

```yaml
  log_dir: logs
  save_last: true
  save_last_every: 1
```

Ba dòng này là **sổ sách**: ghi nhật ký ở đâu, có ghi `last.pt` không, ghi cách mấy epoch.
Không dòng nào đụng tới mô hình, dữ liệu hay phép toán huấn luyện.

Nhưng `config_hash()` băm **toàn bộ** dict config, nên:

```
results/lexicon/seed42/metrics.json
-  "config_hash": "f25b1bbb0fcc"
+  "config_hash": "34f8cee22a1e"
```

trong khi **mọi con số khác trong file y nguyên** — accuracy 0,7471, macro-F1 0,5242,
`train_time_sec` 197,8 s, `n_params` 9.

## 2. Phát hiện thế nào

Đọc `git diff` trước khi commit và thấy `results/lexicon/seed42/metrics.json` bị sửa. Kết quả
`lexicon` đã chốt từ CD1.4a, lẽ ra không được đụng vào — nên phải hỏi *vì sao nó đổi*.

Nghiêm trọng hơn: **ở lượt trao đổi trước tôi đã nói với học viên rằng cách loại
`train.resume` khỏi vân tay "giữ nguyên vân tay cũ của `lexicon` (f25b1bbb0fcc), có test
khoá".** Câu đó **sai**. Test tôi viết chỉ kiểm khoá `resume` một cách cô lập, đúng phần nó
kiểm — nhưng tôi đã kết luận rộng hơn thứ test thật sự chứng minh, trong khi chính tôi cũng
vừa sửa `base.yaml` ở cùng phiên làm việc.

**Cách phát hiện đáng nhớ:** không phải test bắt được, mà là **đọc diff của những file lẽ ra
không được đổi**. Test chỉ kiểm thứ mình nghĩ ra để kiểm; diff cho thấy thứ thật sự đã đổi.

## 3. Nguyên nhân gốc

Hai nguyên nhân chồng lên nhau:

**(a) Ranh giới đặt sai mức.** `config_hash` băm cả dict thay vì băm *những gì quyết định kết
quả*. Ranh giới đúng không phải "file config", mà là "tập khoá ảnh hưởng tới đầu ra".

**(b) Kết luận rộng hơn bằng chứng.** Tôi có một test xanh về khoá `resume`, rồi phát biểu
một điều tổng quát hơn ("giữ nguyên vân tay cũ") mà test đó không chứng minh. Đây là lỗi suy
luận, không phải lỗi code — và nguy hiểm hơn lỗi code vì nó đi thẳng vào lời nói với học viên.

Đáng chú ý: khi thêm khoá `resume` tôi **đã** nhận ra vấn đề này và xử lý đúng. Nhưng ba
khoá `output.*` thêm ở một thời điểm khác, trong một mạch suy nghĩ khác (đang làm tính năng
theo dõi huấn luyện), nên **không nối được với bài học vừa rút ra vài phút trước**.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `results/lexicon/seed42/metrics.json` | Có — đã khôi phục về `f25b1bbb0fcc` |
| `results/bilstm/seed{42,1337,2024}/metrics.json` | Có — sinh lại vân tay theo luật mới |
| Mọi con số kết quả (accuracy, F1, `train_time_sec`, `n_params`) | **Không đổi gì cả** |
| Lời tôi đã nói với học viên ở lượt trước | **Đã đính chính** |

Không có kết quả nào phải chạy lại. Thiệt hại nằm ở chỗ khác: nếu không phát hiện, hai kết
quả **sinh ra từ cùng một cấu hình** sẽ mang hai vân tay khác nhau — làm hỏng đúng công dụng
duy nhất của `config_hash`.

## 5. Đã sửa thế nào

Mở rộng `_KHOA_KHONG_BAM_VAN_TAY` trong `src/nsmgat/utils/io.py`, kèm **tiêu chí quyết định
viết thành một câu ngay trong code**:

> *Đổi khoá này có làm đổi kết quả không?*

| Khoá | Loại khỏi vân tay | Vì sao |
|---|---|---|
| `train.resume` | ✅ có | Liền mạch hay chạy tiếp cho kết quả y hệt |
| `output.log_dir` | ✅ có | Ghi nhật ký ở đâu |
| `output.save_last` | ✅ có | Có ghi `last.pt` không |
| `output.save_last_every` | ✅ có | Ghi cách mấy epoch |
| `output.save_best` | ❌ **không** | Tắt thì đánh giá dùng mô hình epoch **cuối** thay vì epoch tốt nhất — **đổi kết quả thật** |
| `output.results_dir`, `ckpt_dir` | ❌ không | Không đổi kết quả, nhưng đã nằm trong vân tay từ S0.4; loại bây giờ đổi vân tay thêm lần nữa mà không được gì. **Lựa chọn có ý thức**, đã ghi trong code |

Thêm 2 test: `test_them_khoa_SO_SACH_vao_output_KHONG_lam_doi_van_tay` và
`test_doi_save_best_thi_van_tay_PHAI_doi` (mặt còn lại — loại bớt khoá không được làm vân tay
trở nên vô dụng).

Sinh lại `metrics.json` cho cả 4 kết quả bằng `--no-train` (không huấn luyện lại).

## 6. Bài học — phòng lần sau bằng cách nào

**Trước khi commit, đọc `git diff` của những file lẽ ra KHÔNG được đổi — nhất là
`results/**/metrics.json`.** Test chỉ kiểm thứ mình nghĩ ra để kiểm; diff cho thấy thứ thật
sự đã đổi. Lần này diff bắt được, test thì không.

Và: **khi thêm bất kỳ khoá nào vào `configs/base.yaml`, hỏi ngay "khoá này có làm đổi kết
quả không?" — nếu không thì thêm vào `_KHOA_KHONG_BAM_VAN_TAY` trong cùng một lần sửa**,
không để sang lần sau.

Bài học thứ ba, về cách nói: **chỉ phát biểu đúng phạm vi mà test chứng minh.** Test về khoá
`resume` chứng minh điều về khoá `resume` — không chứng minh điều gì về `base.yaml`.

## 7. Có cần đưa vào báo cáo không

- [ ] Có — đưa vào mục 6.2
- [x] Không — sai sót nội bộ, phát hiện trước khi commit, không con số nào bị ảnh hưởng.
      Nhưng bài học *"đọc diff của file lẽ ra không đổi"* đáng một dòng trong phần bàn về
      quy trình đảm bảo tái lập kết quả.
