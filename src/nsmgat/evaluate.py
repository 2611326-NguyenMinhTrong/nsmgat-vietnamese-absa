"""Danh gia mo hinh + ghi metrics.json theo schema DA DONG BANG o step nay.

Xem schema day du va ly do dong bang trong results/README.md.
"""

from __future__ import annotations

import collections
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from sklearn.metrics import accuracy_score, f1_score
from torch.utils.data import DataLoader

from nsmgat.models.base import BaseModel
from nsmgat.utils.io import save_json

_LABELS = [0, 1, 2]


def move_batch_to_device(batch: Dict[str, Any], device: torch.device) -> Dict[str, Any]:
    """Chuyen moi tensor trong batch sang device; giu nguyen cac truong khong
    phai tensor (uid, aspect_text, word_ids, phenomenon - deu la list thuong)."""
    return {
        key: (value.to(device) if isinstance(value, torch.Tensor) else value)
        for key, value in batch.items()
    }


def evaluate(model: BaseModel, loader: DataLoader, device: torch.device) -> Dict[str, Any]:
    """Danh gia tren 1 loader, tra ve accuracy, macro_f1, f1_per_class."""
    model.eval()
    all_preds: List[int] = []
    all_labels: List[int] = []

    with torch.no_grad():
        for batch in loader:
            batch = move_batch_to_device(batch, device)
            logits = model(batch)
            preds = logits.argmax(dim=-1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(batch["labels"].cpu().tolist())

    return {
        "accuracy": accuracy_score(all_labels, all_preds),
        "macro_f1": f1_score(all_labels, all_preds, average="macro", labels=_LABELS, zero_division=0),
        "f1_per_class": f1_score(all_labels, all_preds, average=None, labels=_LABELS, zero_division=0).tolist(),
    }


def evaluate_diagnostic(
    model: BaseModel, diag_loader: Optional[DataLoader], device: torch.device
) -> Dict[str, Dict[str, Any]]:
    """Danh gia rieng theo tung nhom "phenomenon" (negation/contrast/regular/
    both - tuy du lieu thuc te co gi). Neu chua co tap chan doan
    (diag_loader la None hoac rong) thi tra ve {} - KHONG crash, vi tap nay
    chi duoc tao o S6.4.
    """
    if diag_loader is None or len(diag_loader.dataset) == 0:
        return {}

    model.eval()
    preds_by_group: Dict[str, List[int]] = collections.defaultdict(list)
    labels_by_group: Dict[str, List[int]] = collections.defaultdict(list)

    with torch.no_grad():
        for batch in diag_loader:
            labels = batch["labels"].cpu().tolist()
            moved = move_batch_to_device(batch, device)
            logits = model(moved)
            preds = logits.argmax(dim=-1).cpu().tolist()
            for phenomenon, pred, label in zip(batch["phenomenon"], preds, labels):
                group = phenomenon or "regular"
                preds_by_group[group].append(pred)
                labels_by_group[group].append(label)

    result: Dict[str, Dict[str, Any]] = {}
    for group, preds in preds_by_group.items():
        labels = labels_by_group[group]
        result[group] = {
            "macro_f1": f1_score(labels, preds, average="macro", labels=_LABELS, zero_division=0),
            "n": len(labels),
        }
    return result


def write_metrics(
    path: str | Path,
    exp_name: str,
    seed: int,
    test_res: Dict[str, Any],
    diag_res: Dict[str, Dict[str, Any]],
    meta: Dict[str, Any],
) -> None:
    """Ghi metrics.json DUNG schema da dong bang (xem results/README.md).

    meta phai co cac khoa: dataset, train_time_sec, n_params, config_hash.
    3 nhom negation/contrast/regular luon co mat (mac dinh 0 neu chua danh
    gia duoc); nhom nao diag_res co that (vd "both") se duoc giu lai them.
    """
    payload = {
        "exp_name": exp_name,
        "seed": seed,
        "dataset": meta["dataset"],
        "test": {
            "accuracy": test_res["accuracy"],
            "macro_f1": test_res["macro_f1"],
            "f1_per_class": list(test_res["f1_per_class"]),
        },
        "diagnostic": {
            "negation": {"macro_f1": 0.0, "n": 0},
            "contrast": {"macro_f1": 0.0, "n": 0},
            "regular": {"macro_f1": 0.0, "n": 0},
            **diag_res,
        },
        "train_time_sec": meta.get("train_time_sec", 0),
        "n_params": meta.get("n_params", 0),
        "config_hash": meta.get("config_hash", ""),
    }
    save_json(path, payload)
