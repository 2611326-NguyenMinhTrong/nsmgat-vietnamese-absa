# PHIẾU XIN Ý KIẾN GIẢNG VIÊN HƯỚNG DẪN

## Về danh sách mô hình baseline cho Chuyên đề 1

**Kính gửi:** ThS. Phan Thị Huyền Trang

**Học viên:** Nguyễn Minh Trọng — MSHV 2611326

**Ngành:** Khoa học máy tính — Mã số 8480101

**Hướng nghiên cứu:** Phân tích cảm xúc theo khía cạnh (ABSA/ACSA) cho tiếng Việt

**Ngày:** ...... / ...... / 2026

---

## 1. Bối cảnh và mục đích của phiếu này

Chuyên đề 1 của em có bốn nhiệm vụ: khảo sát các nghiên cứu tiên tiến liên quan đề tài, thực nghiệm một số mô hình trong đó, so sánh và đánh giá kết quả, từ đó tìm ra hạn chế và đề xuất hướng cải tiến để thực hiện ở Chuyên đề 2.

Phạm vi em đã dự kiến: thời gian 15 tuần, dữ liệu chính là **UIT-ViSFD** (đã tiền xử lý xong: 23.872 / 3.316 / 6.722 mẫu cho tập huấn luyện / kiểm định / kiểm tra), kèm một tập chẩn đoán 300 câu do em tự gán nhãn.

Em dự kiến thực nghiệm **bốn mô hình baseline**. Vì lựa chọn này quyết định toàn bộ phần so sánh ở Chương 4 và phần lập luận về hạn chế ở Chương 5, em xin phép trình bày lý do chọn từng mô hình và kính mong Cô cho ý kiến trước khi em bắt đầu chạy thực nghiệm (dự kiến từ Tuần 3).

---

## 2. Nguyên tắc em dùng để chọn baseline

Em không chọn theo tiêu chí "bốn mô hình mạnh nhất hiện nay", mà theo tiêu chí **mỗi baseline đại diện cho một cách giải thích khác nhau về việc vì sao bài toán còn khó**.

Lý do: mục tiêu cuối của Chuyên đề 1 là chứng minh được rằng bài toán còn khó vì **thiếu cấu trúc ngôn ngữ tường minh** (phạm vi phủ định, quan hệ chuyển ý). Kết luận đó chỉ vững nếu em loại trừ được các cách giải thích cạnh tranh. Mỗi baseline là một cách giải thích cạnh tranh cần loại trừ.

| Baseline | Giả thuyết cạnh tranh nó đại diện | Nếu giả thuyết đó đúng thì đề tài ra sao |
|---|---|---|
| PhoBERT | Mô hình ngôn ngữ tiền huấn luyện tiếng Việt đã đủ, chỉ cần tinh chỉnh | Hướng nghiên cứu không còn vấn đề để giải |
| Sentic-GCN | Cú pháp cộng tri thức cảm xúc đã đủ, không cần luật ngôn ngữ | Đóng góp thu hẹp còn "thêm luật", quá mỏng cho luận văn |
| ViSoBERT | Vấn đề nằm ở dữ liệu tiền huấn luyện không khớp miền, không phải ở cấu trúc | Lời giải là đổi mô hình nền, không phải thêm tầng ký hiệu |
| LLM | Mô hình đủ lớn thì tự giải quyết được | Đề tài mất tính thời sự |

Bốn mô hình này **không đo cùng một thứ**. Nếu bỏ bất kỳ mô hình nào, sẽ còn lại một cách giải thích chưa được loại trừ, và hội đồng có thể chất vấn đúng vào chỗ đó.

---

## 3. Lý do chọn từng mô hình

### 3.1. PhoBERT-base — mô hình ngôn ngữ tiền huấn luyện tiếng Việt

**Vai trò:** mốc so sánh nền tảng, đại diện cho cách tiếp cận phổ biến nhất hiện nay với tiếng Việt.

**Vì sao chọn:** đây là mô hình được dùng nhiều nhất trong các công trình xử lý ngôn ngữ tiếng Việt gần đây, nên nếu không có nó, bảng kết quả của em không so sánh được với các công bố khác. Ngoài ra, PhoBERT yêu cầu tách từ bằng VnCoreNLP — bước tiền xử lý em đã hoàn thành, nên chi phí triển khai thấp.

