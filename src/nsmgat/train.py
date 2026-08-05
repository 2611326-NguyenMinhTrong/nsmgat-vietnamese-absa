"""CLI huan luyen/danh gia - entry point dung chung cho MOI mo hinh.

    python -m nsmgat.train --config configs/base.yaml --model dummy --seed 42

Dong bang o step nay: chu ky CLI (--config/--model/--seed/--exp-name/
--no-train) va luong load config -> set_seed -> dataset/loader -> model
(qua MODEL_REGISTRY) -> Trainer.train() -> load best ckpt -> evaluate ->
write_metrics. Them model moi = them 1 dong vao MODEL_REGISTRY, khong sua
luong nay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Type

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from nsmgat.data.dataset import ACSADataset, collate_fn
from nsmgat.evaluate import evaluate, evaluate_diagnostic, write_metrics
from nsmgat.models.base import BaseModel
from nsmgat.models.dummy import DummyModel
from nsmgat.trainer import Trainer, resolve_device
from nsmgat.utils.io import load_yaml
from nsmgat.utils.logging import get_logger
from nsmgat.utils.seed import set_seed

logger = get_logger(__name__)

# Them baseline/mo hinh moi: dang ky them 1 dong o day (ten -> class ke thua
# BaseModel, constructor nhan __init__(self, cfg: dict)).
MODEL_REGISTRY: Dict[str, Type[BaseModel]] = {
    "dummy": DummyModel,
}


def load_config(path: str | Path) -> Dict[str, Any]:
    """Doc YAML, ho tro ke thua qua khoa "extends: <file cung thu muc>".

    Config con chi can ghi de truong khac base.yaml; cac truong khong ghi
    de duoc giu nguyen tu file cha (deep-merge theo tung cap dict).
    """
    path = Path(path)
    cfg = load_yaml(path) or {}
    parent_name = cfg.pop("extends", None)
    if parent_name:
        parent_cfg = load_config(path.parent / parent_name)
        cfg = _deep_merge(parent_cfg, cfg)
    return cfg


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _config_hash(cfg: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:12]


def build_model(name: str, cfg: Dict[str, Any]) -> BaseModel:
    if name not in MODEL_REGISTRY:
        raise ValueError(f"Model '{name}' chua dang ky trong MODEL_REGISTRY: {list(MODEL_REGISTRY)}")
    return MODEL_REGISTRY[name](cfg)


def _dataset_name_from_path(path: str) -> str:
    """"data/processed/visfd_train.jsonl" -> "visfd"."""
    return Path(path).stem.rsplit("_", 1)[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Huan luyen/danh gia mo hinh nsmgat")
    parser.add_argument("--config", required=True, help="Duong dan file YAML config")
    parser.add_argument("--model", required=True, help="Ten model trong MODEL_REGISTRY")
    parser.add_argument("--seed", type=int, default=None, help="Ghi de cfg['seed'] neu co")
    parser.add_argument("--exp-name", default=None, help="Mac dinh = ten model")
    parser.add_argument(
        "--no-train", action="store_true", help="Chi danh gia bang checkpoint da co, khong huan luyen"
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    seed = args.seed if args.seed is not None else cfg.get("seed", 42)
    exp_name = args.exp_name or args.model
    cfg["seed"] = seed
    cfg.setdefault("model", {})["name"] = args.model

    set_seed(seed)
    device = resolve_device(cfg.get("device", "cpu"))

    tokenizer = AutoTokenizer.from_pretrained(cfg["model"].get("encoder_name", "vinai/phobert-base-v2"))
    max_seq_len = cfg["train"]["max_seq_len"]
    batch_size = cfg["train"]["batch_size"]

    train_ds = ACSADataset(cfg["data"]["train_path"], tokenizer, max_seq_len)
    dev_ds = ACSADataset(cfg["data"]["dev_path"], tokenizer, max_seq_len)
    test_ds = ACSADataset(cfg["data"]["test_path"], tokenizer, max_seq_len)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    dev_loader = DataLoader(dev_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)

    diag_path = Path(cfg["data"].get("diagnostic_path", ""))
    diag_loader = None
    if diag_path.exists():
        diag_ds = ACSADataset(diag_path, tokenizer, max_seq_len)
        diag_loader = DataLoader(diag_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)

    model = build_model(args.model, cfg)
    trainer = Trainer(model, cfg, train_loader, dev_loader, logger, exp_name=exp_name, seed=seed, device=device)

    start_time = time.time()
    if args.no_train:
        ckpt_path = trainer.ckpt_path
        if not ckpt_path.exists():
            raise FileNotFoundError(f"--no-train nhung chua co checkpoint: {ckpt_path}")
    else:
        ckpt_path = trainer.train()
    train_time_sec = time.time() - start_time

    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    model.to(device)

    test_res = evaluate(model, test_loader, device)
    diag_res = evaluate_diagnostic(model, diag_loader, device)

    results_dir = Path(cfg["output"]["results_dir"]) / exp_name / f"seed{seed}"
    results_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = results_dir / "metrics.json"

    meta = {
        "dataset": _dataset_name_from_path(cfg["data"]["train_path"]),
        "train_time_sec": round(train_time_sec, 1),
        "n_params": model.count_params(),
        "config_hash": _config_hash(cfg),
    }
    write_metrics(metrics_path, exp_name, seed, test_res, diag_res, meta)

    logger.info(f"Da ghi {metrics_path}")


if __name__ == "__main__":
    main()
