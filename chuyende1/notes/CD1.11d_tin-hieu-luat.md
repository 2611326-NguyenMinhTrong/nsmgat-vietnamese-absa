# PHIẾU BÀN GIAO — [CD1.11d] Thí nghiệm can thiệp: PhoBERT có tín hiệu luật về phủ định và chuyển ý

**Ngày:** 01/11/2026 · **Step:** CD1.11d · **Ánh xạ plan gốc:** không có, học viên quyết thêm · **Trạng thái:** mã xong, **chưa chạy**

Câu 2 của giảng viên: "làm thế nào để chứng minh việc mô hình hoá tường minh sẽ cải thiện kết quả". Mục 5.6.2 của báo cáo trả lời là chưa
chứng minh được, chỉ có căn cứ gián tiếp, và chỉ kiểm chứng được bằng thí nghiệm can thiệp. Học viên quyết làm thí nghiệm đó ngay trong
Chuyên đề 1 (01/11/2026).

**Phiếu này và `scripts/phan_tich_tin_hieu_luat.py` được commit TRƯỚC khi có kết quả.** Mục 2 là tiêu chí đặt trước. Sau khi có số, không
sửa tiêu chí; muốn đo thêm thì thêm phép đo và ghi là phân tích sau khi xem.

---

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Một câu mô tả |
|---|---|---|
| `src/nsmgat/data/tin_hieu_luat.py` | Tạo | Bộ đánh dấu: từ phủ định và phạm vi, từ nối chuyển ý và hai vế. Chỉ đọc mặt chữ |
| `src/nsmgat/models/phobert_luat.py` | Tạo | `PhoBERTLuatModel`: PhoBERT cộng thêm vector theo nhãn luật ở đầu vào |
| `src/nsmgat/train.py` | Sửa | Một dòng trong `MODEL_REGISTRY` |
| `configs/phobert_luat.yaml`, `phobert_luat_phu_dinh.yaml`, `phobert_luat_chuyen_y.yaml` | Tạo | Mỗi file khác file cha đúng một khoá |
| `scripts/phan_tich_tin_hieu_luat.py` | Tạo | `do-phu`: luật bắt được bao nhiêu. `cham`: chấm theo tiêu chí ở mục 2 |
| `notebooks/kaggle_tin_hieu_luat.ipynb` | Tạo | 20 lần chạy, một lần bấm; tự kiểm trên trọng số thật trước khi tốn giờ GPU |
| `tests/test_tin_hieu_luat.py`, `tests/test_phan_tich_tin_hieu_luat.py` | Tạo | 25 và 18 test |
| `chuyende1/MODULE.md`, `SO_TAY_LENH.md` (chỉ ở máy), `pLan/chuyende1/progress_cd1.md` | Sửa | Sổ sách |

Chưa chạy huấn luyện. Lệnh của một lần chạy, nằm trong notebook:

```
python -m nsmgat.train --config configs/phobert_luat.yaml --model phobert_luat --exp-name phobert_luat --seed 42
```

---

## 2. ĐỂ LÀM GÌ, VÀ TIÊU CHÍ ĐẶT TRƯỚC

**Vấn đề:** báo cáo chưa có căn cứ trực tiếp nào cho việc xử lý tường minh hai hiện tượng; mọi căn cứ đều từ công trình khác hoặc từ ước lượng
trần. **Sau step này:** có một phép đo can thiệp trên chính dữ liệu này, dù kết quả dương hay âm.

**Câu hỏi được trả lời:** đưa thêm tín hiệu từ khoá về phủ định và chuyển ý ở mức từ, giống nhau cho mọi khía cạnh, vào đầu vào của PhoBERT thì
macro-F1 có tăng không, và nếu tăng thì có phải nhờ hai hiện tượng đó không. **Không** trả lời được: tín hiệu theo từng khía cạnh, luật có độ
tin cậy, đồ thị luật.

**Thí nghiệm** (học viên chọn), 5 seed 42, 1337, 2024, 7, 123, cùng một phiên Kaggle T4 x2:

| `--exp-name` | Config | Vai trò |
|---|---|---|
| `phobert_cung_phien` | `configs/phobert.yaml` | Đối chứng chính |
| `phobert_luat` | `configs/phobert_luat.yaml` | Thí nghiệm chính |
| `phobert_luat_phu_dinh` | `configs/phobert_luat_phu_dinh.yaml` | Loại bỏ: chỉ kênh phủ định |
| `phobert_luat_chuyen_y` | `configs/phobert_luat_chuyen_y.yaml` | Loại bỏ: chỉ kênh chuyển ý |

**Tiêu chí, theo thứ tự.** Khớp các điều kiện ở mục 5.6.2:

