# PHIẾU BÀN GIAO — [CD1.10c, CD1.7] Chuẩn bị mục 4.3 và 4.5 để chỉ còn chờ số đo

Ngày 16/10/2026. Học viên yêu cầu push ba commit và "làm công việc kế tiếp theo plan để xong Chương 4, chưa
sang Chương 5". Hai phần còn thiếu của Chương 4 là mốc tham chiếu GPT-4o (mục 4.3, gói CD1.7) và chi phí suy
luận (mục 4.5, gói CD1.10). Cả hai cần một lần chạy mà Claude không làm thay được: gọi API có trả phí bằng khoá
của học viên, và đo trên GPU của Colab. Bước này làm hết phần không cần số đo.

## 1. ĐÃ LÀM GÌ — danh sách thay đổi

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `scripts/profile_cost.py` | Sửa | Thêm `--kiem [FILE]`: kiểm `cost_profile.json` mang về trước khi đưa vào báo cáo; thêm hằng `LAP_MAC_DINH`, `NGUONG_KHAC` |
| `tests/test_profile_cost.py` | Sửa | Thêm 4 test cho phần kiểm |
| `scripts/make_figures.py` | Sửa | Thêm Hình 4.2 (macro-F1 theo thời gian suy luận, hai khung); cờ `--chi-phi`, `--ket-qua`; màu mô hình từ điển đổi sang xám đậm |
| `tests/test_make_figures.py` | Tạo | 4 test cho Hình 4.2, dùng số đo giả |
| `scripts/doi_chieu_chuong4.py` | Sửa | Kiểm mô tả mốc GPT-4o ở mục 4.3 và cách đo ở mục 4.5 của bản chính (9 chỗ mới) |
| `tests/test_doi_chieu_chuong4.py` | Sửa | Thêm 2 test |
| `chuyende1/report/nhap_rut_gon/Chuong4_ThucNghiem.md` | Sửa, không lên GitHub | Mục 4.3: đoạn "Mốc tham chiếu GPT-4o"; cuối mục 4.4: một dòng [TODO] cho kết quả; mục 4.5: đoạn cách đo thay cho dòng [TODO] cũ |
| `chuyende1/report/nhap_rut_gon/tai_lieu.json` | Sửa, không lên GitHub | Thêm GPT-4o System Card (arXiv:2410.21276), đã mở trang arXiv để đối chiếu tên, tác giả đầu, năm |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` | Ghép lại, Word cập nhật trường và lưu | Sao lưu `..._rutgon.20261016-005722.docx.bak` |
| `chuyende1/gaps/GAP-039_...md`, `INDEX.md` | Tạo, sửa | Máy có GPU GTX 1650 mà nhiều tài liệu ghi "không có GPU" |
| `chuyende1/notes/CD1.10b_...md` | Sửa | Dòng đính chính trỏ về GAP-039 |

## 2. ĐỂ LÀM GÌ — vấn đề mà phần này giải quyết

Khi học viên mang số đo về, Chương 4 phải xong trong một lượt và không có con số nào chưa được kiểm. Muốn vậy,
mọi thứ không phụ thuộc số đo phải có sẵn: lời văn mô tả cách làm, hình vẽ được từ file kết quả, một lệnh nói
ngay file mang về có dùng được không, và công cụ đối chiếu biết phải kiểm gì.

## 3. CƠ CHẾ HOẠT ĐỘNG — phần để học

- Đoạn mới ở mục 4.3 chỉ nêu điều có trong mã và cấu hình: tên mô hình, nhiệt độ 0, câu trả lời không đọc được
  tính là sai, lời dặn không định nghĩa nhãn, zero-shot một lần, few-shot hai ví dụ mỗi lớp dài 5 đến 40 từ chạy
  ba lần, tập con 500 mẫu (164 tiêu cực, 61 trung tính, 275 tích cực, thuộc 455 bình luận). Công cụ đối chiếu
  đọc lại `configs/llm.yaml`, đếm lại tập con trên tập kiểm tra rồi tìm từng cụm trong chương.
- Đoạn mới ở mục 4.5 nêu cách đo của `profile_cost.py`: cả 6.722 mẫu, lô 1 và 32, không dùng độ chính xác hỗn
  hợp, ba lần lặp lấy trung vị, không tính bước tách subword và bước phân tích cú pháp. Chưa có
  `cost_profile.json` thì công cụ so với giá trị mặc định của công cụ đo và in một dòng CHÚ Ý; có file thì so với
  điều kiện thật ghi trong file. Đo khác điều kiện thì đoạn văn bị báo lệch.
- `profile_cost.py --kiem` chia vấn đề làm hai mức. LỖI (mã thoát 1): thiếu mô hình, không đo trên GPU, hai mô
  hình đo trên hai GPU khác nhau, không đo cả tập kiểm tra, thiếu lô 1 hay 32, hoặc một mô hình có `best.pt` mà ở
  lô 32 khác hơn 10 dự đoán so với file đã công bố. CHÚ Ý: đo với trọng số lúc khởi tạo, đo qua nhiều lần chạy,
  lô 1 khác nhiều dự đoán (GAP-035). Mỗi dòng chú ý là một câu báo cáo phải ghi.
- Hình 4.2: khung (a) có sáu mô hình trên trục thời gian logarit, khung (b) phóng to bốn mô hình dùng PhoBERT.
  Trục macro-F1 lấy trung bình và độ lệch chuẩn ba hạt giống từ `metrics.json`; thời gian lấy từ lô 1.

## 4. QUYẾT ĐỊNH THIẾT KẾ — và phương án đã loại

- Số tham số nằm trong chú giải, không ở diện tích điểm như plan ghi. PhoBERT và ba mô hình đồ thị chỉ khác nhau
  0,87 % số tham số, nên diện tích điểm gần bằng nhau và không cho người đọc thêm gì; còn mô hình từ điển 9 tham
  số thì gần như không vẽ được.
- Hai khung thay vì một: vẽ thử bằng số giả cho thấy ở một khung, ba mô hình đồ thị chồng lên nhau và ASGCN nối
  gốc bị che hẳn.
- Màu: bảng màu cũ có cặp xám nhạt (từ điển) và hồng (ASGCN nối gốc) quá gần nhau, cả với mắt thường. Đổi xám nhạt
  sang xám đậm thì bảng màu qua bước kiểm; cặp gần nhất còn lại vẫn cần hình dạng điểm khác nhau để người mù màu
  đỏ lục phân biệt, và mỗi mô hình đã có hình dạng riêng. Hình 5.1 đến 5.4 vẽ lại sẽ đổi màu theo; các hình đó chưa
  có trong báo cáo.
- Kết quả GPT-4o đặt ở cuối mục 4.4 chứ không ở mục 4.3: mục 4.3 mô tả mô hình, mục 4.4 là kết quả. Chưa dựng
  bảng vì chưa có số; thêm một bảng sẽ đổi số các bảng sau nó, nên làm cùng lúc với số liệu.
- Không viết câu về GAP-035 (dự đoán của BiLSTM đổi theo kích thước lô) vào mục 4.3: việc đó chờ học viên chọn (E10).
- Không đo ở máy: máy có card GTX 1650 nhưng PyTorch trong `.venv` là bản CPU (GAP-039). Đo ở Colab giữ cùng loại
  GPU đã huấn luyện bốn mô hình dùng PhoBERT.
- File Word bản chính được lưu lúc 01:42 ngày 15/10, sau lần ghép ngày 13/10. Trước khi ghép đè, Claude ghép lại
  nội dung ngày 13/10 vào một bản sao, cho Word lưu, rồi so từng đoạn: chữ giống hệt; định dạng chỉ khác ở chỗ Word
  tách một đoạn chữ thành hai mẩu cùng định dạng và ở vị trí dấu kết thúc trường danh sách bảng. Không có chỗ sửa tay.

## 5. ĐIỂM NỐI VỚI STEP SAU

Khi có `results/cost_profile.json`:
1. `profile_cost.py --kiem`; còn LỖI thì dừng và báo học viên.
2. Thêm hai cột (thời gian một mẫu ở lô 1 và 32, bộ nhớ GPU đỉnh) vào Bảng 4.6, điền tên GPU, ghi mô hình nào đo
   với trọng số lúc khởi tạo; `make_figures.py --chi 4.2`, đưa Hình 4.2 vào mục 4.5.
3. Thêm chỗ kiểm cho hai cột mới vào `doi_chieu_chuong4.py`; ghép lại.

Khi có kết quả GPT-4o (bốn lần chạy):
1. `eval_llm.py bang`; viết bảng và đoạn kết quả ở cuối mục 4.4 (sáu mô hình chấm lại trên cùng 500 mẫu và hai
   dòng GPT-4o); ghi phiên bản mô hình API trả về và ngày gọi.
2. Thêm chỗ kiểm; sửa số bảng trong `SO_BANG_RUT_GON` nếu bảng mới làm đổi số các bảng sau.
3. Sửa đoạn cuối phần tóm tắt (đang ghi mục 4.3 và 4.5 còn đang làm).

## 6. KIỂM CHỨNG — bằng chứng chạy thật

```
pytest tests/ -q                       513 passed, 1 skipped (trước bước này 503; test bỏ qua là test chỉ chạy khi có GPU)
doi_chieu_chuong4.py                   bản chính 224 chỗ, khớp 224 (trước 215); bản đầy đủ 174, khớp 174
  thử ngược trên bản sao                đổi 164 thành 165, "ba lần" thành "hai lần", nhiệt độ 0 thành 0,7,
                                        gpt-4o thành gpt-4o-mini: cả bốn bị báo lệch
                                        (lần đầu để lọt 0,7 và gpt-4o-mini vì là chuỗi con; đã sửa)
