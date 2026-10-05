# GAP-027 — Ghi sai nơi công bố của bài giới thiệu UIT-ViSFD: KSE thay vì KSEM

**Ngày phát hiện:** 05/10/2026 · **Phát hiện bởi:** Claude Code (khi đọc danh mục tài liệu của một bài khác)
**Loại:** số liệu · **Mức độ:** nghiêm trọng nếu lọt vào bản nộp (trích sai nơi công bố của tập dữ liệu chính) · **Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

Dòng `UIT-ViSFD` của `chuyende1/survey/survey_matrix.csv` ghi nơi công bố là **KSE 2021**.

Nơi công bố đúng là **KSEM 2021**, International Conference on Knowledge Science, Engineering
and Management, thuộc bộ Lecture Notes in Computer Science, trang 647 đến 658.

Hai hội nghị khác nhau hoàn toàn. KSE là Knowledge and Systems Engineering, một hội nghị tổ
chức tại Việt Nam. KSEM là hội nghị quốc tế do Springer xuất bản kỷ yếu.

Chỗ sai đã lan sang `chuyende1/tables/bang_3_9_khao_sat.md`, danh mục tài liệu của bản nháp
Chương 3, và một dòng ví dụ trong `scripts/survey_tools.py`.

## 2. Phát hiện thế nào

Ngày 05/10, khi đọc bài của Thin và Nguyen (2023), mục [14] trong danh mục tài liệu của bài đó
ghi bài UIT-ViSFD tại "International Conference on Knowledge Science, Engineering and
Management, 2021, pp. 647". Tên hội nghị không khớp với ma trận.

Kiểm bằng nguồn thứ hai độc lập là Crossref: DOI `10.1007/978-3-030-82147-0_53`, tên kỷ yếu
"Knowledge Science, Engineering and Management", bộ "Lecture Notes in Computer Science",
trang 647-658, năm 2021. Hai nguồn trùng nhau.

## 3. Nguyên nhân gốc

**Hai nguồn trong chính kho nói khác nhau, và không ai đối chiếu.**

- `ghi_chu` của dòng `UIT-ViSFD` đã tự ghi: nơi công bố do học viên tra ngày 20/09, "chưa đối
  chiếu được bằng nguồn thứ hai". Tức ô này được biết là chưa chắc ngay từ đầu.
- Trong khi đó `chuyende1/survey/doc_bat_buoc.md`, mục `UIT-ViSFD`, đã có sẵn đường dẫn bản
  chính thức trên Springer với đúng DOI nói trên. Chỉ cần mở đường dẫn đó là thấy tên kỷ yếu.

Hai tên viết tắt chỉ khác nhau một chữ cái, và KSE là cái tên quen với người làm xử lý ngôn
ngữ ở Việt Nam, nên nhầm rất tự nhiên. Trang arXiv của bài không ghi nơi công bố.

Dòng này mang trạng thái `da_doc_toan_van` suốt từ ngày 20/09 dù một ô của nó được chính
`ghi_chu` đánh dấu là chưa đối chiếu. `validate` chỉ kiểm ô có trống hay không, không kiểm ô
có đáng tin hay không.

Cùng mẫu hỏng thứ nhất của sổ này: một giá trị lệch ở nguồn lan âm thầm ra mọi thứ dẫn xuất.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `survey_matrix.csv`, dòng `UIT-ViSFD`, cột `hoi_nghi_tap_chi` | Có, đã sửa |
| `chuyende1/tables/bang_3_9_khao_sat.md` | Có, đã sinh lại |
| `chuyende1/report/nhap/Chuong3_KhaoSat.md`, danh mục tài liệu | Có, đã sinh lại |
| `scripts/survey_tools.py`, dòng ví dụ trong trang hướng dẫn của file Excel | Có, đã sửa |
| `chuyende1/trac-nghiem/` đề 01, phiếu bàn giao, plan | Không. Đã tìm, không chỗ nào nhắc nơi công bố |

Không số liệu thực nghiệm nào bị ảnh hưởng. Nhưng nếu lọt vào bản nộp thì đây là trích dẫn sai
cho chính tập dữ liệu của đề tài, thứ hội đồng dễ kiểm nhất.

## 5. Đã sửa thế nào

- Ma trận: `KSE 2021` thành `KSEM 2021 (Knowledge Science, Engineering and Management, LNCS,
  tr. 647–658)`, kèm ghi chú nêu hai nguồn đối chiếu.
- Sinh lại Bảng 3.9 và bản nháp Chương 3.
- `scripts/survey_tools.py`: sửa dòng ví dụ.

## 6. Bài học — phòng lần sau bằng cách nào

**Ô nào mà `ghi_chu` tự nhận là "chưa đối chiếu được" thì dòng đó chưa được mang trạng thái đã
kiểm chứng.** Trước khi viết Chương 3 thành bản nộp, tìm trong cột `ghi_chu` các cụm "chua doi
chieu", "can xac nhan lai", "chưa đối chiếu" và xử lý từng chỗ.

Với nơi công bố của một bài: Crossref trả lời trong một lệnh và không bị chặn như DBLP hay
Semantic Scholar hôm 20/09.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — đã sửa trước khi có bản nộp nào. Giữ trong sổ vì bài học ở mục 6 phải làm
      một lượt trước tuần 13.
