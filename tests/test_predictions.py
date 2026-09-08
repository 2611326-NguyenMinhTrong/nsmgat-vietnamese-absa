"""[GAP-011] Test file du doan tung mau `predictions.jsonl`.

Vi sao can file nay (khong phai chi de tich mot o trong tieu chi hoan thanh):
  - CD1.9 phan tich loi: ma tran nham lan, liet ke ca sai lam vi du muc 5.3
  - CD1.10 so sanh: kiem dinh McNemar giua hai mo hinh CAN du doan tung mau,
    `macro_f1` gop khong du de noi "khac biet nay co y nghia thong ke"
"""

from __future__ import annotations

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from nsmgat.data.dataset import ACSADataset, collate_fn
from nsmgat.evaluate import evaluate
from nsmgat.models.dummy import DummyModel
from nsmgat.utils.io import write_jsonl
from nsmgat.utils.seed import set_seed


def _fixture(path, n: int) -> None:
    write_jsonl(path, [
        {
            "uid": f"visfd-test-{i:05d}-GENERAL",
            "text": "May nay rat tot",
            "tokens": ["May", "nay", "rat", "tot"],
            "pos": ["N", "P", "R", "A"],
            "heads": [1, -1, 1, 1],
            "deprels": ["sub", "root", "adv", "vmod"],
            "aspect": "BATTERY" if i % 2 else "SCREEN",
            "label": i % 3,
            "domain": "visfd",
            "split": "test",
        }
        for i in range(n)
    ])


def _chay(tmp_path, n=12):
    set_seed(42)
    p = tmp_path / "test.jsonl"
    _fixture(p, n)
    tok = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    loader = DataLoader(ACSADataset(p, tok, 32), batch_size=5, collate_fn=collate_fn)
    cfg = {"data": {"train_path": str(p)}, "model": {}, "train": {}, "output": {}}
    return DummyModel(cfg), loader


def test_mac_dinh_KHONG_thu_du_doan(tmp_path):
    """evaluate() chay moi epoch tren tap dev — thu du doan o do la phi bo nho
    va khong ai dung. Phai la lua chon, khong phai mac dinh."""
    model, loader = _chay(tmp_path)
    assert "predictions" not in evaluate(model, loader, torch.device("cpu"))


def test_moi_mau_mot_dong_dung_thu_tu(tmp_path):
    model, loader = _chay(tmp_path, n=12)
    res = evaluate(model, loader, torch.device("cpu"), thu_tung_mau=True)
    rows = res["predictions"]

    assert len(rows) == 12
    assert [r["uid"] for r in rows] == [f"visfd-test-{i:05d}-GENERAL" for i in range(12)]
    assert [r["aspect"] for r in rows] == ["SCREEN" if i % 2 == 0 else "BATTERY" for i in range(12)]
    assert [r["y_true"] for r in rows] == [i % 3 for i in range(12)]


def test_moi_dong_du_truong_de_lam_McNemar_va_ma_tran_nham_lan(tmp_path):
    model, loader = _chay(tmp_path)
    rows = evaluate(model, loader, torch.device("cpu"), thu_tung_mau=True)["predictions"]
    for r in rows:
        assert set(r) == {"uid", "aspect", "y_true", "y_pred", "probs"}
        assert r["y_pred"] in (0, 1, 2)
        assert len(r["probs"]) == 3
        assert abs(sum(r["probs"]) - 1.0) < 1e-4, "probs phai la phan phoi xac suat"


def test_du_doan_khop_voi_accuracy_gop(tmp_path):
    """Neu hai cho nay lech nhau thi mot trong hai dang noi doi — va ca hai
    deu se di vao bao cao."""
    model, loader = _chay(tmp_path, n=15)
    res = evaluate(model, loader, torch.device("cpu"), thu_tung_mau=True)
    rows = res["predictions"]

    dung = sum(1 for r in rows if r["y_pred"] == r["y_true"])
    assert dung / len(rows) == res["accuracy"]
    # y_pred phai la argmax cua chinh probs trong cung mot dong
    for r in rows:
        assert r["y_pred"] == max(range(3), key=lambda i: r["probs"][i])


