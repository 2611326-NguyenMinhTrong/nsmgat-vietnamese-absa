"""[CD1.10] Kiểm Hình 4.2 của scripts/make_figures.py bằng số đo giả, không cần GPU hay kết quả thật."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import compare_baselines as cb  # noqa: E402
import make_figures as mf  # noqa: E402


def _ket_qua_gia(goc: Path) -> Path:
    for i, e in enumerate(mf.MAU_MO_HINH):
        for s in cb.SEEDS:
            d = goc / "results" / e / f"seed{s}"
            d.mkdir(parents=True)
            (d / "metrics.json").write_text(json.dumps({"test": {"macro_f1": 0.5 + i * 0.05 + s % 7 / 1000}}), encoding="utf-8")
    tep = goc / "cost_profile.json"
    tep.write_text(json.dumps({"mo_hinh": {e: {"so_tham_so": 10 ** (i + 1), "theo_co_lo": {"1": {"ms_moi_mau": 0.1 * (i + 1)}}}
                                           for i, e in enumerate(mf.MAU_MO_HINH)}}), encoding="utf-8")
    return tep


def test_hinh_4_2_ve_duoc_tu_so_do(tmp_path):
    tep = _ket_qua_gia(tmp_path)
    assert mf.main(["--chi", "4.2", "--chi-phi", str(tep), "--ket-qua", str(tmp_path / "results"), "--out", str(tmp_path / "hinh")]) == 0
    assert (tmp_path / "hinh" / mf.HINH["4.2"][0]).stat().st_size > 10_000


def test_hinh_4_2_bo_qua_khi_chua_co_so_do(tmp_path, capsys):
    assert mf.main(["--chi", "4.2", "--chi-phi", str(tmp_path / "khong_co.json"), "--out", str(tmp_path / "hinh")]) == 0
    assert "BỎ QUA Hình 4.2" in capsys.readouterr().out
    assert not (tmp_path / "hinh" / mf.HINH["4.2"][0]).exists()


def test_hinh_4_2_bo_mo_hinh_thieu_so_do_o_lo_can_ve(tmp_path, capsys):
    tep = _ket_qua_gia(tmp_path)
    kq = json.loads(tep.read_text(encoding="utf-8"))
    kq["mo_hinh"]["bilstm"]["theo_co_lo"] = {"1": {"loi": "CUDA out of memory"}}
    tep.write_text(json.dumps(kq), encoding="utf-8")
    assert mf.main(["--chi", "4.2", "--chi-phi", str(tep), "--ket-qua", str(tmp_path / "results"), "--out", str(tmp_path / "hinh")]) == 0
    assert "bỏ bilstm" in capsys.readouterr().out


def test_ten_tham_so_va_so_tren_truc():
    assert mf.ten_tham_so(9) == "9 tham số"
    assert mf.ten_tham_so(136_181_763) == "136,2 triệu tham số"
    assert mf.so_truc(0.1) == "0,1" and mf.so_truc(10) == "10"
