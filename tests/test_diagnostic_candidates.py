"""[CD1.8a] Test cho scripts/build_diagnostic_candidates.py.

Ba thu duoc khoa o day, theo thu tu quan trong:
  1. Chong ro ri: khong dong nao ngoai tap test lot duoc vao tap chan doan.
  2. Khong ghi de cong chu thich cua hoc vien.
  3. Tu khoa khop theo token, va nhom doi chung khong lan cau "ngo".

`tests/test_diagnostic.py` de danh cho S6.4 (chot tap chan doan), nen file nay mang
ten khac.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import build_diagnostic_candidates as bdc  # noqa: E402

TEST_THAT = REPO_ROOT / "data" / "processed" / "visfd_test.jsonl"
can_du_lieu = pytest.mark.skipif(
    not TEST_THAT.exists(),
    reason="data/processed/visfd_test.jsonl khong nam trong git — sinh bang scripts/prepare_data.py",
)


def _ex(so: int, aspect: str, label: int, tokens, split: str = "test") -> dict:
    return {
        "uid": f"visfd-{split}-{so:05d}-{aspect}",
        "text": " ".join(tokens),
        "tokens": list(tokens),
        "aspect": aspect,
        "label": label,
        "split": split,
        "domain": "visfd",
    }


def _ghi_jsonl(path: Path, rows) -> Path:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return path


# --- Chong ro ri --------------------------------------------------------------

def test_dong_cua_tap_TRAIN_bi_chan_o_cua_vao(tmp_path):
    """Chot quan trong nhat cua ca tap chan doan: lay cau tu train la ro ri du lieu."""
    p = _ghi_jsonl(tmp_path / "lan.jsonl", [
        _ex(1, "BATTERY", 0, ["pin", "ko", "trâu"]),
        _ex(2, "BATTERY", 0, ["pin", "ko", "trâu"], split="train"),
    ])
    with pytest.raises(ValueError, match="rò rỉ"):
        bdc.doc_tap_test(p)


def test_uid_va_split_la_HAI_dau_hieu_doc_lap(tmp_path):
    """uid dung tien to nhung split sai (hoac nguoc lai) cung phai bi chan."""
    sai_split = _ex(1, "BATTERY", 0, ["pin", "tốt"])
    sai_split["split"] = "dev"
    with pytest.raises(ValueError):
        bdc.doc_tap_test(_ghi_jsonl(tmp_path / "a.jsonl", [sai_split]))

    sai_uid = _ex(1, "BATTERY", 0, ["pin", "tốt"])
    sai_uid["uid"] = "visfd-train-00001-BATTERY"
    with pytest.raises(ValueError):
        bdc.doc_tap_test(_ghi_jsonl(tmp_path / "b.jsonl", [sai_uid]))


def test_thieu_file_thi_bao_ro_chu_khong_nem_traceback(tmp_path, capsys):
    ma = bdc.main(["--test", str(tmp_path / "khong_co.jsonl"), "--out", str(tmp_path / "o.csv")])
    assert ma == 1
    assert "prepare_data" in capsys.readouterr().err


# --- Tu khoa ------------------------------------------------------------------

def test_khop_theo_TOKEN_khong_theo_chuoi_con():
    """'không_khí' la token rieng, khong phai phu dinh. 'không_thể' thi duoc liet ke han."""
    pd, cy, ngo = bdc.tim_tu_khoa(["không_khí", "trong", "lành", "không_tưởng"])
    assert (pd, cy, ngo) == ([], [], [])
    pd, _, _ = bdc.tim_tu_khoa(["không_thể", "chê"])
    assert pd == ["không_thể"]


def test_khop_khong_phan_biet_hoa_thuong_va_khong_lap():
    pd, cy, _ = bdc.tim_tu_khoa(["Ko", "đẹp", "Nhưng", "ko", "tệ", "nhưng", "K", "sao"])
    assert pd == ["ko", "k"]
    assert cy == ["nhưng"]


def test_dang_viet_tat_duoc_khop_theo_mat_chu():
    """VnCoreNLP gan 'ko' la V hoac N, nen khong the dua vao tu loai."""
    for vt in ("ko", "k", "kh", "kg", "hok"):
        assert bdc.tim_tu_khoa(["pin", vt, "trâu"])[0] == [vt]
    assert bdc.PHU_DINH_VIET_TAT <= bdc.PHU_DINH


def test_ba_tap_tu_khoa_khong_giao_nhau():
    """Mot tu nam o hai tap thi nhom cua cau phu thuoc thu tu kiem, loi rat kho thay."""
    assert not (bdc.PHU_DINH & bdc.CHUYEN_Y)
    assert not (bdc.PHU_DINH & bdc.NGO)
    assert not (bdc.CHUYEN_Y & bdc.NGO)


def test_xep_nhom_du_bon_truong_hop():
    assert bdc.xep_nhom(["ko"], ["nhưng"], []) == "ca_hai"
    assert bdc.xep_nhom(["ko"], [], ["mà"]) == "phu_dinh"
    assert bdc.xep_nhom([], ["nhưng"], []) == "chuyen_y"
    assert bdc.xep_nhom([], [], []) == "doi_chung"


def test_cau_chi_co_tu_NGO_bi_loai_chu_KHONG_vao_doi_chung():
    """'bên hông' va 'hông có' cung mat chu. Cau nhu vay khong duoc lam ban nhom doi chung."""
    pd, cy, ngo = bdc.tim_tu_khoa(["cảm_biến", "bên", "hông", "mà", "nhạy"])
    assert (pd, cy) == ([], []) and ngo == ["hông", "mà"]
    assert bdc.xep_nhom(pd, cy, ngo) is None


# --- Chia chi tieu ------------------------------------------------------------

def test_chia_deu_khi_du_hang():
    assert bdc.chia_chi_tieu([500, 500, 500], 200) == [67, 67, 66]
    assert sum(bdc.chia_chi_tieu([500, 500, 500], 250)) == 250


def test_lop_thieu_thi_lay_het_va_phan_du_don_sang_lop_khac():
    """Vi du trong docstring: lop trung lap chi co 62."""
    assert bdc.chia_chi_tieu([123, 62, 235], 200) == [69, 62, 69]


def test_khong_bao_gio_lay_qua_so_co_san():
    lay = bdc.chia_chi_tieu([3, 0, 5], 100)
    assert lay == [3, 0, 5]
    assert bdc.chia_chi_tieu([0, 0, 0], 10) == [0, 0, 0]
    assert bdc.chia_chi_tieu([10, 10, 10], 0) == [0, 0, 0]


# --- Chon mau -----------------------------------------------------------------

def _kho_gia() -> list:
    """60 cau phu dinh, moi cau 3 khia canh mang 3 nhan; 10 token moi cau."""
    rows = []
    for i in range(60):
        tk = ["pin", "ko", "trâu"] + ["x"] * 7
        for kc, nhan in (("BATTERY", 0), ("PRICE", 1), ("GENERAL", 2)):
            rows.append(_ex(i, kc, nhan, tk))
    return rows


def test_cung_seed_thi_ra_dung_cung_ket_qua():
    chi_tieu = {"phu_dinh": 30, "chuyen_y": 0, "ca_hai": 0, "doi_chung": 0}
    a, _ = bdc.chon_ung_vien(_kho_gia(), chi_tieu, seed=42)
    b, _ = bdc.chon_ung_vien(list(reversed(_kho_gia())), chi_tieu, seed=42)
    c, _ = bdc.chon_ung_vien(_kho_gia(), chi_tieu, seed=7)
    assert [u["uid"] for u in a] == [u["uid"] for u in b], "thu tu dau vao khong duoc anh huong ket qua"
    assert [u["uid"] for u in a] != [u["uid"] for u in c]


def test_nhan_duoc_can_bang_va_khong_uid_nao_lap():
    chi_tieu = {"phu_dinh": 30, "chuyen_y": 0, "ca_hai": 0, "doi_chung": 0}
    chon, tk = bdc.chon_ung_vien(_kho_gia(), chi_tieu, seed=42)
    assert Counter(u["nhan_goc"] for u in chon) == {"negative": 10, "neutral": 10, "positive": 10}
    assert len({u["uid"] for u in chon}) == len(chon) == 30
    assert tk["lay"]["phu_dinh"] == [10, 10, 10]


def test_CAN_BANG_NHAN_thang_uu_tien_cau_ngan():
    """Lop trung lap chi co 2 cau ngan va 3 cau dai. Chi tieu 3 moi lop -> phai lay 1 cau dai,
    va la cau dai LECH IT NHAT."""
    rows = [_ex(i, "BATTERY", 0, ["ko"] + ["x"] * 9) for i in range(10)]
    rows += [_ex(100 + i, "BATTERY", 2, ["ko"] + ["x"] * 9) for i in range(10)]
    rows += [_ex(200 + i, "PRICE", 1, ["ko"] + ["x"] * 9) for i in range(2)]
    rows += [_ex(300, "PRICE", 1, ["ko"] + ["x"] * 79),    # 80 token
             _ex(301, "PRICE", 1, ["ko"] + ["x"] * 44),    # 45 token — lech it nhat
             _ex(302, "PRICE", 1, ["ko"] + ["x"] * 59)]    # 60 token
    chi_tieu = {"phu_dinh": 9, "chuyen_y": 0, "ca_hai": 0, "doi_chung": 0}
    chon, tk = bdc.chon_ung_vien(rows, chi_tieu, seed=1)
    trung_lap = [u for u in chon if u["nhan_goc"] == "neutral"]
    assert len(trung_lap) == 3
    assert {u["so_token"] for u in trung_lap} == {10, 45}
    assert tk["ngoai_do_dai"]["phu_dinh"] == [0, 1, 0]

    chon2, _ = bdc.chon_ung_vien(rows, chi_tieu, seed=1, lay_ngoai_do_dai=False)
    assert all(u["so_token"] <= 40 for u in chon2)
    assert sum(u["nhan_goc"] == "neutral" for u in chon2) == 2


def test_van_ban_hien_thi_gop_xuong_dong_thanh_mot_dau_cach():
    r = _ex(1, "BATTERY", 0, ["pin", "ko", "trâu", "a", "b"])
    r["text"] = "pin ko trâu\n\nmáy   nóng\tquá"
    chon, _ = bdc.chon_ung_vien([r], {"phu_dinh": 1, "chuyen_y": 0, "ca_hai": 0, "doi_chung": 0}, seed=1)
    assert chon[0]["text"] == "pin ko trâu máy nóng quá"


# --- Khong ghi de cong chu thich ----------------------------------------------

def _mot_ung_vien() -> list:
    chon, _ = bdc.chon_ung_vien([_ex(1, "BATTERY", 0, ["pin", "ko", "trâu", "a", "b"])],
                                {"phu_dinh": 1, "chuyen_y": 0, "ca_hai": 0, "doi_chung": 0}, seed=1)
    return chon


def _dien_chu_thich(p: Path, **gia_tri: str) -> None:
    """Gia lap hoc vien dien tay vao dong dau tien cua file ung vien."""
    with p.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    rows[0].update(gia_tri)
    with p.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=bdc.COT, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def test_file_dau_ra_dung_cot_va_cot_chu_thich_de_trong(tmp_path):
    p = tmp_path / "c.csv"
    assert bdc.ghi_csv(p, _mot_ung_vien()) is None
    assert p.read_bytes()[:3] == b"\xef\xbb\xbf", "can BOM de Excel doc dung tieng Viet"
    with p.open(encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh)
        assert tuple(rd.fieldnames) == bdc.COT
        dong = next(rd)
    assert all(dong[c] == "" for c in bdc.COT_CHU_THICH)
    assert dong["nhan_goc"] == "negative" and dong["tu_khoa_kich_hoat"] == "ko"


def test_chua_chu_thich_thi_chay_lai_duoc(tmp_path):
    p = tmp_path / "c.csv"
    bdc.ghi_csv(p, _mot_ung_vien())
    assert bdc.dem_dong_da_chu_thich(p) == 0
    assert bdc.ghi_csv(p, _mot_ung_vien()) is None


def test_DA_CHU_THICH_thi_tu_choi_ghi_de_va_KHONG_dong_vao_file(tmp_path):
    """Mau hong cua GAP-017: mot lenh chay lai nuot mat cong lam tay."""
    p = tmp_path / "c.csv"
    bdc.ghi_csv(p, _mot_ung_vien())
    _dien_chu_thich(p, phenomenon="negation", nhan_kiem_tra="negative", ghi_chu="nghi nhan goc sai")
    assert bdc.dem_dong_da_chu_thich(p) == 1
    truoc = p.read_bytes()

    with pytest.raises(FileExistsError, match="chú thích"):
        bdc.ghi_csv(p, _mot_ung_vien())
    assert p.read_bytes() == truoc, "tu choi thi khong duoc doi mot byte nao"


def test_ghi_de_thi_sao_luu_truoc_va_ban_sao_khop_gitignore(tmp_path):
    p = tmp_path / "c.csv"
    bdc.ghi_csv(p, _mot_ung_vien())
    _dien_chu_thich(p, ghi_chu="chi dien moi cot ghi chu cung tinh la da chu thich")
    truoc = p.read_bytes()

    sao_luu = bdc.ghi_csv(p, _mot_ung_vien(), ghi_de=True)
    assert sao_luu is not None and sao_luu.read_bytes() == truoc
    assert sao_luu.name.endswith(".csv.bak"), ".gitignore chan *.csv.bak"
    assert bdc.dem_dong_da_chu_thich(p) == 0


def test_main_tu_choi_thi_tra_ma_1_va_noi_cach_thoat(tmp_path, capsys):
    src = _ghi_jsonl(tmp_path / "t.jsonl", [_ex(1, "BATTERY", 0, ["pin", "ko", "trâu", "a", "b"])])
    out = tmp_path / "c.csv"
    assert bdc.main(["--test", str(src), "--out", str(out), "--so-phu-dinh", "1"]) == 0
    _dien_chu_thich(out, phenomenon="negation")
    capsys.readouterr()
    assert bdc.main(["--test", str(src), "--out", str(out), "--so-phu-dinh", "1"]) == 1
    loi = capsys.readouterr().err
    assert "--ghi-de" in loi and "--out" in loi


def test_chi_thong_ke_khong_tao_file(tmp_path):
    src = _ghi_jsonl(tmp_path / "t.jsonl", [_ex(1, "BATTERY", 0, ["pin", "ko", "trâu", "a", "b"])])
    out = tmp_path / "c.csv"
    assert bdc.main(["--test", str(src), "--out", str(out), "--chi-thong-ke"]) == 0
    assert not out.exists()


# --- Tren du lieu that --------------------------------------------------------

def test_ten_lop_khop_schema():
    from nsmgat.schema import LABEL_NAMES
    assert list(bdc.TEN_LOP) == LABEL_NAMES


@can_du_lieu
def test_tren_tap_test_that_ra_du_800_va_khong_dong_nao_ngoai_test(tmp_path):
    out = tmp_path / "candidates.csv"
    assert bdc.main(["--out", str(out)]) == 0
    with out.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == sum(bdc.CHI_TIEU_MAC_DINH.values()) == 800
    assert all(r["uid"].startswith("visfd-test-") for r in rows)
    assert len({r["uid"] for r in rows}) == len(rows)
    assert Counter(r["nhom_ung_vien"] for r in rows) == bdc.CHI_TIEU_MAC_DINH
    dem = Counter(r["nhan_goc"] for r in rows)
    assert max(dem.values()) - min(dem.values()) <= 4, f"nhan lech qua muc: {dem}"


@can_du_lieu
def test_nhom_doi_chung_that_su_khong_co_tu_khoa_nao(tmp_path):
    """Doc lai tu file dau ra va doi chieu voi token goc, khong tin vao bien trung gian."""
    out = tmp_path / "candidates.csv"
    bdc.main(["--out", str(out)])
    goc = {r["uid"]: r for r in bdc.doc_tap_test(TEST_THAT)}
    with out.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    tat_ca = bdc.PHU_DINH | bdc.CHUYEN_Y | bdc.NGO
    for r in rows:
        tk = {t.lower() for t in goc[r["uid"]]["tokens"]}
        if r["nhom_ung_vien"] == "doi_chung":
            assert not (tk & tat_ca), r["uid"]
            assert r["tu_khoa_kich_hoat"] == ""
        else:
            assert r["tu_khoa_kich_hoat"], r["uid"]
        assert r["nhan_goc"] == bdc.TEN_LOP[goc[r["uid"]]["label"]]
        assert r["aspect"] == goc[r["uid"]]["aspect"]


@can_du_lieu
def test_file_ung_vien_trong_kho_khop_voi_lan_sinh_lai(tmp_path):
    """candidates.csv da commit phai sinh lai duoc tu ma nguon hien tai, tru ba cot chu thich."""
    da_co = REPO_ROOT / "data" / "diagnostic" / "candidates.csv"
    if not da_co.exists():
        pytest.skip("chua sinh data/diagnostic/candidates.csv")
    out = tmp_path / "candidates.csv"
    bdc.main(["--out", str(out)])

    def doc(p):
        with p.open(encoding="utf-8-sig", newline="") as fh:
            return [{k: v for k, v in r.items() if k not in bdc.COT_CHU_THICH} for r in csv.DictReader(fh)]

    assert doc(da_co) == doc(out)