**Nếu bỏ:** không còn mốc tham chiếu chung với cộng đồng nghiên cứu tiếng Việt.

### 3.2. Sentic-GCN — mạng nơ-ron đồ thị kết hợp tri thức cảm xúc

**Vai trò:** đây là **baseline quan trọng nhất trong bốn mô hình**, dù không phải mô hình mạnh nhất.

**Vì sao chọn:** vì nó là họ hàng gần nhất của mô hình em dự kiến đề xuất ở Chuyên đề 2. Mô hình đề xuất gồm ba thành phần: đồ thị cú pháp, đồ thị cảm xúc và đồ thị luật ngôn ngữ có độ tin cậy hiệu chỉnh từ dữ liệu. Sentic-GCN đã có hai thành phần đầu.

> Sentic-GCN = đồ thị cú pháp + tri thức cảm xúc
>
> Mô hình đề xuất = đồ thị cú pháp + tri thức cảm xúc + **đồ thị luật có độ tin cậy**

Vì vậy hiệu số kết quả giữa mô hình đề xuất và Sentic-GCN **chính là** phần đóng góp của em, đo được trực tiếp, không cần lập luận vòng vo.

**Nếu bỏ:** em chỉ so được với PhoBERT, và phản biện có thể nói rằng cải thiện đạt được là do "thêm đồ thị nói chung" chứ không phải do cơ chế luật mà em đề xuất. Em sẽ không có số liệu để trả lời.

### 3.3. ViSoBERT — mô hình tiền huấn luyện cho văn bản mạng xã hội tiếng Việt

**Vai trò:** loại trừ một yếu tố gây nhiễu mà em cho là nguy hiểm nhất.

**Vì sao chọn:** UIT-ViSFD là bình luận sản phẩm trên mạng, có viết tắt, sai chính tả, teencode, biểu tượng cảm xúc. PhoBERT được tiền huấn luyện chủ yếu trên văn bản chuẩn (Wikipedia, báo chí). Nếu em chỉ có PhoBERT và quan sát thấy nó sai ở các câu phủ định, sẽ có **hai cách giải thích không phân biệt được**:

1. Mô hình không nắm được phạm vi phủ định — đây là giả thuyết của em;
2. Mô hình đơn giản là chưa quen với kiểu văn bản mạng xã hội.

ViSoBERT được tiền huấn luyện trên chính loại văn bản đó. Nếu nó thu hẹp khoảng cách thì cách giải thích thứ hai đúng, và em phải điều chỉnh hướng nghiên cứu. Nếu nó **cũng sai tương tự ở nhóm câu phủ định** thì yếu tố gây nhiễu được loại bỏ, và giả thuyết của em vững hơn hẳn.

**Nếu bỏ:** đây là điểm em cho rằng phản biện dễ chất vấn nhất, với câu hỏi: *"Có chắc là do cấu trúc ngôn ngữ, hay chỉ vì PhoBERT không hợp với văn bản mạng xã hội?"*

Đây cũng là mô hình duy nhất trong bốn mô hình mà em đưa vào **để cố gắng bác bỏ chính giả thuyết của mình**.

### 3.4. Mô hình ngôn ngữ lớn (LLM) — đánh giá zero-shot và few-shot

**Vai trò:** mốc tham chiếu, không phải baseline so sánh chặt chẽ.

**Vì sao chọn — hai lý do:**

1. Về khoa học: kiểm định giả thuyết "mô hình đủ lớn thì tự giải quyết được", vốn là quan điểm phổ biến hiện nay.
2. Về thực tế: em nghĩ khả năng cao sẽ có thành viên hội đồng đặt câu hỏi *"vì sao không dùng ChatGPT hay Gemini?"*. Không có số liệu để trả lời sẽ là một điểm yếu, dù câu hỏi này không sâu về mặt học thuật.

**Hạn chế em xin nêu trước:** kết quả gọi qua API **không tái lập tuyệt đối được** (nhà cung cấp có thể cập nhật mô hình bất kỳ lúc nào). Vì vậy em dự kiến xếp nó vào nhóm *mốc tham chiếu* và ghi rõ tên mô hình, phiên bản, ngày gọi, cùng toàn văn câu lệnh trong phụ lục — chứ không đặt ngang hàng với ba mô hình còn lại trong các kết luận so sánh.

---

