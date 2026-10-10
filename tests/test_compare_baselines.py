"""[CD1.10] Kiểm scripts/compare_baselines.py."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics import accuracy_score, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import compare_baselines as m  # noqa: E402


def _gia_lap(so_cau=300, seed=0):
    rng = np.random.default_rng(seed)
    uid, vang = [], []
    for c in range(so_cau):
        for kc in ("A", "B", "C")[: rng.integers(1, 4)]:
            uid.append(f"visfd-test-{c:05d}-{kc}")
            vang.append(int(rng.choice(3, p=[0.33, 0.12, 0.55])))
    return uid, np.asarray(vang), rng


def _doan(vang, ti_le_dung, rng):
    d = vang.copy()
    sai = rng.random(len(d)) > ti_le_dung
    d[sai] = (d[sai] + rng.integers(1, 3, sai.sum())) % 3
    return d


def test_do_do_khop_sklearn():
    uid, vang, rng = _gia_lap()
    doan = _doan(vang, 0.8, rng)
    _, dem = m.dem_theo_cau(uid, vang, doan)
    f1, acc = m.do_do(dem.sum(axis=0))
    assert f1 == pytest.approx(f1_score(vang, doan, average="macro"))
    assert acc == pytest.approx(accuracy_score(vang, doan))


def test_lop_khong_bao_gio_duoc_doan_thi_f1_bang_khong():
    o = np.array([5, 0, 0, 3, 0, 0, 0, 0, 7], dtype=float)  # lop 1 khong duoc doan lan nao
    f1, _ = m.do_do(o)
    assert f1 == pytest.approx((2 * 5 / (5 + 8) + 0 + 1) / 3)


def test_hai_mo_hinh_giong_het_thi_hieu_so_bang_khong_va_p_bang_mot():
    uid, vang, rng = _gia_lap()
    _, dem = m.dem_theo_cau(uid, vang, _doan(vang, 0.8, rng))
    a = np.stack([dem] * 3)
    r = m.kiem_dinh(a, a.copy(), 300, np.random.default_rng(1))
    assert r["macro_f1"]["hieu_so"] == 0 and r["macro_f1"]["p"] == 1.0
    assert r["macro_f1"]["ci95_duoi"] == r["macro_f1"]["ci95_tren"] == 0


def test_mo_hinh_hon_ro_thi_p_nho_va_khoang_tin_cay_khong_chua_khong():
    uid, vang, rng = _gia_lap(so_cau=600)
    a = np.stack([m.dem_theo_cau(uid, vang, _doan(vang, 0.92, rng))[1] for _ in range(3)])
    b = np.stack([m.dem_theo_cau(uid, vang, _doan(vang, 0.70, rng))[1] for _ in range(3)])
    r = m.kiem_dinh(a, b, 1000, np.random.default_rng(2))
    assert r["macro_f1"]["hieu_so"] > 0.1 and r["macro_f1"]["p"] < 0.01
    assert r["macro_f1"]["ci95_duoi"] > 0 and r["accuracy"]["ci95_duoi"] > 0
    nguoc = m.kiem_dinh(b, a, 1000, np.random.default_rng(2))
    assert nguoc["macro_f1"]["hieu_so"] == pytest.approx(-r["macro_f1"]["hieu_so"])


def test_cung_seed_thi_ra_cung_ket_qua():
    uid, vang, rng = _gia_lap()
    a = np.stack([m.dem_theo_cau(uid, vang, _doan(vang, 0.85, rng))[1] for _ in range(3)])
    b = np.stack([m.dem_theo_cau(uid, vang, _doan(vang, 0.83, rng))[1] for _ in range(3)])
    assert m.kiem_dinh(a, b, 400, np.random.default_rng(7)) == m.kiem_dinh(a, b, 400, np.random.default_rng(7))


def test_file_lech_uid_thi_dung(tmp_path):
    for exp, dao in (("x", False), ("y", True)):
        for s in m.SEEDS:
            d = tmp_path / exp / f"seed{s}"
            d.mkdir(parents=True)
            rows = [{"uid": f"visfd-test-0000{i}-A", "y_true": i % 3, "y_pred": 0} for i in range(4)]
            if dao:
                rows.reverse()
            (d / "predictions.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    with pytest.raises(ValueError):
        m.nap(tmp_path, ["x", "y"])


def test_tren_ket_qua_that_hieu_so_quan_sat_khop_metrics_json():
    goc = Path(__file__).resolve().parents[1] / "results"
    if not (goc / "phobert" / "seed42" / "predictions.jsonl").exists():
        pytest.skip("không có kết quả thật")
    cau, du = m.nap(goc, ["phobert", "asgcn"])
    assert len(cau) == 2187
    r = m.kiem_dinh(du["asgcn"], du["phobert"], 200, np.random.default_rng(0))

    def tb(exp):
        return np.mean([json.loads((goc / exp / f"seed{s}" / "metrics.json").read_text(encoding="utf-8"))["test"]["macro_f1"]
                        for s in m.SEEDS])

    assert r["macro_f1"]["hieu_so"] == pytest.approx(tb("asgcn") - tb("phobert"), abs=1e-9)