1. **Công nhận cải thiện.** Một phép chính duy nhất: macro-F1 trên toàn tập kiểm tra, `phobert_luat` so với `phobert_cung_phien`. Công nhận khi
   đồng thời: hiệu số dương; p bootstrap theo bình luận nhỏ hơn 0,05; cùng dấu ở cả năm seed (tiêu chí mục 4.2); p hoán vị seed nhỏ hơn 0,05.
2. **Quy được cho hai hiện tượng.** Chỉ xét khi đã công nhận ở bước 1. Hiệu của hiệu số macro-F1 giữa bình luận có từ khoá và bình luận không có từ
   khoá nào phải có khoảng tin cậy 95 % nằm hẳn trên 0. Bình luận không có từ khoá có đầu vào y hệt `phobert`, nên là nhóm đối chứng tự nhiên.
3. **Phép phụ, chỉ đọc như dấu hiệu, không hiệu chỉnh so nhiều lần:** F1 lớp trung tính; bình luận trái nhãn; các nhóm của tập chẩn đoán, trên mọi dòng
   và trên dòng đồng ý với nhãn gốc; hiệu của hiệu số trên tập chẩn đoán; số lỗi ước lượng theo ô; so với `phobert` đã công bố và `asgcn_khong_gcn`.
4. **Loại bỏ.** Mỗi biến thể so với `phobert_cung_phien`, và `phobert_luat` so với mỗi biến thể. Chỉ dùng để nói kênh nào đem lại phần tăng khi bước 1 đạt.

**Cách đọc từng kết cục, viết trước:**

| Kết cục | Báo cáo được nói | Báo cáo không được nói |
|---|---|---|
| Đạt 1 và 2 | Trên dữ liệu này, tín hiệu từ khoá ở đầu vào đem lại mức tăng đo được, và phần tăng nằm ở nơi luật tác động | Hướng Neuro-Symbolic Multi-Graph đã được chứng minh; đồ thị có ích |
| Đạt 1, không đạt 2 | Có mức tăng, nhưng chưa quy được cho hai hiện tượng | Nhờ xử lý phủ định, chuyển ý |
| Không đạt 1 | Tín hiệu này không đem lại lợi ích đo được; phép đo không phát hiện được hiệu số dưới khoảng 0,3 điểm | Mô hình hoá tường minh là vô ích; hướng theo từng khía cạnh đã bị bác bỏ |

**Độ nhạy của phép đo, tính trước:** độ lệch chuẩn giữa các seed của PhoBERT là 0,256 điểm. Mô phỏng phép hoán vị với 5 seed mỗi bên: hiệu số thật 0,3 điểm
đạt p < 0,05 khoảng 33 % số lần, 0,4 điểm 54 %, 0,5 điểm 75 %, 0,6 điểm 89 %. Với 3 seed mỗi bên, p nhỏ nhất là 0,1 nên không bao giờ đạt. Mọi chênh lệch giữa các
mô hình dùng PhoBERT ở Chương 4 đều dưới 1 điểm, và Krishna và cộng sự thấy luật chuyển ý gần như hết tác dụng trên ELMo, nên kết cục "không đạt 1" là có thể xảy ra.

**Hạn chế biết trước:**

1. Nhãn giống nhau cho mọi khía cạnh của một bình luận; mục 5.6.3 nói tín hiệu phải khác theo khía cạnh. Mô hình chỉ có thể tự nối nhãn với khía cạnh qua self-attention.
2. Luật không có độ tin cậy, và đúng dưới ba phần năm số mẫu nó bắt ở mức khía cạnh (mục 5.3).
3. Danh sách từ khoá được chọn sau khi đếm trên tập kiểm tra, ở bước dựng tập chẩn đoán (CD1.8a). Việc chọn dựa trên số đếm và từ loại, không dựa trên nhãn cảm xúc và không dựa trên kết quả mô hình. Ở step này không thêm, không bớt từ nào.
4. Người chú thích thứ hai (điều kiện 3) và bộ cặp câu tối thiểu (điều kiện 5) chưa có. `best.pt` của 10 lần chạy chính được giữ trong output Kaggle, để sau chạy phép cặp câu mà không phải huấn luyện lại.
5. Không dò siêu tham số, đúng như mọi mô hình ở Chương 4. Lớp nhúng nhãn học với learning rate của đầu phân loại, theo quy tắc sẵn có của trainer.

---

## 3. CƠ CHẾ HOẠT ĐỘNG

**Ý tưởng:** PhoBERT đọc câu qua vector của từng từ. Ta cộng thêm vào vector đó một vector nhỏ cho biết từ này đứng ở đâu trong cấu trúc phủ định, chuyển ý. Vector thêm vào bắt đầu bằng 0, nên ban đầu mô hình chính là PhoBERT; nó chỉ khác đi khi huấn luyện thấy có ích.

