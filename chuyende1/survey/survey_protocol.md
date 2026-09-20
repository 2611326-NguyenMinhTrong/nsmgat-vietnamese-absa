# GIAO THỨC KHẢO SÁT SOTA — `[CD1.2]`

> **Trạng thái:** giao thức đã chốt (27/08/2026). Mục 5 và 6 điền dần khi tìm.
> Đặc tả: `pLan/chuyende1/PLAN_CHUYENDE1.md` mục 5 → CD1.2.
>
> ⚠️ Giao thức này viết **trước** khi tìm bài. Khảo sát có giao thức viết trước là thứ
> phân biệt khảo sát khoa học với danh sách bài đọc ngẫu nhiên — và hội đồng sẽ hỏi
> "em tìm bằng cách nào".

## 1. Câu hỏi khảo sát

| Mã | Câu hỏi | Trả lời ở mục nào của báo cáo |
|---|---|---|
| CH1 | Các họ phương pháp nào đang là SOTA cho ABSA/ACSA, ưu–nhược từng họ? | 3.2 – 3.7 |
| CH2 | Riêng tiếng Việt đã có gì? Tập dữ liệu nào, kết quả đến đâu? | 3.8 |
| CH3 | Phủ định và chuyển ý được xử lý ra sao trong các công trình đó? | 3.9 (cột `xu_ly_phu_dinh_chuyen_y`) |
| CH4 | Khoảng trống nào còn đủ lớn để làm luận văn? | 3.10 |

CH3 là câu hỏi **riêng của đề tài này** — nó không có trong khảo sát ABSA thông thường.
Chính nó biến ma trận khảo sát thành bằng chứng cho Chương 5, chứ không chỉ là phần "nền".

## 2. Nguồn tìm kiếm

| Nguồn | Vai trò |
|---|---|
| ACL Anthology | Chính, cho NLP quốc tế. Ưu tiên vì có toàn văn miễn phí và metadata chuẩn |
| IEEE Xplore, Scopus | Tạp chí kỹ thuật |
| arXiv | Bài mới chưa qua phản biện — **đánh dấu riêng** ở cột `ghi_chu`, dùng thận trọng |
| Google Scholar | Truy vết trích dẫn xuôi/ngược từ các bài hạt giống |
| VLSP, RIVF, KSE, NAFOSTED | Hội nghị trong nước — nguồn chính cho CH2 |

**Chiến lược:** bắt đầu từ ~8 bài hạt giống đã biết tên (xem `survey_matrix.csv`), rồi
truy vết trích dẫn hai chiều. Cách này phủ tốt hơn là chỉ gõ từ khoá, vì thuật ngữ trong
lĩnh vực không thống nhất (ABSA / ATSC / ACSA / targeted sentiment).

## 3. Từ khoá

**Tiếng Anh**

```
"aspect-based sentiment analysis"
"aspect category sentiment analysis"
"aspect sentiment triplet extraction"
"ABSA graph neural network"
"syntax-aware aspect sentiment"
"dependency tree sentiment classification"
"affective knowledge sentiment graph"
"Vietnamese sentiment analysis"
"Vietnamese pre-trained language model"
"neuro-symbolic sentiment analysis"
"negation scope sentiment"
"contrastive discourse marker sentiment"
```

**Tiếng Việt**

```
"phân tích cảm xúc theo khía cạnh"
"phân tích quan điểm tiếng Việt"
"phân tích cảm xúc mức khía cạnh"
"xử lý phủ định tiếng Việt"
```

**Kết hợp:** mỗi từ khoá nhóm phương pháp × mỗi từ khoá ngôn ngữ, để không bỏ sót các
công trình áp dụng phương pháp quốc tế cho tiếng Việt.

## 4. Tiêu chí nhận / loại

**Nhận** khi thoả **cả ba**:

1. Có thực nghiệm định lượng, nêu rõ tập dữ liệu và độ đo;
2. Công bố ở hội nghị/tạp chí có phản biện — **hoặc** là mô hình nền tảng tiếng Việt được
   dùng rộng rãi (PhoBERT, ViSoBERT…) kể cả khi công bố ở arXiv;
3. Thuộc phạm vi: ABSA/ACSA, hoặc phân tích cảm xúc tiếng Việt, hoặc phương pháp
   neuro-symbolic cho phân loại văn bản.

**Loại** khi thuộc **bất kỳ** trường hợp nào:

1. Báo cáo kỹ thuật/blog không qua phản biện và không phải mô hình nền tảng;
2. Trùng lặp — giữ bản mới nhất, ghi bản cũ vào `ghi_chu`;
3. Không nêu rõ tập dữ liệu hoặc độ đo → không đưa vào bảng so sánh được;
4. Chỉ phân loại cảm xúc mức tài liệu/câu, không có khái niệm khía cạnh — **trừ khi** bài
   đó bàn riêng về phủ định hoặc chuyển ý (liên quan CH3).

