# PHIẾU BÀN GIAO — [CD1.12j] Khảo sát: khi nào đồ thị đóng góp được trên mô hình ngôn ngữ tiền huấn luyện

Ngày 16/10/2026. Học viên hỏi: muốn chắc chắn đồ thị không giúp ích, hoặc tốt hơn là khảo sát các bài báo xem có cách nào
đồ thị đóng góp được không. Phiếu này đi cùng phiếu CD1.12i (phân tích) và notebook Kaggle đối chứng (đang chạy).

## 1. ĐÃ LÀM GÌ

- Tra 16 công trình bằng tìm kiếm có chủ đích (không phải tìm hệ thống theo giao thức ở `survey_protocol.md`), mỗi
  công trình đều kiểm được nơi đăng trên ACL Anthology, arXiv hoặc trang nhà xuất bản. Ba công trình đã có trong
  `survey_matrix.csv` (RGAT, DualGCN, HuLogicRules2016); mười ba công trình còn lại là mới.
- Chưa đọc toàn văn công trình mới nào. Mọi nhận định dưới đây lấy từ phần tóm tắt hoặc mô tả phương pháp; con số chỉ
  ghi khi tóm tắt nêu. Trước khi đưa vào báo cáo phải đọc toàn văn và kiểm từng con số (quy tắc 7).
- Không sửa ma trận khảo sát, bản nháp hay file Word.

## 2. CÂU TRẢ LỜI NGẮN

"Chắc chắn đồ thị không giúp" chỉ chứng minh được trong phạm vi hẹp: ba kiến trúc này, đồ thị từ VnCoreNLP, bài toán nhóm
khía cạnh, PhoBERT. Các lần chạy trên Kaggle sẽ làm phạm vi đó chắc hơn (5 seed, tách cách gộp khỏi GCN, gỡ fp16). Không
thí nghiệm nào chứng minh được "mọi loại đồ thị đều vô ích".

Tài liệu nói hai điều cùng lúc. Một, kết quả của chuyên đề **khớp** với các nghiên cứu đã có: cây phụ thuộc do bộ phân tích tự
động sinh ra thêm rất ít cho mô hình tiền huấn luyện. Hai, có năm hướng mà đồ thị đã cho thấy đóng góp, và cả năm đều nhắm
đúng những chỗ phân tích ở CD1.12i chỉ ra là đồ thị hiện tại đang thiếu.

## 3. BẰNG CHỨNG ĐỒ THỊ CÚ PHÁP TỰ ĐỘNG THÊM ÍT CHO MÔ HÌNH TIỀN HUẤN LUYỆN

| Công trình | Nơi đăng | Điều tìm thấy | Khớp với chuyên đề ở đâu |
|---|---|---|---|
| Dai, Yan, Sun, Liu, Qiu. Does syntax matter? A strong baseline for Aspect-based Sentiment Analysis with RoBERTa | NAACL 2021, tr. 1816–1829 | RoBERTa tinh chỉnh đơn thuần ngang hoặc hơn kết quả tốt nhất đã công bố trên sáu tập, bốn ngôn ngữ; cây suy từ RoBERTa tốt hơn cây của bộ phân tích khi đưa vào mô hình đồ thị | PhoBERT ngang ba mô hình đồ thị (Bảng 4.3, 4.4) |
| Sachan, Zhang, Qi, Hamilton. Do Syntax Trees Help Pre-trained Transformers Extract Information? | EACL 2021 | Cây cú pháp chỉ giúp khi là cây do người gán; với cây tự động, mức tăng nhỏ hoặc không có, kể cả với bộ phân tích chuyên miền | 55,4 % mẫu kiểm tra có đồ thị bị chia cắt; 24,8 % từ đổi cha khi ép phân tích cả bình luận (`force_single_parse_probe.json`) |
| Li và cộng sự. Dual Graph Convolutional Networks for ABSA (DualGCN, đã có trong ma trận) | ACL 2021, tr. 6319–6329 | Tự nêu: lợi ích của đồ thị phụ thuộc bị giới hạn bởi lỗi phân tích cú pháp và văn bản bình luận không trang trọng | Bình luận UIT-ViSFD viết không chuẩn hoá |
| Krishna, Jyothi, Iyyer. Revisiting the Importance of Encoding Logic Rules in Sentiment Classification | EMNLP 2018, tr. 4743–4751 | Khi lấy trung bình trên nhiều seed, chưng cất luật "A nhưng B" của Hu và cộng sự (2016) không còn cho lợi ích; ELMo tự học được hành vi giống luật | Cảnh báo trực tiếp cho NS-MGAT: luật tường minh có thể bị mô hình ngữ cảnh "nuốt" mất; cần nhiều seed |