# --- Chay that CLI, kiem cai bay --no-train -----------------------------------


def _chay_cli(tmp_path, monkeypatch, them: list[str] = ()) -> dict:
    import json
    import sys

    import yaml

    from nsmgat import train as train_mod

    d = tmp_path
    for ten in ("train", "dev", "test"):
        _fixture(d / f"visfd_{ten}.jsonl", 20)

    cfg_path = d / "thu.yaml"
    cfg_path.write_text(yaml.safe_dump({
        "seed": 42,
        "device": "cpu",
        "data": {
            "train_path": str(d / "visfd_train.jsonl"),
            "dev_path": str(d / "visfd_dev.jsonl"),
            "test_path": str(d / "visfd_test.jsonl"),
            "diagnostic_path": str(d / "khong_co.jsonl"),
        },
        "model": {"name": "dummy", "encoder_name": "vinai/phobert-base-v2"},
        "train": {
            "epochs": 1, "batch_size": 8, "lr": 1e-2, "encoder_lr": 1e-2,
            "weight_decay": 0.0, "warmup_ratio": 0.1, "max_grad_norm": 1.0,
            "early_stop_patience": 3, "max_seq_len": 32, "use_amp": False,
        },
        "output": {
            "results_dir": str(d / "results"), "ckpt_dir": str(d / "ckpt"),
            "log_dir": str(d / "logs"), "save_best": True, "save_last": True,
        },
    }), encoding="utf-8")

    monkeypatch.setattr(sys, "argv", [
        "train", "--config", str(cfg_path), "--model", "dummy", "--seed", "42", *them,
    ])
    train_mod.main()
    return json.loads((d / "results" / "dummy" / "seed42" / "metrics.json").read_text(encoding="utf-8"))


def test_cli_ghi_predictions_jsonl_ben_canh_metrics(tmp_path, monkeypatch):
    from nsmgat.utils.io import read_jsonl

    _chay_cli(tmp_path, monkeypatch)
    pred = tmp_path / "results" / "dummy" / "seed42" / "predictions.jsonl"
    assert pred.exists(), "GAP-011: phai ghi predictions.jsonl canh metrics.json"

    rows = read_jsonl(pred)
    assert len(rows) == 20  # dung bang so Example cua tap test
    assert set(rows[0]) == {"uid", "aspect", "y_true", "y_pred", "probs"}


def test_no_train_KHONG_xoa_mat_train_time_sec_da_do_duoc(tmp_path, monkeypatch):
    """Cai bay: --no-train khong huan luyen nen do duoc ~0 giay. Ghi de len
    metrics.json cu se xoa mat chi phi huan luyen that — vd bilstm/seed42 =
    3389,7 s, chay lai de lay lai mat gan mot tieng. Va do la mot cot trong
    Bang 4.5 so sanh chi phi giua cac baseline.
    """
    import json

    lan_1 = _chay_cli(tmp_path, monkeypatch)
    mp = tmp_path / "results" / "dummy" / "seed42" / "metrics.json"

    # Dat mot con so nhan biet duoc thay vi dua vao dong ho: `dummy` huan luyen
    # 1 epoch het chua toi 0,05 s nen lam tron ra 0,0 — khong do duoc gi.
    # 3389.7 la chi phi that cua bilstm/seed42, dung luon cho de nho.
    goc = json.loads(mp.read_text(encoding="utf-8"))
    goc["train_time_sec"] = 3389.7
    mp.write_text(json.dumps(goc, ensure_ascii=False, indent=2), encoding="utf-8")

    lan_2 = _chay_cli(tmp_path, monkeypatch, them=["--no-train"])
    assert lan_2["train_time_sec"] == 3389.7, "--no-train da ghi de train_time_sec ve ~0"
    # Nhung ket qua danh gia thi van phai duoc tinh lai binh thuong
    assert lan_2["test"]["accuracy"] == lan_1["test"]["accuracy"]