Ngoại lệ ở mục 4 là có chủ ý: một bài về phạm vi phủ định trong phân loại cảm xúc mức câu
vẫn có giá trị cho Chương 5, dù không phải ABSA.

## 5. Quy trình sàng lọc — năm con số N₁…N₅

**Đây là gì:** năm con số kể lại *bạn đã đi từ "gõ từ khoá" tới "45 bài trong ma trận" bằng
đường nào*. Chúng dựng thành sơ đồ luồng ở mục 3.1 của báo cáo.

**Vì sao hội đồng quan tâm:** câu hỏi kinh điển là *"sao em chọn đúng 45 bài này mà không
phải 45 bài khác?"*. Không có năm con số này thì câu trả lời chỉ là "em tìm được bấy nhiêu"
— nghe như đọc ngẫu nhiên. Có chúng thì đó là một **quy trình lặp lại được**: người khác gõ
đúng truy vấn của bạn sẽ ra kết quả tương đương. Đó là ranh giới giữa "khảo sát có phương
pháp" và "danh sách bài báo".

Cứ hình dung như một cái phễu — mỗi bước bỏ bớt một số bài, và bạn phải nói được **bỏ vì lý
do gì**:

| Con số | Nghĩa | Bỏ bớt vì | Bạn ghi ở đâu |
|---|---|---|---|
| **N₁** — thu thập thô | Tổng số kết quả **mọi lần tìm** cộng lại, chưa lọc gì | — | Cộng cột "Số kết quả" của mục 6 |
| **N₂** — sau khi loại trùng | Cùng một bài hiện ra ở nhiều truy vấn / nhiều nguồn thì chỉ tính **một** | Trùng lặp | Tự đếm, ghi vào bảng dưới |
| **N₃** — sau sàng tiêu đề + tóm tắt | Chỉ đọc **tiêu đề và tóm tắt**, loại bài lạc đề | Không thuộc phạm vi mục 4 | Tự đếm, ghi vào bảng dưới |
| **N₄** — vào ma trận | Đã **mở nguồn gốc**, xác nhận tác giả/năm/nơi công bố, điền đủ các ô | Không kiểm chứng được nguồn | `survey_tools.py stats` tự đếm |
| **N₅** — phân tích sâu | Đã **đọc toàn văn**, hiểu phương pháp và kết quả | Chỉ cần nhắc tên, không cần đào sâu | `survey_tools.py stats` tự đếm |

Phễu đi xuống dần: N₁ ≥ N₂ ≥ N₃ ≥ N₄ ≥ N₅.

| Bước | Số bài | Ngày | Cách lấy số |
|---|---|---|---|
| N₁ — thu thập thô | | | Cộng cột "Số kết quả" ở mục 6 |
| N₂ — sau khi loại trùng | | | Tự đếm khi gộp kết quả các truy vấn |
| N₃ — sau sàng tiêu đề + tóm tắt | | | Tự đếm sau khi đọc tiêu đề/tóm tắt |
| N₄ — sau đọc toàn văn (vào ma trận) | **1** | 20/09/2026 | `survey_tools.py stats` → dòng N4 |
| N₅ — phân tích sâu trong Chương 3 | **1** | 20/09/2026 | `survey_tools.py stats` → dòng N5 |

**Chỉ tiêu:** N₁ ≥ 70 · N₄ ≥ 45 · N₅ ≈ 25.

**Hiện tại N₄ = N₅ = 1** vì mới `UIT-ViSFD` được kiểm chứng (20/09/2026). Ba con số đầu còn
trống vì **chưa ai ghi nhật ký tìm kiếm ở mục 6** — 21 dòng còn lại trong ma trận là tên bài
lấy sẵn từ kế hoạch, không phải kết quả của một lần tìm có ghi lại.

> **Việc của học viên:** mỗi lần ngồi tìm bài, ghi một dòng vào bảng mục 6 **ngay lúc tìm**.
> N₁ chính là tổng cột "Số kết quả" của bảng đó. Ghi lại từ trí nhớ sau một tuần thì con số
> không còn đáng tin, mà hội đồng lại hỏi đúng những con số này.

**Việc của Claude Code:** cập nhật hai dòng N₄ / N₅ trong bảng trên (chạy
`survey_tools.py stats`, chép số vào) mỗi khi kiểm chứng xong một bài.

## 6. Nhật ký tìm kiếm — điền ngay khi tìm

