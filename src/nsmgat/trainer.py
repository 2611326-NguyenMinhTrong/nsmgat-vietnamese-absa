"""Trainer dung chung cho MOI mo hinh cua du an (baseline va NS-MGAT).

Co che resume (luu/tiep tuc optimizer+scheduler+epoch qua cac phien Colab
bi ngat) se duoc THEM o S4.4, KHONG doi chu ky Trainer.train() khi lam viec do.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup

from nsmgat.evaluate import evaluate, move_batch_to_device
from nsmgat.models.base import BaseModel


def resolve_device(name: str) -> torch.device:
    """Chuyen ten thiet bi trong config thanh torch.device.

    Tu dong lui ve cpu neu yeu cau "cuda" nhung khong co GPU - de chay
    duoc tren may local khong GPU (huan luyen that van chay tren Colab,
    xem chien luoc o S4.4).
    """
    if name == "cuda" and not torch.cuda.is_available():
        return torch.device("cpu")
    return torch.device(name)


def _build_optimizer(model: nn.Module, cfg: Dict[str, Any]) -> torch.optim.Optimizer:
    """AdamW voi learning rate rieng cho encoder (neu model co thuoc tinh
    `.encoder`, vd PhoBERTClassifier o S1.1) va phan con lai (head)."""
    train_cfg = cfg["train"]
    if hasattr(model, "encoder"):
        encoder_params = list(model.encoder.parameters())
        encoder_ids = {id(p) for p in encoder_params}
        head_params = [p for p in model.parameters() if id(p) not in encoder_ids]
        param_groups = [
            {"params": encoder_params, "lr": train_cfg["encoder_lr"]},
            {"params": head_params, "lr": train_cfg["lr"]},
        ]
    else:
        param_groups = [{"params": list(model.parameters()), "lr": train_cfg["lr"]}]
    return torch.optim.AdamW(param_groups, weight_decay=train_cfg["weight_decay"])


class Trainer:
    """Vong lap huan luyen dung chung: AdamW (lr rieng encoder/head), linear
    warmup, gradient clipping, early stopping theo dev macro-F1, luu
    checkpoint tot nhat, mixed precision tuy chon qua config.
    """

    def __init__(
        self,
        model: BaseModel,
        cfg: Dict[str, Any],
        train_loader: DataLoader,
        dev_loader: DataLoader,
        logger,
        exp_name: str,
        seed: int,
        device: Optional[torch.device] = None,
    ):
        self.model = model
        self.cfg = cfg
        self.train_loader = train_loader
        self.dev_loader = dev_loader
        self.logger = logger
        self.exp_name = exp_name
        self.seed = seed
        self.device = device or resolve_device(cfg.get("device", "cpu"))
        self.model.to(self.device)

        self.ckpt_dir = Path(cfg["output"]["ckpt_dir"]) / exp_name / f"seed{seed}"
        self.ckpt_dir.mkdir(parents=True, exist_ok=True)
        self.ckpt_path = self.ckpt_dir / "best.pt"

    def train(self) -> Path:
        """Chay vong lap huan luyen, tra ve duong dan checkpoint tot nhat."""
        train_cfg = self.cfg["train"]
        save_best = self.cfg["output"].get("save_best", True)

        optimizer = _build_optimizer(self.model, self.cfg)
        total_steps = max(1, train_cfg["epochs"] * len(self.train_loader))
        warmup_steps = int(train_cfg["warmup_ratio"] * total_steps)
        scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

        use_amp = bool(train_cfg.get("use_amp", False)) and self.device.type == "cuda"
        scaler = torch.amp.GradScaler(self.device.type, enabled=use_amp)
        criterion = nn.CrossEntropyLoss()

        best_macro_f1 = -1.0
        patience_left = train_cfg["early_stop_patience"]

        for epoch in range(1, train_cfg["epochs"] + 1):
            self.model.train()
            total_loss = 0.0
            n_batches = 0

            for batch in self.train_loader:
                batch = move_batch_to_device(batch, self.device)
                optimizer.zero_grad()

                with torch.amp.autocast(self.device.type, enabled=use_amp):
                    logits = self.model(batch)
                    loss = criterion(logits, batch["labels"])

                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), train_cfg["max_grad_norm"])
                scaler.step(optimizer)
                scaler.update()
                scheduler.step()

                total_loss += loss.item()
                n_batches += 1

            avg_loss = total_loss / max(1, n_batches)
            dev_metrics = evaluate(self.model, self.dev_loader, self.device)
            self.logger.info(
                f"[{self.exp_name}/seed{self.seed}] epoch {epoch}/{train_cfg['epochs']} "
                f"| train_loss={avg_loss:.4f} | dev_acc={dev_metrics['accuracy']:.4f} "
                f"| dev_macro_f1={dev_metrics['macro_f1']:.4f}"
            )

            if dev_metrics["macro_f1"] > best_macro_f1:
                best_macro_f1 = dev_metrics["macro_f1"]
                patience_left = train_cfg["early_stop_patience"]
                if save_best:
                    torch.save(self.model.state_dict(), self.ckpt_path)
            else:
                patience_left -= 1
                if patience_left <= 0:
                    self.logger.info(
                        f"Dung som o epoch {epoch} "
                        f"(khong cai thien sau {train_cfg['early_stop_patience']} epoch)"
                    )
                    break

        if not self.ckpt_path.exists():
            # epochs=0 hoac save_best=False - van luu de buoc load lai khong crash
            torch.save(self.model.state_dict(), self.ckpt_path)

        return self.ckpt_path
