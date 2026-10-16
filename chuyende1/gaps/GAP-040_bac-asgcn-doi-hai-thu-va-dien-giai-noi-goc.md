# GAP-040 — Bậc PhoBERT lên ASGCN đổi hai thứ chứ không phải một; diễn giải "đồ thị bị chia cắt là một nguyên nhân" không đứng được khi tách nhóm

**Ngày phát hiện:** 16/10/2026 · **Phát hiện bởi:** Claude Code, khi học viên hỏi "có thật là bổ sung đồ thị chưa mang lại cải thiện rõ rệt không, vì sao"
**Loại:** phương pháp · tài liệu
**Mức độ:** nghiêm trọng (không đổi con số nào, nhưng đổi cách quy kết quả cho thành phần nào)
**Trạng thái:** 🔴 Mở, chờ học viên chọn: chạy thí nghiệm đối chứng, hay chỉ sửa lời văn

---

## 1. Sai ở đâu

**(a) "Mỗi bậc chỉ thêm một thành phần" không đúng ở bậc 3 lên bậc 4.**

| Mô hình | Vector đưa vào lớp phân loại |
|---|---|
| `phobert` (`src/nsmgat/models/phobert.py`, dòng 78) | biểu diễn token `<s>` của cặp câu |
| `asgcn` (`src/nsmgat/models/asgcn.py`, dòng 372–384) | trung bình subword về mức từ, chỉ lấy vế câu, bỏ `<s>`; gộp có trọng số bằng attention với truy vấn là vế khía cạnh; GCN chỉ tạo khoá cho attention |

Tức là từ PhoBERT lên ASGCN đổi **cách đọc ra** (từ `<s>` sang gộp attention theo khía cạnh trên các từ) **và** thêm GCN.
Hiệu số −1,21 macro-F1 là hiệu của cả hai thay đổi, không riêng cú pháp.

Những chỗ đang viết như thể chỉ thêm cú pháp:

- `chuyende1/report/nhap_rut_gon/Chuong4_ThucNghiem.md`: dòng 3 ("mỗi bậc chỉ thêm một thành phần"), Bảng 4.2 dòng bậc 4
  ("Cây phụ thuộc cú pháp"), dòng 82 ("để hiệu số với bậc 3 chỉ còn là phần cú pháp"), dòng 127 ("Thêm cây phụ thuộc
  không cải thiện kết quả"), dòng 227 ("Hai bước thêm cấu trúc lên trên PhoBERT, là cú pháp và điểm cảm xúc của từ").
- `TrangDau.md` dòng 28, `Chuong1_TongQuan.md` dòng 19 ("mỗi bậc thêm một thành phần").
- Docstring `src/nsmgat/models/asgcn.py` ("Moi bac them DUNG MOT thu") và chú thích `configs/asgcn.yaml`.

Bậc 4 lên 4b (nối gốc) và 4 lên 5 (Sentic-GCN) thì đúng là chỉ đổi một thứ: hai mô hình đó kế thừa `ASGCNModel`.

**(b) Dòng 129 của Chương 4** viết: "Kết quả gợi ý rằng việc hơn một nửa số đồ thị bị chia thành các cây rời nhau là một
nguyên nhân làm ASGCN kém ổn định". Tách tập kiểm tra theo việc nối gốc có đổi đồ thị hay không (đổi đúng ở 3.726 mẫu có
từ hai gốc trở lên, không đổi ở 2.996 mẫu một gốc), phần ASGCN nối gốc hơn ASGCN **lớn hơn ở nhóm đồ thị không đổi**:

| Nhóm | Nối gốc trừ ASGCN, macro-F1 | KTC 95 % | p |
|---|---|---|---|
| Đồ thị không đổi (một gốc, 2.996 mẫu) | +1,06 | +0,29 đến +1,85 | 0,008 |
| Đồ thị có đổi (từ hai gốc, 3.726 mẫu) | +0,66 | +0,09 đến +1,22 | 0,024 |

