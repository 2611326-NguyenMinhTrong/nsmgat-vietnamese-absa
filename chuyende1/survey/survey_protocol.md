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
| N₁ — thu thập thô | **258** | 22/09/2026 | Cộng cột "Số kết quả" ở mục 6 (28 truy vấn: 111 đợt 2 + 147 đợt 3) |
| N₂ — sau khi loại trùng | **24** | 22/09/2026 | 11 bài đợt 2 + 13 bài đợt 3, không trùng nhau |
| N₃ — sau sàng tiêu đề + tóm tắt | **24** | 22/09/2026 | Cả 24 đều đúng phạm vi mục 4 sau khi đọc tiêu đề và tóm tắt |
| N₄ — sau đọc toàn văn (vào ma trận) | **xem `survey_tools.py stats`** | 22/09/2026 | `survey_tools.py stats` → dòng N4 |
| N₅ — phân tích sâu trong Chương 3 | **xem `survey_tools.py stats`** | 22/09/2026 | `survey_tools.py stats` → dòng N5 |

**Chỉ tiêu:** N₁ ≥ 70 · N₄ ≥ 45 · N₅ ≈ 25.

**Lưu ý về N₁:** công cụ tìm kiếm Claude Code dùng trả về **top kết quả hiển thị** (thường
9–10 dòng mỗi truy vấn), không phải tổng số trang như khung tìm kiếm của Google Scholar —
N₁ ở đây là tổng số dòng đã lướt qua, không phải tổng số bài tồn tại khớp truy vấn. Ghi rõ
để không hiểu nhầm là đã quét hết 111 bài.

**Vì sao N₄ (45) lớn hơn N₃ (24):** N₄ đếm mọi dòng đã kiểm chứng trong ma trận, gồm 24 dòng
đi qua phễu tìm kiếm có ghi log ở trên và 21 dòng "hạt giống" (tên lấy sẵn từ kế hoạch, không qua
bước tìm). Khi vẽ sơ đồ luồng ở mục 3.1 của báo cáo phải tách hai nhánh này ra, không được vẽ
như thể 45 bài cùng đi qua một phễu 249 kết quả.