Hai điều rút ra: (a) kết quả âm của chuyên đề không phải lỗi cài đặt hiếm gặp mà là hiện tượng đã được ghi nhận; (b) bài
học phương pháp của Krishna và cộng sự trùng với việc chuyên đề đang làm (thêm seed ở R2).

## 4. NĂM HƯỚNG ĐỒ THỊ ĐÃ ĐÓNG GÓP ĐƯỢC, ĐỐI CHIẾU VỚI CHỖ THIẾU CỦA CHUYÊN ĐỀ

### Hướng A. Neo đồ thị vào khía cạnh

Chỗ thiếu (CD1.12i, lý do 1): đồ thị giống hệt nhau cho mọi khía cạnh của một bình luận; ở câu trái cảm xúc (53,4 % mẫu)
không mô hình đồ thị nào hơn PhoBERT.

- Wang và cộng sự, R-GAT (ACL 2020, tr. 3229–3238; đã có trong ma trận): dựng lại cây phụ thuộc thành cây có gốc là khía
  cạnh rồi tỉa, mã hoá bằng graph attention có quan hệ; tác giả báo cáo cả GAT lẫn BERT đều tăng rõ.
- Li, Yin, Zhong, SCAN (arXiv 2010.01461; theo OpenAlex là chương sách Springer LNCS 2020, [CẦN TÌM: xác nhận NLPCC 2020]):
  đúng bài toán **nhóm khía cạnh**. Graph attention trên cây thành phần, một mô-đun phát hiện nhóm khía cạnh làm nhiệm vụ
  phụ, và một hàm mất mát tương tác đẩy mô-đun đó về các nút chỉ báo một nhóm duy nhất; mô-đun cảm xúc đọc từ các nút đó.
- Locate-Combine (NLPCC 2021, [CẦN TÌM: tác giả]; mã tại github.com/SCIR-MSA-Team/LC-ACSA): định vị cụm từ ứng với nhóm khía
  cạnh trước, rồi dùng GCN trên cây phụ thuộc lấy từ cảm xúc liên quan tới cụm đó.
- AC-MIMLLN (arXiv 2010.02656, [CẦN TÌM: nơi đăng]): coi mỗi câu là một túi từ, tìm các từ then chốt cho từng nhóm khía
  cạnh rồi gộp; không dùng đồ thị nhưng giải đúng bài toán neo.

Gợi ý cho NS-MGAT: thêm một **nút khía cạnh** nối vào các từ được định vị là thuộc nhóm đó (bằng attention của vế khía cạnh
hoặc bằng danh sách từ khoá theo nhóm), để đường truyền tin trên đồ thị khác nhau theo khía cạnh.

### Hướng B. Cạnh có loại

Chỗ thiếu (lý do 3): ASGCN bỏ nhãn quan hệ, "không" và "rất" là láng giềng như nhau.

- Tian, Chen, Song, T-GCN (NAACL 2021, tr. 2910–2922): đưa loại quan hệ phụ thuộc vào GCN, attention cân các cạnh theo
  loại, cộng một bộ gộp nhiều lớp; báo cáo kết quả tốt nhất trên sáu tập tiếng Anh.
- R-GAT ở hướng A cũng mã hoá loại quan hệ.

Gợi ý: đây là chỗ NS-MGAT đã định làm (cạnh logic có loại). Điểm mới cần thêm là phép gộp có tính toán tử (phủ định lật
cực, "nhưng" làm vế sau thắng), không chỉ trọng số khác nhau theo loại.

### Hướng C. Lấy cấu trúc từ chính PhoBERT thay vì bộ phân tích cú pháp

Chỗ thiếu: đồ thị từ VnCoreNLP bị chia cắt ở hơn nửa số mẫu và không ổn định.

- Dai và cộng sự (2021, mục 3): cây suy từ RoBERTa đã tinh chỉnh tốt hơn cây của bộ phân tích.
- Chen, Teng, Wang, Zhang, dotGCN (ACL 2022, tr. 2051–2064): cây ý kiến tiềm ẩn suy từ attention giữa khía cạnh và ngữ cảnh,
  không cần bộ phân tích, nhắm chính vào ngôn ngữ ít tài nguyên; cạnh tranh được trên sáu tập tiếng Anh và một tập tiếng Trung.
- Xiao, Wu, Chen, Deng, BERT4GCN (EMNLP 2021, tr. 9193–9200): dùng đầu ra các lớp giữa của BERT làm tín hiệu ngữ pháp cho GCN.

Gợi ý: thí nghiệm rẻ cho CĐ2 là thay đồ thị VnCoreNLP bằng đồ thị suy từ attention của PhoBERT, giữ nguyên mọi thứ khác.

### Hướng D. Đồ thị giữa các khía cạnh của cùng một bình luận

Chỗ thiếu: mỗi cặp (bình luận, khía cạnh) đang được dự đoán độc lập, trong khi trung bình một bình luận có 3,07 khía cạnh
và 53,4 % mẫu nằm trong bình luận có khía cạnh không cùng nhãn.

