# GAP-032 — 60 dòng được gán lại sớm hơn mốc 14 ngày

**Ngày phát hiện:** 13/10/2026 · **Phát hiện bởi:** lệnh `finalize_diagnostic.py kappa` (từ chối chạy)
**Loại:** phương pháp · quy trình
**Mức độ:** trung bình (chặn được trước khi chốt tập; chưa con số nào vào báo cáo)
**Trạng thái:** 🟡 Chờ học viên chọn cách đo lại (ba phương án ở mục 5)

---

## 1. Sai ở đâu

Cách đo độ nhất quán đã chốt ngày 13/10: học viên tự gán lại 60 dòng sau ít nhất 14 ngày, không nhìn
nhãn cũ. Mẫu được rút lúc 01:27 ngày 13/10, mốc sớm nhất là 27/10. Học viên gán lại xong lúc 09:19
ngày 13/10, cùng ngày rút mẫu.

So các bản sao lưu của `candidates.csv` để biết nhãn lần đầu của 60 dòng có từ khi nào:

| Nhãn lần đầu vào CSV | Số dòng | Cách lần gán lại |
|---|---|---|
| Trước 04:56 ngày 11/10 | 32 | từ 2 đến dưới 8 ngày (tập ứng viên có từ 05/10) |
| Từ 04:56 ngày 11/10 đến 00:55 ngày 13/10 | 27 | dưới 2,5 ngày |
| 01:45 ngày 13/10 (dòng đổi theo K2) | 1 | dưới 8 giờ |

Không dòng nào cách đủ 14 ngày.

## 2. Phát hiện thế nào

Lệnh `kappa` đọc ngày trong `data/diagnostic/gan_lai_60.json` và dừng với mã 2. File
`data/diagnostic/kappa.json` không được tạo, nên lệnh `chot` vẫn khoá.

## 3. Nguyên nhân gốc

File `gan_lai_60.xlsx` được sinh ra trước ngày được phép mở 14 ngày. Chốt chặn đặt ở lệnh tính, không
đặt ở file: file mở và điền được bất cứ lúc nào. Lời nhắc cuối phiên trước lại gộp việc này vào cùng
một dòng với hai việc làm được ngay ("sao lưu, đọc 10 ca cùng sai, gán lại 60 dòng từ 27/10").

## 4. Ảnh hưởng lan tới đâu

- Báo cáo: chưa bị ảnh hưởng. Mục 4.1.2 và 4.6 vẫn để trống chờ số đo nhất quán.
- 60 dòng này nay đã được đọc hai lần trong vòng 8 ngày, không dùng lại được cho phép đo cách 14 ngày.
  Tập còn 739 dòng khác (negation 105, contrast 166, both 69, regular 399), đủ để rút một mẫu mới.
- Con số đo sớm là cận trên của độ nhất quán thật, vì người gán có thể còn nhớ nhãn cũ.

## 5. Đã xử lý thế nào, và việc còn mở

Đã làm ngày 13/10:

- Tính riêng độ trùng của hai lần gán và lưu ở `data/diagnostic/kappa_gan_lai_som_20261013.json`, với
  trường `loai` ghi rõ là đo sớm. Tên khác `kappa.json` nên không mở khoá lệnh `chot`.
- Sao một bản file lần 2 thành `data/diagnostic/gan_lai_60.lan2-20261013.xlsx.bak`.
- Lập `chuyende1/report/nhap/lech_gan_lai_1310.md` liệt kê các dòng lệch để học viên xem.

Kết quả đo sớm (không phải số đo chính thức):

| Phép đo trên 60 dòng | Trùng | Kappa |
|---|---|---|
| Nhóm hiện tượng, bốn giá trị | 48 (80,0 %) | 0,733 |
| Có phủ định hay không (negation hoặc both) | 57 (95,0 %) | 0,900 |
| Có chuyển ý hay không (contrast hoặc both) | 51 (85,0 %) | 0,700 |
| Nhãn cảm xúc sau kiểm tra | 50 (83,3 %) | 0,753 |

Trong 12 dòng lệch về hiện tượng, 7 dòng lệch giữa `both` và `negation`. Nhóm `both` giữ nguyên 9 trên
15 dòng. Chỗ không ổn định là việc xét câu có chuyển ý hay không khi câu đã có phủ định; đây cũng là
ranh giới mà kết quả sơ bộ dựa vào để nói nhóm cả hai khó hơn nhóm phủ định.

Về nhãn cảm xúc: lần 1 không đồng ý với nhãn gốc ở 12 dòng, lần 2 ở 7 dòng, cả hai lần ở 5 dòng.

Ba phương án đo lại, chờ học viên chọn:

1. Dùng luôn số đo sớm và ghi đúng khoảng cách thật (dưới 8 ngày). Không tốn thêm công; bằng chứng yếu.
2. Giữ nhãn hiện có. Từ 27/10 rút 60 dòng khác và gán lại; báo cáo cả hai lần đo.
3. Xem 12 dòng lệch để làm rõ quy tắc chuyển ý, soát lại 203 dòng của hai nhóm `negation` và `both`
   theo quy tắc đã rõ, rồi sau 14 ngày kể từ lần soát mới rút 60 dòng khác để đo.

## 6. Bài học

Thứ chưa được phép mở thì đừng sinh ra trước. Mẫu gán lại nên được rút vào đúng ngày gán, khi đó
chốt chặn nằm ở bước tạo file chứ không ở bước tính. Lời nhắc việc có điều kiện ngày tháng phải đứng
riêng một dòng.
