"""[CD1.4b] Test co che chay tiep (--resume) cua Trainer.

Test trung tam la `test_tiep_tuc_cho_ket_qua_GIONG_HET_chay_lien_mach`. Ly do
no quan trong hon ca: mot co che chay tiep LAM SAI con nguy hiem hon la khong
co co che nao. Khong co thi mat thoi gian, biet ngay. Co ma sai thi so trong
metrics.json van ra binh thuong, khong ai nhan ra, va ket qua trong bao cao
khong con tai lap duoc — hoi dong chay lai se ra so khac.

Cho de sai nhat la trang thai sinh so ngau nhien: quen khoi phuc no thi tu
epoch tiep theo, thu tu xao tron du lieu se khac han lan chay lien mach.
"""

from __future__ import annotations

import pytest
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from nsmgat.data.dataset import ACSADataset, collate_fn
from nsmgat.models.dummy import DummyModel
from nsmgat.trainer import Trainer
from nsmgat.utils.io import write_jsonl
from nsmgat.utils.logging import get_logger
from nsmgat.utils.seed import set_seed

logger = get_logger("test_resume")

SO_EPOCH = 4
NGAT_SAU_EPOCH = 2


def _viet_fixture(path, n: int) -> None:
    write_jsonl(path, [
        {
            "uid": f"test-{i:05d}-GENERAL",
            "text": "May nay rat tot",
            "tokens": ["May", "nay", "rat", "tot"],
            "pos": ["N", "P", "R", "A"],
            "heads": [1, -1, 1, 1],
            "deprels": ["sub", "root", "adv", "vmod"],
            "aspect": "GENERAL",
            "label": i % 3,
            "domain": "test",
            "split": "train",
        }
        for i in range(n)
    ])


@pytest.fixture(scope="module")
def du_lieu(tmp_path_factory):
    d = tmp_path_factory.mktemp("resume_data")
    _viet_fixture(d / "train.jsonl", 60)
    _viet_fixture(d / "dev.jsonl", 15)
    tok = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    train_ds = ACSADataset(d / "train.jsonl", tok, 32)
    dev_ds = ACSADataset(d / "dev.jsonl", tok, 32)
    loaders = (
        DataLoader(train_ds, batch_size=8, shuffle=True, collate_fn=collate_fn),
        DataLoader(dev_ds, batch_size=8, shuffle=False, collate_fn=collate_fn),
    )
    duong_dan = {
        "train_path": str(d / "train.jsonl"),
        "dev_path": str(d / "dev.jsonl"),
        "test_path": str(d / "dev.jsonl"),
    }
    return loaders, duong_dan


def lam_cfg(ckpt_dir, duong_dan, **ghi_de) -> dict:
    cfg = {
        "seed": 42,
        "device": "cpu",
        "data": dict(duong_dan),
        "model": {"name": "dummy", "encoder_name": "vinai/phobert-base-v2"},
        "train": {
            "epochs": SO_EPOCH,
            "batch_size": 8,
            "lr": 1e-2,
            "encoder_lr": 1e-2,
            "weight_decay": 0.0,
            "warmup_ratio": 0.1,
            "max_grad_norm": 1.0,
            "early_stop_patience": 99,  # tat dung som de test chay du SO_EPOCH
            "max_seq_len": 32,
            "use_amp": False,
        },
        "output": {"ckpt_dir": str(ckpt_dir), "results_dir": str(ckpt_dir), "save_best": True},
    }
    for khoa, gia_tri in ghi_de.items():
        cfg["train"][khoa] = gia_tri
    return cfg


def chay(cfg, loaders, seed: int = 42) -> Trainer:
    set_seed(seed)
    trainer = Trainer(DummyModel(cfg), cfg, *loaders, logger, exp_name="dummy", seed=seed)
    trainer.train()
    return trainer


def trang_thai_cuoi(trainer: Trainer) -> dict:
    """Trong so o CUOI epoch cuoi — lay tu last.pt chu khong phai best.pt,
    vi best.pt co the la cua epoch giua chung."""
    return torch.load(trainer.last_path, map_location="cpu", weights_only=False)


# --- Test trung tam -----------------------------------------------------------