Đợt 3 (22/09/2026) có 2 truy vấn chỉ để xác minh nơi công bố của một bài đã tìm thấy, không để
tìm bài mới — vẫn ghi vào bảng dưới cho đủ, cột "Số giữ lại" bằng 0.

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
| 22/09/2026 | Web search (Claude Code) | `"SemEval-2014 Task 4" "Aspect Based Sentiment Analysis" Pontiki authors venue` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"NRC-Canada-2014" Kiritchenko aspect sentiment SemEval feature SVM` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Target-dependent Twitter Sentiment Classification" Jiang authors ACL 2011` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Towards Generative Aspect-Based Sentiment Analysis" Zhang Li Deng authors ACL 2021` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Is ChatGPT a Good Sentiment Analyzer" Wang authors arxiv` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Instruction Tuning for Few-Shot Aspect-Based Sentiment Analysis" Varia authors venue` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `neuro-symbolic aspect-based sentiment analysis rule neural hybrid explainable paper` | 10 | 0 *(không có ứng viên mới rõ ràng, dẫn tới truy vấn tiếp theo)* |
| 22/09/2026 | Web search (Claude Code) | `"Neurosymbolic AI" "third wave" Garcez Lamb survey foundational paper` | 10 | 1 |
| 22/09/2026 | Web search (Claude Code) | `SemEval-2016 Task 5 "Aspect Based Sentiment Analysis" Pontiki authors venue` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `SemEval-2015 Task 12 "Aspect Based Sentiment Analysis" Pontiki authors venue` | 10 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Neuro-Symbolic Models for Sentiment Analysis" ICCS 2022 authors full` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"neural-symbolic" OR "neuro-symbolic" reasoning explainable NLP text classification survey authors venue 2021` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"VLSP Shared Task: Sentiment Analysis" Huyen Nguyen authors full list Journal Computer Science Cybernetics 2018` | 9 | 1 *(truy vấn gốc để xác minh tác giả VLSP-2018; giữ lại bài ABSA son môi tiếng Việt xuất hiện trong kết quả)* |
| 22/09/2026 | Web search (Claude Code) | `"A New Approach for Vietnamese Aspect-Based Sentiment Analysis" PhoBERT UIT-ViSFD 2022 authors` | 9 | 1 *(bài cần tìm nằm trên IEEE, không đọc được; giữ lại bài CTU xuất hiện trong kết quả)* |
| 22/09/2026 | Web search (Claude Code) | `"Harnessing Deep Neural Networks with Logic Rules" Hu ACL 2016 sentiment "but" rule` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Toward contextual valence shifters in Vietnamese reviews" authors ROCLING 2017` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Relational Graph Attention Network for Aspect-based Sentiment Analysis" Wang ACL 2020 authors` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Aspect-Level Sentiment Analysis Via Convolution over Dependency Tree" Sun EMNLP 2019` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"What's great and what's not: learning to classify the scope of negation for improved sentiment analysis" Councill` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"The Effect of Negators, Modals, and Degree Adverbs on Sentiment Composition" Kiritchenko Mohammad WASSA 2016` | 9 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Recursive Deep Models for Semantic Compositionality Over a Sentiment Treebank" Socher EMNLP 2013 negation` | 10 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Effective LSTMs for Target-Dependent Sentiment Classification" Tang COLING 2016` | 10 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Adaptive Recursive Neural Network for Target-dependent Twitter Sentiment Classification" Dong ACL 2014` | 10 | 1 |
| 22/09/2026 | Web search (Claude Code) | `"Vietnamese Sentiment Analysis: An Overview and Comparative Study of Fine-tuning Pretrained Language Models" authors` | 9 | 0 *(bài trên ACM, chưa tải được)* |
| 22/09/2026 | Web search (Claude Code) | `"Multi-task Solution for Aspect Category Sentiment Analysis on Vietnamese Datasets" authors venue` | 9 | 1 *(bài cần tìm trên IEEE; giữ lại bài "Is word segmentation necessary..." xuất hiện trong kết quả)* |
| 22/09/2026 | Web search (Claude Code) | `"Is word segmentation necessary for Vietnamese sentiment classification" Duc-Vu Nguyen conference published` | 9 | 0 *(xác minh nơi công bố)* |
| 22/09/2026 | Web search (Claude Code) | `"Is word segmentation necessary for Vietnamese sentiment classification" 2022 International Conference NICS OR KSE OR MAPR OR RIVF IEEE 10013874` | 9 | 0 *(xác minh nơi công bố; kết quả cuối lấy từ Crossref)* |
| 22/09/2026 | Web search (Claude Code) | `Moore Barnes 2021 "Multi-task Learning of Negation and Speculation for Targeted Sentiment Classification" NAACL` | 9 | 1 |

*(ví dụ, giữ lại để tham khảo định dạng)* 21/09/2026 · Google Scholar · `"aspect-based sentiment analysis" Vietnamese` · 47 · 6

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

**⚠️ Hiểu lầm thường gặp: đánh dấu `da_kiem_url` KHÔNG PHẢI chỉ cần xác nhận
tác giả/năm/nơi công bố.** `validate` đọc code ([`survey_tools.py`
dòng ~242](../../scripts/survey_tools.py)) bắt buộc: hễ `trang_thai` khác `chua_kiem` thì
**toàn bộ 19 cột của dòng đó phải điền xong hết**, không còn ô nào `[CẦN TÌM]` — kể cả
`ket_qua_tot_nhat`, `do_do_bao_cao`, `xu_ly_phu_dinh_chuyen_y`. Xác nhận xong tác giả/năm/nơi
công bố mà các ô nội dung khác vẫn còn `[CẦN TÌM]` thì **dòng đó vẫn phải để `chua_kiem`** —
xem ví dụ đầy đủ ở mục 7b ngay dưới đây.

`scripts/survey_tools.py table` **từ chối sinh bảng 3.9** nếu còn dòng `chua_kiem` được
chọn đưa vào bảng. Đây là chốt chặn kỹ thuật: không thể vô tình đưa một trích dẫn chưa
kiểm chứng vào cuốn báo cáo.

**Lệnh dùng hằng ngày khi khảo sát:**

```bash
python scripts/survey_tools.py validate   # cấu trúc file có hợp lệ không
python scripts/survey_tools.py stats      # tiến độ: phủ 6 nhóm tới đâu, kiểm chứng bao nhiêu
python scripts/survey_tools.py table      # sinh bảng 3.9 (chỉ từ dòng đã kiểm chứng)
```

## 7b. Ví dụ làm thật một dòng — `ASGCN`, ngày 22/09/2026

Ca này làm mẫu ngay trên dòng `ASGCN` trong `survey_matrix.csv`, giữ nguyên vết để bạn đối
chiếu. Ba bước đã xảy ra đúng theo thứ tự:

