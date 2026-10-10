# CD1.10a — Kiểm định bootstrap, thẩm định hai file khảo sát, và số liệu sơ bộ của tập chẩn đoán

**Ngày:** 11/10/2026 · **Trạng thái:** ✅ ba việc xong; `cost_profile.json` của CD1.10 chưa làm · **Step kế:** chờ học viên gán xong (CD1.8c)

Học viên đang gán nhãn dở và yêu cầu: làm trước việc làm được, ghi lại việc học viên cần làm,
và xem hai file khảo sát tự làm có giúp tối ưu đề tài không, với yêu cầu mọi dữ liệu phải thật.

---

## 1. ĐÃ LÀM GÌ

| File | Việc | Lên GitHub? |
|---|---|---|
| `scripts/compare_baselines.py` + `tests/test_compare_baselines.py` | Tạo. Kiểm định bootstrap ghép cặp, 7 test | Có |
| `results/compare_baselines.json`, `chuyende1/tables/bang_4_kiem_dinh.md` | Sinh ra từ lệnh trên | Có |
| `chuyende1/report/nhap/Chuong{1,2,4}_*.md` | Đưa kết quả kiểm định vào; thêm Bảng 4.6, đánh số lại các bảng sau | Không |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong.docx` | Ghép lại từ bản nháp | Không |
| `scripts/chu_thich_chan_doan.py` | `tu-excel` quy ô kiểm tra trùng nhãn gốc về `dong_y`; thêm 1 test | Có |
| `chuyende1/report/nhap/docs/THAM_DINH_hai_file_khao_sat.md` | Tạo. Bản thẩm định | Không |
| `chuyende1/gaps/GAP-029_*.md` + `INDEX.md` | Tạo | Có |
| `pLan/chuyende1/VIEC_CAN_LAM.md` | Tạo. Sổ nhắc việc của học viên | Không |
| `data/diagnostic/candidates_chu_thich.20261011-claude.xlsx.bak` | Bản dự phòng của file đang gán dở. **File sinh ra, bạn tự quyết xoá** | Không |

Không sửa hai file `.docx` khảo sát, không sửa file `.xlsx` đang gán.

## 2. ĐỂ LÀM GÌ

- Bản nháp Chương 4 có năm chỗ viết "chưa kiểm định". Dự đoán của 18 lần chạy đã có sẵn, nên
  kiểm định không phải chờ gì.
- Hai file khảo sát mang câu "đã thẩm định toàn văn" nhưng chưa ai dò lại. Đưa vào báo cáo mà
  không dò là rủi ro lớn nhất hiện nay về tính trung thực của số liệu.
- 397 dòng đã gán đủ để nhìn sơ bộ xem giả thuyết của đề tài có dấu hiệu đúng không, trước khi
  bỏ thêm 15 giờ gán tiếp.

## 3. CƠ CHẾ — phần để học

### 3.1. Vì sao lấy mẫu theo câu

Một câu sinh trung bình ba mẫu (ba khía cạnh) chung văn bản. Mô hình đọc sai câu đó thì thường
sai cả ba. Nếu coi 6.722 mẫu là độc lập, khoảng tin cậy sẽ hẹp hơn thật. Mỗi lần lấy mẫu vì vậy
rút có hoàn lại 2.187 **câu**, mẫu đi theo câu.

### 3.2. p ở đây trả lời câu hỏi gì, và không trả lời câu hỏi gì

Trả lời: "nếu tập kiểm tra là một bộ câu khác rút từ cùng nguồn, hiệu số trung bình ba seed này
có còn không?". Không trả lời: "nếu huấn luyện lại với ba seed khác thì sao?".

Ví dụ rõ nhất là ASGCN so với PhoBERT: hiệu số −1,21 điểm, p < 0,001, khoảng tin cậy không chứa
số 0. Nhưng ở seed 42 ASGCN lại hơn 0,20 điểm. Kiểm định đúng, và kết luận "cú pháp làm hại"
vẫn chưa được phép rút ra, vì nguồn bất định lớn hơn (seed) nằm ngoài kiểm định. Quy ước của
chuyên đề: đáng tin khi p < 0,05 **và** cùng dấu ở cả ba seed.

### 3.3. Kết quả

| A | B | Hiệu số macro-F1 | p | Hiệu số accuracy | p | Cùng dấu ba seed? |
|---|---|---|---|---|---|---|
| BiLSTM | Từ điển | +27,09 | < 0,001 | +11,73 | < 0,001 | Có |
| PhoBERT | BiLSTM | +7,15 | < 0,001 | +5,44 | < 0,001 | Có |
| ASGCN | PhoBERT | −1,21 | < 0,001 | −0,53 | 0,001 | Không |
| ASGCN nối gốc | ASGCN | +0,83 | < 0,001 | +0,32 | 0,021 | Không |
| Sentic-GCN | ASGCN | +1,07 | < 0,001 | +0,12 | 0,504 | Không |
| ASGCN nối gốc | PhoBERT | −0,38 | 0,205 | −0,21 | 0,200 | |
| Sentic-GCN | PhoBERT | −0,14 | 0,630 | −0,41 | 0,021 | |

Đọc: chỉ hai bậc đầu của thang qua được cả hai điều kiện. Sentic-GCN và ASGCN nối gốc không
khác PhoBERT về macro-F1. Sentic-GCN hơn ASGCN về macro-F1 nhưng không hơn về accuracy, khớp
với nhận định cũ rằng nó đổi lỗi ở lớp lớn lấy điểm ở lớp trung tính.

### 3.4. Số liệu SƠ BỘ trên 397 dòng đã gán

**Chưa được dùng trong báo cáo.** Chưa đủ 100 dòng mỗi nhóm, chưa có người chú thích thứ hai,
định nghĩa lớp trung tính chưa chốt. Tính bằng đoạn mã tạm chỉ đọc file `.xlsx`.

Accuracy (%) chấm theo **nhãn gốc**, trung bình ba seed:

| Nhóm bạn gán | Số dòng | BiLSTM | PhoBERT | ASGCN | ASGCN nối gốc | Sentic-GCN |
|---|---|---|---|---|---|---|
| regular | 196 | 86,2 | 90,3 | 89,1 | 90,8 | 91,0 |
| negation | 53 | 80,5 | 88,1 | 84,3 | 87,4 | 89,9 |
| contrast | 99 | 74,7 | 86,5 | 85,2 | 87,2 | 91,6 |
| both | 48 | 75,0 | 72,9 | 76,4 | 75,7 | 72,2 |

Ba điều thấy được, đều ở mức dấu hiệu:

1. **Chỉ riêng phủ định hoặc chỉ riêng chuyển ý làm PhoBERT tụt ít:** 2 đến 4 điểm so với nhóm
   thường. Với 53 và 99 dòng, mức chênh này nằm trong sai số.
2. **Khi một khía cạnh chịu cả hai hiện tượng, mọi mô hình tụt mạnh:** PhoBERT từ 90,3 xuống
   72,9. Đây là dấu hiệu rõ nhất, nhưng mới 48 dòng.
3. **Mô hình yếu hơn tụt nhiều hơn:** BiLSTM tụt 11,5 điểm ở nhóm chuyển ý, PhoBERT tụt 3,8.

Nếu chấm theo nhãn **bạn cho là đúng**, mọi mô hình tụt xuống khoảng 75 % ở cả nhóm thường. Đó
không phải mô hình kém đi mà là 22,9 % số dòng bạn không đồng ý với nhãn gốc; xem mục 7.

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao |
|---|---|---|---|
| Đơn vị lấy mẫu | Câu | Mẫu | Mẫu cùng câu không độc lập |
| Xử lý ba seed | Kiểm định trên trung bình ba seed | Kiểm định riêng từng seed rồi gộp p | Gộp p cần giả định độc lập mà ba lần chạy trên cùng tập kiểm tra không có |
| Cặp so sánh | Bảy cặp định trước | Mọi cặp | So mọi cặp rồi chọn cặp đẹp là câu cá |
| Hai file khảo sát | Viết bản thẩm định riêng, không sửa file của học viên | Sửa thẳng | File là của học viên; và nguồn của báo cáo vẫn là ma trận |
| Số liệu sơ bộ | Chỉ ghi ở phiếu này | Đưa vào mục 4.6 | Chưa qua kappa, chưa đủ mẫu |
| Ô kiểm tra trùng nhãn gốc | Tự quy về `dong_y` lúc ghi CSV, có in ra | Báo lỗi và chặn | Nghĩa của hai cách ghi là một; chặn thì 397 dòng không vào được CSV |

## 5. ĐIỂM NỐI

- Bảng 4.6 phải sinh lại khi thêm mô hình (mốc tham chiếu bằng mô hình ngôn ngữ lớn, hoặc mô hình của Chuyên đề 2).
- Cùng cách lấy mẫu theo câu sẽ dùng cho tập chẩn đoán, nơi số mẫu nhỏ nên khoảng tin cậy còn quan trọng hơn.
- Mục 3.4 là căn cứ cho ba điều chỉnh định hướng ở mục 7.

## 6. KIỂM CHỨNG

```
409 passed
```

- Hàm tính macro-F1 và accuracy của script khớp `sklearn` trên dữ liệu giả.
- Trên kết quả thật, hiệu số quan sát khớp hiệu của hai giá trị trong `metrics.json` tới 1e-9.
  Test này đã bắt được một lỗi thật khi viết: bản đầu trộn macro-F1 với accuracy lúc lấy trung bình.
- Chạy lại với hạt giống lấy mẫu khác: mọi p đổi không quá 0,02, không p nào đổi phía so với 0,05.
- Đã tìm khắp kho: không chi tiết sai nào của hai file khảo sát lọt ra ngoài thư mục của chúng.
- **Chưa kiểm:** số trang và danh sách tác giả của 58 tài liệu trong hai file, ngoài bốn bài đã
  nêu; cuốn Word chưa mở bằng Word.

## 7. TỐI ƯU ĐỀ TÀI — nhận định, không phải quyết định

1. **Điểm tựa của đề tài nên dời từ "phủ định và chuyển ý" sang "khía cạnh chịu đồng thời nhiều
   hiện tượng", nếu số liệu cuối giữ đúng hướng hiện tại.** Thang baseline cho thấy thêm cú pháp
   và điểm cảm xúc lên PhoBERT không hơn PhoBERT. Số sơ bộ cho thấy riêng một hiện tượng chỉ làm
   PhoBERT tụt vài điểm. Chỗ tụt 17 điểm là nhóm `both`. Một mô hình đề xuất nhắm vào đúng nhóm
   đó có chỗ để hơn; nhắm vào phủ định nói chung thì dư địa nhỏ. Cần gán đủ rồi mới chốt.
2. **Nên gán thêm cho nhóm `both` tới khoảng 100 dòng**, ngang ba nhóm kia, vì đây có thể thành
   nhóm quan trọng nhất và 48 dòng cho khoảng tin cậy rộng cỡ ±13 điểm.
3. **Tỉ lệ 22,9 % không đồng ý với nhãn gốc phải được giải quyết trước khi viết bất cứ điều gì
   về lớp trung tính.** 39 trong 57 dòng PRICE trung tính bị bạn cho là tích cực. Nếu bài gốc
   quy ước như vậy thì cột kiểm tra của bạn phải theo quy ước đó. Nếu không thì đây là một phát
   hiện về chất lượng nhãn, đáng một mục trong Chương 5, và giải thích một phần vì sao mọi mô
   hình đều yếu ở lớp trung tính.
4. **Phủ định viết tắt** (41 % câu có phủ định chỉ dùng "ko", "k") là phát hiện chắc chắn nhất
   hiện có và rẻ để khai thác: một thí nghiệm thăm dò đổi dạng viết tắt về "không" trước khi tách
   từ, rồi đo lại, không cần mô hình mới.
5. **Hai rủi ro về tính trung thực còn mở:** GAP-026 (cách mô tả việc tìm tài liệu) và tám tài
   liệu viết theo trí nhớ trong `tai_lieu.json`.

Việc của bạn: `pLan/chuyende1/VIEC_CAN_LAM.md`.