**Ví dụ:** bình luận "pin không trâu lắm nhưng màn_hình đẹp", khía cạnh BATTERY. Đầu vào `<s> pin không trâu lắm nhưng màn_hình đẹp </s></s> pin </s>`.

| Từ | pin | không | trâu | lắm | nhưng | màn_hình | đẹp | (vế khía cạnh) |
|---|---|---|---|---|---|---|---|---|
| Kênh phủ định | 0 | TỪ | PHẠM VI | PHẠM VI | 0 | 0 | 0 | 0 |
| Kênh chuyển ý | NHƯỢNG | NHƯỢNG | NHƯỢNG | NHƯỢNG | TỪ | NHẤN | NHẤN | 0 |

Vector đầu vào của "trâu" là `nhúng(trâu) + nhúng_phủ_định(PHẠM VI) + nhúng_chuyển_ý(NHƯỢNG)`. Với 768 chiều, kênh phủ định có 3 nhãn và kênh chuyển ý có 4 nhãn, số tham số thêm là 7 × 768 = 5.376, từ 135.000.579 thành 135.005.955. Từ không có nhãn nào được cộng 0 và hàng đó không bao giờ được cập nhật. Cùng bình luận đó với khía cạnh SCREEN thì nhãn y hệt, chỉ khác vế khía cạnh; đó là hạn chế 1.

**Từ nối nhượng bộ đảo vị trí:** "tuy pin yếu, máy đẹp" và "máy đẹp dù pin yếu" đều có "pin yếu" là vế nhượng, "máy đẹp" là vế nhấn, dù từ nối đứng ở hai chỗ.

**Vì sao hiệu số sạch:**

- Cùng seed thì lớp phân loại, thứ tự mini-batch và dropout trùng với `phobert`, vì tạo lớp mới không rút số ngẫu nhiên.
- Bình luận không có từ khoá nào có đầu vào y hệt `phobert`, chỉ khác do trọng số của bộ mã hoá đã học khác đi. Nhờ vậy so được nơi luật chạm tới với nơi không chạm tới, trên 2.454 mẫu không có từ khoá so với 4.268 mẫu có từ khoá, chứ không chỉ trên vài trăm dòng của tập chẩn đoán.

**Chỗ dễ hiểu sai nhất:**

- Nhãn **không** bảo mô hình lật cực. Nó chỉ nói "từ này ở trong phạm vi phủ định". Mô hình tự học việc đó có nghĩa gì, kể cả việc không có nghĩa gì.
- Đối chứng là PhoBERT **chạy lại**, không phải 5 seed đã công bố. Ba trong năm seed cũ chạy trên Colab, và PhoBERT seed 42 chạy lại trên Kaggle đã lệch 0,17 điểm, cùng cỡ với hiệu ứng cần đo.
- p hoán vị là phép chặt nhất trong các tiêu chí ở đây: nó so hiệu số với chính dao động giữa các lần huấn luyện lại.

---

## 4. QUYẾT ĐỊNH THIẾT KẾ

| Quyết định | Đã chọn | Phương án loại | Vì sao loại |
|---|---|---|---|
| Đưa tín hiệu vào đâu | Cộng vào vector đầu vào của từng từ | Nối cờ "có phủ định" vào vector `<s>` trước lớp phân loại | Chỉ mức bình luận, không mang cấu trúc, không phải cơ chế mục 5.6.3 mô tả |
| Dạng tín hiệu | Lớp nhúng học được | Chèn token đặc biệt vào câu | Đổi độ dài, đổi chỗ cắt câu dài, đổi đầu vào của cả bình luận không có từ khoá |
| Khởi tạo | Bằng 0, không rút số ngẫu nhiên | Ngẫu nhiên | Mỗi seed thành một lần khởi tạo khác, hiệu số lẫn dao động |
| Số kênh | Hai kênh độc lập | Một kênh gộp sáu nhãn | Một từ có thể mang cả hai; tắt một luật phải không đổi luật kia |
| Phạm vi phủ định | Đến dấu câu hoặc từ nối gần nhất, không giới hạn số từ | Cửa sổ N từ | N là siêu tham số phải dò. Trên tập huấn luyện trung vị 4 từ, phân vị 90 là 11 từ |
| Vế chuyển ý | Trong một câu, không dừng ở dấu phẩy; từ nhượng bộ xử lý riêng | Coi mọi từ nối như "nhưng" | "tuy A, B" sẽ gán ngược hai vế |
| Danh sách từ khoá | Bản chép, có test canh hai nơi không lệch | Chuyển danh sách sang `src/`, script import lại | Phải sửa script đã đóng băng; đúng cách đã dùng với `TEN_LOP` |
| Nơi đặt mã | `src/nsmgat/data/`, `models/` | `src/nsmgat/rules/` | `rules/` thuộc Chuyên đề 2 (`MODULE.md` mục 2.3); đây không phải S2.2 |
| Đối chứng chính | Chạy lại trong cùng phiên | `phobert` đã công bố | Lẫn Colab với Kaggle. Học viên chọn |
| Biến thể loại bỏ | Chạy luôn trong phiên này, xếp cuối hàng | Chạy sau nếu bước 1 đạt | Không cần mở phiên thứ hai, môi trường Kaggle có thể đã đổi. Học viên chọn |

