# PHIẾU BÀN GIAO — [CD1.10e] Điền mục 4.5: chi phí suy luận đo trên Kaggle

Ngày 16/10/2026. Học viên chạy notebook `notebooks/kaggle_do_chi_phi.ipynb` trên Kaggle, mang `results/cost_profile.json`
về và yêu cầu điền mục 4.5.

## 1. ĐÃ LÀM GÌ

| File | Tạo/Sửa | Mô tả |
|---|---|---|
| `results/cost_profile.json` | Học viên mang về, đưa vào kho | Số đo của sáu mô hình trên Tesla T4, commit `e4cc63a` |
| `chuyende1/figures/hinh_4_2_danh_doi_chi_phi.png` | Tạo | Hình 4.2 vẽ từ số đo thật |
| `scripts/make_figures.py` | Sửa | Khung (a) có vạch 0,1 để đọc được điểm của mô hình từ điển; khung (b) ghi tên cạnh điểm vì các mô hình đồ thị chồng lên nhau |
| `scripts/doi_chieu_chuong4.py` | Sửa | Kiểm hai cột mới của Bảng 4.6 (gắn đúng hàng của từng mô hình) và chín con số, câu so sánh của đoạn kết quả; file chi phí thiếu mô hình thì báo lệch thay vì dừng |
| `tests/test_doi_chieu_chuong4.py` | Sửa | Thêm 3 test |
| `chuyende1/report/nhap_rut_gon/Chuong4_ThucNghiem.md` | Sửa, không lên GitHub | Bảng 4.6 thêm hai cột; hai đoạn kết quả; Hình 4.2; bỏ dòng [TODO] của mục 4.5 |
| `chuyende1/report/nhap_rut_gon/TrangDau.md` | Sửa, không lên GitHub | Phần tóm tắt không còn ghi chi phí suy luận là đang làm |
| `chuyende1/report/ChuyenDe1_NguyenMinhTrong_rutgon.docx` | Ghép lại, Word cập nhật trường và lưu | Sao lưu `..._rutgon.20261016-031610.docx.bak` |

## 2. KẾT QUẢ ĐO

Tesla T4, một lần chạy, torch 2.11.0, transformers 5.16.1. Thời gian là mili giây cho một mẫu, trung vị ba lần lặp.

| Mô hình | Trọng số | Lô 1 | Lô 32 | Bộ nhớ đỉnh lô 32 (MB) | Dự đoán khác (lô 1 / 32) |
|---|---|---|---|---|---|
| Từ điển | đã huấn luyện | 0,243 | 0,027 | 9,3 | 0 / 0 |
| BiLSTM | đã huấn luyện | 1,967 | 0,108 | 133,5 | 59 / 10 |
| PhoBERT | khởi tạo | 8,941 | 5,548 | 657,9 | không kiểm được |
| ASGCN | khởi tạo | 11,557 | 6,069 | 662,4 | không kiểm được |
| ASGCN nối gốc | đã huấn luyện | 11,712 | 6,097 | 662,4 | 0 / 0 |
| Sentic-GCN | đã huấn luyện | 11,778 | 6,179 | 662,4 | 0 / 0 |

Đọc ra: ba mô hình đồ thị chậm hơn PhoBERT 29 đến 32 % ở lô 1 và 9 đến 11 % ở lô 32, bộ nhớ đỉnh cao hơn 4,5 MB, và
macro-F1 không cao hơn PhoBERT (mục 4.4). Sentic-GCN chậm hơn ASGCN 0,22 ms ở lô 1. Lệch dự đoán của BiLSTM giống hệt
lần đo trên CPU ngày 13/10 (GAP-035), nên không do Kaggle.

## 3. VIẾT VÀO BÁO CÁO THẾ NÀO

- Hai cột thêm vào Bảng 4.6 thay vì một bảng mới: thêm bảng sẽ đổi số mọi bảng sau nó. Thời gian ghi hai chữ số thập
  phân, dạng "lô 1 / lô 32"; bộ nhớ ghi một chữ số thập phân để mức chênh 4,5 MB trong lời văn khớp với bảng.
