"""[CD1.4b] Test bo doc log cua scripts/watch_train.py.

Mot cong cu theo doi ma doc SAI con te hon la khong co: no lam nguoi dung tin
vao con so bia. Cac test o day khoa lai dung dinh dang log ma `trainer.py` va
`train.py` dang sinh ra — neu ai doi dinh dang log, test nay do truoc khi hoc
vien phat hien bang mat.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from watch_train import TrangThai, khoang, phan_tich  # noqa: E402


def dong_log(gio: str, msg: str) -> str:
    return f"2026-09-07 {gio} | __main__ | INFO | {msg}"


def dong_epoch(gio: str, k: int, tong: int, loss: float, acc: float, f1: float) -> str:
    return dong_log(
        gio,
        f"[bilstm/seed42] epoch {k}/{tong} | train_loss={loss:.4f} "
        f"| dev_acc={acc:.4f} | dev_macro_f1={f1:.4f}",
    )


# --- Dinh dang thoi gian ------------------------------------------------------


@pytest.mark.parametrize(
    "giay,mong_doi",
    [(0, "0s"), (45, "45s"), (60, "1p00s"), (243, "4p03s"), (3600, "1g00p"), (5880, "1g38p")],
)
def test_dinh_dang_khoang_thoi_gian(giay, mong_doi):
    assert khoang(giay) == mong_doi


# --- Doc log ------------------------------------------------------------------


def test_do_dung_thoi_gian_tung_epoch():
    """Thoi gian epoch = hieu dau thoi gian hai dong log lien tiep."""
    tt = TrangThai()
    phan_tich(
        "\n".join([
            dong_log("10:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
            dong_log("10:02:00", "Chuan bi xong (tokenize + dung mo hinh) — bat dau huan luyen"),
            dong_epoch("10:06:00", 1, 30, 0.72, 0.80, 0.69),
            dong_epoch("10:10:30", 2, 30, 0.48, 0.84, 0.74),
        ]),
        tt,
    )
    # Epoch 1 tinh tu luc CHUAN BI XONG, khong phai tu luc bat dau chuong trinh —
    # neu khong, epoch 1 se bi cong oan 2 phut tokenize (GAP-008).
    assert tt.epochs[0]["keo_dai"] == 240
    assert tt.epochs[1]["keo_dai"] == 270
    assert (tt.chuan_bi_xong - tt.bat_dau).total_seconds() == 120


def test_doc_duoc_ke_hoach_tu_config_that():
    """Moc BAT DAU ghi ro config nao — nho do biet duoc so epoch va kien nhan
    ma KHONG phai doan."""
    tt = TrangThai()
    phan_tich(
        dong_log("10:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
        tt,
    )
    assert tt.exp == "bilstm" and tt.seed == 42 and tt.device == "cpu"
    assert tt.tong_epoch == 30  # doc that tu configs/bilstm.yaml
    assert tt.kien_nhan_toi_da == 5


def test_dem_nguoc_kien_nhan_va_moc_tot_nhat():
    tt = TrangThai()
    phan_tich(
        "\n".join([
            dong_log("10:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
            dong_epoch("10:04:00", 1, 30, 0.7, 0.80, 0.70),  # tot nhat
            dong_epoch("10:08:00", 2, 30, 0.6, 0.84, 0.75),  # tot nhat
            dong_epoch("10:12:00", 3, 30, 0.5, 0.84, 0.74),  # tut -> 4
            dong_epoch("10:16:00", 4, 30, 0.4, 0.84, 0.73),  # tut -> 3
        ]),
        tt,
    )
    assert tt.f1_tot_nhat == pytest.approx(0.75)
    assert tt.kien_nhan_con == 3


def test_kien_nhan_duoc_NAP_LAI_khi_cai_thien_tro_lai():
    """Giong luat trong trainer.py: cai thien la dat lai bo dem, khong phai
    tru don. Doc sai cho nay se bao dung som sai luc."""
    tt = TrangThai()
    phan_tich(
        "\n".join([
            dong_log("10:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
            dong_epoch("10:04:00", 1, 30, 0.7, 0.80, 0.70),
            dong_epoch("10:08:00", 2, 30, 0.6, 0.80, 0.69),  # tut -> 4
            dong_epoch("10:12:00", 3, 30, 0.5, 0.85, 0.80),  # tot nhat -> nap lai 5
        ]),
        tt,
    )
    assert tt.kien_nhan_con == 5


def test_chi_lay_LAN_CHAY_CUOI_trong_file_nhieu_lan_chay():
    """File log mo che do noi tiep, nen mot file co the chua nhieu lan chay.
    Lay nham lan cu se tron so cua hai lan khac nhau vao mot bang."""
    tt = TrangThai()
    phan_tich(
        "\n".join([
            dong_log("09:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
            dong_epoch("09:04:00", 1, 30, 0.9, 0.70, 0.60),
            dong_epoch("09:08:00", 2, 30, 0.8, 0.72, 0.62),
            dong_log("10:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
            dong_epoch("10:04:00", 1, 30, 0.7, 0.80, 0.70),
        ]),
        tt,
    )
    assert len(tt.epochs) == 1
    assert tt.f1_tot_nhat == pytest.approx(0.70)


def test_nhan_ra_dung_som():
    tt = TrangThai()
    phan_tich(
        "\n".join([
            dong_log("10:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
            dong_epoch("10:04:00", 1, 30, 0.7, 0.80, 0.70),
            dong_log("10:08:00", "Dung som o epoch 6 (khong cai thien sau 5 epoch)"),
        ]),
        tt,
    )
    assert tt.xong and "DỪNG SỚM" in tt.ly_do_xong


def test_chua_thay_metrics_thi_KHONG_bao_la_xong_tot_dep():
    """Da mat mot lan huan luyen vi tuong no chay xong (exit code 0) trong khi
    thuc te bi giet o epoch 8/30. Tom tat phai noi ro dieu do."""
    tt = TrangThai()
    phan_tich(
        "\n".join([
            dong_log("10:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
            dong_epoch("10:04:00", 1, 30, 0.7, 0.80, 0.70),
            dong_log("10:08:00", "Dung som o epoch 6 (khong cai thien sau 5 epoch)"),
        ]),
        tt,
    )
    assert "CHƯA" in tt.tom_tat()

    tt.an(dong_log("10:09:00", "Da ghi results/bilstm/seed42/metrics.json"))
    assert "CHƯA" not in tt.tom_tat()
    assert "results/bilstm/seed42/metrics.json" in tt.tom_tat()


def test_doc_duoc_log_KHONG_co_moc_bat_dau():
    """File log cu (sinh truoc khi co tinh nang nay) van phai doc duoc, chi la
    khong biet ke hoach — khong duoc sap."""
    tt = TrangThai()
    ra = phan_tich(
        "\n".join([
            dong_epoch("10:04:00", 1, 30, 0.7, 0.80, 0.70),
            dong_epoch("10:08:00", 2, 30, 0.6, 0.84, 0.75),
        ]),
        tt,
    )
    assert len(ra) == 2
    assert tt.tong_epoch == 30  # suy tu "epoch k/30"
    assert tt.epochs[0]["keo_dai"] is None  # khong co moc truoc -> khong bia so
    assert tt.epochs[1]["keo_dai"] == 240


# --- Lan chay tiep (--resume) -------------------------------------------------


def test_hieu_dung_lan_CHAY_TIEP_khong_dem_lai_tu_dau():
    """Log cua lan chay tiep chi co cac epoch tu cho dut tro di. Neu dem so
    DONG thay vi doc so epoch, moi uoc luong gio xong deu sai."""
    tt = TrangThai()
    phan_tich(
        "\n".join([
            dong_log("14:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
            # Dung thu tu that: train.py ghi "Chuan bi xong" TRUOC khi goi
            # trainer.train(), con dong "Chay tiep" do _tiep_tuc() ghi ben trong.
            dong_log("14:00:10", "Chuan bi xong (dung dataset + mo hinh) — bat dau huan luyen"),
            dong_log("14:00:20", "Chay tiep tu epoch 9/30 (da chay 28.5 phut, "
                                 "best dev_macro_f1 = 0.7933, kien nhan con 4)"),
            dong_epoch("14:04:20", 9, 30, 0.11, 0.8670, 0.7925),
        ]),
        tt,
    )
    assert tt.epoch_da_co == 8
    assert len(tt.epochs) == 1
    assert "epoch 10" in tt.dong_trang_thai(), (
        "phai bao dang chay epoch 10, khong phai epoch 2"
    )
    assert "Số epoch chạy: 9" in tt.tom_tat()


# --- Nhac don dep -------------------------------------------------------------


def test_nhac_xoa_last_pt_khi_chay_xong_nhung_KHONG_tu_xoa(tmp_path, monkeypatch):
    """Hoc vien muon duoc NHAC, khong muon bi tu dong xoa: xoa nham mot
    checkpoint dat vai gio huan luyen thi khong lay lai duoc."""
    import watch_train

    gia_lap = tmp_path / "checkpoints" / "bilstm" / "seed42"
    gia_lap.mkdir(parents=True)
    (gia_lap / "last.pt").write_bytes(b"x" * 3_000_000)
    monkeypatch.setattr(watch_train, "REPO_ROOT", tmp_path)

    tt = TrangThai()
    phan_tich(
        "\n".join([
            dong_log("10:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
            dong_epoch("10:04:00", 1, 30, 0.7, 0.80, 0.70),
            dong_log("10:05:00", "Da ghi results/bilstm/seed42/metrics.json"),
            dong_log("10:05:01", "=== KET THUC bilstm/seed42 ==="),
        ]),
        tt,
    )
    tom_tat = tt.tom_tat()
    assert "Có thể dọn" in tom_tat and "last.pt" in tom_tat
    assert (gia_lap / "last.pt").exists(), "script chi duoc NHAC, khong duoc tu xoa"


def test_khong_nhac_don_khi_lan_chay_CHUA_xong(tmp_path, monkeypatch):
    """Dang chay do dang ma xoa last.pt la mat luon kha nang chay tiep."""
    import watch_train

    gia_lap = tmp_path / "checkpoints" / "bilstm" / "seed42"
    gia_lap.mkdir(parents=True)
    (gia_lap / "last.pt").write_bytes(b"x" * 1000)
    monkeypatch.setattr(watch_train, "REPO_ROOT", tmp_path)

    tt = TrangThai()
    phan_tich(
        "\n".join([
            dong_log("10:00:00", "=== BAT DAU bilstm/seed42 | config=configs/bilstm.yaml | device=cpu ==="),
            dong_epoch("10:04:00", 1, 30, 0.7, 0.80, 0.70),
            dong_log("10:08:00", "Dung som o epoch 6 (khong cai thien sau 5 epoch)"),
        ]),
        tt,
    )
    assert "Có thể dọn" not in tt.tom_tat()