doi_chieu_ban_rut_gon.py               4 con số lạ (164, 275, 455, 61): nội dung mới chỉ có ở bản chính, đã kiểm ở trên
doi_chieu_ban_goc.py kiem              455 và 500 đứng cạnh trích dẫn GPT-4o bị ghi "chưa có bản gốc": số của chuyên đề
profile_cost.py --kiem                 chưa có file: mã thoát 1, in "Chưa có results\cost_profile.json"
make_figures.py --chi 4.2              chưa có file: in "BỎ QUA Hình 4.2"; vẽ thử bằng số giả vào thư mục tạm, đã xem ảnh
Word, file bản chính                    70 trang (trước 69); Chương 4 trang 21 đến 38 (18 trang); 2 dòng [TODO];
                                        khổ A4; 61 tài liệu tham khảo
nvidia-smi                             GeForce GTX 1650, 4096 MiB, driver 451.67; torch 2.13.0+cpu, cuda: False
```

## 7. DỪNG LẠI VÀ HỎI

1. E8: chạy phép đo trên Colab theo VIEC_CAN_LAM (chạy cả sáu mô hình trong một lần), mang `cost_profile.json` về.
2. E9: xác nhận `gpt-4o` và phương án bốn lần chạy, rồi tự chạy với khoá của bạn (§11k của sổ tay lệnh). Đoạn
   phương pháp ở mục 4.3 đã viết theo đúng phương án này.
3. E10 (GAP-035): giữ nguyên BiLSTM và thêm một câu vào mục 4.3, hay sửa mô hình và huấn luyện lại.
4. GAP-039: câu "máy cá nhân của em không có GPU" trong báo cáo tiến độ gửi cô có cần sửa không.
