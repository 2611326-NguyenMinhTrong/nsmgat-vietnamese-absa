"""[CD1.8d] Kiểm scripts/finalize_diagnostic.py: rút mẫu gán lại và tính kappa."""

import datetime as dt
import json
import sys
from pathlib import Path

import pytest
from openpyxl import load_workbook
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import chu_thich_chan_doan as ct  # noqa: E402
import finalize_diagnostic as m  # noqa: E402
from build_diagnostic_candidates import COT  # noqa: E402


def _csv(tmp_path: Path, moi_nhom: int = 6) -> Path:
    rows = []
    for i, ph in enumerate(m.NHOM_RUT):
        for j in range(moi_nhom):
            r = dict.fromkeys(COT, "")
            r.update(uid=f"visfd-test-{i * 100 + j:05d}-BATTERY", text=f"câu {i}-{j}", aspect="BATTERY", nhan_goc="negative",
                     nhom_ung_vien="phu_dinh", tu_khoa_kich_hoat="không", so_token="5", phenomenon=ph, nhan_kiem_tra="dong_y")
            rows.append(r)
    p = tmp_path / "candidates.csv"
    ct.ghi_csv(p, rows)
    return p


def _gan_lai(xlsx: Path, lan1: dict, doi: int = 0) -> None:
    """Điền lần hai giống lần một, trừ `doi` dòng đầu bị đổi hiện tượng."""
    wb = load_workbook(xlsx)
    ws = wb[ct.TEN_SHEET]
    c = {k: i for i, k in enumerate(ct.COT_XLSX)}
    for n, hang in enumerate(ws.iter_rows(min_row=2)):
        ph = lan1[hang[c["uid"]].value]["phenomenon"]
        if n < doi:
            ph = "regular" if ph != "regular" else "negation"
        hang[c["phenomenon"]].value = ph
        hang[c["nhan_kiem_tra"]].value = "dong_y"
    wb.save(xlsx)


def test_kappa_khop_sklearn_va_hai_ca_bien():
    a = ["negation", "contrast", "regular", "regular", "both", "negation", "regular", "contrast"]
    b = ["negation", "regular", "regular", "regular", "both", "contrast", "regular", "contrast"]
    k, p_o, _ = m.kappa_cohen(a, b)
    assert k == pytest.approx(cohen_kappa_score(a, b)) and p_o == pytest.approx(6 / 8)
    assert m.kappa_cohen(a, a)[0] == pytest.approx(1.0)
    assert m.kappa_cohen(["x", "x"], ["x", "x"])[0] == 1.0
    with pytest.raises(ValueError):
        m.kappa_cohen(["x"], [])


def test_rut_phan_tang_deu_tat_dinh_va_bao_loi_khi_thieu(tmp_path):
    rows = ct.doc_csv(_csv(tmp_path))
    chon = m.rut_phan_tang(rows, 4, seed=1)
    assert len(chon) == 16 and len({r["uid"] for r in chon}) == 16
    assert {ph: sum(r["phenomenon"] == ph for r in chon) for ph in m.NHOM_RUT} == dict.fromkeys(m.NHOM_RUT, 4)
    assert [r["uid"] for r in chon] == [r["uid"] for r in m.rut_phan_tang(rows, 4, seed=1)]
    with pytest.raises(ValueError):
        m.rut_phan_tang(rows, 7, seed=1)


def test_file_gan_lai_khong_lo_nhan_cu_va_khong_bi_de(tmp_path):
    p, x = _csv(tmp_path), tmp_path / "lai.xlsx"
    assert m.main(["rut-mau", "--csv", str(p), "--xlsx", str(x), "--moi-nhom", "3"]) == 0
    ws = load_workbook(x)[ct.TEN_SHEET]
    c = {k: i for i, k in enumerate(ct.COT_XLSX)}
    for hang in ws.iter_rows(min_row=2, values_only=True):
        assert all(hang[c[k]] in (None, "") for k in ct.COT_CHU_THICH)
    assert "nhom_ung_vien" not in ct.COT_XLSX
    so = json.loads((tmp_path / "lai.json").read_text(encoding="utf-8"))
    assert len(so["uid"]) == 12
    assert m.main(["rut-mau", "--csv", str(p), "--xlsx", str(x), "--moi-nhom", "3"]) == 2


def test_kappa_chan_khi_chua_du_14_ngay_va_khi_gan_chua_xong(tmp_path):
    p, x = _csv(tmp_path), tmp_path / "lai.xlsx"
    m.main(["rut-mau", "--csv", str(p), "--xlsx", str(x), "--moi-nhom", "3"])
    out = tmp_path / "k.json"
    assert m.main(["kappa", "--csv", str(p), "--xlsx", str(x), "--out", str(out)]) == 2
    assert m.main(["kappa", "--csv", str(p), "--xlsx", str(x), "--out", str(out), "--bo-qua-ngay"]) == 1  # chưa gán
    assert not out.exists()


def test_kappa_dat_va_khong_dat(tmp_path, capsys):
    p, x = _csv(tmp_path), tmp_path / "lai.xlsx"
    m.main(["rut-mau", "--csv", str(p), "--xlsx", str(x), "--moi-nhom", "5"])
    lan1 = {r["uid"]: r for r in ct.doc_csv(p)}
    so = tmp_path / "lai.json"
    d = json.loads(so.read_text(encoding="utf-8"))
    d["som_nhat_duoc_gan_lai"] = (dt.date.today() - dt.timedelta(days=1)).strftime(m.DINH_DANG_NGAY)
    so.write_text(json.dumps(d), encoding="utf-8")
    out = tmp_path / "k.json"
    _gan_lai(x, lan1, doi=1)
    assert m.main(["kappa", "--csv", str(p), "--xlsx", str(x), "--out", str(out)]) == 0
    kq = json.loads(out.read_text(encoding="utf-8"))
    assert kq["loai"] == "nhat_quan_mot_nguoi" and kq["so_dong"] == 20 and len(kq["uid_lech"]) == 1
    assert kq["phenomenon"]["ti_le_trung"] == pytest.approx(19 / 20) and kq["phenomenon"]["kappa"] > 0.9
    _gan_lai(x, lan1, doi=10)
    assert m.main(["kappa", "--csv", str(p), "--xlsx", str(x), "--out", str(out)]) == 3
    assert "CHƯA ĐẠT" in capsys.readouterr().out
