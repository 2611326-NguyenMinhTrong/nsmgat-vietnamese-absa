# CD1.8c — Học viên gán xong 800 dòng; kiểm định nghĩa trung tính với bài gốc

**Ngày:** 13/10/2026 · **Trạng thái:** ✅ phần gán xong; còn hai quyết định trước khi chốt tập · **Step kế:** CD1.8d

---

## 1. ĐÃ LÀM GÌ

| Ai | Việc |
|---|---|
| Học viên | Gán đủ 800 dòng, đưa về CSV bằng `tu-excel`. Tự xác định định nghĩa ba lớp cảm xúc vì bài gốc không có |
| Claude | Tải lại bài UIT-ViSFD (arXiv v2) để kiểm: xác nhận bài không có câu định nghĩa, nhưng Bảng 1 có ví dụ cho từng khía cạnh |
| Claude | `docs/annotation_guideline.md` mục 5: thay đoạn giữ chỗ bằng ghi chú nguồn, thêm đoạn về quy ước PRICE có số đếm |
| Claude | Bản nháp Chương 4, mục 4.1.1: điền nguồn thu thập và quy trình gán nhãn của bộ dữ liệu, lấy từ bài |
| Claude | `chuyende1/survey/survey_matrix.csv`, dòng `UIT-ViSFD`: ghi thêm các chi tiết vừa đọc lại |
| Claude | `pLan/chuyende1/VIEC_CAN_LAM.md`: cập nhật |

## 2. ĐỂ LÀM GÌ

Tập chẩn đoán là bằng chứng chính của đề tài. Trước khi chốt, cần biết ba điều: định nghĩa dùng
để gán có căn cứ không, nhãn của học viên lệch nhãn gốc ở đâu và vì sao, và các nhóm có đủ mẫu không.

## 3. CƠ CHẾ — phần để học

### 3.1. Bài gốc nói gì về ba lớp cảm xúc

Không có câu định nghĩa. Mục 3.2 chỉ nói người gán xác định khía cạnh rồi gán Pos, Neu, Neg, và
Bảng 1 cho mỗi khía cạnh một ví dụ. Hai ví dụ trung tính:

| Khía cạnh | Ví dụ trong Bảng 1 | Nhãn |
|---|---|---|
| PERFORMANCE | cấu hình có thể chấp nhận được | Neu |
| PRICE | giá cả ở mức trung bình | Neu |

Định nghĩa học viên tự viết ("trung bình hoặc chỉ chấp nhận được") khớp với cả hai ví dụ. Trong
báo cáo phải ghi đây là định nghĩa do học viên xác định, đối chiếu với ví dụ của bài.

### 3.2. Vì sao 27 % dòng lệch nhãn gốc không có nghĩa là nhãn gốc sai 27 %

Học viên không đồng ý với nhãn gốc ở 216 trên 800 dòng. 94 trong số đó thuộc PRICE, và 79 là
PRICE trung tính mà học viên cho là tích cực, kiểu "quá ngon trong tầm giá".

Đếm trên tập huấn luyện:

| Mẫu PRICE | Tiêu cực | Trung tính | Tích cực |
|---|---|---|---|
| có "tầm giá", không có ý kiến về chính cái giá (789 mẫu) | 27 | **706** | 56 |
| có "giá rẻ", "giá hợp lý", "đáng tiền" (123 mẫu) | 14 | 7 | **102** |

Người gán của bộ dữ liệu theo một quy ước nhất quán: giá chỉ làm khung thì PRICE trung tính, lời
khen thuộc về máy. Bảng 1 cũng định nghĩa PRICE là "các bình luận nêu giá cụ thể". Vì vậy phần
lớn 79 dòng đó là **khác quy ước**, không phải nhãn sai. Nếu viết vào Chương 5 rằng "27 % nhãn
gốc sai" thì đó là một khẳng định sai.

### 3.3. Số liệu sơ bộ trên đủ 800 dòng

Chưa có kappa nên **chưa đưa vào báo cáo**. Accuracy (%) theo nhãn gốc, trung bình ba seed:

| Nhóm | Số dòng | BiLSTM | PhoBERT | ASGCN | ASGCN nối gốc | Sentic-GCN |
|---|---|---|---|---|---|---|
| regular | 401 | 86,0 | 91,4 | 89,5 | 91,1 | 92,0 |
| negation | 128 | 82,3 | 90,4 | 86,7 | 88,0 | 92,7 |
| contrast | 186 | 72,6 | 84,6 | 83,5 | 84,4 | 87,1 |
| both | 84 | 69,8 | 71,8 | 73,8 | 74,6 | 74,6 |

So với lần đọc trên 397 dòng ngày 11/10, hình ảnh rõ hơn: với PhoBERT, phủ định đơn lẻ gần như
không làm tụt (−1,0 điểm), chuyển ý làm tụt vừa (−6,8), có cả hai thì tụt mạnh (−19,6). Mọi mô
hình đều dưới 75 % ở nhóm `both`.

### 3.4. Nhóm ứng viên và nhãn thật lệch nhau bao nhiêu

| Nhóm ứng viên (theo từ khoá) | Học viên gán đúng hiện tượng của nhóm |
|---|---|
| phủ định (250) | 105 negation, 18 both; 109 regular |
| chuyển ý (200) | 122 contrast, 2 both; 75 regular |
| cả hai (150) | 61 both |
| đối chứng (200) | 175 regular; 25 có hiện tượng (dùng "mà", "còn" hoặc từ ngoài danh sách) |

Khoảng một nửa số dòng có từ phủ định không bị từ đó tác động. Đây là số liệu cho Chương 5 và
cho bộ luật của Chuyên đề 2: tìm từ khoá thì dễ, xác định từ đó tác động lên khía cạnh nào mới khó.

## 4. QUYẾT ĐỊNH

| Quyết định | Đã chọn | Vì sao |
|---|---|---|
| Ghi định nghĩa trung tính là của ai | Của học viên, có đối chiếu với Bảng 1 | Bài gốc không có định nghĩa |
| Không sửa 79 dòng PRICE thay học viên | Để học viên quyết (A9) | Là nhãn của học viên |
| Không đưa số sơ bộ vào báo cáo | Chờ kappa | Chưa biết nhãn hiện tượng có lặp lại được không |

## 5. ĐIỂM NỐI

CD1.8d cần: quyết A9 và K2 (cùng gốc), quyết A10 (300 hay toàn bộ), người chú thích thứ hai.

## 6. KIỂM CHỨNG

- File `.xlsx` và CSV khớp từng dòng ở cả ba cột chú thích.
- Mọi trích dẫn từ bài gốc lấy từ bản arXiv v2 tải về ngày 13/10, đọc trực tiếp.
- Hai số đếm PRICE dùng biểu thức tìm cụm từ; có thể sót vài cách viết, không đổi kết luận.

## 7. CÂU HỎI

1. A9: sửa 79 dòng PRICE về `dong_y` theo quy ước của bộ dữ liệu (đề xuất), hay giữ?
2. A4: giữ quy tắc K2 không?
3. A10: chốt 300 dòng hay dùng toàn bộ?
4. Đã có người chú thích thứ hai chưa?
