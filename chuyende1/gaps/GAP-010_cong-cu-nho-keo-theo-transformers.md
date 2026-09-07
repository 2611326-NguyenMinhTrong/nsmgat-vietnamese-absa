# GAP-010 — Công cụ nhỏ kéo theo cả `transformers` chỉ để đọc một file YAML

**Ngày phát hiện:** 07/09/2026 · **Phát hiện bởi:** học viên (chạy thử `try_lexicon.py`)
**Loại:** code · **Mức độ:** nhẹ · **Trạng thái:** ✅ Đã sửa

---

## 1. Sai ở đâu

Học viên chạy `python scripts/try_lexicon.py --text "..."` và nhận:

```
ModuleNotFoundError: No module named 'transformers'
```

Truy vết chuỗi import:

```
try_lexicon.py
  └─ from nsmgat.train import load_config        ← chỉ cần 1 hàm đọc YAML ~15 dòng
       └─ nsmgat/train.py
            └─ from transformers import AutoTokenizer   ← ở cấp module!
```

`LexiconModel` **không dùng tokenizer**, không dùng `transformers` ở bất cứ đâu. Nhưng công
cụ vẫn sập vì `train.py` import `AutoTokenizer` ở cấp module, và `load_config` lại nằm trong
chính file đó.

## 2. Hai nguyên nhân, tách bạch

**(a) Nguyên nhân trực tiếp — của học viên:** chạy bằng `python` (Python hệ thống) thay vì
Python của môi trường ảo. Đo được:

| | `transformers` | `torch` | `yaml` |
|---|---|---|---|
| `python` (hệ thống) | ❌ | ✅ | ✅ |
| `.venv\Scripts\python.exe` | ✅ 5.14.1 | ✅ | ✅ |

**(b) Nguyên nhân gốc — của tôi:** đặt `load_config` trong `train.py`. Hàm đó thuần tuý là
**đọc file YAML có kế thừa**, không liên quan gì tới huấn luyện. Để nó ở đó nghĩa là *mọi
công cụ nhỏ muốn đọc config đều bị kéo theo cả `transformers` + `torch`*.

Nếu chỉ sửa (a) — bảo học viên dùng venv — thì lỗi thiết kế (b) vẫn còn, và sẽ cắn lại ở
mọi script nhỏ sau này.

## 3. Đã sửa thế nào

Chuyển `load_config` + `_deep_merge` từ `train.py` sang `utils/io.py` (nơi đã có
`read_jsonl`, `load_yaml`, `save_json`).

- `train.py` import lại từ đó → `from nsmgat.train import load_config` **vẫn chạy**, không phá
  API của ai
- Hợp đồng đóng băng của `train.py` (chữ ký CLI + luồng xử lý) **không đổi** — chỉ dời một
  hàm phụ trợ
- `try_lexicon.py` giờ import `from nsmgat.utils.io import load_config, read_jsonl`

**Kết quả:** công cụ chạy được bằng **cả** `python` hệ thống lẫn venv. Đã kiểm cả hai.

Bổ sung: khi thiếu VnCoreNLP, cảnh báo cũ chỉ nói "tách theo khoảng trắng" mà không nói **hậu
quả**. Đã sửa thành nêu rõ `'màn hình' → 'màn' + 'hình'` thay vì `'màn_hình'` nên tra cứu kém
chính xác, kèm lệnh chạy bằng venv để chính xác.

## 4. Bài học

**Hàm tiện ích thuần tuý (đọc file, xử lý chuỗi) không được nằm trong module có phụ thuộc
nặng.** Vị trí của một hàm quyết định phụ thuộc của mọi thứ import nó.

Cách kiểm rẻ: *"nếu chỉ muốn dùng hàm này thôi thì phải cài những gì?"* — với `load_config`
câu trả lời đúng ra là `pyyaml`, nhưng thực tế là `transformers` + `torch` + toàn bộ cây phụ
thuộc của chúng.

## 5. Có cần đưa vào báo cáo không

- [ ] Có
- [x] **Không** — lỗi kỹ thuật nội bộ, không ảnh hưởng kết quả nghiên cứu.
