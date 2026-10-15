"""[CD1.10] Kiểm scripts/profile_cost.py: cách bấm giờ, cách ghi kết quả, và phép đối chiếu dự đoán."""

import json
import sys
from pathlib import Path

import pytest
import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import profile_cost as m  # noqa: E402

from nsmgat.utils.io import write_jsonl  # noqa: E402


class _MoHinhGia(nn.Module):
    """Đoán nhãn bằng input_ids[:, 0] % 3 và đếm số lần được gọi. Có `_cache` như mô hình từ điển."""

    def __init__(self):
        super().__init__()
        self.so_lan_goi = 0
        self.kich_thuoc_dem_luc_goi = []
        self._cache = {}

    def forward(self, batch):
        self.so_lan_goi += 1
        self.kich_thuoc_dem_luc_goi.append(len(self._cache))
        self._cache[self.so_lan_goi] = 1
        return torch.nn.functional.one_hot(batch["input_ids"][:, 0] % 3, 3).float()


def _lo(so_mau: int, co_lo: int):
    items = [{"input_ids": [i, 0], "label": i % 3} for i in range(so_mau)]
    return m.chia_lo(items, co_lo, lambda xs: {"input_ids": torch.tensor([x["input_ids"] for x in xs]),
                                               "labels": torch.tensor([x["label"] for x in xs])})


def test_chia_lo_khong_bo_sot_mau():
    lo = _lo(10, 4)
    assert [len(b["labels"]) for b in lo] == [4, 4, 2]


def test_do_thoi_gian_lap_du_so_lan_va_xoa_bo_nho_dem():
    mo_hinh = _MoHinhGia()
    lo = _lo(10, 4)  # 3 lô
    kq = m.do_thoi_gian(mo_hinh, lo, torch.device("cpu"), lap=2, khoi_dong=1)
    assert len(kq["thoi_gian"]) == 2 and all(t >= 0 for t in kq["thoi_gian"])
    assert kq["nhan"] == [i % 3 for i in range(10)]
    assert kq["dinh"] is None and kq["dinh_giu_cho"] is None  # trên CPU không có số đo bộ nhớ GPU
    assert mo_hinh.so_lan_goi == 1 + 2 * 3
    # lô đầu của mỗi lần lặp thấy bộ nhớ đệm rỗng: bộ nhớ đệm được xoá trước mỗi lần bấm giờ
    assert mo_hinh.kich_thuoc_dem_luc_goi == [0, 0, 1, 2, 0, 1, 2]


def _repo_gia(tmp_path: Path, so_mau: int = 12) -> None:
    ban_ghi = [{"uid": f"visfd-test-{i:05d}-GENERAL", "text": "May nay rat tot", "tokens": ["May", "nay", "rat", "tot"],
                "pos": ["N", "P", "R", "A"], "heads": [1, -1, 1, 1], "deprels": ["sub", "root", "adv", "vmod"],
                "aspect": "GENERAL", "label": i % 3, "domain": "visfd", "split": "test"} for i in range(so_mau)]
    for ten in ("train", "dev", "test"):
        write_jsonl(tmp_path / f"{ten}.jsonl", ban_ghi)
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "dummy.yaml").write_text(json.dumps({
        "seed": 42, "device": "cpu",
        "data": {"train_path": str(tmp_path / "train.jsonl"), "dev_path": str(tmp_path / "dev.jsonl"),
                 "test_path": str(tmp_path / "test.jsonl")},
        "model": {"name": "dummy", "encoder_name": "vinai/phobert-base-v2", "hidden_dim": 16, "dropout": 0.1},
        "train": {"max_seq_len": 32, "batch_size": 4},
        "output": {"results_dir": str(tmp_path / "results"), "ckpt_dir": str(tmp_path / "checkpoints")},
    }), encoding="utf-8")


