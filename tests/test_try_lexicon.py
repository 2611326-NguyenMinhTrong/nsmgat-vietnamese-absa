"""[CD1.4a] Test cong cu thu tay scripts/try_lexicon.py.

Cong cu thu tay cung la code — neu no lech voi mo hinh that thi no se day
nguoi dung toi ket luan sai. Cac test duoi day canh hai thu:
  1. Tra tu hoat dong ca khi go KHONG DAU (nguoi Viet hay go tat)
  2. Cong cu KHONG de lai rac trong trang thai mo hinh sau khi chay

Khong test phan VnCoreNLP (can Java, khoi dong ~5s) — phan do da duoc kiem
gian tiep qua CD1.3.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from try_lexicon import bo_dau, du_doan, tra_tu, xem_cau  # noqa: E402


class MoHinhGia:
    """Nhai LexiconModel du de test cong cu, khong can nap file that."""

    def __init__(self) -> None:
        self.lexicon = {"tuyệt_vời": 0.56, "chán": -0.84, "pin": 0.13}
        self.uid_to_tokens: dict[str, list[str]] = {}
        self._cache: dict[str, tuple[float, float]] = {}
        self.calibrate = torch.nn.Linear(2, 3)

    def _dac_trung(self, uid: str) -> tuple[float, float]:
        if uid in self._cache:
            return self._cache[uid]
        tokens = self.uid_to_tokens.get(uid, [])
        diem = [self.lexicon[t.lower()] for t in tokens if t.lower() in self.lexicon]
        kq = (sum(diem) / len(diem), len(diem) / len(tokens)) if diem else (0.0, 0.0)
        self._cache[uid] = kq
        return kq


@pytest.fixture
def model() -> MoHinhGia:
    return MoHinhGia()


# --- Bo dau ------------------------------------------------------------------


@pytest.mark.parametrize(
    "co_dau, khong_dau",
    [
        ("tuyệt_vời", "tuyet_voi"),
        ("chán", "chan"),
        ("đẹp", "dep"),
        ("Đ", "d"),
        ("pin", "pin"),
    ],
)
def test_bo_dau(co_dau, khong_dau):
    assert bo_dau(co_dau) == khong_dau


# --- Tra tu ------------------------------------------------------------------


def test_tra_tu_co_dau(model, capsys):
    tra_tu(model, "chán")
    assert "-0.8400" in capsys.readouterr().out


def test_tra_tu_KHONG_dau_van_tim_duoc(model, capsys):
    """Nguoi Viet hay go tat khong dau — cong cu phai tim duoc."""
    tra_tu(model, "tuyet_voi")
    ra = capsys.readouterr().out
    assert "go khong dau" in ra
    assert "tuyệt_vời" in ra
    assert "+0.5600" in ra


def test_tra_tu_khong_co_thi_khong_goi_y_rac(model, capsys):
    """Loi that gap 07/09: goi y tu gan giong tra ve rac ('_', 'e', 'i') vi
    so khop chuoi con qua tho. Chi duoc goi y tu du dai."""
    tra_tu(model, "xyzabc")
    ra = capsys.readouterr().out
    assert "KHONG co trong tu dien" in ra
    if "Tu gan giong" in ra:
        goi_y = ra.split("Tu gan giong:")[1].split("\n")[0]
        for tu in goi_y.split(","):
            assert len(tu.strip()) >= 3, f"goi y qua ngan: {tu!r}"


# --- Khong de lai rac --------------------------------------------------------


def test_xem_cau_khong_de_lai_rac_trong_mo_hinh(model, capsys):
    """xem_cau() them uid tam vao model.uid_to_tokens de goi dung code that.
    Neu quen don, trang thai mo hinh se phinh dan va gay nham lan."""
    truoc_tokens = dict(model.uid_to_tokens)
    truoc_cache = dict(model._cache)

    xem_cau(model, ["pin", "chán"], "thu")
    capsys.readouterr()

    assert model.uid_to_tokens == truoc_tokens, "con sot uid tam trong uid_to_tokens"
    assert model._cache == truoc_cache, "con sot uid tam trong cache"


def test_go_hai_cau_lien_tiep_khong_dung_lai_cache_cu(model, capsys):
    """Hai cau khac nhau dung chung uid tam — phai xoa cache giua hai lan,
    neu khong cau thu hai se nhan dac trung cua cau thu nhat."""
    xem_cau(model, ["pin"], "cau 1")
    ra1 = capsys.readouterr().out
    xem_cau(model, ["chán"], "cau 2")
    ra2 = capsys.readouterr().out

    assert "+0.1300" in ra1
    assert "-0.8400" in ra2
    assert "mean_score = +0.1300" in ra1
    assert "mean_score = -0.8400" in ra2


# --- Du doan -----------------------------------------------------------------


def test_du_doan_tra_ve_dung_dinh_dang(model):
    model.uid_to_tokens["x"] = ["pin", "chán"]
    nhan, prob, mean_score, coverage = du_doan(model, "x")

    assert nhan in (0, 1, 2)
    assert len(prob) == 3
    assert abs(sum(prob) - 1.0) < 1e-5, "xac suat phai tong bang 1"
    assert coverage == 1.0
    assert mean_score == pytest.approx((0.13 - 0.84) / 2)


def test_token_khong_tra_cuu_duoc_thi_coverage_giam(model):
    model.uid_to_tokens["y"] = ["pin", "zzz", "www"]
    _, _, _, coverage = du_doan(model, "y")
    assert coverage == pytest.approx(1 / 3)