Ghi **ngay lúc đang tìm**, không ghi lại từ trí nhớ. Cột "Truy vấn nguyên văn" phải chép
**đúng chuỗi đã gõ**, kể cả dấu ngoặc kép — để người khác gõ lại ra kết quả tương đương.

| Ngày | Nguồn | Truy vấn nguyên văn | Số kết quả | Số giữ lại |
|---|---|---|---|---|
| *(ví dụ)* 21/09/2026 | Google Scholar | `"aspect-based sentiment analysis" Vietnamese` | 47 | 6 |
| | | | | |

- **Nguồn:** ACL Anthology · IEEE Xplore · Scopus · arXiv · Google Scholar · VLSP · RIVF · KSE
- **Số kết quả:** con số trang tìm kiếm hiện ra (nếu quá lớn thì ghi số bạn thực sự lướt qua,
  và ghi rõ trong ngoặc, ví dụ `312 (chỉ xét 50 đầu)`)
- **Số giữ lại:** số bài bạn thấy đáng xem tiếp sau khi liếc tiêu đề

Xoá dòng *(ví dụ)* khi bắt đầu ghi dòng thật.

## 7. Quy trình kiểm chứng — chống bịa trích dẫn

Quy tắc số 7 của repo cấm bịa trích dẫn. Ở đây quy tắc đó được **cưỡng chế bằng công cụ**,
không dựa vào trí nhớ.

Mỗi dòng trong `survey_matrix.csv` có cột `trang_thai` với đúng ba giá trị:

| Giá trị | Nghĩa | Được dùng ở đâu |
|---|---|---|
| `chua_kiem` | Mới có tên bài, chưa mở nguồn | Không được trích dẫn trong báo cáo |
| `da_kiem_url` | Đã mở trang gốc, xác nhận tác giả / năm / nơi công bố | Được đưa vào bảng 3.9 |
| `da_doc_toan_van` | Đã đọc hết bài, hiểu phương pháp và kết quả | Được phân tích sâu ở mục 3.2 – 3.8 |

Trường nào chưa xác minh được thì ghi `[CẦN TÌM: ...]`, **không đoán, không để trống**.

`scripts/survey_tools.py table` **từ chối sinh bảng 3.9** nếu còn dòng `chua_kiem` được
chọn đưa vào bảng. Đây là chốt chặn kỹ thuật: không thể vô tình đưa một trích dẫn chưa
kiểm chứng vào cuốn báo cáo.

**Lệnh dùng hằng ngày khi khảo sát:**

```bash
python scripts/survey_tools.py validate   # cấu trúc file có hợp lệ không
python scripts/survey_tools.py stats      # tiến độ: phủ 6 nhóm tới đâu, kiểm chứng bao nhiêu
python scripts/survey_tools.py table      # sinh bảng 3.9 (chỉ từ dòng đã kiểm chứng)
```

## 8. Bài báo quan trọng — gắn cờ bắt buộc đọc kỹ

Ngoài kiểm chứng để đưa vào Bảng 3.9, một số ít công trình (5–10 bài) quan trọng hơn hẳn
phần còn lại — loại mà nếu bảo vệ bị hỏi sâu mà không trả lời được thì mất điểm ngay. Những
bài đó được theo dõi riêng ở
[`chuyende1/survey/doc_bat_buoc.md`](doc_bat_buoc.md).

Quy tắc gắn cờ và tiêu chí "quan trọng": xem `README.md` mục "Quy định riêng của học viên"
phần D. Tóm tắt: mỗi khi phát hiện một bài như vậy, phải (1) thêm vào `doc_bat_buoc.md`,
(2) thêm dòng vào ma trận này nếu chưa có, (3) **nói rõ ngay trong câu trả lời** và yêu cầu
học viên đọc kỹ — không âm thầm thêm vào rồi đi tiếp.

## 9. Từ điển cột — điền ô nào nghĩa là gì

> Ba nơi nói cùng một điều, cố ý: mục này (đầy đủ), hai dòng `#MO_TA` / `#VI_DU` ngay trong
> `survey_matrix.csv` (tra nhanh khi đang điền), và `survey_tools.py validate` (cưỡng chế).
> Đổi từ vựng ở đây thì phải đổi cả ba.