def test_ca_luong_voi_mo_hinh_dummy(tmp_path, monkeypatch, capsys):
    _repo_gia(tmp_path)
    monkeypatch.setattr(m, "THI_NGHIEM", {"dummy": ("configs/dummy.yaml", "dummy")})

    # Lần 1: chưa có best.pt thì đo với trọng số lúc khởi tạo và nói rõ
    assert m.main(["--goc", str(tmp_path), "--exp", "dummy", "--co-lo", "1", "4", "--lap", "2", "--device", "cpu"]) == 0
    ra = json.loads((tmp_path / "results" / "cost_profile.json").read_text(encoding="utf-8"))["mo_hinh"]["dummy"]
    assert ra["trong_so"] == "khoi_tao" and ra["so_mau"] == 12 and ra["ca_tap_kiem_tra"]
    assert set(ra["theo_co_lo"]) == {"1", "4"}
    for muc in ra["theo_co_lo"].values():
        assert muc["ms_nho_nhat"] <= muc["ms_moi_mau"] <= muc["ms_lon_nhat"]
        assert muc["bo_nho_dinh_mb"] is None and muc["so_du_doan_khac"] is None
    assert ra["moi_truong"]["thiet_bi"] == "cpu" and ra["moi_truong"]["torch"] == torch.__version__
    assert "trọng số lúc khởi tạo" in capsys.readouterr().out

    # Lần 2: có best.pt và có predictions.jsonl thì đếm được số dự đoán khác
    from nsmgat.train import build_model
    from nsmgat.utils.io import load_config

    cfg = load_config(tmp_path / "configs" / "dummy.yaml")
    mo_hinh = build_model("dummy", cfg)
    ckpt = tmp_path / "checkpoints" / "dummy" / "seed42" / "best.pt"
    ckpt.parent.mkdir(parents=True)
    torch.save(mo_hinh.state_dict(), ckpt)
    assert m.main(["--goc", str(tmp_path), "--exp", "dummy", "--co-lo", "4", "--lap", "1", "--device", "cpu"]) == 0
    ra = json.loads((tmp_path / "results" / "cost_profile.json").read_text(encoding="utf-8"))["mo_hinh"]["dummy"]
    assert ra["trong_so"] == "best.pt" and ra["theo_co_lo"]["4"]["so_du_doan_khac"] is None  # chưa có predictions.jsonl

    # ghi predictions.jsonl sai hẳn một mẫu rồi đo lại
    from transformers import AutoTokenizer

    from nsmgat.data.dataset import ACSADataset, collate_fn

    ds = ACSADataset(cfg["data"]["test_path"], AutoTokenizer.from_pretrained("vinai/phobert-base-v2"), 32, False)
    mo_hinh.eval()
    with torch.no_grad():
        doan = mo_hinh(collate_fn([ds[i] for i in range(len(ds))])).argmax(-1).tolist()
    d = tmp_path / "results" / "dummy" / "seed42"
    d.mkdir(parents=True)
    hang = [{"uid": ds[i]["uid"], "aspect": "GENERAL", "y_true": ds[i]["label"], "y_pred": doan[i]} for i in range(len(ds))]
    hang[3]["y_pred"] = (hang[3]["y_pred"] + 1) % 3
    write_jsonl(d / "predictions.jsonl", hang)
    assert m.main(["--goc", str(tmp_path), "--exp", "dummy", "--co-lo", "4", "--lap", "1", "--device", "cpu"]) == 0
    ra = json.loads((tmp_path / "results" / "cost_profile.json").read_text(encoding="utf-8"))["mo_hinh"]["dummy"]
    assert ra["theo_co_lo"]["4"]["so_du_doan_khac"] == 1


def test_chi_in_khong_ghi_file(tmp_path, monkeypatch):
    _repo_gia(tmp_path)
    monkeypatch.setattr(m, "THI_NGHIEM", {"dummy": ("configs/dummy.yaml", "dummy")})
    assert m.main(["--goc", str(tmp_path), "--exp", "dummy", "--co-lo", "4", "--lap", "1", "--so-mau", "5", "--device", "cpu", "--chi-in"]) == 0
    assert not (tmp_path / "results" / "cost_profile.json").exists()


def test_loi_o_mot_co_lo_khong_lam_mat_so_cua_co_lo_khac(tmp_path, monkeypatch):
    _repo_gia(tmp_path)
    monkeypatch.setattr(m, "THI_NGHIEM", {"dummy": ("configs/dummy.yaml", "dummy")})
    that = m.do_thoi_gian

    def hong_o_lo_4(model, lo, device, lap, khoi_dong):
        if len(lo[0]["labels"]) == 4:
            raise RuntimeError("CUDA out of memory (giả)")
        return that(model, lo, device, lap, khoi_dong)

    monkeypatch.setattr(m, "do_thoi_gian", hong_o_lo_4)
    assert m.main(["--goc", str(tmp_path), "--exp", "dummy", "--co-lo", "4", "1", "--lap", "1", "--device", "cpu"]) == 0
    ra = json.loads((tmp_path / "results" / "cost_profile.json").read_text(encoding="utf-8"))["mo_hinh"]["dummy"]
    assert "loi" in ra["theo_co_lo"]["4"] and "ms_moi_mau" in ra["theo_co_lo"]["1"]


def test_bang_thi_nghiem_khop_file_cau_hinh_that():
    goc = Path(__file__).resolve().parents[1]
    assert list(m.THI_NGHIEM) == ["lexicon", "bilstm", "phobert", "asgcn", "asgcn_linked", "senticgcn"]
    for exp, (tep, _) in m.THI_NGHIEM.items():
        assert (goc / tep).exists(), exp
    # asgcn_linked dùng chung lớp mô hình với asgcn, như train.py
    assert m.THI_NGHIEM["asgcn_linked"][1] == "asgcn"


