# GAP-026 — Nhật ký tìm kiếm là tra theo tên bài đã biết, không phải một phễu sàng lọc

**Ngày phát hiện:** 05/10/2026 · **Phát hiện bởi:** Claude Code (khi viết mục 3.1 của bản nháp Chương 3)
**Loại:** phương pháp · **Mức độ:** nghiêm trọng nếu để nguyên (ảnh hưởng cách mô tả phương pháp khảo sát trước hội đồng) · **Trạng thái:** 🔴 Mở, chờ học viên quyết

---

## 1. Sai ở đâu

Dàn ý cuốn báo cáo yêu cầu mục 3.1 có một sơ đồ luồng sàng lọc: thu N₁ kết quả, loại trùng
còn N₂, sàng tiêu đề và tóm tắt còn N₃, đọc toàn văn còn N₄. Dàn ý viết rõ: có sơ đồ này là
dấu hiệu khảo sát có phương pháp.

`chuyende1/survey/survey_protocol.md` mục 5 và 6 đã có đủ các con số đó: N₁ = 258, N₂ = N₃ =
24. Nhưng đọc lại từng truy vấn trong nhật ký mục 6 thì thấy:

| Loại truy vấn | Số truy vấn | Ví dụ |
|---|---|---|
| Tra theo **tên bài hoặc tên tác giả đã biết**, để tìm bản gốc | 24 | `"Target-dependent Twitter Sentiment Classification" Jiang authors ACL 2011` |
| Tra để xác minh nơi công bố của một bài đã có | 2 | `"Is word segmentation necessary for Vietnamese sentiment classification" Duc-Vu Nguyen conference published` |
| **Từ khoá mở**, không nhắm một bài cụ thể | **2** | `neuro-symbolic aspect-based sentiment analysis rule neural hybrid explainable paper` |

Tức 26 trong 28 truy vấn được đặt ra để tra một bài đã biết tên, chứ không để tìm bài mới.
Những bài đó đã được chọn từ trước bằng một đường không ghi lại.

Đếm kỹ thì có **bốn** công trình thật sự được phát hiện qua kết quả tìm kiếm: một từ truy vấn
từ khoá mở (`HamiltonNeSyNLP`), và ba từ những truy vấn tra tên bài khác nhưng lại giữ một bài
hiện ra bên cạnh (`ViABSALipstick`, `PhoBERTPhoneReviewsCTU`, `WordSegVNSentiment`, theo ghi chú
ở cột "Số giữ lại"). Hai mươi công trình còn lại trong 24 là bài đã biết tên trước khi tra.

Vì vậy con số "258 kết quả, giữ lại 24" **không mô tả một quá trình sàng lọc**. Mỗi truy vấn
tra tên trả về khoảng 9 dòng, trong đó 1 dòng là bài đang tìm và 8 dòng còn lại không hề được
xét như ứng viên. Vẽ thành phễu 258 rồi 24 sẽ khiến người đọc hiểu rằng đã có 234 bài bị loại
qua sàng lọc, điều chưa từng xảy ra.

## 2. Phát hiện thế nào

Khi viết câu mô tả cách tìm tài liệu cho mục 3.1, cần nêu vài từ khoá đã dùng. Mở nhật ký ra
để chép thì thấy gần như không truy vấn nào là từ khoá của mục 3 giao thức.

Giao thức đã tự ghi một nửa vấn đề này, ở đoạn "Lưu ý về N₁": công cụ chỉ trả về kết quả hiển
thị đầu tiên. Nửa còn lại, rằng các truy vấn là tra tên chứ không phải tìm mở, thì chưa ai ghi.

## 3. Nguyên nhân gốc

**Hai việc khác nhau được ghi vào cùng một bảng.** Bảng mục 6 được thiết kế để ghi việc *tìm*
bài. Ngày 22/09, thứ thực sự được ghi vào là việc *kiểm chứng nguồn gốc* của những bài mà
Claude Code đã đề xuất tên. Hai việc dùng chung một công cụ nên trông giống nhau, nhưng chỉ
việc thứ nhất mới sinh ra một cái phễu.