Nếu nối gốc có lợi nhờ sửa đồ thị thì phần hơn phải dồn vào nhóm có đổi. Ở đây ngược lại, nên phần hơn 0,83 điểm khớp với
việc hai lần huấn luyện cho hai bộ trọng số khác nhau hơn là với việc sửa đồ thị. Cùng hướng: phần ASGCN thua PhoBERT là
−1,80 điểm ở nhóm một gốc và −0,77 điểm ở nhóm bị chia cắt, tức không dồn vào chỗ đồ thị bị chia cắt.

## 2. Phát hiện thế nào

Đặt `forward()` của `PhoBERTClassifier` và `ASGCNModel` cạnh nhau khi tìm lý do đồ thị không giúp; rồi tách tập kiểm tra
theo số gốc của đồ thị và tính lại bootstrap ghép cặp theo bình luận (cùng hàm `kiem_dinh` của `compare_baselines.py`).

## 3. Nguyên nhân gốc

- Nguyên tắc "mỗi bậc đổi đúng một biến" được kiểm ở **mức config** (kế thừa `asgcn.yaml`, test
  `test_asgcn_linked_khac_asgcn_DUNG_MOT_khoa`) nhưng chưa kiểm ở **mức kiến trúc** giữa hai lớp mô hình khác nhau.
  Giả định ngầm: "cùng bộ mã hoá PhoBERT thì chỉ còn khác phần cú pháp".
- Diễn giải nối gốc rút từ hiệu số trên toàn tập, chưa kiểm hiệu số có nằm đúng ở nhóm mà can thiệp chạm tới không.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| Mọi con số ở Bảng 4.3, 4.4, 4.5, 4.8, 4.9, Phụ lục C | Không. Số đúng, chỉ cách quy kết quả đổi |
| Kết luận "ba mô hình đồ thị không hơn PhoBERT" | Không. Vẫn đứng, còn chắc hơn sau phân tích ở phiếu CD1.12i |
| Câu "cú pháp không đem lại lợi ích đo được" (dòng 127, 227) | Có. Chỉ nói được "đầu đồ thị kiểu ASGCN (cách đọc ra mới cộng GCN) không đem lại lợi ích" |
| Đoạn "Tác động của đồ thị bị chia cắt" (dòng 129) | Có. Bằng chứng tách nhóm không ủng hộ |
| Dòng 3, Bảng 4.2, dòng 82 Chương 4; TrangDau dòng 28; Chương 1 dòng 19 | Có |
| Docstring `asgcn.py`, chú thích `asgcn.yaml` | Có, khi học viên đồng ý |

## 5. Đã sửa thế nào

Chưa sửa. Hai hướng, học viên chọn (phiếu CD1.12i mục 7):

1. Chạy mô hình đối chứng "PhoBERT cộng gộp attention theo khía cạnh, không GCN" (`gcn_layers: 0`, đã thử chạy được, không
   cần sửa mã) để tách hai thứ, rồi viết lại theo kết quả.
2. Không chạy thêm: sửa lời văn cho đúng phạm vi ("đầu đồ thị kiểu ASGCN", bỏ hoặc đảo đoạn nối gốc), ghi thành giới hạn.

## 6. Bài học — phòng lần sau bằng cách nào

Khi khẳng định hai mô hình "chỉ khác một thành phần", đặt hai hàm `forward()` cạnh nhau và liệt kê mọi chỗ khác, không
chỉ so config. Khi quy một hiệu số cho một can thiệp, tính hiệu số riêng ở nhóm mẫu can thiệp chạm tới và nhóm không chạm.

## 7. Có cần đưa vào báo cáo không

- [x] Có, sửa lời văn ở mục 4.3, 4.4, 4.7 và câu "mỗi bậc thêm một thành phần" ở phần tóm tắt và Chương 1
- [ ] Không
