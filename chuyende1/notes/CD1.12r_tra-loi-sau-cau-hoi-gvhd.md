# PHIẾU BÀN GIAO — [CD1.12r] Trả lời sáu câu hỏi của giảng viên hướng dẫn trong báo cáo

**Ngày:** 31/10/2026 · **Step:** CD1.12 (viết báo cáo) · **Thời gian thực tế:** khoảng nửa ngày

Học viên chuyển sáu câu hỏi của giảng viên và yêu cầu: "đưa ra giải pháp tối ưu nhất và thực hiện chỉnh sửa theo từng yêu cầu cho tốt
nhất". Phát hiện gốc ghi ở GAP-045.

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `scripts/phan_tich_bo_sung.py` + `tests/test_phan_tich_bo_sung.py` | Tạo | Ba phép đo mới, chỉ đọc dự đoán đã có: loại lỗi theo nhóm, phần lỗi và mức tăng tối đa, vì sao đồ thị không giúp; 7 test |
| `results/phan_tich_bo_sung.json` | Tạo | Kết quả, 10.000 lần bootstrap, seed 42 |
| `chuyende1/report/nhap_rut_gon/Chuong5_HanCheVaDinhHuong.md` (không push) | Sửa | Viết lại 5.2, thêm 5.4, đổi 5.4 cũ thành 5.5, tách 5.5 cũ thành 5.6.1 đến 5.6.3, thêm Bảng 5.1 và 5.3, Bảng 5.1 cũ thành 5.2 |
| `.../Chuong4_ThucNghiem.md` (không push) | Sửa | Mục 4.1.1 thêm hai đoạn, mục 4.1.2 thêm cách dựng và tiêu chí, câu cuối mục 4.7 |
| `.../Chuong6_KetLuan.md`, `Chuong1_TongQuan.md`, `TrangDau.md`, `tai_lieu.json` (không push) | Sửa | Chương 6 nối sang 5.4, 5.6, mục 6.3 việc 6 bỏ "nếu còn điều kiện"; mục 1.5; câu cuối Tóm tắt; thêm tài liệu Dai 2021 |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` (không push) | Sửa | Ghép `--chi 5 6 tai_lieu --ghi-de`; sửa Chương 1, Chương 4, Tóm tắt, hai số tài liệu ở Bảng A.1 bằng COM; cập nhật mục lục; lưu 13:09:02 ngày 31/10, 79 trang |
| `scripts/doi_chieu_chuong4.py`, `doi_chieu_chuong5.py`, `doi_chieu_chuong6.py` + test | Sửa | Chỗ kiểm cho mọi số, ví dụ, nhận định mới; chứng cứ nguyên văn của Dai, DualGCN, Moore |
| `chuyende1/survey/survey_matrix.csv`, `khong_trinh_bay.csv`, `survey_protocol.md` | Sửa | Dòng `DaiDoesSyntaxMatter2021` (58 dòng, Bảng A.1 vẫn 34 công trình), nhật ký tìm |
| `chuyende1/gaps/GAP-045_...md`, `INDEX.md`, `chuyende1/MODULE.md`, `SO_TAY_LENH.md` (chỉ ở máy), `pLan/chuyende1/progress_cd1.md` | Tạo, sửa | Sổ sách |

Sao lưu: bản nháp ở `nhap_rut_gon/sao_luu/20261031-yeu-cau-gvhd/`; khảo sát ở `chuyende1/survey/sao_luu_20261031/`; Word ở
`..._rutgon.20261031-truoc-yeu-cau-gvhd.docx.bak` (trước mọi thay đổi, trùng mã băm file lưu 24/10), `..._rutgon.20261031-130854.docx.bak`
(lệnh ghép tự sao lưu), `..._rutgon.20261031-sau-ghep-truoc-com.docx.bak` (sau ghép, trước COM). Trong `data/cache/nguon_goc/` còn hai
file `SachanSyntaxTrees2021.*` đã tải nhưng không dùng (bài về trích xuất thông tin, đã bỏ).

---

## 2. ĐỂ LÀM GÌ

- **Vấn đề:** báo cáo nói "đây là căn cứ" cho hướng đề tài mà số đo không đỡ nổi, và thiếu tiêu chí, lý do mà hội đồng chắc chắn hỏi.
- **Sau step này:** mỗi câu hỏi có một chỗ trả lời trực tiếp trong báo cáo, kèm số chạy lại được.

---

## 3. CƠ CHẾ

| Câu của giảng viên | Trả lời | Ở đâu |
|---|---|---|
| 1. Cơ sở chọn Neuro-Symbolic Multi-Graph | Số đo không chứng minh hướng này tốt hơn; giữ như giả thuyết với ba lập luận và Bảng 5.3 theo từng thành phần. Hai trong ba đồ thị chưa có căn cứ, nên đa đồ thị là khung thí nghiệm, chưa phải kiến trúc đã chốt | 5.6.1 |
| 2. Căn cứ nào cho việc mô hình hoá tường minh | Tiền đề chỉ đúng một phần: hai hiện tượng chiếm khoảng 46 % số lỗi. Ba loại căn cứ gián tiếp, không cùng chiều; năm điều kiện kiểm chứng đặt trước | 5.6.2 |
| 3. Dựng tập chẩn đoán, tiêu chí | Hai bước, bốn tiêu chí kèm phép thử, ví dụ thật, các trường hợp loại trừ | 4.1.2 |
| 4. Vì sao chỉ UIT-ViSFD | Hai lý do chọn; đối chiếu từng tập ở Bảng 3.3; thừa nhận chưa đánh giá tổng quát hoá; chuyển VLSP 2018 sang Chuyên đề 2 | 4.1.1, 6.2, 6.3 |
| 5. Vì sao ASGCN, Sentic-GCN chưa hiệu quả | Sáu cách giải thích xếp theo độ chắc của bằng chứng; chưa thể quy cho tiếng Việt | 5.4 |
| 6. Lỗi phổ biến nhất của PhoBERT, ví dụ | Đoán có cực cho mẫu trung tính; Bảng 5.1, ba ví dụ mỗi nhóm một mẫu | 5.2 |

Cách tính mức tăng tối đa ở câu 2, ví dụ một ô: ô (có từ phủ định, nhãn tiêu cực) có 719 mẫu trên tập kiểm tra, tập chẩn đoán rút 84
dòng, mỗi dòng đại diện cho khoảng 8,6 mẫu. Với mỗi dòng có hiện tượng, lấy cặp (nhãn thật, nhãn đoán) của từng seed, nhân trọng số, cộng
thành một ma trận lỗi ước lượng. Trừ ma trận này khỏi ma trận nhầm lẫn của PhoBERT, chuyển về đường chéo, tính lại macro-F1: tăng 3,23
điểm nếu sửa hết. Chỉ tính dòng người chú thích đồng ý với nhãn gốc: 1,45 điểm. Phần lỗi nghi do nhãn không sửa được bằng kiến trúc.

Kết quả đáng lưu ý nhất ở câu 5: giả thuyết "cây cú pháp kém là nguyên nhân chính" KHÔNG đứng được. Nếu đúng thì GCN phải có ích hơn ở
bình luận không có dạng viết tắt; thực tế ASGCN vẫn giảm (-0,45, p 0,089), và ở bình luận chỉ dùng từ phủ định dạng chuẩn còn giảm rõ
hơn (-1,19, p 0,010). Trong khi đó Dai và cộng sự 2021 có đúng cùng kết quả trên tiếng Anh: ASGCN đặt trên RoBERTa thấp hơn RoBERTa với
một lớp MLP ở cả ba tập.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Câu trả lời cho câu 1 và 2 | Nói thẳng: chưa chứng minh, là giả thuyết | Viết lại cho hướng đề tài có vẻ được số đo ủng hộ | Số đo không đỡ; đúng lỗi mà giảng viên vừa chỉ ra |
| Công cụ cho số mới | Script riêng, kết quả file riêng | Thêm nhóm vào `doi_chung_do_thi.py` | Đổi dãy số ngẫu nhiên, các giá trị p đã in ở Chương 4 xê dịch |
| Tài liệu về cú pháp | Thêm Dai 2021, ghi vào `khong_trinh_bay.csv` | Thêm cả Sachan 2021; thêm vào Chương 3 | Sachan về tác vụ khác, chưa đọc hết; thêm vào Chương 3 đổi số 34 công trình |
| Quyết định 16/10 "không ghi khảo sát đồ thị nếu chưa chứng minh được đồ thị có ích" | Vẫn giữ: chỉ thêm bài giải thích vì sao đồ thị KHÔNG giúp | Thêm các hướng đồ thị đóng góp được ở phiếu CD1.12j | Câu hỏi mới của giảng viên khác câu lúc đó |
| Vị trí câu 5 | Mục mới 5.4, đổi số 5.4 và 5.5 cũ | Nhét vào mục 4.7 | Cần số của mục 5.1, 5.3; giảng viên cần chỗ tìm được ngay |
| Ví dụ câu 6 | Mẫu PhoBERT sai cả năm seed, người chú thích đồng ý nhãn gốc, một mẫu mỗi nhóm | Rút ngẫu nhiên; giữ mẫu CAMERA cũ | Mẫu nhãn bị nghi ngờ không minh hoạ được lỗi của mô hình; có ghi rõ là chọn để minh hoạ |
| Đưa vào Word | Chương 5, 6 và danh mục ghép; Chương 1, 4, Tóm tắt, Phụ lục dùng COM | Ghép cả | Chương 4 có phương trình, lệnh ghép tự dừng; các phần còn lại có chỗ học viên sửa tay |
| Tóm tắt | Câu rất ngắn | Câu đầy đủ như mục 5.6 | Câu dài làm dấu ngắt trang rơi sang trang sau, sinh trang trắng |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- Dòng `[TODO]` GPT-4o cuối mục 4.4 vẫn còn; có kết quả thì `doi_chieu_chuong6.py` báo câu GPT-4o ở mục 6.1.
- Bảng 5.3 ngắt qua hai trang (trang in 51, 52). Việc đổi nhỏ về chữ sẽ đổi chỗ ngắt, nên xử lý khi chốt bản nộp.
- File từ 69 lên 79 trang: danh sách bảng +1, Chương 4 +2, Chương 5 +6 (từ 10 lên 16), Chương 6 +1. Chương 1 đến 6 nay 59 trang.
- Hướng dẫn chú thích (`docs/annotation_guideline.md`) mục 3.2 và danh sách từ khoá trong mã hơi khác nhau về từ ít gặp; báo cáo dùng cách
  nói "và một số từ khác" nên vẫn đúng.

---

## 6. KIỂM CHỨNG

```
doi_chieu_chuong4.py     247 chỗ, khớp 247
doi_chieu_chuong5.py     122 chỗ, khớp 122; mọi con số có chỗ kiểm; chứng cứ nguyên văn của các công trình có trong bản gốc
doi_chieu_chuong6.py     37 nhận định, khớp hết; không con số lạ
survey_tools.py validate hợp lệ, 58 dòng; table-gon vẫn 34 công trình
kiem_sua_tay_word.py     trước khi ghép: mã 1, 20 chỗ, đã đọc từng chỗ WORD, đều là câu cũ dự kiến thay; sau: mã 2
pytest tests -q          581 passed, 1 skipped in 111.37s
```

- Chạy thử trên bản sao trước: file thật giống hệt bản thử về chữ (515 khối). So với file trước khi sửa: 9 phương trình, 21 chỉ số, 3 hình
  không đổi, 11 lên 13 bảng; bìa, lời cảm ơn, lời cam đoan, chữ viết tắt, Chương 2, Chương 3 giống hệt.
- Đoạn mới ở Chương 4 cùng kiểu Normal, căn đều. Xem ảnh xuất từ Word các trang in iii, 22, 42, 51.
- Sự cố lúc chạy thử, đều trên bản sao: (1) tiến trình Word ẩn do script mở không thoát sau lỗi, giữ khoá file, đã dừng và sửa script;
  (2) Find của Word trả lại kết quả cũ khi kết quả nằm trong ô bảng, làm phép kiểm "chỉ một lần" báo sai; (3) chèn đoạn bằng
  `InsertParagraphAfter` rồi `Next()` làm đoạn mới mang kiểu Heading 3, bước so sánh bắt được; (4) Tóm tắt dài thêm một dòng sinh một trang trắng.
- Chưa kiểm: nhận định định tính thuần lập luận ở mục 5.4 (cách 4) và 5.6.1 không có phép đo riêng, đã ghi rõ trong chữ là lập luận.

---

## 7. DỪNG LẠI VÀ HỎI

1. Mục 6.3 nay cam kết đánh giá trên VLSP 2018 (trước đây "nếu còn điều kiện"), kèm một phần tập chẩn đoán gán tay. Bạn có đồng ý cam kết này với cô không?
2. Mục 5.6.1 nói thẳng: hai trong ba đồ thị chưa có căn cứ, đa đồ thị là khung thí nghiệm. Bạn có muốn giữ cách nói này khi tên đề tài có chữ Multi-Graph không?
3. Có muốn có căn cứ trực tiếp cho câu 2 ngay trong Chuyên đề 1 không: huấn luyện PhoBERT có thêm tín hiệu luật trên Kaggle? Mô hình và số seed là bạn quyết; chưa làm gì.
4. Chương 5 nay 16 trang, file 79 trang. Giữ, hay cắt?

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi hay yêu cầu của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi không |
|---|---|---|
| 01/11/2026, câu hỏi 1: đồng ý cam kết đánh giá trên VLSP 2018 | Giữ nguyên mục 6.3 | Không; ghi vào sổ quyết định |
| 01/11/2026, câu hỏi 2: giữ cách nói ở mục 5.6.1 | Giữ nguyên | Không |
| 01/11/2026, câu hỏi 3: có huấn luyện PhoBERT có tín hiệu luật trên Kaggle; chọn 5 seed của Chương 4, 20 lần chạy | Thành step CD1.11d, phiếu `CD1.11d_tin-hieu-luat.md` | Có: mô hình, config, công cụ chấm, notebook |
| 01/11/2026, câu hỏi 4: số trang để cắt khi hoàn thành | Chưa cắt | Không; nhắc lại khi chốt bản nộp |
