# CD1.9 — Phân tích lỗi của thang baseline (năm lát cắt)

Ngày 13/10/2026, làm sớm hơn lịch (tuần 10) vì không phụ thuộc việc gán lại.

## 1. ĐÃ LÀM GÌ

Viết `scripts/error_analysis.py` (thay khung rỗng cũ) và `tests/test_error_analysis.py` (6 test).
Công cụ đọc dự đoán của 18 lần chạy đã có, không chạy mô hình, và cắt lỗi theo năm cách:

| Lát cắt | Câu hỏi | Bảng |
|---|---|---|
| Cặp lớp bị nhầm | Lỗi dồn vào cặp lớp nào | A |
| Khía cạnh | Khía cạnh nào khó, có đi cùng số mẫu huấn luyện không | B |
| Độ dài câu | Câu dài có khó hơn không | C |
| Loại câu | Câu có nhãn trái nhau giữa các khía cạnh khó hơn bao nhiêu; mô hình có đoán một nhãn cho cả câu không | D, E |
| Giao lỗi | Bao nhiêu mẫu cả bốn mô hình dùng PhoBERT cùng sai, chúng là gì | F đến I |

Lát cắt thứ sáu của kế hoạch, theo hiện tượng ngôn ngữ, đã có số sơ bộ ở
`CD1.8e_cham-theo-nhom.md`.

Kết quả: `chuyende1/tables/bang_5_phan_tich_loi.md`, `results/error_analysis.json`. Mười ca cùng
sai để đọc tay: `chuyende1/report/nhap/ca_cung_sai.md` (file nháp, không push).

## 2. HAI ĐỊNH NGHĨA DÙNG TRONG BẢNG

- Luôn sai: một mô hình sai trên mẫu đó ở cả ba seed. Sai ở một seed có thể là may rủi của lần
  huấn luyện; sai ở cả ba thì là tính chất của mô hình.
- Cùng sai: cả bốn mô hình PhoBERT, ASGCN, ASGCN nối gốc, Sentic-GCN đều luôn sai, tức 12 lần
  chạy không lần nào đúng.

## 3. KẾT QUẢ CHÍNH

Mọi số là trung bình ba seed trên 6.722 mẫu kiểm tra.

**1. Lỗi xoay quanh lớp trung tính.** Với PhoBERT, 81,4 % số lỗi có lớp trung tính ở một đầu
(nhãn thật hoặc nhãn đoán). Tỉ lệ tìm lại lớp trung tính là 67,8 %, hai lớp kia trên 94 %.
Sentic-GCN tìm lại trung tính tốt nhất (72,4 %) nhưng đổi lại đoán nhầm tích cực thành trung
tính nhiều hơn (27,6 % số lỗi của nó, so với 19,5 % ở PhoBERT).

**2. Câu trái nhãn khó hơn rõ.** 986 trên 2.187 câu có ít nhất hai khía cạnh mang nhãn khác
nhau. Trên mẫu thuộc các câu đó PhoBERT đạt 87,7 %, trên mẫu thuộc câu nhiều khía cạnh cùng
nhãn đạt 97,1 %, chênh 9,4 điểm, p dưới 0,001. Cả sáu mô hình đều có chênh lệch này.

**3. Sụp nhãn có nhưng không phải chuyện chính.** PhoBERT đoán cùng một nhãn cho mọi khía cạnh
ở 12,0 % số câu trái nhãn; Sentic-GCN 10,3 %, ASGCN 15,0 %. Mô hình từ điển là 100 % vì nó
không nhìn khía cạnh. Ở câu có đúng hai nhãn, khoảng 60 đến 68 % lỗi của các mô hình mạnh rơi
vào nhãn còn lại của câu chứ không phải nhãn thứ ba.

**4. Câu dài khó hơn.** PhoBERT 94,9 % ở câu đến 20 từ, 84,6 % ở câu trên 80 từ, chênh 10,3
điểm. Ba mô hình đồ thị không khá hơn PhoBERT ở câu dài (84,3 đến 85,3 %).

**5. Khía cạnh ít dữ liệu thì kém hơn, nhưng bằng chứng yếu.** Tương quan hạng giữa số mẫu
huấn luyện và macro-F1 là 0,52 với PhoBERT (p 0,13) và 0,65 đến 0,76 với ba mô hình đồ thị
(p dưới 0,05). Chỉ có 10 khía cạnh nên không nên nói mạnh.