**Bước 1 — Tìm nguồn gốc.** Gõ tên + vài từ khoá đặc trưng lên Google Scholar /
ACL Anthology: `"Aspect-based Sentiment Classification with Aspect-specific Graph
Convolutional Networks" Zhang EMNLP 2019`. Ra đúng một kết quả khớp.

**Bước 2 — Mở trực tiếp trang gốc (không tin vào kết quả tìm kiếm).** Mở
`https://aclanthology.org/D19-1464/` — đây là trang chính thức của kỷ yếu hội nghị, không
phải trang thứ ba. Đọc được: tiêu đề đầy đủ, ba tác giả (Chen Zhang, Qiuchi Li, Dawei Song),
nơi công bố EMNLP-IJCNLP 2019. Mở thêm kho mã nguồn `github.com/GeneZC/ASGCN` (repo tự giới
thiệu là "Code ... for EMNLP 2019 paper" — tự nhận đúng là mã của bài này) để xác nhận
`co_ma_nguon = co`.

→ Đến đây, 5 ô đã điền chắc chắn: `tieu_de`, `nam`, `hoi_nghi_tap_chi`, `nguon_url`,
`co_ma_nguon`.

**Bước 3 — Thử điền nốt các ô nội dung, và PHÁT HIỆN chưa đủ.** README của kho mã nguồn chỉ
nhắc tới tập `rest14`, không liệt kê đủ **ba** tập benchmark bài báo dùng, và không có bảng
kết quả. Tức là 6 ô còn lại — `bieu_dien_dau_vao`, `tap_du_lieu`, `do_do_bao_cao`,
`ket_qua_tot_nhat`, `xu_ly_phu_dinh_chuyen_y`, `co_giai_thich` — **không thể điền có trách
nhiệm** nếu chỉ đọc tóm tắt và README. Phải mở PDF, đọc mục Model và Experiments.

**Kết quả:** dòng `ASGCN` vẫn giữ `trang_thai = chua_kiem` — dù đã xác nhận được nguồn gốc
thật, dòng này **chưa đủ điều kiện** gọi là "đã kiểm chứng" theo định nghĩa của công cụ.
5 ô đã điền chắc vẫn giữ nguyên (không phải làm lại), chỉ còn việc đọc toàn văn để điền nốt
6 ô kia rồi mới đổi `trang_thai` thành `da_kiem_url` (hoặc `da_doc_toan_van` nếu đọc sâu
luôn, vì phần lớn công sức đọc PDF cho `da_kiem_url` và `da_doc_toan_van` trùng nhau — lên
hẳn `da_doc_toan_van` thường không tốn thêm nhiều).

**Bài học rút ra:** "kiểm chứng" không phải một hành động, mà là một **ngưỡng** — dòng chỉ
qua ngưỡng khi *toàn bộ* thông tin cần thiết đã có, không phải khi phần dễ nhất (tên tác giả)
đã xong. `validate` chính là người trông ngưỡng đó, không phải trí nhớ hay cảm giác "chắc là
xong rồi".

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
| `tieu_de` | Tiêu đề đầy đủ, **chép nguyên văn** từ nguồn gốc — dùng dựng danh mục tài liệu tham khảo | Tự do. Không tự dịch, không viết tắt |
| `trang_thai` | Mức kiểm chứng — xem mục 7 | `chua_kiem` · `da_kiem_url` · `da_doc_toan_van` |
| `nam` | Năm công bố | 4 chữ số |
| `hoi_nghi_tap_chi` | Nơi công bố. Chỉ có tiền ấn phẩm thì ghi `arXiv` | Tự do. VD `EMNLP 2020` |
| `ho_phuong_phap` | Nhóm phương pháp của Chương 3 | `G1_co_dien` · `G2_tuan_tu_attention` · `G3_plm` · `G4_do_thi` · `G5_sinh_prompting` · `G6_neuro_symbolic` · `TAI_NGUYEN` |
| `bieu_dien_dau_vao` | **Công trình biến văn bản thành số bằng cách nào** trước khi mô hình lập luận | Bắt đầu bằng một mã (bảng dưới), chi tiết trong ngoặc |
| `co_dung_do_thi` | Mô hình có dùng đồ thị không | `co` · `khong` |
| `loai_do_thi` | Loại đồ thị | `cu_phap` · `ngu_nghia` · `tri_thuc` · `khac` · **để trống** nếu `co_dung_do_thi = khong` |
| `co_tri_thuc_ngoai` | Có dùng tri thức ngoài dữ liệu huấn luyện không (từ điển cảm xúc, SenticNet, ontology) | `co` · `khong` |
| `ngon_ngu` | Ngôn ngữ thực nghiệm | `vi` · `en` · `da_ngu` · `khac` (một ngôn ngữ đơn khác, vd tiếng Ba Lan — ghi rõ tên ngôn ngữ trong `ghi_chu`; thêm 22/09/2026) |
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

