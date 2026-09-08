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


def evaluate(
    model: BaseModel,
    loader: DataLoader,
    device: torch.device,
    thu_tung_mau: bool = False,
) -> Dict[str, Any]:
    """Danh gia tren 1 loader, tra ve accuracy, macro_f1, f1_per_class.

    `thu_tung_mau=True` thi thu them du doan CUA TUNG MAU vao khoa
    "predictions" (xem `write_predictions`). Mac dinh TAT vi ham nay chay moi
    epoch tren tap dev — khong can giu lai gi. Chi bat khi danh gia tap test.

    [GAP-011] Truoc day chi tra ve so gop, nen khong lam duoc ma tran nham lan
    (CD1.9) lan kiem dinh McNemar giua hai mo hinh (CD1.10) — ca hai deu can
    du doan tung mau, khong phai macro_f1 gop.
    """
    model.eval()
    all_preds: List[int] = []
    all_labels: List[int] = []
    rows: List[Dict[str, Any]] = []

    with torch.no_grad():
        for batch in loader:
            batch = move_batch_to_device(batch, device)
            logits = model(batch)
            preds = logits.argmax(dim=-1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(batch["labels"].cpu().tolist())

            if thu_tung_mau:
                probs = torch.softmax(logits.float(), dim=-1).cpu().tolist()
                for uid, aspect, y_true, y_pred, p in zip(
                    batch["uid"], batch["aspect_text"],
                    batch["labels"].cpu().tolist(), preds.cpu().tolist(), probs,
                ):
                    rows.append({
                        "uid": uid,
                        "aspect": aspect,
                        "y_true": int(y_true),
                        "y_pred": int(y_pred),
                        "probs": [round(x, 6) for x in p],
                    })

    ket_qua = {
        "accuracy": accuracy_score(all_labels, all_preds),
        "macro_f1": f1_score(all_labels, all_preds, average="macro", labels=_LABELS, zero_division=0),
        "f1_per_class": f1_score(all_labels, all_preds, average=None, labels=_LABELS, zero_division=0).tolist(),
    }
    if thu_tung_mau:
        ket_qua["predictions"] = rows
    return ket_qua


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