@pytest.mark.skipif(not torch.cuda.is_available(), reason="cần GPU")
def test_tren_gpu_co_so_do_bo_nho():
    kq = m.do_thoi_gian(_MoHinhGia().cuda(), _lo(8, 4), torch.device("cuda"), lap=1, khoi_dong=1)
    assert kq["dinh"] is not None


def _ket_qua_gia(**doi) -> dict:
    """File cost_profile.json đủ sáu mô hình, đo trên một GPU, một lần chạy; `doi` sửa từng mô hình."""
    mt = {"thoi_diem": "2026-10-20T10:00:00", "thiet_bi": "cuda", "ten_gpu": "Tesla T4"}
    ra = {"mo_hinh": {}}
    for e in m.THI_NGHIEM:
        r = {"exp": e, "trong_so": "best.pt", "so_mau": 6722, "ca_tap_kiem_tra": True, "so_lan_lap": 3,
             "moi_truong": dict(mt), "theo_co_lo": {str(c): {"ms_moi_mau": 1.0, "so_du_doan_khac": 0} for c in m.CO_LO_MAC_DINH}}
        for k, v in doi.get(e, {}).items():
            r[k] = v
        ra["mo_hinh"][e] = r
    return ra


def test_kiem_ket_qua_day_du_thi_khong_co_loi():
    assert m.kiem_ket_qua(_ket_qua_gia(), 6722) == ([], [])


def test_kiem_ket_qua_bat_loi_chan():
    kq = _ket_qua_gia(phobert={"moi_truong": {"thoi_diem": "2026-10-20T10:00:00", "ten_gpu": "Tesla P100"}},
                      bilstm={"ca_tap_kiem_tra": False, "so_mau": 64},
                      asgcn={"theo_co_lo": {"1": {"ms_moi_mau": 1.0, "so_du_doan_khac": 0}, "32": {"loi": "CUDA out of memory"}}},
                      senticgcn={"theo_co_lo": {"1": {"ms_moi_mau": 1.0, "so_du_doan_khac": 0},
                                                "32": {"ms_moi_mau": 1.0, "so_du_doan_khac": m.NGUONG_KHAC + 1}}})
    del kq["mo_hinh"]["lexicon"]
    loi, _ = m.kiem_ket_qua(kq, 6722)
    van = "\n".join(loi)
    assert "thiếu mô hình: lexicon" in van
    assert "GPU khác nhau" in van and "Tesla P100 (phobert)" in van
    assert "bilstm: chỉ đo 64 mẫu" in van
    assert "asgcn: lô 32 báo lỗi" in van
    assert f"senticgcn, lô 32: {m.NGUONG_KHAC + 1} dự đoán khác" in van


def test_kiem_ket_qua_chi_nhac_nhung_cho_phai_ghi_trong_bao_cao():
    kq = _ket_qua_gia(phobert={"trong_so": "khoi_tao"},
                      bilstm={"theo_co_lo": {"1": {"ms_moi_mau": 1.0, "so_du_doan_khac": 59},
                                             "32": {"ms_moi_mau": 1.0, "so_du_doan_khac": 0}}},
                      lexicon={"moi_truong": {"thoi_diem": "2026-10-21T09:00:00", "ten_gpu": "Tesla T4"}})
    loi, chu_y = m.kiem_ket_qua(kq, 6722)
    assert loi == []
    van = "\n".join(chu_y)
    assert "phobert: đo với trọng số lúc khởi tạo" in van
    assert "bilstm, lô 1: 59 dự đoán khác" in van  # lô 1 chỉ bị nhắc (GAP-035)
    assert "trong 2 lần chạy" in van


def test_lenh_kiem_khong_can_torch_va_tra_ma_thoat(tmp_path, capsys):
    assert m.main(["--goc", str(tmp_path), "--kiem"]) == 1
    assert "Chưa có" in capsys.readouterr().out
    tep = tmp_path / "results" / "cost_profile.json"
    tep.parent.mkdir(parents=True)
    tep.write_text(json.dumps(_ket_qua_gia(), ensure_ascii=False), encoding="utf-8")
    assert m.main(["--goc", str(tmp_path), "--kiem"]) == 0
    assert "dùng được cho báo cáo" in capsys.readouterr().out
    kq = _ket_qua_gia()
    kq["mo_hinh"]["phobert"]["moi_truong"]["ten_gpu"] = None
    tep.write_text(json.dumps(kq, ensure_ascii=False), encoding="utf-8")
    assert m.main(["--goc", str(tmp_path), "--kiem"]) == 1
    assert "không đo trên GPU: phobert" in capsys.readouterr().out