def test_tiep_tuc_cho_ket_qua_GIONG_HET_chay_lien_mach(du_lieu, tmp_path, monkeypatch):
    """Chay lien mach 4 epoch, so voi: chay 2 epoch -> bi ngat -> chay tiep.

    Hai duong phai cho ra trong so Y HET NHAU. Neu khac, nghia la co gi do
    trong trang thai (RNG, optimizer, scheduler) chua duoc khoi phuc dung.
    """
    loaders, duong_dan = du_lieu
    lien_mach = chay(lam_cfg(tmp_path / "lien_mach", duong_dan), loaders)

    # --- Mo phong bi ngat: nem loi ngay truoc khi danh gia epoch thu 3 ---
    that = __import__("nsmgat.trainer", fromlist=["evaluate"]).evaluate
    dem = {"n": 0}

    def evaluate_gia(*a, **kw):
        dem["n"] += 1
        if dem["n"] > NGAT_SAU_EPOCH:
            raise RuntimeError("mo phong mat dien / tien trinh bi giet")
        return that(*a, **kw)

    monkeypatch.setattr("nsmgat.trainer.evaluate", evaluate_gia)

    with pytest.raises(RuntimeError):
        chay(lam_cfg(tmp_path / "bi_ngat", duong_dan), loaders)

    goi_do_dang = torch.load(
        tmp_path / "bi_ngat" / "dummy" / "seed42" / "last.pt",
        map_location="cpu", weights_only=False,
    )
    assert goi_do_dang["epoch"] == NGAT_SAU_EPOCH
    assert goi_do_dang["xong"] is False

    # --- Chay tiep ---
    monkeypatch.setattr("nsmgat.trainer.evaluate", that)
    tiep = chay(lam_cfg(tmp_path / "bi_ngat", duong_dan, resume=True), loaders)

    a, b = trang_thai_cuoi(lien_mach), trang_thai_cuoi(tiep)
    assert b["epoch"] == SO_EPOCH, "chay tiep phai chay het so epoch con lai"

    for ten, gia_tri in a["model"].items():
        assert torch.equal(gia_tri, b["model"][ten]), (
            f"trong so {ten!r} khac nhau — chay tiep KHONG tai lap duoc lan chay lien mach"
        )
    assert a["best_macro_f1"] == pytest.approx(b["best_macro_f1"])


# --- Noi dung last.pt ---------------------------------------------------------


def test_last_pt_du_thu_de_dung_lai_dung_cho(du_lieu, tmp_path):
    loaders, duong_dan = du_lieu
    goi = trang_thai_cuoi(chay(lam_cfg(tmp_path / "noi_dung", duong_dan), loaders))
    for khoa in ("epoch", "xong", "model", "optimizer", "scheduler", "scaler",
                 "best_macro_f1", "patience_left", "thoi_gian_da_chay",
                 "ngau_nhien", "config_hash"):
        assert khoa in goi, f"thieu {khoa!r} — se khong dung lai dung cho da dung"
    for bo in ("python", "numpy", "torch"):
        assert bo in goi["ngau_nhien"], f"thieu trang thai ngau nhien cua {bo!r}"
    assert goi["xong"] is True


def test_ghi_last_pt_khong_lam_hong_file_cu(du_lieu, tmp_path):
    """Ghi ra file tam roi doi ten: khong bao gio ton tai mot last.pt cut dau."""
    loaders, duong_dan = du_lieu
    trainer = chay(lam_cfg(tmp_path / "an_toan", duong_dan), loaders)
    assert trainer.last_path.exists()
    assert not trainer.last_path.with_name("last.pt.tmp").exists(), "con sot file tam"
    torch.load(trainer.last_path, map_location="cpu", weights_only=False)  # doc duoc


def test_tat_duoc_bang_save_last(du_lieu, tmp_path):
    loaders, duong_dan = du_lieu
    cfg = lam_cfg(tmp_path / "tat", duong_dan)
    cfg["output"]["save_last"] = False
    trainer = chay(cfg, loaders)
    assert not trainer.last_path.exists()


# --- Chan cac truong hop nguy hiem --------------------------------------------


def test_TU_CHOI_chay_tiep_khi_cau_hinh_da_doi(du_lieu, tmp_path):
    """Chay tiep bang cau hinh khac = tron hai cau hinh vao mot ket qua, va
    config_hash trong metrics.json se noi doi ve cach ket qua duoc sinh ra.
    Tha dung han con hon de so do di vao bao cao."""
    loaders, duong_dan = du_lieu
    chay(lam_cfg(tmp_path / "doi_cfg", duong_dan), loaders)

    cfg_khac = lam_cfg(tmp_path / "doi_cfg", duong_dan, resume=True, lr=5e-3)  # doi lr
    with pytest.raises(ValueError, match="cau hinh da doi"):
        chay(cfg_khac, loaders)


def test_resume_ma_chua_co_last_pt_thi_chay_tu_dau_chu_khong_sap(du_lieu, tmp_path):
    loaders, duong_dan = du_lieu
    trainer = chay(lam_cfg(tmp_path / "chua_co", duong_dan, resume=True), loaders)
    assert trang_thai_cuoi(trainer)["epoch"] == SO_EPOCH