- Cai, Tu, Zhou, Yu, Xia, Hier-GCN (COLING 2020, tr. 833–843): đúng bài toán nhóm khía cạnh; GCN tầng dưới mô hình quan hệ
  giữa các nhóm khía cạnh, tầng trên mô hình quan hệ giữa nhóm khía cạnh và cảm xúc.
- Zhao, Hou, Wu, SDGCN (Knowledge-Based Systems, [CẦN TÌM: tập, trang]; arXiv 1906.04501): GCN trên các khía cạnh để mô hình
  phụ thuộc cảm xúc giữa chúng; tác giả báo cáo phụ thuộc giữa khía cạnh "rất có ích".
- Liang và cộng sự, InterGCN (COLING 2020): đồ thị dị loại gộp quan hệ hướng khía cạnh và quan hệ giữa các khía cạnh.

Gợi ý: đây là loại đồ thị khác hẳn đồ thị trên từ, và chưa được thử trong chuyên đề. Nó nhắm đúng nhóm câu trái cảm xúc.

### Hướng E. Đo ở chỗ đồ thị lẽ ra có ích

- Xing và cộng sự, ARTS (EMNLP 2020, tr. 3594–3605): tập kiểm tra thông thường không cho biết mô hình có tách được cảm xúc
  của khía cạnh đích khỏi khía cạnh khác không; trên tập kiểm tra độ bền ARTS, độ chính xác của chín mô hình giảm tới
  69,73 %.

Gợi ý: một phần đóng góp của đồ thị có thể không hiện trên toàn tập kiểm tra mà chỉ hiện trên tập kiểm tra khó. Chuyên đề
đã có tập chẩn đoán phủ định và chuyển ý; có thể thêm một tập kiểu ARTS cho tiếng Việt (đổi cảm xúc của khía cạnh không
phải đích, giữ khía cạnh đích) ở CĐ2.

## 5. Ý NGHĨA CHO HƯỚNG ĐỀ TÀI

NS-MGAT hiện đã có hướng B (cạnh logic có loại) và một phần hướng E (tập chẩn đoán). Thiếu hướng A (neo khía cạnh) thì đồ thị
logic cũng sẽ giống nhau cho mọi khía cạnh của một bình luận, và rất có thể gặp lại đúng kết quả âm của ASGCN. Hướng C và D
là hai thí nghiệm rẻ đáng thử trước khi dựng toàn bộ mô hình. Rủi ro cần nói thẳng với giảng viên hướng dẫn: Krishna và cộng
sự (2018) và Dai và cộng sự (2021) cho thấy mô hình ngữ cảnh có thể tự học những gì luật và cây cú pháp mang lại; thiết kế
thí nghiệm của CĐ2 phải để kết quả âm vẫn là một kết luận có giá trị (so với đối chứng như R1, nhiều seed, đo trên tập khó).

## 6. KIỂM CHỨNG

- Nơi đăng, số trang, tác giả: lấy từ trang ACL Anthology hoặc arXiv trả về khi tra; ba chỗ chưa xác nhận được ghi
  [CẦN TÌM].
- Đối chiếu ma trận: tìm theo tên trong `survey_matrix.csv` và các file `.md` của `chuyende1/survey/`; chỉ RGAT, DualGCN,
  HuLogicRules2016 có mặt (cả ba không nằm trong `khong_trinh_bay.csv`).
- Không con số nào trong phiếu này lấy từ bảng kết quả của các bài; chỉ từ tóm tắt.

## 7. DỪNG LẠI VÀ HỎI

1. Có đưa phần này vào báo cáo Chuyên đề 1 không? Nếu có, nên vào mục 4.7 hoặc Chương 5 (bàn luận) chứ không vào Chương 3,
   vì Chương 3 được viết như khảo sát 34 công trình; thêm công trình vào Chương 3 sẽ đổi Bảng 3.1 và các con số đếm.
2. Có thêm các công trình mới vào `survey_matrix.csv` (ghi rõ nguồn là tìm có chủ đích, ngày 16/10/2026) không?
3. Hướng C và D có đưa vào kế hoạch CĐ2 như hai thí nghiệm thử trước không?

Nguồn đã tra: aclanthology.org/2021.naacl-main.146, 2021.eacl-main.228, 2021.acl-long.494, D18-1505, P16-1228,
2020.acl-main.295, 2021.naacl-main.231, 2022.acl-long.145, 2021.emnlp-main.724, 2020.coling-main.72, 2020.coling-main.13,
2020.emnlp-main.292; arXiv 2010.01461, 2010.02656, 1906.04501; scholar.hit.edu.cn (Locate-Combine).

## 8. GHI CHÚ SAU KHI TRAO ĐỔI *(điền sau)*
