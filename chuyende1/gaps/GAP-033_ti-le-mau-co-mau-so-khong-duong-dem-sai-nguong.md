# GAP-033 — Tỉ lệ mẫu có mẫu số không dương ở Sentic-GCN được đếm theo ngưỡng khác với lời mô tả

**Ngày phát hiện:** 13/10/2026 · **Phát hiện bởi:** Claude Code, khi viết bước kiểm trước cho từ điển có sẵn
**Loại:** số liệu · tài liệu
**Mức độ:** nhẹ (một con số trong báo cáo sai, kết luận không đổi)
**Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

Mục 4.3 của báo cáo viết: mẫu số chuẩn hoá của Sentic-GCN có thể không dương, "trên tập huấn luyện
có 0,079 % số từ rơi vào trường hợp đó, thuộc 3,70 % số mẫu". Con số thứ hai sai. Đếm lại bằng
chính lớp mô hình:

| Tập huấn luyện, 23.872 mẫu | Số đếm lại | Số trong báo cáo |
|---|---|---|
| Từ có mẫu số ≤ 0 | 735 (0,079 %) | 735 (0,079 %) |
| Mẫu có ít nhất một từ như vậy | 596 (2,50 %) | 884 (3,70 %) |

884 không thể đúng với lời mô tả: 735 từ thì nhiều nhất nằm trong 735 mẫu.

Con số 884 là số mẫu có ít nhất một từ mà mẫu số **không quá 0,1**. Quét ngưỡng trên cả ba phần dữ
liệu cho đúng ba con số cũ: 884, 107 và 264 mẫu (3,70 %, 3,23 %, 3,93 %). Tức là hàng "số từ" đếm
theo ngưỡng 0, hàng "số mẫu" đếm theo ngưỡng 0,1, và cả hai được đặt dưới cùng một lời mô tả.

Sai cùng chỗ ở bốn nơi khác: bảng mục 3.4 của `chuyende1/notes/CD1.6b_senticgcn.md`, docstring của
`src/nsmgat/models/senticgcn.py`, sổ quyết định trong `progress_cd1.md`, và câu "khoảng 70 % số lô
có token mang mẫu số âm" ở hai phiếu CD1.6b (với ngưỡng 0 là khoảng 55 %).

## 2. Phát hiện thế nào

`scripts/build_lexicon_external.py kiem` được viết để đo mẫu số cho bảng điểm mới. Để tin được nó,
Claude chạy nó trên bảng điểm cũ và so với số đã ghi. Số từ khớp, mức nhỏ nhất khớp, số mẫu lệch.

## 3. Nguyên nhân gốc

Phép đo ngày 03/10 là một đoạn mã chạy một lần, không lưu lại. Bảng trong phiếu ghép hai phép đếm
khác ngưỡng vào một tiêu đề. Đợt rà Chương 2 đến 4 (GAP-031) có dừng ở đúng câu này nhưng chỉ sửa
phạm vi ("trên UIT-ViSFD" thành "trên tập huấn luyện"); nó chép lại hai con số từ phiếu chứ không
đếm lại, vì công cụ đối chiếu Chương 4 không phủ con số này.

## 4. Ảnh hưởng lan tới đâu

- Báo cáo: một con số ở mục 4.3. Nhận định đi kèm ("mẫu số có thể không dương, chuyên đề giữ nguyên
  công thức") không đổi.
- Kết quả thực nghiệm: không ảnh hưởng. Không dòng mã nào chạy khác đi.
- Quyết định 03/10 (chạy y hệt bài gốc, không kẹp mẫu số) dựa một phần vào con số "70 % số lô". Số
  đúng là khoảng 55 %; lập luận của quyết định không phụ thuộc vào mức đó.

## 5. Đã sửa thế nào

- Mục 4.3 của bản nháp: 3,70 % thành 2,50 %. Đã ghép lại vào file Word.
- Phiếu `CD1.6b_senticgcn.md`: bảng tách thành hai hàng, mỗi hàng ghi rõ ngưỡng. Phiếu
  `CD1.6b_chay-3-seed.md` và docstring của mô hình có ghi chú sửa.
- Phép đo nay nằm trong mã: `build_lexicon_external.py kiem`, có test chốt số trên tập phát triển
  (86 từ, 69 mẫu). `doi_chieu_chuong4.py --do-mau-so` kiểm câu này của báo cáo.

## 6. Bài học

Con số nào vào báo cáo thì phép đo ra nó phải nằm trong một lệnh chạy lại được. Số chép từ phiếu
bàn giao là số chưa được kiểm, kể cả khi phiếu do chính mình viết. Và hai con số đặt cạnh nhau dưới
một lời mô tả thì phải thử một phép kiểm chéo đơn giản: ở đây là "số mẫu không thể lớn hơn số từ".