**Cách phân biệt 5 mã — hai câu hỏi liên tiếp, hỏi đúng thứ tự:**

```
Câu hỏi 1: Từ có đi qua một vector HỌC ĐƯỢC (embedding layer), hay chỉ bị đếm/tra bảng?

  Chỉ đếm / tra bảng có sẵn (không có embedding layer nào)
  ├─ Đếm tần suất từ/cụm từ, KHÔNG quan tâm nghĩa cảm xúc  → dac_trung_thu_cong
  │    (BoW, TF-IDF, n-gram, đếm POS)
  └─ Tra bảng ĐIỂM CẢM XÚC có sẵn cho từng từ              → tu_dien_cam_xuc
       (vd "tốt"=+1, "tệ"=−1 — như baseline `lexicon` của đề tài)

  Có vector/embedding học được, đưa vào mạng sâu hơn (LSTM/CNN/Transformer)
  └─ Câu hỏi 2: "Từ 'pin' ở hai câu khác nhau — vector của nó có
     giống hệt nhau không?"
     ├─ CÓ, luôn giống hệt dù câu khác nhau     → embedding_tinh
     │    (GloVe/word2vec/fastText TIỀN HUẤN LUYỆN, hay cả khởi tạo
     │    ngẫu nhiên rồi tự học — "tĩnh" nghĩa là KHÔNG đổi theo câu,
     │    không phải "không tiền huấn luyện")
     └─ KHÔNG, đổi tuỳ câu chứa nó               → embedding_ngu_canh
          (dấu hiệu chắc chắn: một Transformer tiền huấn luyện kiểu
          BERT/PhoBERT/ViSoBERT chạy cả câu qua rồi mới ra vector từng từ)

Không khớp cái nào ở trên (đồ thị cú pháp thuần không kèm vector từ, ảnh, âm thanh...)
└─ khac — PHẢI giải thích rõ trong ngoặc VÀ trong `ghi_chu`
```

**Bẫy hay gặp nhất: lẫn `embedding_tinh` với `embedding_ngu_canh` theo "có tiền huấn luyện
hay không".** Sai — phải hỏi đúng câu hỏi 2 ở trên ("vector có đổi theo câu không"), không
phải "có tải sẵn trọng số không". GloVe là tiền huấn luyện nhưng vẫn **tĩnh**.

**Ví dụ làm thật — `ATAE-LSTM` (Wang et al., EMNLP 2016), 22/09/2026:** đọc được (qua 2 nguồn
phụ vì không mở trực tiếp được PDF gốc trong phiên đó) mô hình nối vector khía cạnh vào
**từng** vector từ GloVe rồi mới đưa vào LSTM. GloVe không đổi theo câu chứa nó → câu hỏi 1
"có embedding không" = có, câu hỏi 2 "vector có đổi theo câu không" = không →

```
embedding_tinh (GloVe, mức từ, nối thêm vector khía cạnh)
```

Xem dòng `ATAE-LSTM` thật trong `survey_matrix.csv` — 5 ô đã điền chắc, còn 6 ô
`[CẦN TÌM]` (kể cả `co_ma_nguon`: tìm được vài bản GitHub nhưng đều do **người khác** viết
lại, không phải tác giả gốc tự công bố — nên KHÔNG được đánh `co`, phải để `[CẦN TÌM]` cho
tới khi xác nhận được tác giả có công bố mã hay không).

### Hai dòng chú thích trong file CSV

`survey_matrix.csv` có hai dòng đầu là `#MO_TA` (mô tả từng cột) và `#VI_DU` (một dòng điền
mẫu, **số liệu bịa**). Mọi dòng có `ref_key` bắt đầu bằng `#` đều bị các công cụ bỏ qua:
không tính vào thống kê, không lọt vào Bảng 3.9. **Đừng xoá chúng** — đó là chỗ tra nhanh
khi đang điền, và chúng đi theo cả vòng xuất/nhập Excel.
