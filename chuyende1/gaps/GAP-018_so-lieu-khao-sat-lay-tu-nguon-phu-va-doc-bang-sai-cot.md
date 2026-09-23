# GAP-018 — Số liệu khảo sát lấy từ nguồn phụ và đọc bảng sai cột

**Ngày phát hiện:** 22/09/2026 · **Phát hiện bởi:** Claude Code (đối chiếu chéo khi đọc bài mới)
**Loại:** số liệu
**Mức độ:** nghiêm trọng nếu để lâu (các ô này sẽ đi thẳng vào Bảng 3.9 của báo cáo)
**Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

Trong đợt thêm 12 công trình mới vào `chuyende1/survey/survey_matrix.csv` (22/09/2026, lần 2),
9 dòng có ô ghi sai so với chính bài gốc:

| Dòng | Ô sai | Đã ghi | Đúng theo bài gốc |
|---|---|---|---|
| `VoZhang2015` | `ket_qua_tot_nhat`, `tap_du_lieu` | 69,7% là mô hình Target-dep+; cùng tập với Jiang 2011 | 69,7% là Target-dep; Target-dep+ là 71,1% (Bảng 5); tập của Dong et al. 2014 |
| `Jiang2011` | `ket_qua_tot_nhat`, `co_tri_thuc_ngoai`, `co_dung_do_thi` | acc 63,4%; không từ điển; không đồ thị | 63,4% là số SVM-dep do Dong et al. 2014 cài lại trên tập khác; số gốc là 68,3% trên 3 lớp (Bảng 5); bài dùng từ điển General Inquirer và đồ thị tweet liên quan |
| `NRCCanada2014` | `ket_qua_tot_nhat` | "đứng đầu cả hai miền" | Nhất SB3, SB4; ba SB1; nhất Laptop và nhì Restaurant ở SB2 |
| `SemEval2014` | `ket_qua_tot_nhat`, `co_ma_nguon` | DLIREC 84,01% ở miền Laptop; không có mã | Miền Restaurant; có mã baseline (footnote 7) |
| `SemEval2015` | `co_ma_nguon` | không có mã | Có mã baseline và script đánh giá (mục 4.2) |
| `SemEval2016` | `co_ma_nguon`, `tap_du_lieu`, `ghi_chu` | không có mã; 6 miền; 16 đồng tác giả | Có mã baseline; 7 miền (sót khách sạn); 17 đồng tác giả |
| `GenerativeABSA` | `ket_qua_tot_nhat` | "F1 73,64%" không nói tập nào | 73,64 là Rest16; Rest14 là 77,13 |
| `ChatGPTSentiment` | `ghi_chu`, `tap_du_lieu` | bài tự xây các tập 14-Res/Lap-Negation | Các tập này của Moore & Barnes (2021); bài chỉ tự rút SST-2-Neg/Spec |
| `KoconNeuroSymbolic` | `ket_qua_tot_nhat`, `ngon_ngu` | SE = "Sentence Embedding"; tiếng Anh | SE = Sentiment Embeddings (mục 4.6); dữ liệu tiếng Ba Lan |

## 2. Phát hiện thế nào

Không phải do học viên hay kiểm thử bắt được, mà do **đối chiếu chéo tình cờ** khi đọc bài
mới ở đợt 3: bảng kết quả của TD-LSTM trích lại số của Vo & Zhang (Target-dep 69,7, Target-dep+
71,1) và của Jiang (SVM-dep 63,4), lệch với cái đã ghi. Từ đó rà lại toàn bộ 12 dòng của đợt 2
từ PDF gốc thì lộ thêm 7 dòng.

Cách phát hiện đáng giữ: **bảng so sánh baseline của bài sau là nguồn đối chiếu miễn phí cho bài
trước.** R-GAT (Bảng 2) cũng xác nhận lại đúng số của ASGCN, CDT, RAM, IAN, ATAE-LSTM.

## 3. Nguyên nhân gốc

Ba cơ chế khác nhau, không phải một:

1. **Lấy số từ nguồn phụ thay vì bài gốc.** Số 63,4% của Jiang lấy từ bảng baseline của
   Vo & Zhang, không mở bảng của chính Jiang. Con số đó đúng, nhưng là số của người khác cài lại
   trên tập khác, nên ghép với ô `tap_du_lieu` của Jiang thì thành một cặp mâu thuẫn.
2. **Đọc bảng nhiều cột từ văn bản trích bằng `pypdf` chế độ thường.** Chế độ này làm xáo thứ tự
   cột (SemEval-2014 Bảng 4 hai cột Laptop/Restaurant bị đọc lệch; GenerativeABSA mất tên cột).
   Chế độ `extraction_mode='layout'` giữ đúng vị trí cột.
3. **Điền theo suy luận thay vì tìm câu trong bài.** "Bài định nghĩa tác vụ thì không có mã" là
   một giả định, không phải điều đọc được; cả 3 bài SemEval đều có câu nói rõ mã baseline tải được.
   "SE là Sentence Embedding" là đoán nghĩa chữ viết tắt, không tra mục định nghĩa.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| 9 dòng trong `survey_matrix.csv` | Có — đã sửa |
| `chuyende1/user-require/BaoCaoTienDo-GVHD.md` | Không — báo cáo chỉ dùng tổng số dòng và phát hiện về ChatGPT; phát hiện ChatGPT đã đối chiếu lại Bảng 2 theo chế độ layout, đúng |
| `pLan/chuyende1/progress_cd1.md` | Không — chỉ ghi tổng số |
| Bảng 3.9 | Chưa sinh — không bị ảnh hưởng |

## 5. Đã sửa thế nào

Mở lại từng PDF gốc (vẫn còn trong thư mục kết quả của công cụ), trích bằng cả hai chế độ,
tìm đúng câu hoặc đúng bảng cho từng ô, rồi ghi đè 9 dòng bằng script dùng `csv.writer`.
Mỗi dòng đã sửa có một đoạn "SUA 22/09/2026 (lan 3)" trong `ghi_chu` nói rõ ô nào sai và câu
nào trong bài làm căn cứ. Riêng cột `ngon_ngu` phải mở rộng từ vựng thêm giá trị `khac`
(sửa đồng bộ `scripts/survey_tools.py`, mục 9 `survey_protocol.md` và dòng `#MO_TA`), vì bộ
giá trị cũ `vi | en | da_ngu` không có cách ghi đúng cho một bài tiếng Ba Lan.

## 6. Bài học — phòng lần sau bằng cách nào

**Mỗi con số ghi vào ma trận phải trỏ được tới một bảng hoặc một câu cụ thể của CHÍNH bài đó;
bảng nhiều cột luôn đọc bằng `extraction_mode='layout'`; ô có/không (`co_ma_nguon`,
`co_tri_thuc_ngoai`...) phải tìm thấy câu trong bài, không suy từ loại bài.**

Kèm theo: sau mỗi đợt, lấy bảng baseline của bài mới nhất trong đợt đối chiếu ngược với các
dòng cũ có cùng mô hình.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — sai sót nội bộ khi dựng ma trận, đã sửa trước khi sinh Bảng 3.9, chưa lọt vào
      văn bản nào gửi GVHD.
