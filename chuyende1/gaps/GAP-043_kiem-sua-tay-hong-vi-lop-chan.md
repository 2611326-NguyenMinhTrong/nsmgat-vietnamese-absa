# GAP-043 — Lớp chặn mới của lệnh ghép làm `kiem_sua_tay_word.py` hỏng, chỗ sửa tay của học viên suýt không được phát hiện

**Ngày phát hiện:** 18/10/2026 · **Phát hiện bởi:** Claude Code, khi kiểm file Word trước lúc viết Chương 5
**Loại:** công cụ (thay đổi ở một script làm hỏng script khác dùng nó)
**Mức độ:** trung bình (không mất dữ liệu, nhưng công cụ bảo vệ chỗ sửa tay ngừng chạy gần một ngày mà không ai biết)
**Trạng thái:** ✅ Đã sửa ngày 18/10/2026

---

## 1. Sai ở đâu

Ở CD1.12p (17/10/2026), `scripts/nhap_chuong_vao_docx.py` được thêm lớp chặn: phần sắp bị thay có phương trình Word hay chữ
chỉ số trên, dưới thì lệnh dừng với mã 3, kể cả khi có `--ghi-de`.

`scripts/kiem_sua_tay_word.py` hoạt động bằng cách ghép thử bản nháp vào một BẢN SAO của file Word rồi so chữ. Lần ghép thử đó
gọi chính lệnh ghép, nên từ CD1.12p nó luôn gặp lớp chặn (Chương 2 có 8 phương trình, Chương 4 có 1) và dừng với
`RuntimeError: lệnh ghép thử báo lỗi (mã 3)`. Tức là công cụ kiểm chỗ sửa tay không còn chạy được.

Ngày 18/10, file Word có giờ lưu 17:47 ngày 17/10, sau lần lưu cuối của Claude (17:11): học viên đã sửa thêm ba chỗ (mục 1.3,
hai đoạn ở mục 4.7). Nếu không sửa công cụ thì không biết được ba chỗ đó là gì.

## 2. Phát hiện thế nào

Chạy `kiem_sua_tay_word.py` theo quy trình trước khi đụng file Word, thấy lỗi mã 3 thay cho danh sách chỗ khác.

## 3. Nguyên nhân gốc

Thêm lớp chặn mà không tìm các nơi khác gọi `nhap_chuong_vao_docx.main`. Test của `kiem_sua_tay_word.py` thay lệnh ghép bằng
hàm giả (monkeypatch), nên không test nào chạy hai script cùng nhau. Phiếu CD1.12p ghi `kiem_sua_tay_word.py` ra mã 2 "sau khi
sửa Word": lần chạy đó diễn ra TRƯỚC khi thêm lớp chặn, nên đúng lúc đó nhưng không còn đúng khi commit.

## 4. Ảnh hưởng lan tới đâu

| Bị ảnh hưởng | Có phải sửa theo không |
|---|---|
| `scripts/kiem_sua_tay_word.py` | Có: gọi lệnh ghép với cờ mới `--ghep-thu` |
| `scripts/nhap_chuong_vao_docx.py` | Có: thêm `--ghep-thu`, chỉ dùng khi ghép vào bản sao để so chữ |
| Ba chỗ học viên sửa lúc 17:47 | Đã đưa vào bản nháp ngày 18/10 (sao lưu ở `nhap_rut_gon/sao_luu/20261018-sua-tay-1747/`) |
| `scripts/doi_chieu_chuong4.py` | Có: ba chỗ kiểm ở mục 4.7 đổi theo câu chữ mới của học viên, điều kiện số liệu giữ nguyên |
| File Word | Không đổi |

## 5. Đã sửa thế nào

- `nhap_chuong_vao_docx.py --ghep-thu`: bỏ qua lớp chặn định dạng; trợ giúp của cờ ghi rõ không dùng với file thật.
- `kiem_sua_tay_word.ghep_thu` truyền `--ghi-de --ghep-thu`.
- Hai test mới: `test_ghep_thu_qua_duoc_lop_chan_phuong_trinh` (kiểm cờ được truyền) và một dòng trong
  `test_phan_co_phuong_trinh_hoac_chi_so_thi_khong_ghep_ke_ca_ghi_de` (lệnh ghép với `--ghep-thu` chạy qua phần có phương trình).
- Chạy thật trên file Word: ra mã 1 với ba chỗ; đưa vào bản nháp xong ra mã 2.

## 6. Bài học — phòng lần sau bằng cách nào

Thêm một điều kiện dừng vào một lệnh thì tìm mọi nơi gọi lệnh đó (`grep` tên hàm `main` của module) và chạy chúng một lần với
dữ liệu thật. Kết quả kiểm ghi trong phiếu phải là lần chạy SAU thay đổi cuối cùng trước khi commit.

## 7. Có cần đưa vào báo cáo không

- [ ] Có
- [x] Không — lỗi công cụ nội bộ, không đổi số liệu nào của báo cáo
