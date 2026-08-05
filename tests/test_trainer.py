"""Test end-to-end Trainer + evaluate + write_metrics voi DummyModel tren 50 mau.

Kiem tra khung train/eval dung chung hoat dong dung va metrics.json sinh ra
DUNG schema da dong bang o S0.4 (xem results/README.md).
"""

from __future__ import annotations

import json

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from nsmgat.data.dataset import ACSADataset, collate_fn
from nsmgat.evaluate import evaluate, evaluate_diagnostic, write_metrics
from nsmgat.models.dummy import DummyModel
from nsmgat.trainer import Trainer, resolve_device
from nsmgat.utils.io import write_jsonl
from nsmgat.utils.logging import get_logger
from nsmgat.utils.seed import set_seed

logger = get_logger("test_trainer")


def _make_fixture_jsonl(path, n: int) -> None:
    records = [
        {
            "uid": f"test-train-{i:05d}-GENERAL",
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
    ]
    write_jsonl(path, records)


def test_trainer_end_to_end_dummy(tmp_path):
    set_seed(42)

    train_path = tmp_path / "train.jsonl"
    dev_path = tmp_path / "dev.jsonl"
    test_path = tmp_path / "test.jsonl"
    _make_fixture_jsonl(train_path, n=50)
    _make_fixture_jsonl(dev_path, n=12)
    _make_fixture_jsonl(test_path, n=12)

    cfg = {
        "seed": 42,
        "device": "cpu",
        "data": {
            "train_path": str(train_path),
            "dev_path": str(dev_path),
            "test_path": str(test_path),
            "diagnostic_path": str(tmp_path / "diagnostic_khong_ton_tai.jsonl"),
        },
        "model": {"name": "dummy", "encoder_name": "vinai/phobert-base-v2"},
        "train": {
            "epochs": 2,
            "batch_size": 8,
            "lr": 1e-2,
            "encoder_lr": 1e-2,
            "weight_decay": 0.0,
            "warmup_ratio": 0.1,
            "max_grad_norm": 1.0,
            "early_stop_patience": 5,
            "max_seq_len": 32,
            "use_amp": False,
        },
        "output": {
            "results_dir": str(tmp_path / "results"),
            "ckpt_dir": str(tmp_path / "checkpoints"),
            "save_best": True,
        },
    }

    device = resolve_device(cfg["device"])
    tokenizer = AutoTokenizer.from_pretrained(cfg["model"]["encoder_name"])
    max_seq_len = cfg["train"]["max_seq_len"]
    batch_size = cfg["train"]["batch_size"]

    train_ds = ACSADataset(train_path, tokenizer, max_seq_len)
    dev_ds = ACSADataset(dev_path, tokenizer, max_seq_len)
    test_ds = ACSADataset(test_path, tokenizer, max_seq_len)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    dev_loader = DataLoader(dev_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)

    model = DummyModel(cfg)
    trainer = Trainer(
        model, cfg, train_loader, dev_loader, logger, exp_name="dummy_test", seed=42, device=device
    )
    ckpt_path = trainer.train()
    assert ckpt_path.exists()

    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    test_res = evaluate(model, test_loader, device)
    diag_res = evaluate_diagnostic(model, None, device)
    assert diag_res == {}

    metrics_path = tmp_path / "results" / "dummy_test" / "seed42" / "metrics.json"
    meta = {
        "dataset": "test",
        "train_time_sec": 1.0,
        "n_params": model.count_params(),
        "config_hash": "abc123",
    }
    write_metrics(metrics_path, "dummy_test", 42, test_res, diag_res, meta)

    assert metrics_path.exists()
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))

    assert payload["exp_name"] == "dummy_test"
    assert payload["seed"] == 42
    assert payload["dataset"] == "test"
    assert set(payload["test"].keys()) == {"accuracy", "macro_f1", "f1_per_class"}
    assert len(payload["test"]["f1_per_class"]) == 3
    assert set(payload["diagnostic"].keys()) == {"negation", "contrast", "regular"}
    for group in ("negation", "contrast", "regular"):
        assert payload["diagnostic"][group] == {"macro_f1": 0.0, "n": 0}
    assert payload["train_time_sec"] == 1.0
    assert payload["n_params"] == model.count_params()
    assert payload["config_hash"] == "abc123"
