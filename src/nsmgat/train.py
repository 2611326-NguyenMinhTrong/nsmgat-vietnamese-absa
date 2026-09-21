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
from nsmgat.models.bilstm import BiLSTMModel
from nsmgat.models.dummy import DummyModel
from nsmgat.models.lexicon import LexiconModel
from nsmgat.models.phobert import PhoBERTClassifier
from nsmgat.trainer import Trainer, resolve_device
# load_config nam o utils/io.py de cong cu nho khong bi keo theo transformers
# (xem ghi chu trong ham do). Van import lai o day de
# `from nsmgat.train import load_config` khong gay.
from nsmgat.utils.io import config_hash, load_config, write_jsonl  # noqa: F401
from nsmgat.utils.logging import get_logger, them_file_log
from nsmgat.utils.seed import set_seed

logger = get_logger(__name__)

# Them baseline/mo hinh moi: dang ky them 1 dong o day (ten -> class ke thua
# BaseModel, constructor nhan __init__(self, cfg: dict)).
MODEL_REGISTRY: Dict[str, Type[BaseModel]] = {
    "dummy": DummyModel,
    "lexicon": LexiconModel,  # [CD1.4a] baseline tu dien — san tuyet doi
    "bilstm": BiLSTMModel,  # [CD1.4b] moc truoc ky nguyen tien huan luyen
    "phobert": PhoBERTClassifier,  # [CD1.5] moc so sanh chinh cua Chuong 4
}


# Chuyen sang utils/io.py de Trainer dung chung khi doi chieu luc --resume.
# Giu ten cu o day cho cac cho da import.
_config_hash = config_hash


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
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Chay TIEP tu checkpoints/<exp>/seed<N>/last.pt thay vi chay lai tu dau",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    seed = args.seed if args.seed is not None else cfg.get("seed", 42)
    exp_name = args.exp_name or args.model
    cfg["seed"] = seed
    cfg.setdefault("model", {})["name"] = args.model
    cfg["train"]["resume"] = args.resume

    set_seed(seed)
    device = resolve_device(cfg.get("device", "cpu"))

    # Ghi log ra file de theo doi tu cua so khac (scripts/watch_train.py) va de
    # log con lai sau khi dong terminal. Dong moc duoi day la thu watch_train.py
    # dua vao de biet lan chay hien tai bat dau tu dau va doc config nao.
    log_path = them_file_log(
        logger, Path(cfg["output"].get("log_dir", "logs")) / exp_name / f"seed{seed}.log"
    )
    logger.info(
        f"=== BAT DAU {exp_name}/seed{seed} | config={args.config} | device={device} ==="
    )
    logger.info(f"Log ghi tai {log_path} — theo doi: python scripts/watch_train.py "
                f"--exp {exp_name} --seed {seed}")

    tokenizer = AutoTokenizer.from_pretrained(cfg["model"].get("encoder_name", "vinai/phobert-base-v2"))
    max_seq_len = cfg["train"]["max_seq_len"]
    batch_size = cfg["train"]["batch_size"]

    # pair_mode: noi khia canh vao cau thanh cap (chi phobert bat, xem
    # dataset.py). Mac dinh False de khong doi dau vao cua bilstm.
    pair_mode = bool(cfg["data"].get("pair_mode", False))

    train_ds = ACSADataset(cfg["data"]["train_path"], tokenizer, max_seq_len, pair_mode)
    dev_ds = ACSADataset(cfg["data"]["dev_path"], tokenizer, max_seq_len, pair_mode)
    test_ds = ACSADataset(cfg["data"]["test_path"], tokenizer, max_seq_len, pair_mode)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    dev_loader = DataLoader(dev_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)

    diag_path = Path(cfg["data"].get("diagnostic_path", ""))
    diag_loader = None
    if diag_path.exists():
        diag_ds = ACSADataset(diag_path, tokenizer, max_seq_len, pair_mode)
        diag_loader = DataLoader(diag_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)

    model = build_model(args.model, cfg)
    trainer = Trainer(model, cfg, train_loader, dev_loader, logger, exp_name=exp_name, seed=seed, device=device)

    # Moc nay tach thoi gian KHOI DONG (dung dataset + dung mo hinh) khoi thoi
    # gian huan luyen that, de epoch 1 khong nhin nhu cham bat thuong.
    #
    # LUU Y: day KHONG phai chi phi tokenize ma GAP-008 noi toi. ACSADataset
    # tokenize LUOI — trong __getitem__, tuc la trai deu vao trong cac epoch,
    # khong nam o day. Rieng bilstm co tokenize truoc o day de dung id_map.
    logger.info("Chuan bi xong (dung dataset + mo hinh) — bat dau huan luyen")

    start_time = time.time()
    if args.no_train:
        ckpt_path = trainer.ckpt_path
        if not ckpt_path.exists():
            raise FileNotFoundError(f"--no-train nhung chua co checkpoint: {ckpt_path}")
    else:
        ckpt_path = trainer.train()
    # Cong ca thoi gian cua CAC PHIEN TRUOC (khac 0 khi --resume): con so trong
    # metrics.json phai la tong chi phi huan luyen that, khong phai chi phi cua
    # rieng doan chay cuoi cung. Neu khong, mot mo hinh bi ngat vai lan se nhin
    # nhu re hon han cac mo hinh khac trong Bang 4.5.
    train_time_sec = time.time() - start_time + trainer.thoi_gian_phien_truoc

    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    model.to(device)

    test_res = evaluate(model, test_loader, device, thu_tung_mau=True)
    diag_res = evaluate_diagnostic(model, diag_loader, device)

    results_dir = Path(cfg["output"]["results_dir"]) / exp_name / f"seed{seed}"
    results_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = results_dir / "metrics.json"

    # --no-train KHONG huan luyen gi, nen train_time_sec do duoc o day ~ 0.
    # Ghi de len metrics.json cu se XOA MAT chi phi huan luyen that da do
    # duoc — vd bilstm/seed42 = 3389,7 s. Con so do la mot cot trong Bang 4.5,
    # va chay lai de lay lai mat gan mot tieng. Nen giu lai con so cu.
    if args.no_train and metrics_path.exists():
        cu = json.loads(metrics_path.read_text(encoding="utf-8"))
        train_time_sec = cu.get("train_time_sec", train_time_sec)
        logger.info(
            f"--no-train: giu nguyen train_time_sec = {train_time_sec} s tu lan chay truoc "
            f"(lan nay khong huan luyen nen khong do duoc)"
        )

    meta = {
        "dataset": _dataset_name_from_path(cfg["data"]["train_path"]),
        "train_time_sec": round(train_time_sec, 1),
        "n_params": model.count_params(),
        "config_hash": _config_hash(cfg),
    }
    write_metrics(metrics_path, exp_name, seed, test_res, diag_res, meta)
    pred_path = results_dir / "predictions.jsonl"
    write_jsonl(pred_path, test_res["predictions"])

    logger.info(f"Da ghi {metrics_path}")
    logger.info(f"Da ghi {pred_path} ({len(test_res['predictions']):,} dong)")
    logger.info(f"=== KET THUC {exp_name}/seed{seed} ===")


if __name__ == "__main__":
    main()