| Cột | Nghĩa | Giá trị hợp lệ |
|---|---|---|
| `ref_key` | Khoá trích dẫn ngắn, **duy nhất**, dùng xuyên suốt báo cáo | Tự do, không dấu cách. VD `ASGCN` |
| `trang_thai` | Mức kiểm chứng — xem mục 7 | `chua_kiem` · `da_kiem_url` · `da_doc_toan_van` |
| `nam` | Năm công bố | 4 chữ số |
| `hoi_nghi_tap_chi` | Nơi công bố. Chỉ có tiền ấn phẩm thì ghi `arXiv` | Tự do. VD `EMNLP 2020` |
| `ho_phuong_phap` | Nhóm phương pháp của Chương 3 | `G1_co_dien` · `G2_tuan_tu_attention` · `G3_plm` · `G4_do_thi` · `G5_sinh_prompting` · `G6_neuro_symbolic` · `TAI_NGUYEN` |
| `bieu_dien_dau_vao` | **Công trình biến văn bản thành số bằng cách nào** trước khi mô hình lập luận | Bắt đầu bằng một mã (bảng dưới), chi tiết trong ngoặc |
| `co_dung_do_thi` | Mô hình có dùng đồ thị không | `co` · `khong` |
| `loai_do_thi` | Loại đồ thị | `cu_phap` · `ngu_nghia` · `tri_thuc` · `khac` · **để trống** nếu `co_dung_do_thi = khong` |
| `co_tri_thuc_ngoai` | Có dùng tri thức ngoài dữ liệu huấn luyện không (từ điển cảm xúc, SenticNet, ontology) | `co` · `khong` |
| `ngon_ngu` | Ngôn ngữ thực nghiệm | `vi` · `en` · `da_ngu` |
| `tap_du_lieu` | Tập dữ liệu thực nghiệm chính | Tự do, nhiều tập ngăn bằng `+` |
| `do_do_bao_cao` | Độ đo bài báo dùng — **ghi rõ macro hay micro** | Tự do. VD `accuracy, macro-F1` |
| `ket_qua_tot_nhat` | Con số tốt nhất **kèm tập đạt được** | Tự do. VD `acc 85,2 / macro-F1 78,4 (Restaurant)` |
| `xu_ly_phu_dinh_chuyen_y` | Bài có xử lý phủ định / chuyển ý không — câu hỏi khảo sát CH3 | `co` · `khong` · `mot_phan` |
| `co_giai_thich` | Mô hình có đưa ra giải thích cho dự đoán không | `co` · `khong` |
| `co_ma_nguon` | Có công khai mã nguồn không | `co` · `khong` |
| `nguon_url` | Link bản gốc — DOI, arXiv hoặc ACL Anthology | Bắt buộc khi `trang_thai` khác `chua_kiem` |
| `ghi_chu` | Tự do | Ghi cả **cách kiểm chứng** một ô khó |

Ô chưa biết thì ghi `[CẦN TÌM]` — không đoán, không để trống (trừ `loai_do_thi` như trên).

### Mã của `bieu_dien_dau_vao`

Đây là trục chia sáu nhóm phương pháp, nên phải điền nhất quán mới so sánh được.

| Mã | Đầu vào thực chất của mô hình | Ví dụ |
|---|---|---|
| `dac_trung_thu_cong` | Đếm từ: BoW, TF-IDF, n-gram | SVM / Naive Bayes trong bài UIT-ViSFD |
| `tu_dien_cam_xuc` | Điểm cảm xúc tra sẵn của từng từ | Baseline `lexicon` của đề tài |
| `embedding_tinh` | Mỗi từ (hoặc subword) **một vector cố định**, không đổi theo ngữ cảnh — dù là tiền huấn luyện (fastText, word2vec, GloVe) hay học từ đầu | Bi-LSTM của bài UIT-ViSFD · baseline `bilstm` của đề tài |
| `embedding_ngu_canh` | Vector của một từ **đổi theo câu chứa nó** — mô hình tiền huấn luyện | PhoBERT, ViSoBERT, BERT |
| `khac` | Không rơi vào bốn loại trên | Ghi rõ trong ngoặc và trong `ghi_chu` |

Chi tiết viết trong ngoặc, gồm **tên cụ thể** và **mức chia**:

```
embedding_tinh (fastText, mức từ)
embedding_tinh (học từ đầu, subword PhoBERT, 300 chiều)
embedding_ngu_canh (PhoBERT-base-v2, subword)
```

**Đừng trộn kiến trúc vào ô này.** `embedding + BiLSTM` là một giá trị sai: `BiLSTM` là mô
hình, thuộc cột `ho_phuong_phap`. Lỗi này đã xảy ra thật — xem GAP-016.

### Hai dòng chú thích trong file CSV

`survey_matrix.csv` có hai dòng đầu là `#MO_TA` (mô tả từng cột) và `#VI_DU` (một dòng điền
mẫu, **số liệu bịa**). Mọi dòng có `ref_key` bắt đầu bằng `#` đều bị các công cụ bỏ qua:
không tính vào thống kê, không lọt vào Bảng 3.9. **Đừng xoá chúng** — đó là chỗ tra nhanh
khi đang điền, và chúng đi theo cả vòng xuất/nhập Excel.