- Tên bảng giữ cụm "Số tham số và thời gian huấn luyện" (công cụ đối chiếu đòi cụm này) và thêm phần chi phí suy luận.
  Cột "Thiết bị" đổi thành "Thiết bị huấn luyện" cho khỏi lẫn với thiết bị đo.
- Lời văn ghi rõ: đo trên Tesla T4 của Kaggle; PhoBERT và ASGCN đo với trọng số lúc khởi tạo và vì sao vẫn dùng được;
  ba mô hình còn bộ trọng số cho đúng từng dự đoán; BiLSTM lệch vì dự đoán đổi theo kích thước lô.
- Câu "phần thời gian thêm đến từ các thành phần mà mô hình đồ thị có thêm" chỉ nêu khác biệt kiến trúc ở mục 4.3 (gộp
  subword về mức từ, ma trận kề, hai lớp GCN, lớp attention theo khía cạnh); không có phép đo tách từng thành phần.
- Câu về lô 64 của BiLSTM lấy từ lần đo trên CPU ngày 13/10 ghi ở GAP-035, không phải lần đo trên Kaggle.

## 4. QUYẾT ĐỊNH THIẾT KẾ

- Hình 4.2 dùng thời gian ở lô 1: đó là độ trễ khi xử lý từng bình luận một. Lô 32 nằm ở bảng.
- Ở khung (b), ASGCN nối gốc và Sentic-GCN chỉ cách nhau 0,07 ms nên điểm chồng nhau. Không dịch điểm (sẽ sai số
  liệu); ghi tên trực tiếp cạnh điểm, tên bên trái được đẩy ra xa để không chạm vạch sai số của ASGCN.
- Notebook Kaggle đã chạy (`notebooks/da-chay/cost/phien-2026-10-16-kaggle.ipynb`) chưa đưa vào kho: output có đường
  dẫn chứa tên tài khoản Kaggle của học viên, mà kho GitHub công khai. Chờ học viên quyết.

## 5. ĐIỂM NỐI VỚI STEP SAU

Chương 4 còn đúng một chỗ trống: kết quả GPT-4o ở cuối mục 4.4 (E9). Câu về BiLSTM ở mục 4.5 nên được xem lại cùng E10
(GAP-035): nếu học viên chọn sửa mô hình và huấn luyện lại thì câu đó và các con số của BiLSTM đều đổi.

## 6. KIỂM CHỨNG

```
profile_cost.py --kiem                  dùng được cho báo cáo; 3 dòng chú ý (BiLSTM lô 1, PhoBERT và ASGCN khởi tạo)
doi_chieu_chuong4.py                    bản chính 239 chỗ, khớp 239 (trước 224); bản đầy đủ 174, khớp 174
  thử ngược trên bản sao                 sửa 6,10 thành 6,11, 662,4 thành 662,5, "29 đến 32" thành "29 đến 31", 0,22 thành 0,21,
                                        37 thành 36: cả sáu chỗ bị báo lệch, hàng sai bị chỉ đúng tên mô hình
pytest tests/ -q                        520 passed, 1 skipped
Word, file bản chính                     68 trang; Chương 4 trang 21 đến 39 (19 trang); danh sách hình 2 mục; 1 dòng [TODO];
                                        Bảng 4.6 rộng 438,9 pt trong vùng chữ 439,4 pt; Hình 4.2 rộng 15 cm
Hình 4.2                                 đã xem ảnh sau từng lần vẽ: nhãn không chồng, trục có vạch 0,1
```

## 7. DỪNG LẠI VÀ HỎI

1. Có đưa notebook Kaggle đã chạy vào kho không? Nếu có, Claude thay tên tài khoản trong output bằng `<tai-khoan>`
   trước khi commit; hoặc giữ notebook chỉ ở máy.
2. Có push commit này không?
3. E9 (GPT-4o) và E10 (GAP-035) vẫn chờ bạn.