Phía sau đó là quyết định ngày 22/09/2026 trong sổ quyết định: học viên giao Claude Code tìm
và đọc toàn văn để đẩy nhanh tiến độ. Nhiều khả năng danh sách ứng viên vì thế đến từ gợi ý
của Claude Code rồi mới được kiểm chứng từng bài, chứ không đến từ kết quả tìm kiếm. Đây là
suy ra từ dạng của các truy vấn, phiên làm việc hôm đó không để lại ghi chép nào về cách lập
danh sách. Mỗi bài đều đã được đọc toàn văn nên **nội dung ma trận đáng tin**. Thứ không có là
bằng chứng về **độ phủ**: không biết còn bao nhiêu công trình liên quan chưa được xét.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| Mục 3.1 của báo cáo, sơ đồ luồng sàng lọc | **Có.** Không được vẽ phễu 258 rồi 24 |
| Mục 3.10, mọi câu dạng "chưa có công trình nào" | **Có.** Phải giới hạn trong 45 công trình đã khảo sát. Bản nháp đã viết như vậy |
| Nội dung 46 dòng của ma trận | Không. Từng dòng đã đọc toàn văn từ bản gốc |
| Mục 6.2 của báo cáo, hạn chế của chuyên đề | Có, nếu chọn phương án B dưới đây |
| Câu hỏi "em tìm tài liệu bằng cách nào" ở buổi bảo vệ | **Có.** Phải có câu trả lời thật, chuẩn bị trước |

Số liệu trong ma trận vẫn dùng được nguyên vẹn. Thứ phải sửa là **cách gọi tên phương pháp**.

## 5. Đã sửa thế nào

Mới sửa phần viết, chưa sửa phần gốc:

- Bản nháp Chương 3 mục 3.1 mô tả đúng thực tế: mở rộng dần từ một tập công trình nền tảng,
  kèm một đoạn `[CẦN KIỂM]` nêu rõ 26 truy vấn tra tên và 2 truy vấn mở. Không có sơ đồ phễu.
- `chuyende1/survey/gap_analysis.md` có mục "Ba chỗ làm phạm vi khảo sát yếu đi".

**Hai phương án, chờ học viên quyết:**

**A. Làm cho cái phễu có thật.** Chạy một lượt tìm kiếm từ khoá mở trên Google Scholar hoặc
ACL Anthology với các từ khoá ở mục 3 của giao thức, ghi mỗi truy vấn một dòng vào nhật ký
với số kết quả thật, rồi sàng tiêu đề và tóm tắt. Ước lượng 3 đến 5 giờ tay. Kết quả có thể
là thêm vài công trình vào ma trận, hoặc xác nhận 45 công trình hiện có đã phủ đủ. Cả hai đều
là bằng chứng về độ phủ mà hiện chưa có.

**B. Gọi đúng tên việc đã làm.** Mô tả trong mục 3.1 là khảo sát có chủ đích, mở rộng từ các
công trình nền tảng, không tuyên bố tính hệ thống. Bỏ sơ đồ phễu. Thêm một câu vào mục 6.2 về
hạn chế này. Không tốn thêm giờ, nhưng mất điểm mạnh mà dàn ý nhắm tới.

Dù chọn phương án nào, còn một việc chỉ học viên quyết được: **có nêu trong báo cáo rằng việc
tìm và đọc tài liệu có công cụ trí tuệ nhân tạo hỗ trợ hay không**, theo quy định của trường
và ý kiến của GVHD. Claude Code không quyết thay việc này và không viết câu nào che nó đi.

## 6. Bài học — phòng lần sau bằng cách nào

**Trước khi dùng một con số để mô tả một quá trình, đọc lại từng dòng dữ liệu sinh ra con số
đó và hỏi: dòng này có đúng là một bước của quá trình ấy không.** Tổng 258 là phép cộng đúng
của một cột có thật, nhưng cột đó không đo thứ mà sơ đồ định nói.

Cùng họ với mẫu hỏng thứ hai của sổ này, GAP-013: con số đúng, ngữ cảnh của nó bị mất.

## 7. Có cần đưa vào báo cáo không

- [x] **Có**, dưới dạng tuỳ phương án: mô tả lượt tìm kiếm bổ sung ở mục 3.1 (phương án A),
      hoặc một câu về giới hạn độ phủ ở mục 6.2 (phương án B).
- [ ] Không
