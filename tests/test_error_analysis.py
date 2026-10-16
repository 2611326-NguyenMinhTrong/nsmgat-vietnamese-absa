"""[CD1.9] Kiểm scripts/error_analysis.py: các lát cắt đếm đúng trên dữ liệu dựng tay và khớp kết quả thật."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import error_analysis as m  # noqa: E402

# Bốn câu: 0 có một khía cạnh; 1 có hai khía cạnh cùng nhãn; 2 có đúng hai nhãn; 3 có đủ ba nhãn.
MAU = [("00000", "GENERAL", 2, 5), ("00001", "BATTERY", 0, 30), ("00001", "CAMERA", 0, 30),
       ("00002", "PRICE", 1, 50), ("00002", "GENERAL", 2, 50),
       ("00003", "BATTERY", 0, 90), ("00003", "PRICE", 1, 90), ("00003", "SCREEN", 2, 90)]


def _dung(tmp_path: Path, doan_theo_mo_hinh=None) -> Path:
    """Ghi test.jsonl, train.jsonl và predictions.jsonl. Mặc định mọi mô hình đoán đúng hết."""
    test = [{"uid": f"visfd-test-{c}-{a}", "aspect": a, "label": y, "tokens": ["x"] * n, "text": f"câu {c}"} for c, a, y, n in MAU]
    (tmp_path / "test.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in test), encoding="utf-8")
    train = [{"aspect": a} for a, n in (("GENERAL", 5), ("BATTERY", 4), ("PRICE", 3), ("CAMERA", 2), ("SCREEN", 1)) for _ in range(n)]
    (tmp_path / "train.jsonl").write_text("".join(json.dumps(r) + "\n" for r in train), encoding="utf-8")
    for exp in m.MO_HINH:
        doan = (doan_theo_mo_hinh or {}).get(exp, [y for _, _, y, _ in MAU])
        for s in m.cb.SEEDS:
            d = tmp_path / "kq" / exp / f"seed{s}"
            d.mkdir(parents=True)
            (d / "predictions.jsonl").write_text(
                "".join(json.dumps({"uid": r["uid"], "y_true": r["label"], "y_pred": p}) + "\n" for r, p in zip(test, doan)), encoding="utf-8")
    return tmp_path


def test_loai_cau_va_o_dem(tmp_path):
    goc = _dung(tmp_path)
    test, vang, doan = m.nap(goc / "kq", goc / "test.jsonl", ["phobert"])
    cau, idx = m.chi_so_cau(test)
    assert len(cau) == 4 and idx.tolist() == [0, 1, 1, 2, 2, 3, 3, 3]
    loai = m.loai_cau(idx, vang)
    assert loai.tolist() == [1, 0, 0, 2, 2, 2, 2, 2]  # 1 = một khía cạnh, 0 = cùng nhãn, 2 = trái nhãn
    o = m.dem(loai, 3, idx, 4, vang, doan["phobert"])
    assert o.shape == (3, len(m.cb.SEEDS), 4, 9) and o.sum() == 8 * len(m.cb.SEEDS)
    assert o[2].sum(axis=(1, 2)).tolist() == [5.0] * len(m.cb.SEEDS) and o[2, 0, 3].sum() == 3
    bo = loai.copy()
    bo[0] = -1
    assert m.dem(bo, 3, idx, 4, vang, doan["phobert"]).sum() == 7 * len(m.cb.SEEDS)


def test_nap_dung_khi_lech_nhan_that(tmp_path):
    goc = _dung(tmp_path)
    p = goc / "kq" / "asgcn" / "seed1337" / "predictions.jsonl"
    dong = p.read_text(encoding="utf-8").splitlines()
    r = json.loads(dong[0])
    r["y_true"] = 0
    p.write_text("\n".join([json.dumps(r)] + dong[1:]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="không cùng thứ tự uid hoặc nhãn thật"):
        m.nap(goc / "kq", goc / "test.jsonl", ["phobert", "asgcn"])


def test_ma_tran_sup_nhan_va_giao_loi(tmp_path):
    that = [y for _, _, y, _ in MAU]
    # phobert: câu 2 đoán tích cực cho cả hai khía cạnh (sụp nhãn, lỗi rơi vào nhãn kia của câu); câu 3 sai một mẫu.
    sai_a = that.copy()
    sai_a[3] = 2
    sai_a[6] = 0
    # ba mô hình còn lại trong nhóm mạnh: chỉ sai mẫu thứ 3, theo kiểu rơi vào nhãn thứ ba.
    sai_b = that.copy()
    sai_b[3] = 0
    goc = _dung(tmp_path, {"phobert": sai_a, "asgcn": sai_b, "asgcn_linked": sai_b, "senticgcn": sai_b})
    test, vang, doan = m.nap(goc / "kq", goc / "test.jsonl", m.MO_HINH)
    _, idx = m.chi_so_cau(test)
    loai = m.loai_cau(idx, vang)

    mt = m.lat_ma_tran(vang, doan)
    assert mt["phobert"]["so_loi"] == 2 and mt["bilstm"]["so_loi"] == 0
    assert mt["phobert"]["phan_loi_theo_cap"]["1->2"] == pytest.approx(0.5)
    assert mt["phobert"]["ti_le_tim_lai"] == pytest.approx([1.0, 0.0, 1.0])

    sn = m.lat_sup_nhan(idx, vang, doan, loai)
    assert sn["so_cau_trai_nhan"] == 2 and sn["so_cau_dung_hai_nhan"] == 1
    assert sn["mo_hinh"]["phobert"]["ti_le_sup_nhan"] == pytest.approx(0.5)
    assert sn["mo_hinh"]["phobert"]["phan_loi_sang_nhan_kia"] == 1.0
    assert sn["mo_hinh"]["asgcn"]["ti_le_sup_nhan"] == 0.0 and sn["mo_hinh"]["asgcn"]["phan_loi_sang_nhan_kia"] == 0.0

    g = m.lat_giao_loi(test, vang, doan, loai, m.MANH)
    assert g["cung_sai"] == 1 and g["chi_so_cung_sai"] == [3]
    assert g["theo_so_mo_hinh_luon_sai"] == {"0": 6, "1": 1, "2": 0, "3": 0, "4": 1}
    assert g["luon_sai"]["phobert"] == 2 and g["khong_lan_chay_nao_sai"] == 6
    assert g["cung_sai_theo_nhan"] == {"tiêu cực": 0, "trung tính": 1, "tích cực": 0}
    assert g["cung_sai_o_cau_trai_nhan"] == 1 and g["cung_sai_theo_khia_canh"] == {"PRICE": 1}
    assert g["cung_sai_nhan_that_sang_nhan_doan"] == {"trung tính -> tiêu cực": 1}  # 9 trên 12 lần chạy đoán tiêu cực


def test_luon_sai_doi_hoi_sai_o_ca_ba_seed(tmp_path):
    goc = _dung(tmp_path)
    p = goc / "kq" / "phobert" / "seed42" / "predictions.jsonl"
    dong = [json.loads(d) for d in p.read_text(encoding="utf-8").splitlines()]
    dong[0]["y_pred"] = 0
    p.write_text("".join(json.dumps(r) + "\n" for r in dong), encoding="utf-8")
    test, vang, doan = m.nap(goc / "kq", goc / "test.jsonl", m.MO_HINH)
    _, idx = m.chi_so_cau(test)
    g = m.lat_giao_loi(test, vang, doan, m.loai_cau(idx, vang), m.MANH)
    assert g["luon_sai"]["phobert"] == 0 and g["sai_it_nhat_mot_seed"]["phobert"] == 1 and g["khong_lan_chay_nao_sai"] == 7


def test_lenh_ghi_file_va_chi_ghi_ca_khi_duoc_yeu_cau(tmp_path, capsys):
    that = [y for _, _, y, _ in MAU]
    sai = that.copy()
    sai[3] = 0
    goc = _dung(tmp_path, dict.fromkeys(m.MANH, sai))
    chung = ["--results", str(goc / "kq"), "--test", str(goc / "test.jsonl"), "--train", str(goc / "train.jsonl"), "--so-lan", "40",
             "--out-json", str(goc / "e.json"), "--out-md", str(goc / "e.md"), "--out-ca", str(goc / "ca.md")]
    assert m.main(chung + ["--chi-in"]) == 0
    assert not (goc / "e.json").exists() and not (goc / "ca.md").exists()
    assert m.main(chung) == 0 and not (goc / "ca.md").exists()
    kq = json.loads((goc / "e.json").read_text(encoding="utf-8"))
    assert kq["giao_loi"]["uid_cung_sai"] == ["visfd-test-00002-PRICE"] and "chi_so_cung_sai" not in kq["giao_loi"]
    assert kq["khia_canh"]["thu_tu"] == ["GENERAL", "BATTERY", "PRICE", "CAMERA", "SCREEN"]
    assert "hieu_voi_moc" not in kq["khia_canh"]["ket_qua"]["phobert"]["BATTERY"]["accuracy"]
    assert set(kq["do_dai"]["phobert"]) == {x[0] for x in m.DO_DAI} and kq["do_dai"]["phobert"]["tren_80"]["n"] == 3
    bang = (goc / "e.md").read_text(encoding="utf-8")
    assert "Bảng A." in bang and "Bảng I." in bang and "câu 00002" not in bang  # bảng không chứa câu của bộ dữ liệu
    assert m.main(chung + ["--ca", "5"]) == 0
    assert "visfd-test-00002-PRICE" in (goc / "ca.md").read_text(encoding="utf-8")


def test_tren_ket_qua_that_so_loi_khop_metrics_json():
    goc = Path(__file__).resolve().parents[1]
    if not (goc / "results/phobert/seed42/predictions.jsonl").exists() or not (goc / "data/processed/visfd_test.jsonl").exists():
        pytest.skip("không có kết quả thật hoặc dữ liệu đã xử lý")
    test, vang, doan = m.nap(goc / "results", goc / "data/processed/visfd_test.jsonl", ["phobert", "senticgcn"])
    mt = m.lat_ma_tran(vang, doan)
    for exp in ("phobert", "senticgcn"):
        acc = np.mean([json.loads((goc / f"results/{exp}/seed{s}/metrics.json").read_text(encoding="utf-8"))["test"]["accuracy"] for s in m.cb.SEEDS])
        assert mt[exp]["so_loi"] == pytest.approx((1 - acc) * len(test), abs=1e-6)
    cau, idx = m.chi_so_cau(test)
    loai = m.loai_cau(idx, vang)
    assert len(cau) == 2187 and len(set(idx[loai == 2].tolist())) == 986  # 45,1 % câu có nhãn trái nhau, khớp số đã báo cáo