## 4. Đối chiếu với các nhóm phương pháp trong khảo sát

Ở phần khảo sát (Chương 3), em dự kiến phân loại các công trình thành sáu nhóm. Bốn baseline phủ ba nhóm còn đang phát triển:

| Nhóm phương pháp | Baseline đại diện | Ghi chú |
|---|---|---|
| 1. Đặc trưng thủ công + học máy cổ điển (SVM, CRF) | không chọn | Đã được nhiều công trình chứng minh thua mô hình tiền huấn luyện; em trình bày qua khảo sát, không chạy lại |
| 2. Mạng nơ-ron tuần tự + attention (LSTM) | không chọn | Cùng lý do |
| 3. Mô hình ngôn ngữ tiền huấn luyện | PhoBERT, ViSoBERT | ✔ |
| 4. Mạng nơ-ron đồ thị | Sentic-GCN | ✔ |
| 5. Sinh và prompting | LLM | ✔ |
| 6. **Kết hợp nơ-ron và ký hiệu (neuro-symbolic)** | **để trống có chủ ý** | ← đây là khoảng trống em dự kiến lấp ở Chuyên đề 2 |

Em để trống nhóm 6 một cách có chủ ý. Khi đưa bảng này vào Chương 3, bản thân nó đã cho thấy vị trí đóng góp dự kiến của đề tài.

---

## 5. Các mô hình em đã cân nhắc nhưng chưa chọn

| Mô hình | Lý do chưa chọn | Sẵn sàng bổ sung nếu Cô yêu cầu |
|---|---|---|
| BiLSTM + attention | Đã bị mô hình tiền huấn luyện vượt xa | Có — chi phí thấp (khoảng 1 giờ GPU), và làm phép so "có đồ thị / không đồ thị" rõ hơn. **Đây là mô hình em thấy đáng bổ sung nhất nếu Cô muốn thêm** |
| ASGCN (đồ thị cú pháp thuần) | Trùng vai trò với Sentic-GCN | Có — xin xem thêm mục 6.1 |
| PhoBERT-large | Trùng vai trò với PhoBERT-base, chỉ khác quy mô | Cân nhắc — tốn khoảng gấp ba thời gian huấn luyện |
| BARTpho (mô hình sinh) | Trùng nhóm 5 với LLM | Cân nhắc |
| Đánh giá chéo miền trên VLSP 2018 | Cần thêm khoảng 2 tuần | Đề nghị để sang Chuyên đề 2 |

---

## 6. Hai vấn đề kỹ thuật em đang phân vân, kính mong Cô cho ý kiến

Em xin nêu trước hai điểm em đã tự phát hiện khi rà soát kế hoạch, để Cô biết em không bỏ qua chúng.

### 6.1. Sentic-GCN cần từ điển cảm xúc tiếng Việt

Mô hình gốc dùng SenticNet, vốn là tài nguyên tiếng Anh. Với tiếng Việt em phải thay bằng từ điển khác. Rủi ro: nếu từ điển có độ phủ kém trên văn bản mạng xã hội, Sentic-GCN sẽ cho kết quả thấp, và khi đó **em không phân biệt được** hai khả năng: (a) phương pháp đồ thị thật sự không hợp với bài toán này; hay (b) chỉ là do từ điển quá thưa.

Kết luận (a) mà thực chất là (b) sẽ làm đóng góp của Chuyên đề 2 trông lớn hơn thực tế.

Em đề xuất ba phương án:

| Phương án | Nội dung | Chi phí thêm |
|---|---|---|
| **A** *(em nghiêng về phương án này)* | Thêm một bước đo độ phủ của từ điển trên tập huấn luyện và báo cáo con số đó trong Chương 4 | Khoảng nửa ngày |
| B | Thay Sentic-GCN bằng ASGCN (đồ thị cú pháp thuần, không cần từ điển cảm xúc) | Không đổi, nhưng mất thành phần tri thức cảm xúc khỏi phép so sánh |
| C | Chạy cả Sentic-GCN và ASGCN | Thêm khoảng một ngày GPU, đổi lại tách bạch được đóng góp của cú pháp và của tri thức cảm xúc |

### 6.2. Cách hiểu "seed" đối với mô hình LLM

