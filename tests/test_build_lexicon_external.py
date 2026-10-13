"""[CD1.6c] Kiểm scripts/build_lexicon_external.py: đổi từ điển có sẵn sang bảng điểm và kiểm mẫu số."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_lexicon_external as m  # noqa: E402

SENTICNET = (
    "senticnet = {}\n"
    "senticnet['tot'] = [0, 0, 0.659, 0, '#pleasantness', None, 'positive', 0.659, 'a', 'b', 'c', 'd', 'e']\n"
    "senticnet['may'] = [0, -0.951, 0, 0, '#rage', None, 'negative', -0.951, 'a', 'b', 'c', 'd', 'e']\n"
    "senticnet['man_hinh'] = [0, 0, 0.1, 0, '#joy', None, 'positive', 0.1, 'a', 'b', 'c', 'd', 'e']\n"
)


def _du_lieu(tmp_path: Path, cau, phan: str = "train") -> Path:
    """cau: danh sách (tokens, heads, khía cạnh). Ghi một file visfd_<phan>.jsonl đúng khuôn của data/processed."""
    d = tmp_path / "dl"
    d.mkdir(exist_ok=True)
    with (d / f"visfd_{phan}.jsonl").open("w", encoding="utf-8") as fh:
        for i, (tokens, heads, khia_canh) in enumerate(cau):
            fh.write(json.dumps({"uid": f"visfd-{phan}-{i:05d}-{khia_canh}", "text": " ".join(tokens), "tokens": tokens,
                                 "pos": ["N"] * len(tokens), "heads": heads, "deprels": ["x"] * len(tokens),
                                 "aspect": khia_canh, "label": 1, "domain": "visfd", "split": phan}, ensure_ascii=False) + "\n")
    return d


def test_senticnet_tra_theo_mat_chu_bo_dau_va_ghi_khoa_co_dau(tmp_path, capsys):
    nguon = tmp_path / "senticnet.py"
    nguon.write_text(SENTICNET, encoding="utf-8")
    d = _du_lieu(tmp_path, [(["Máy", "tốt", ",", "may", "Màn_hình", "xyz"], [1, -1, 1, 1, 1, 1], "GENERAL")])
    ra = tmp_path / "lexicon_sn.json"
    assert m.main(["senticnet", "--nguon", str(nguon), "--du-lieu", str(d), "--ra", str(ra)]) == 0
    td = json.loads(ra.read_text(encoding="utf-8"))
    # `máy` và `may` cùng nhận điểm của khái niệm `may`: đúng cái nhiễu trùng mặt chữ mà docstring cảnh báo
    assert td == {"may": -0.951, "màn_hình": 0.1, "máy": -0.951, "tốt": 0.659}
    assert b"\r" not in ra.read_bytes()
    mo_ta = json.loads(ra.with_suffix(".meta.json").read_text(encoding="utf-8"))
    assert mo_ta["sha256_bang_diem"] == hashlib.sha256(ra.read_bytes()).hexdigest() and mo_ta["so_muc"] == 4
    assert mo_ta["so_muc_am"] == 2 and mo_ta["nguon"] == "senticnet.py"
    assert mo_ta["sha256_bang_diem"] in capsys.readouterr().out


def test_senticnet_dung_khi_khong_co_du_lieu(tmp_path):
    nguon = tmp_path / "senticnet.py"
    nguon.write_text(SENTICNET, encoding="utf-8")
    assert m.main(["senticnet", "--nguon", str(nguon), "--du-lieu", str(tmp_path / "khong_co"), "--ra", str(tmp_path / "x.json")]) == 1
    assert not (tmp_path / "x.json").exists()


def test_vswn_lay_trung_binh_cac_tap_dong_nghia_va_noi_gach_duoi(tmp_path):
    nguon = tmp_path / "vswn.txt"
    nguon.write_text("# POS\tID\tPosScore\tNegScore\tSynsetTerms\tGloss\n"
                     "a\t001\t0.75\t0\tvui vẻ#1 hấp_dẫn#2\tmột lời giải thích\n"
                     "a\t002\t0\t0.25\tvui vẻ#3\tlời giải thích khác\n"
                     "a\t003\tx\t0\thỏng#1\tdòng hỏng bị bỏ qua\n", encoding="utf-8")
    td = m.doc_vswn_diem(nguon)
    assert td == {"hấp_dẫn": pytest.approx(0.75), "vui_vẻ": pytest.approx(0.25)}
    ra = tmp_path / "lexicon_vswn.json"
    assert m.main(["vswn", "--nguon", str(nguon), "--du-lieu", str(tmp_path / "khong_co"), "--ra", str(ra)]) == 0
    lan1 = ra.read_bytes()
    assert m.main(["vswn", "--nguon", str(nguon), "--du-lieu", str(tmp_path / "khong_co"), "--ra", str(ra)]) == 0
    assert ra.read_bytes() == lan1  # tất định: cùng nguồn thì cùng sha256


def test_kiem_dem_theo_mau_va_bao_khi_mau_so_bang_khong(tmp_path, capsys):
    # Hai mẫu dùng chung một câu hai từ nối nhau. Hàng của mỗi từ có hai ô: tự nối (2s + 1) và cạnh (s + s + 1).
    d = _du_lieu(tmp_path, [(["a", "b"], [-1, 0], "GENERAL"), (["a", "b"], [-1, 0], "CAMERA")])
    td = tmp_path / "td.json"

    td.write_text(json.dumps({"a": -0.75, "b": -0.75}), encoding="utf-8")  # E = -1, mẫu số 0: kích dây bẫy
    r = m.thong_ke_mau_so(td, d)["train"]
    assert (r["so_mau"], r["so_tu"], r["tu_kich_bay"], r["mau_kich_bay"]) == (2, 4, 4, 2)
    assert r["mau_so_nho_nhat"] == pytest.approx(0.0, abs=1e-7)
    assert m.main(["kiem", "--tu-dien", str(td), "--du-lieu", str(d)]) == 1
    assert "KHÔNG HUẤN LUYỆN ĐƯỢC" in capsys.readouterr().out

    td.write_text(json.dumps({"a": -1.0, "b": -1.0}), encoding="utf-8")  # E = -2, mẫu số -1: đổi dấu nhưng chạy được
    r = m.thong_ke_mau_so(td, d)["train"]
    assert (r["tu_mau_so_khong_duong"], r["mau_dinh"], r["tu_kich_bay"]) == (4, 2, 0)
    assert r["mau_so_nho_nhat"] == pytest.approx(1.0)
    assert m.main(["kiem", "--tu-dien", str(td), "--du-lieu", str(d)]) == 0

    td.write_text(json.dumps({}), encoding="utf-8")  # không từ nào có điểm: A = D, mẫu số 3
    r = m.thong_ke_mau_so(td, d)["train"]
    assert (r["tu_mau_so_khong_duong"], r["canh_am"], r["mau_so_nho_nhat"]) == (0, 0, pytest.approx(3.0))


def test_kiem_tren_tu_dien_tu_suy_khop_so_da_do():
    """Chốt lại phép đếm trên dữ liệu thật: 735 từ, 596 mẫu ở tập huấn luyện (GAP-033)."""
    goc = Path(__file__).resolve().parents[1]
    td, du_lieu = goc / "data/lexicon_from_train.json", goc / "data/processed"
    if not td.exists() or not (du_lieu / "visfd_dev.jsonl").exists():
        pytest.skip("không có từ điển tự suy hoặc không có data/processed")
    r = m.thong_ke_mau_so(td, du_lieu, phan=("dev",))["dev"]
    assert (r["so_mau"], r["tu_mau_so_khong_duong"], r["mau_dinh"], r["tu_kich_bay"], r["tu_gan_khong"]) == (3316, 86, 69, 0, 0)
