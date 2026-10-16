"""[CD1.12i] Test scripts/doi_chung_do_thi.py: phép hoán vị seed, mặt nạ nhóm, và chạy trọn trên dữ liệu giả."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import doi_chung_do_thi as dc  # noqa: E402


def test_hoan_vi_tach_han_cho_p_nho_nhat():
    """5 với 5, tách hẳn: chỉ hai cách chia (đúng và đảo) đạt hiệu số tuyệt đối lớn nhất -> p = 2/252."""
    a = np.array([0.90, 0.91, 0.92, 0.93, 0.94])
    b = np.array([0.80, 0.81, 0.82, 0.83, 0.84])
    assert dc.hoan_vi_seed(a, b) == pytest.approx(2 / 252)


def test_hoan_vi_giong_nhau_cho_p_bang_1():
    a = np.array([0.85, 0.86, 0.87])
    assert dc.hoan_vi_seed(a, a.copy()) == pytest.approx(1.0)


def test_hoan_vi_5_voi_3_p_nho_nhat_la_1_tren_56():
    """Hai nhóm khác cỡ thì không có cách chia "đảo" cùng hiệu số: chọn 5 giá trị thấp nhất làm A vẫn chứa
    hai giá trị cao, nên chỉ đúng một trong 56 cách chia đạt hiệu số quan sát."""
    a = np.array([0.90, 0.91, 0.92, 0.93, 0.94])
    b = np.array([0.80, 0.81, 0.82])
    assert dc.hoan_vi_seed(a, b) == pytest.approx(1 / 56)


def test_mat_na_trai_cam_xuc_va_nhom_chan_doan():
    uid = ["t-0-A", "t-0-B", "t-1-A", "t-1-B", "t-2-A"]
    vang = np.array([0, 2, 1, 1, 2])
    chan_doan = [{"uid": "t-0-A", "phenomenon": "negation"}, {"uid": "t-1-A", "phenomenon": "both"},
                 {"uid": "t-2-A", "phenomenon": "contrast"}]
    m = dc.mat_na_nhom(uid, vang, chan_doan)
    assert m["trai_cam_xuc"].tolist() == [True, True, False, False, False]
    assert m["co_phu_dinh"].tolist() == [True, False, True, False, False]
    assert m["co_chuyen_y"].tolist() == [False, False, True, False, True]
    assert m["ca_hai"].tolist() == [False, False, True, False, False]


def test_uid_chan_doan_la_thi_dung():
    with pytest.raises(ValueError, match="không có trong tập kiểm tra"):
        dc.mat_na_nhom(["t-0-A"], np.array([0]), [{"uid": "t-9-A", "phenomenon": "both"}])


def _gia(tmp_path: Path, monkeypatch) -> Path:
    """Tập kiểm tra 40 bình luận x 2 khía cạnh; asgcn đúng hết, các mô hình khác đúng 70 %."""
    rng = np.random.default_rng(0)
    uid = [f"visfd-test-{i:05d}-{k}" for i in range(40) for k in ("A", "B")]
    vang = rng.integers(0, 3, len(uid))
    goc = tmp_path / "results"
    seed_tn = {"phobert": (1, 2, 3), "phobert_fp32": (1, 2), "asgcn_khong_gcn": (1, 2, 3),
               "asgcn": (1, 2, 3), "asgcn_linked": (1, 2, 3), "senticgcn": (1, 2, 3)}
    for exp, seeds in seed_tn.items():
        for s in seeds:
            d = goc / exp / f"seed{s}"
            d.mkdir(parents=True)
            doan = vang if exp == "asgcn" else np.where(rng.random(len(uid)) < 0.7, vang, (vang + 1) % 3)
            (d / "predictions.jsonl").write_text(
                "".join(json.dumps({"uid": u, "y_true": int(g), "y_pred": int(p)}) + "\n" for u, g, p in zip(uid, vang, doan)),
                encoding="utf-8")
    (tmp_path / "test.jsonl").write_text("".join(json.dumps({"uid": u}) + "\n" for u in uid), encoding="utf-8")
    (tmp_path / "cd.jsonl").write_text(
        "".join(json.dumps({"uid": u, "phenomenon": ("negation", "contrast", "both")[i % 3]}) + "\n"
                for i, u in enumerate(uid[:30])), encoding="utf-8")
    monkeypatch.setattr(dc, "SEED_THI_NGHIEM", seed_tn)
    return goc


def test_chay_tron_va_bat_duoc_do_thi_co_ich(tmp_path, monkeypatch):
    goc = _gia(tmp_path, monkeypatch)
    out = tmp_path / "kq.json"
    rc = dc.main(["--results", str(goc), "--test", str(tmp_path / "test.jsonl"), "--chan-doan", str(tmp_path / "cd.jsonl"),
                  "--so-lan", "300", "--out-json", str(out)])
    assert rc == 0
    kq = json.loads(out.read_text(encoding="utf-8"))
    assert len(kq["cap"]) == len(dc.CAP) * len(dc.NHOM)
    dat = {(r["nhom"], r["a"], r["b"]) for r in kq["do_thi_co_ich"]}
    assert ("toan_bo", "asgcn", "asgcn_khong_gcn") in dat
    assert all(r["a"] in dc.DO_THI for r in kq["do_thi_co_ich"])


def test_thu_tu_uid_lech_thi_dung(tmp_path, monkeypatch):
    goc = _gia(tmp_path, monkeypatch)
    (tmp_path / "test.jsonl").write_text(json.dumps({"uid": "khac"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="thứ tự uid"):
        dc.phan_tich(goc, tmp_path / "test.jsonl", tmp_path / "cd.jsonl", 100, 0)