**6. Có 212 mẫu cả bốn mô hình cùng sai, bằng 3,2 % tập kiểm tra.** Trong đó 53,8 % có nhãn
thật trung tính (toàn tập là 12,2 %) và 87,3 % nằm trong câu trái nhãn (toàn tập là 53,4 %).
Ngược lại, 5.636 mẫu (83,8 %) không bị lần chạy nào trong 12 lần đoán sai.

**7. Bốn mô hình sai gần như cùng chỗ.** Mỗi mô hình luôn sai ở 351 đến 374 mẫu, và 212 mẫu
trong đó là chung. Thêm đồ thị cú pháp hay tri thức cảm xúc không gỡ được phần lớn lỗi của
PhoBERT.

## 4. BỐN CHỖ KHÔNG ĐƯỢC ĐỌC QUÁ TAY

1. **212 mẫu cùng sai không hẳn là 212 lỗi của mô hình.** 35 mẫu trong số đó nằm trong 800 dòng
   bạn đã xem, và bạn không đồng ý với nhãn gốc ở 20 trên 35 (57 %), so với 144 trên 800 (18 %)
   của cả tập ứng viên. Tức một phần đáng kể có thể là nhãn gốc có vấn đề hoặc là quy ước của
   bộ dữ liệu mà mô hình không học được. Đây là nhận định của một người trên 35 mẫu, chưa đủ để
   đưa ra tỉ lệ. Việc A14 bên dưới là để có thêm bằng chứng.
2. **Câu trái nhãn và lớp trung tính dính nhau.** Câu trái nhãn chứa phần lớn mẫu trung tính, mà
   trung tính vốn khó. Bảng D không tách được hai nguyên nhân này. Vì thế bảng macro-F1 theo
   loại câu không được in ra: câu cùng nhãn gần như không có mẫu trung tính nên con số không so
   được.
3. **Câu dài có thể bị cắt.** Mô hình cắt đầu vào ở 128 mảnh từ; 1,64 % mẫu kiểm tra bị cắt, và
   chúng dồn vào nhóm trên 80 từ (6,5 % số mẫu). Một phần chênh lệch ở Bảng C có thể do cắt chứ
   không do độ dài. Chưa tách.
4. **Mọi phân tích làm trên tập kiểm tra**, là tập đã dùng để báo cáo kết quả chính. Các nhận
   định ở đây là mô tả, không phải kết quả kiểm định trên dữ liệu mới.

## 5. Ý NGHĨA CHO CHUYÊN ĐỀ 2

Ghi lại để bàn với cô, chưa phải kết luận:

- Chỗ còn dư địa rõ nhất là lớp trung tính trong câu có nhiều khía cạnh trái nhãn, và câu vừa
  phủ định vừa chuyển ý (số sơ bộ: mọi mô hình rơi 16 đến 20 điểm).
- Phủ định đứng riêng không phải chỗ yếu của PhoBERT theo số sơ bộ. Nếu Chuyên đề 2 lấy "xử lý
  phủ định" làm động cơ chính thì cần nói lại cho khớp số liệu.
- Trần cải tiến thực tế thấp hơn con số 8 % lỗi còn lại nếu một phần lỗi là do nhãn.

## 6. KIỂM CHỨNG

```
426 passed   (cả bộ)
```

- Số lỗi của PhoBERT và Sentic-GCN tính ở đây khớp accuracy trong `metrics.json`.
- Số câu trái nhãn tính ra 986 trên 2.187, khớp 45,1 % đã báo cáo ở Chương 4.
- Lệnh dừng nếu file dự đoán lệch thứ tự hoặc lệch nhãn thật so với tập kiểm tra.
- Bảng `.md` và file `.json` không chứa câu của bộ dữ liệu, chỉ có mã mẫu.
- Chưa làm: hình (heatmap ma trận nhầm lẫn, biểu đồ theo độ dài, sơ đồ giao lỗi); mục 5.1 của
  báo cáo; tách ảnh hưởng của việc cắt đầu vào.

## 7. VIỆC CỦA BẠN

**Đọc 10 ca cùng sai** (việc A14 trong `pLan/chuyende1/VIEC_CAN_LAM.md`):

- File: `chuyende1/report/nhap/ca_cung_sai.md`.
- Mỗi ca có câu, khía cạnh, nhãn thật, dự đoán của bốn mô hình.
- Dưới mỗi ca ghi thêm một dòng: `- Nhận xét: nhãn thật đúng / nhãn thật sai / không rõ; lý do ngắn`.
- Khoảng 30 phút. Kết quả dùng để viết mục 5.1 và để biết 212 mẫu kia đáng tin tới đâu.
