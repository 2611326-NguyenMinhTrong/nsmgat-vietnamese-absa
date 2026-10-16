"""[CD1.12f] Kiểm phần tìm kiếm của scripts/doi_chieu_chuong4.py trên văn bản tí hon, không cần dữ liệu thật."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import doi_chieu_chuong4 as m  # noqa: E402

VAN = """## 4.4. Kết quả

Lời văn có câu cần tìm, cao hơn 1,07 điểm.

Bảng 4.3: Kết quả trên tập kiểm tra của X

| Mô hình | Accuracy |
|---|---|
| PhoBERT   tinh chỉnh | 91,86 |

Bảng C.3: Macro-F1 trên bốn nhóm của tập chẩn đoán

| Mô hình | Thường |
|---|---|
| PhoBERT tinh chỉnh | 90,0 |

Bảng 4.2: Thang mô hình và thành phần được thêm ở mỗi bậc

| Bậc | Mô hình | Số tham số |
|---|---|---|
| 1 | Từ điển | 9 |
| 4 | ASGCN | 136.181.763 |
| 4b | ASGCN nối gốc | 136.181.763 |
"""


def test_moi_bang_duoc_kiem_deu_co_so_o_ban_chinh_va_tu_khoa():
    assert set(m.SO_BANG_RUT_GON) == set(m.TU_KHOA_BANG)
    assert len(set(m.SO_BANG_RUT_GON.values())) == len(m.SO_BANG_RUT_GON)  # không hai bảng nào trỏ về cùng một số


def test_tach_bang_lay_ten_va_hang_bo_khoang_trang_thua():
    b = m.tach_bang(VAN)
    assert list(b) == ["4.3", "C.3", "4.2"]
    assert b["4.3"]["ten"] == "Kết quả trên tập kiểm tra của X"
    assert "| PhoBERT tinh chỉnh | 91,86 |" in b["4.3"]["van"]
    assert b["4.2"]["hang"][-1] == "| 4b | ASGCN nối gốc | 136.181.763 |"
    with pytest.raises(ValueError):
        m.tach_bang(VAN + "\nBảng 4.3: Trùng số\n\n| a |\n")


def test_hang_bang_phai_nam_o_dung_bang():
    b, van = m.tach_bang(VAN), m.chuan(VAN)
    # Bảng 4.5 của bản đầy đủ là Bảng 4.3 của bản chính
    da_kiem, lech, bo_qua = m.tim([("Bảng 4.5, phobert", "| PhoBERT tinh chỉnh | 91,86 |")], van, b, "rut_gon")
    assert (da_kiem, lech, bo_qua) == (1, [], 0)
    # hàng của bảng macro-F1 (4.12, tức C.3) không được tính là có ở bảng accuracy 4.11 (tức 4.8)
    _, lech, _ = m.tim([("Bảng 4.12, dòng 1", "| PhoBERT tinh chỉnh | 91,86 |")], van, b, "rut_gon")
    assert len(lech) == 1 and "nằm ở Bảng 4.3 chứ không ở Bảng C.3" in lech[0][2] and lech[0][0] == "Bảng C.3, dòng 1"
    _, lech, _ = m.tim([("Bảng 4.11, dòng 1", "| PhoBERT tinh chỉnh | 90,0 |")], van, b, "rut_gon")
    assert "bản nháp không có Bảng 4.8" in lech[0][2]
    # ở bản đầy đủ số bảng giữ nguyên
    _, lech, _ = m.tim([("Bảng 4.5, phobert", "| PhoBERT tinh chỉnh | 91,86 |")], van, b, "day_du")
    assert "bản nháp không có Bảng 4.5" in lech[0][2]


def test_cum_chu_loi_van_cau_bo_qua_va_cau_cua_phan_tom_tat():
    b, van = m.tach_bang(VAN), m.chuan(VAN)
    kiem = [("Lời văn, a", "cao hơn 1,07 điểm"), ("Lời văn, b", "cao hơn 1,08 điểm"), ("4.6, chỉ ở bản kia", None),
            (m.DAU_TOM_TAT + "c", "đạt 86,64 %")]
    da_kiem, lech, bo_qua = m.tim(kiem, van, b, "rut_gon")
    assert (da_kiem, [x[0] for x in lech], bo_qua) == (2, ["Lời văn, b"], 2)  # chưa có phần tóm tắt thì bỏ qua chỗ của nó
    da_kiem, lech, bo_qua = m.tim(kiem, van, b, "rut_gon", tom_tat="PhoBERT đạt  86,64 % trên tập kiểm tra.")
    assert (da_kiem, [x[0] for x in lech], bo_qua) == (3, ["Lời văn, b"], 1)
    # cụm của phần tóm tắt chỉ tìm trong phần tóm tắt, dù thân bài có đúng cụm đó
    _, lech, _ = m.tim([(m.DAU_TOM_TAT + "d", "cao hơn 1,07 điểm")], van, b, "rut_gon", tom_tat="Không có cụm ấy.")
    assert len(lech) == 1 and "phần tóm tắt" in lech[0][2]


def test_theo_ban_va_doi_so_bang():
    assert m.theo_ban("day_du", day_du="a", rut_gon="b") == "a" and m.theo_ban("rut_gon", day_du="a") is None
    assert m.doi_so_bang("rut_gon", "4.6, số phép so ở Bảng 4.15") == "4.6, số phép so ở Bảng C.5"
    assert m.doi_so_bang("day_du", "Bảng 4.15, dòng 2") == "Bảng 4.15, dòng 2"


def test_bang_bo_o_ban_chinh_thi_bo_qua_o_ban_chinh_van_kiem_o_ban_luu():
    """Bảng phân bố theo khía cạnh (4.2 ở bản đầy đủ) bị học viên bỏ khỏi bản chính ngày 16/10/2026."""
    b, van = m.tach_bang(VAN), m.chuan(VAN)
    kiem = [("Bảng 4.2, GENERAL", "| GENERAL | 294 | 83 | 1.004 | 1.381 |")]
    assert m.tim(kiem, van, b, "rut_gon") == (0, [], 1)
    da_kiem, lech, _ = m.tim(kiem, van, b, "day_du")
    assert da_kiem == 1 and len(lech) == 1  # bản lưu vẫn kiểm (đoạn mẫu không có hàng này nên báo lệch)
    assert m.kiem_ten_bang(b, "rut_gon", ["4.2"]) == []
    assert m.doi_so_bang("rut_gon", "Bảng 4.2, GENERAL") == "Bảng 4.2, GENERAL"


def test_ten_bang_phai_chua_tu_khoa():
    b, van = m.tach_bang(VAN), m.chuan(VAN)
    kiem = m.kiem_ten_bang(b, "rut_gon", ["4.5", "4.12"])
    assert m.tim(kiem, van, b, "rut_gon")[1] == []
    # đổi tên hai bảng cho nhau: hàng vẫn còn nhưng tên không còn đúng
    doi = VAN.replace("Kết quả trên tập kiểm tra của X", "Macro-F1 gì đó")
    b2 = m.tach_bang(doi)
    lech = m.tim(m.kiem_ten_bang(b2, "rut_gon", ["4.5"]), m.chuan(doi), b2, "rut_gon")[1]
    assert len(lech) == 1 and "Kết quả trên tập kiểm tra" in lech[0][1]
    # bảng không có trong bản nháp cũng bị báo
    assert len(m.tim(m.kiem_ten_bang(b, "rut_gon", ["4.9"]), van, b, "rut_gon")[1]) == 1


def test_so_tham_so_phai_o_dung_hang_cua_bac():
    b, van = m.tach_bang(VAN), m.chuan(VAN)
    dung = m.kiem_thang_mo_hinh(b, "rut_gon", {"1": "9", "4": "136.181.763", "4b": "136.181.763"})
    assert m.tim(dung, van, b, "rut_gon")[1] == []
    sai = m.kiem_thang_mo_hinh(b, "rut_gon", {"1": "136.181.763", "5": "9"})  # sai số ở bậc 1, không có hàng của bậc 5
    assert [x[0] for x in m.tim(sai, van, b, "rut_gon")[1]] == ["Bảng 4.2, số tham số của bậc 1", "Bảng 4.2, số tham số của bậc 5"]


def test_doc_tom_tat_va_so_la(tmp_path):
    f = tmp_path / "TrangDau.md"
    assert m.doc_tom_tat(f) is None
    f.write_text("# LỜI CẢM ƠN\n\nCảm ơn 3 lần.\n\n# TÓM TẮT\n\nĐạt 86,64 % trên 799 mẫu.\n\n# MỤC KHÁC\n\n12 thứ khác.\n", encoding="utf-8")
    tom_tat = m.doc_tom_tat(f)
    assert tom_tat == "Đạt 86,64 % trên 799 mẫu."
    assert m.so_la_trong_tom_tat(tom_tat, "Thân bài có 86,64 và 799.") == []
    assert m.so_la_trong_tom_tat(tom_tat, "Thân bài chỉ có 86,46 và 799.") == ["86,64"]


def test_cau_dinh_tinh_va_cach_viet_p():
    assert m.neu(True, "câu", "mô tả") == ("mô tả", "câu")
    assert m.neu(False, "câu", "mô tả")[1].startswith("SỐ LIỆU KHÔNG CÒN ĐỠ CÂU")
    assert m.p_loi(0.0004) == "p nhỏ hơn 0,001" and m.p_loi(0.2049) == "p bằng 0,205"


def test_cach_do_chi_phi_lay_tu_file_khi_co(tmp_path, capsys):
    # chưa có file: so với giá trị mặc định của công cụ đo
    cum = dict(m.so_lieu_chi_phi(tmp_path, 6722))
    assert "chưa có" in capsys.readouterr().out
    assert cum["4.5, số mẫu và kích thước lô"].startswith("toàn bộ 6.722 mẫu của tập kiểm tra ở hai kích thước lô, 1 và 32,")
    assert cum["4.5, số lần lặp"] == "mỗi cấu hình lặp ba lần và lấy trung vị"
    # có file: lấy đúng điều kiện đã đo
    tep = tmp_path / "results" / "cost_profile.json"
    tep.parent.mkdir()
    r = {"so_lan_lap": 5, "so_mau": 6722, "seed": 42, "theo_co_lo": {"1": {}, "8": {}, "64": {}}}
    tep.write_text(json.dumps({"mo_hinh": {"phobert": r, "asgcn": r}}), encoding="utf-8")
    cum = dict(m.so_lieu_chi_phi(tmp_path, 6722))
    assert "ba kích thước lô, 1 và 8 và 64" in cum["4.5, số mẫu và kích thước lô"]
    assert cum["4.5, số lần lặp"] == "mỗi cấu hình lặp năm lần và lấy trung vị"
    # hai mô hình đo khác điều kiện: đòi một cụm không thể có, để chắc chắn bị báo lệch
    tep.write_text(json.dumps({"mo_hinh": {"phobert": r, "asgcn": {**r, "so_lan_lap": 3}}}), encoding="utf-8")
    assert m.so_lieu_chi_phi(tmp_path, 6722)[0][1].startswith("[các mô hình")


def test_mo_ta_moc_llm_dem_lai_tap_con(tmp_path):
    goc = Path(__file__).resolve().parents[1]
    (tmp_path / "configs").mkdir()
    cfg = (goc / "configs" / "llm.yaml").read_text(encoding="utf-8")
    (tmp_path / "configs" / "llm.yaml").write_text(cfg, encoding="utf-8")
    assert m.so_lieu_llm(tmp_path) == []  # chưa có danh sách mẫu: bỏ qua
    (tmp_path / "data" / "processed").mkdir(parents=True)
    hang = [{"uid": f"visfd-test-{i // 2:05d}-{'GENERAL' if i % 2 else 'PRICE'}", "label": i % 3} for i in range(9)]
    (tmp_path / "data" / "processed" / "visfd_test.jsonl").write_text("\n".join(json.dumps(h) for h in hang) + "\n", encoding="utf-8")
    (tmp_path / "results").mkdir()
    (tmp_path / "results" / "llm_subset_uids.json").write_text(json.dumps({"uid": [h["uid"] for h in hang[:7]]}), encoding="utf-8")
    cum = dict(m.so_lieu_llm(tmp_path))
    # 7 mẫu đầu: nhãn 0,1,2,0,1,2,0 thuộc 4 bình luận (00000 đến 00003)
    assert cum["4.3, tập con"] == "một tập con 7 mẫu rút phân tầng theo nhãn từ tập kiểm tra (3 tiêu cực, 2 trung tính, 2 tích cực, thuộc 4 bình luận)"
    assert cum["4.3, nhiệt độ"] == "với nhiệt độ bằng 0."
    assert cum["4.3, tên mô hình ngôn ngữ lớn"] == "tên gọi trên giao diện lập trình là gpt-4o,"
    assert "thêm hai ví dụ cho mỗi lớp" in cum["4.3, few-shot"] and "chạy ba lần với ba bộ ví dụ" in cum["4.3, few-shot"]


def _chi_phi_gia(goc: Path) -> None:
    """cost_profile.json và metrics.json giả cho sáu mô hình: PhoBERT nhanh nhất trong bốn mô hình dùng PhoBERT."""
    ms = {"lexicon": (0.2, 0.02), "bilstm": (2.0, 0.1), "phobert": (10.0, 5.0), "asgcn": (13.0, 5.5), "asgcn_linked": (13.1, 5.6),
          "senticgcn": (13.2, 5.7)}
    mh = {}
    for e, (a, b) in ms.items():
        mh[e] = {"trong_so": "khoi_tao" if e in ("phobert", "asgcn") else "best.pt", "so_mau": 6722, "so_lan_lap": 3, "seed": 42,
                 "moi_truong": {"ten_gpu": "Tesla T4"},
                 "theo_co_lo": {"1": {"ms_moi_mau": a, "so_du_doan_khac": 3 if e == "bilstm" else 0, "bo_nho_dinh_mb": 1.0},
                                "32": {"ms_moi_mau": b, "so_du_doan_khac": 1 if e == "bilstm" else 0,
                                       "bo_nho_dinh_mb": 600.0 if e == "phobert" else (604.5 if e in ("asgcn", "asgcn_linked", "senticgcn") else 9.3)}}}
        for s in m.cb.SEEDS:
            d = goc / "results" / e / f"seed{s}"
            d.mkdir(parents=True)
            (d / "metrics.json").write_text(json.dumps({"test": {"macro_f1": 0.86 if e == "phobert" else 0.85}}), encoding="utf-8")
    (goc / "results" / "cost_profile.json").write_text(json.dumps({"mo_hinh": mh}), encoding="utf-8")


def test_cot_chi_phi_phai_nam_dung_hang_cua_mo_hinh(tmp_path):
    _chi_phi_gia(tmp_path)
    dong = [f"| {m.TEN[e]} | 1 | 2,0 | CPU | {a} | {b} |" for e, a, b in (
        ("lexicon", "0,20 / 0,02", "9,3"), ("bilstm", "2,00 / 0,10", "9,3"), ("phobert", "10,00 / 5,00", "600,0"),
        ("asgcn", "13,00 / 5,50", "604,5"), ("asgcn_linked", "13,10 / 5,60", "604,5"), ("senticgcn", "13,20 / 5,70", "604,5"))]
    van = "Bảng 4.6: Số tham số và thời gian huấn luyện\n\n| a |\n|---|\n" + "\n".join(dong) + "\n"
    kq = dict(m.kiem_cot_chi_phi(m.tach_bang(van), "rut_gon", tmp_path))
    assert len(kq) == 6 and all(not v.startswith(f"| {m.TEN[e]} | ...") for e, v in zip(m.MO_HINH, kq.values()))
    # đổi số của hai hàng cho nhau thì cả hai bị đòi lại đúng số của mình
    van_sai = van.replace("13,00 / 5,50", "X").replace("13,10 / 5,60", "13,00 / 5,50").replace("X", "13,10 / 5,60")
    kq = dict(m.kiem_cot_chi_phi(m.tach_bang(van_sai), "rut_gon", tmp_path))
    assert kq["Bảng 4.9, chi phí suy luận của asgcn"].endswith("| 13,00 / 5,50 | 604,5 |") and " ... " in kq["Bảng 4.9, chi phí suy luận của asgcn"]
    assert m.kiem_cot_chi_phi(m.tach_bang(van), "day_du", tmp_path) == []  # bản đầy đủ không có hai cột này


def test_ket_qua_chi_phi_tinh_lai_tu_file(tmp_path):
    _chi_phi_gia(tmp_path)
    mh = json.loads((tmp_path / "results" / "cost_profile.json").read_text(encoding="utf-8"))["mo_hinh"]
    kq = dict(m.ket_qua_chi_phi(tmp_path, mh))
    assert kq["4.5, GPU"] == "Phép đo chạy trên GPU Tesla T4"
    assert kq["4.5, BiLSTM khác dự đoán"] == "BiLSTM khác 3 trong 6.722 dự đoán ở lô 1 và 1 ở lô 32"
    assert kq["4.5, mô hình đồ thị chậm hơn"] == "chậm hơn PhoBERT từ 30 đến 32 % ở lô 1 và từ 10 đến 14 % ở lô 32"
    assert kq["4.5, bộ nhớ thêm"] == "bộ nhớ đỉnh chỉ cao hơn 4,5 MB"
    assert kq["4.5, Sentic-GCN so với ASGCN"] == "Sentic-GCN chỉ chậm hơn ASGCN 0,20 ms một mẫu ở lô 1"
    assert kq["4.5, mô hình nhẹ nhanh hơn"] == "mô hình từ điển nhanh hơn PhoBERT khoảng 50 lần và BiLSTM khoảng 5,0 lần"
    assert not kq["4.5, đánh đổi"].startswith("SỐ LIỆU KHÔNG CÒN")
    assert not kq["4.5, dự đoán trùng"].startswith("SỐ LIỆU KHÔNG CÒN")


def test_file_chi_phi_thieu_mo_hinh_bi_bao_lech_chu_khong_dung(tmp_path):
    tep = tmp_path / "results" / "cost_profile.json"
    tep.parent.mkdir()
    r = {"so_lan_lap": 3, "so_mau": 6722, "seed": 42, "theo_co_lo": {"1": {"ms_moi_mau": 1.0}, "32": {"ms_moi_mau": 1.0}}}
    tep.write_text(json.dumps({"mo_hinh": {"phobert": r}}), encoding="utf-8")
    cum = dict(m.so_lieu_chi_phi(tmp_path, 6722))
    assert cum["4.5, kết quả chi phí"].startswith("[cost_profile.json thiếu mô hình: lexicon")
    kq = dict(m.kiem_cot_chi_phi({}, "rut_gon", tmp_path))
    assert kq["Bảng 4.9, chi phí suy luận của lexicon"].startswith("[cost_profile.json không có số đo")