Với ba mô hình huấn luyện được, em chạy ba seed khác nhau để báo cáo giá trị trung bình kèm độ lệch chuẩn. Nhưng với LLM gọi qua API ở nhiệt độ 0, ba lần chạy cho kết quả gần như giống hệt nhau, nên độ lệch chuẩn sẽ bằng 0 — con số này **đúng về mặt tính toán nhưng gây hiểu lầm**, vì người đọc sẽ tưởng LLM là mô hình ổn định nhất trong bảng.

Em đề xuất: với zero-shot thì chạy một lần và ghi rõ là tất định (không báo độ lệch chuẩn); với few-shot thì chạy ba lần với **ba bộ ví dụ mẫu khác nhau**, và độ lệch chuẩn khi đó đo được một đại lượng có ý nghĩa thật là *độ nhạy của mô hình với việc chọn ví dụ*.

---

## 7. Chi phí và tính khả thi

Các con số dưới đây là **ước tính**, em sẽ đo thực tế và báo cáo lại ở mốc Tuần 8.

| Hạng mục | Ước tính |
|---|---|
| PhoBERT — 3 seed + dò 3 giá trị tốc độ học | 4 – 6 giờ GPU |
| Sentic-GCN — 3 seed + dò 3 giá trị tốc độ học | 6 – 8 giờ GPU |
| ViSoBERT — 3 seed + dò 3 giá trị tốc độ học | 4 – 6 giờ GPU |
| LLM — gọi API | 2 – 5 USD |
| **Tổng** | **khoảng 15 – 20 giờ GPU, trải từ Tuần 3 đến Tuần 7** |

Em dự kiến chạy trên Google Colab. Phần khung huấn luyện, đánh giá và cơ chế lưu/khôi phục tiến trình đã hoàn thành từ giai đoạn chuẩn bị.

Để bảo đảm so sánh công bằng, em áp dụng cùng một quy trình cho cả bốn mô hình: cùng cách chia dữ liệu, cùng bước tiền xử lý, cùng độ dài câu tối đa, cùng cách chọn điểm dừng theo tập kiểm định, và **cùng ngân sách dò siêu tham số** (mỗi mô hình được thử đúng ba giá trị tốc độ học). Em nghĩ điểm cuối cùng là quan trọng nhất, vì nếu dò nhiều cấu hình cho mô hình này mà ít cho mô hình kia thì bảng kết quả sẽ không còn ý nghĩa.

---

## 8. Phiếu ý kiến của Cô

**8.1. Về danh sách bốn mô hình baseline**

- [ ] Chấp thuận danh sách như đề xuất
- [ ] Chấp thuận nhưng cần **bớt**: ................................................................
- [ ] Chấp thuận nhưng cần **thêm**: ................................................................
- [ ] Cần trao đổi thêm

**8.2. Về vấn đề từ điển cảm xúc cho Sentic-GCN** *(mục 6.1)*

- [ ] Phương án A — thêm bước đo độ phủ từ điển
- [ ] Phương án B — thay bằng ASGCN
- [ ] Phương án C — chạy cả hai
- [ ] Ý kiến khác: ................................................................

**8.3. Về cách hiểu "seed" đối với LLM** *(mục 6.2)*

- [ ] Đồng ý với đề xuất của học viên
- [ ] Ý kiến khác: ................................................................

**8.4. Ý kiến khác của Cô**

.....................................................................................................

.....................................................................................................

.....................................................................................................

.....................................................................................................

**8.5. Về nhịp báo cáo tiến độ**

Em dự kiến báo cáo kết quả bốn baseline vào **Tuần 8**. Cô có muốn thêm mốc báo cáo nào không?

- [ ] Giữ nguyên một mốc ở Tuần 8
- [ ] Thêm mốc ở Tuần: ..................

---

Em xin chân thành cảm ơn Cô đã dành thời gian đọc và cho ý kiến.

*Tp. Hồ Chí Minh, ngày ...... tháng ...... năm 2026*

*Học viên*

*Nguyễn Minh Trọng*

---

*Ghi chú: Các mô hình được nhắc trong phiếu này gồm PhoBERT (Nguyen và Nguyen, 2020), Sentic-GCN (Liang và cộng sự, 2022), ViSoBERT (Nguyen và cộng sự, 2023). Trích dẫn đầy đủ theo chuẩn IEEE sẽ được kiểm chứng và bổ sung trong phần khảo sát ở Tuần 2.*