---

## 5. ĐIỂM NỐI VỚI STEP SAU

- **Học viên chạy Kaggle** theo ô đầu của notebook: gắn dataset cũ, GPU T4 x2, Internet On, Save & Run All. Khoảng 4 đến 5 giờ.
- Mang `ket_qua.zip` về `data\cache\kaggle_tin_hieu_luat\` rồi báo Claude. Claude kiểm từng file, đưa vào `results/`, chạy `phan_tich_tin_hieu_luat.py cham`.
- Sau đó sửa báo cáo theo đúng cách đọc ở mục 2: mục 5.6.2 hiện viết "chỉ kiểm chứng được bằng thí nghiệm can thiệp ở chuyên đề tiếp theo" phải đổi, Bảng 5.3 hàng đồ thị luật, Chương 6, phần Tóm tắt. Word sửa bằng COM và ghép riêng Chương 5, 6 như quy trình cũ.
- Điều kiện 3 (người thứ hai) và điều kiện 5 (cặp câu tối thiểu) vẫn là việc của Chuyên đề 2.

---

## 6. KIỂM CHỨNG

```
pytest tests -q            624 passed, 1 skipped (trước step này 581 passed, 1 skipped; thêm 25 + 18 test)
doi_chieu_chuong4/5/6      mã 0; step này không sửa báo cáo, file Word giữ nguyên mã băm B2734D19...
```

**Trên trọng số PhoBERT thật, dữ liệu dev, CPU (script tạm, không nằm trong repo):**

```
so tham so phobert: 135000579 | phobert_luat: 135005955
lop phan loai trung khi cung seed: True
so mau trong batch: 16 | co tu khoa: 12
sai khac lon nhat cua logits (tin hieu 0, trong so that): 0.0
phu_dinh chuan gradient theo nhan: [0.0, 0.03877, 0.18968]
chuyen_y chuan gradient theo nhan: [0.0, 0.01409, 0.12333, 0.32271]
```

Sau một bước chỉ cập nhật lớp nhúng nhãn, logits của 12 mẫu có từ khoá đổi, của 4 mẫu không có từ khoá giữ đúng 0,000000. Notebook lặp lại phép kiểm trùng khớp này trên Kaggle trước khi huấn luyện.

**Độ phủ của luật** (`do-phu`). Trên tập huấn luyện, dùng khi thiết kế: 7.669 bình luận; có từ phủ định 55,1 %, có từ nối 28,0 %, cả hai 18,3 %, không từ khoá nào 35,3 %; phạm vi phủ định trung vị 4 từ, phân vị 90 là 11 từ, rỗng 4,9 %. Trên tập kiểm tra, xem sau khi đã chốt luật, không dùng để chỉnh gì: 2.187 bình luận; 55,9 %, 26,2 %, 17,6 %, 35,5 %; trung vị 4 từ, phân vị 90 là 11 từ, rỗng 4,6 %.

**Công cụ chấm:** test trên repo giả cho đúng kết luận ở năm tình huống: dự đoán y hệt, tăng đúng chỗ có từ khoá, tăng ở chỗ luật không chạm tới, một seed ngược chiều, thiếu seed. Chạy thử trên dữ liệu thật với dự đoán đóng vai (`asgcn_khong_gcn` đóng `phobert_luat`, `phobert` đóng đối chứng) để bắt lỗi chạy và đo giờ: 190 giây với 10.000 lần lấy mẫu. Các con số của lượt đó không phải kết quả thí nghiệm.

**Chưa kiểm được ở máy này:** chưa có lần huấn luyện thật nào trên GPU với `phobert_luat`; notebook dựng từ `kaggle_doi_chung_do_thi.ipynb` đã chạy thành công, chỉ đổi danh sách việc, ô kiểm trọng số thật và ô tổng hợp, nhưng bản mới chưa chạy trên Kaggle. Đọc kỹ tab *Logs* sau 10 phút đầu như ô đầu của notebook hướng dẫn.

---

## 7. DỪNG LẠI VÀ HỎI

Không còn câu hỏi mở: mô hình, seed, phạm vi chạy, commit đều đã do học viên chọn ngày 01/11/2026. Việc tiếp theo là học viên bấm chạy trên Kaggle.

---

## 8. GHI CHÚ SAU KHI TRAO ĐỔI

| Câu hỏi hay yêu cầu của học viên | Trả lời tóm tắt | Có dẫn tới thay đổi không |
|---|---|---|
| | | |