def test_thoi_gian_duoc_CONG_DON_qua_cac_lan_chay(du_lieu, tmp_path, monkeypatch):
    """train_time_sec trong metrics.json phai la tong chi phi that. Neu chi
    tinh doan chay cuoi, mo hinh bi ngat vai lan se nhin nhu re bat thuong
    trong Bang 4.5 so sanh chi phi."""
    loaders, duong_dan = du_lieu
    that = __import__("nsmgat.trainer", fromlist=["evaluate"]).evaluate
    dem = {"n": 0}

    def evaluate_gia(*a, **kw):
        dem["n"] += 1
        if dem["n"] > NGAT_SAU_EPOCH:
            raise RuntimeError("mo phong bi ngat")
        return that(*a, **kw)

    monkeypatch.setattr("nsmgat.trainer.evaluate", evaluate_gia)
    with pytest.raises(RuntimeError):
        chay(lam_cfg(tmp_path / "cong_don", duong_dan), loaders)

    goi_1 = torch.load(tmp_path / "cong_don" / "dummy" / "seed42" / "last.pt",
                       map_location="cpu", weights_only=False)
    da_chay_lan_1 = goi_1["thoi_gian_da_chay"]
    assert da_chay_lan_1 > 0

    monkeypatch.setattr("nsmgat.trainer.evaluate", that)
    trainer = chay(lam_cfg(tmp_path / "cong_don", duong_dan, resume=True), loaders)

    # Trainer bao lai cho train.py so giay cua CAC PHIEN TRUOC de cong vao.
    assert trainer.thoi_gian_phien_truoc == pytest.approx(da_chay_lan_1)
    assert trang_thai_cuoi(trainer)["thoi_gian_da_chay"] > da_chay_lan_1


def test_co_resume_hay_khong_KHONG_lam_doi_config_hash(du_lieu, tmp_path):
    """config_hash phai mo ta CAU HINH THI NGHIEM, khong phai cach chay.

    Chay lien mach va chay tiep cho ra ket qua giong het nhau, nen chung bat
    buoc phai mang cung mot van tay trong metrics.json. Test nay cung khoa
    luon tinh tuong thich nguoc: config chua tung co khoa `resume` (vi du lan
    chay lexicon o CD1.4a) phai giu nguyen van tay cu.
    """
    from nsmgat.utils.io import config_hash

    _, duong_dan = du_lieu
    khong_co = lam_cfg(tmp_path / "vt", duong_dan)
    khong_co["train"].pop("resume", None)
    tat = lam_cfg(tmp_path / "vt", duong_dan, resume=False)
    bat = lam_cfg(tmp_path / "vt", duong_dan, resume=True)

    assert config_hash(khong_co) == config_hash(tat) == config_hash(bat)


def test_doi_sieu_tham_so_thi_van_tay_PHAI_doi(du_lieu, tmp_path):
    """Mat con lai cua test tren: bo bot khoa khoi van tay khong duoc lam no
    tro nen vo dung."""
    from nsmgat.utils.io import config_hash

    _, duong_dan = du_lieu
    assert config_hash(lam_cfg(tmp_path / "vt", duong_dan)) != config_hash(
        lam_cfg(tmp_path / "vt", duong_dan, lr=5e-3)
    )


def test_them_khoa_SO_SACH_vao_output_KHONG_lam_doi_van_tay(du_lieu, tmp_path):
    """[GAP-014] Thêm một dòng sổ sách vào base.yaml không được làm đổi vân tay
    của mọi kết quả đã chạy xong.

    Đã xảy ra thật: thêm `log_dir` / `save_last` / `save_last_every` ở CD1.4b
    làm `lexicon/seed42` đổi từ f25b1bbb0fcc sang 34f8cee22a1e trong khi MỌI
    con số trong metrics.json y nguyên. Vân tay phải mô tả cấu hình thí nghiệm,
    không mô tả cách ghi sổ.
    """
    from nsmgat.utils.io import config_hash

    _, duong_dan = du_lieu
    goc = lam_cfg(tmp_path / "vt", duong_dan)
    goc["train"].pop("resume", None)
    van_tay_goc = config_hash(goc)

    them_so_sach = lam_cfg(tmp_path / "vt", duong_dan)
    them_so_sach["train"].pop("resume", None)
    them_so_sach["output"].update({
        "log_dir": "logs", "save_last": True, "save_last_every": 2,
    })
    assert config_hash(them_so_sach) == van_tay_goc


def test_doi_save_best_thi_van_tay_PHAI_doi(du_lieu, tmp_path):
    """Mặt còn lại: `save_best` KHÔNG phải sổ sách. Tắt nó thì đánh giá dùng
    mô hình ở epoch CUỐI thay vì epoch tốt nhất — đổi kết quả thật."""
    from nsmgat.utils.io import config_hash

    _, duong_dan = du_lieu
    a = lam_cfg(tmp_path / "vt", duong_dan)
    b = lam_cfg(tmp_path / "vt", duong_dan)
    b["output"]["save_best"] = False
    assert config_hash(a) != config_hash(b)
