"""Trainer dung chung cho MOI mo hinh cua du an (baseline va NS-MGAT).

[CD1.4b] Co che TIEP TUC (resume) da lam — S4.4 keo len som vi da mat hai lan
huan luyen bilstm do tien trinh bi giet giua chung. Dung nhu ke hoach da ghi:
chu ky `Trainer.train()` KHONG doi; bat/tat qua `cfg["train"]["resume"]`.

TIEP TUC MOT LAN CHAY DANG DO
------------------------------
Sau MOI epoch, ghi `checkpoints/<exp>/seed<N>/last.pt` gom du thu de dung lai
dung cho da dung:

    epoch da xong · trong so mo hinh · trang thai optimizer · scheduler ·
    GradScaler · best_macro_f1 · kien nhan con lai · thoi gian da chay ·
    va TRANG THAI SINH SO NGAU NHIEN (random, numpy, torch, torch.cuda)

Trang thai ngau nhien la phan de quen nhat va la phan quan trong nhat. Thieu
no thi thu tu xao tron du lieu tu epoch tiep theo se khac, va ket qua cua mot
lan chay bi ngat roi chay tiep se KHAC voi ket qua chay lien mach — luc do so
trong metrics.json khong con tai lap duoc. Co no thi hai duong di cho ra ket
qua giong het nhau; test `test_tiep_tuc_cho_ket_qua_GIONG_HET_chay_lien_mach`
khoa dieu do lai.

Ghi file theo kieu "ghi ra file tam roi doi ten" — mat dien giua chung thi
last.pt cu van con nguyen, khong bi cut dau.

GIA PHAI TRA: moi epoch ghi ~3 lan kich thuoc mo hinh (trong so + 2 buffer cua
AdamW). Voi bilstm (4M tham so) la ~48MB, khong dang ke. Voi phobert (135M) la
~1,6GB moi epoch — neu o cham thi dat `output.save_last_every: 2` de ghi cach
epoch, hoac `output.save_last: false` de tat han.
"""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup

from nsmgat.evaluate import evaluate, move_batch_to_device
from nsmgat.models.base import BaseModel
from nsmgat.utils.io import config_hash


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


def _luu_an_toan(obj: Any, path: Path) -> None:
    """Ghi ra file tam roi doi ten de. Mat dien/bi giet giua chung thi file cu
    van con nguyen ven, thay vi thanh mot file cut dau khong doc duoc.

    Path.replace() goi os.replace() — ghi de nguyen tu, chay dung tren Windows.
    """
    tam = path.with_name(path.name + ".tmp")
    torch.save(obj, tam)
    tam.replace(path)


def _trang_thai_ngau_nhien() -> Dict[str, Any]:
    """Chup lai trang thai CUA CA BON bo sinh so ngau nhien dang dung.

    Bon cai nay dung khop voi utils/seed.py:set_seed(). Thieu bat ky cai nao,
    lan chay tiep se re sang mot nhanh ngau nhien khac.
    """
    return {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state(),
        "torch_cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
    }


def _nap_trang_thai_ngau_nhien(tt: Dict[str, Any]) -> None:
    random.setstate(tt["python"])
    np.random.set_state(tt["numpy"])
    torch.set_rng_state(tt["torch"].cpu().to(torch.uint8))
    if tt.get("torch_cuda") is not None and torch.cuda.is_available():
        torch.cuda.set_rng_state_all(tt["torch_cuda"])


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
        # Khac best.pt (chi co trong so, va chi luu khi dev tot len): last.pt
        # ghi SAU MOI EPOCH va co du thu de dung lai dung cho da dung.
        self.last_path = self.ckpt_dir / "last.pt"
        # So giay huan luyen tich luy tu CAC PHIEN TRUOC (0 neu chay tu dau).
        # train.py cong vao train_time_sec de con so trong metrics.json van la
        # tong chi phi that, khong phai chi phi cua doan chay cuoi cung.
        self.thoi_gian_phien_truoc = 0.0

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
        bat_dau_tu = 1

        if train_cfg.get("resume", False):
            bat_dau_tu, best_macro_f1, patience_left = self._tiep_tuc(
                optimizer, scheduler, scaler
            )
        elif self.last_path.exists():
            self.logger.info(
                f"Co {self.last_path} tu lan chay truoc. Neu muon chay TIEP thay vi "
                f"chay lai tu dau, them --resume vao lenh."
            )

        moc_gio = time.time()

        for epoch in range(bat_dau_tu, train_cfg["epochs"] + 1):
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
            # dev_macro_f1 in 6 chu so chu khong phai 4: day la con so QUYET DINH
            # (luu best.pt hay khong, tru kien nhan hay khong). O 4 chu so, hai
            # epoch khac nhau that su co the in ra cung mot so — da gap that o
            # bilstm/seed42 epoch 6 va 7 deu ra 0.7933 — khien moi cong cu doc
            # log ve sau dem nguoc kien nhan lech mot epoch so voi thuc te.
            self.logger.info(
                f"[{self.exp_name}/seed{self.seed}] epoch {epoch}/{train_cfg['epochs']} "
                f"| train_loss={avg_loss:.4f} | dev_acc={dev_metrics['accuracy']:.4f} "
                f"| dev_macro_f1={dev_metrics['macro_f1']:.6f}"
            )

            dung_som = False
            if dev_metrics["macro_f1"] > best_macro_f1:
                best_macro_f1 = dev_metrics["macro_f1"]
                patience_left = train_cfg["early_stop_patience"]
                if save_best:
                    _luu_an_toan(self.model.state_dict(), self.ckpt_path)
            else:
                patience_left -= 1
                dung_som = patience_left <= 0

            # Ghi last.pt SAU khi da xu ly early stopping, de trang thai luu
            # xuong khop dung voi trang thai o cuoi epoch nay.
            da_chay = self.thoi_gian_phien_truoc + (time.time() - moc_gio)
            self._luu_de_tiep_tuc(
                epoch, optimizer, scheduler, scaler, best_macro_f1, patience_left,
                da_chay=da_chay, xong=dung_som or epoch >= train_cfg["epochs"],
            )

            if dung_som:
                self.logger.info(
                    f"Dung som o epoch {epoch} "
                    f"(khong cai thien sau {train_cfg['early_stop_patience']} epoch)"
                )
                break

        if not self.ckpt_path.exists():
            # epochs=0 hoac save_best=False - van luu de buoc load lai khong crash
            _luu_an_toan(self.model.state_dict(), self.ckpt_path)

        return self.ckpt_path

    # --- Tiep tuc mot lan chay dang do ---------------------------------------

    def _luu_de_tiep_tuc(
        self,
        epoch: int,
        optimizer: torch.optim.Optimizer,
        scheduler: Any,
        scaler: Any,
        best_macro_f1: float,
        patience_left: int,
        da_chay: float,
        xong: bool,
    ) -> None:
        out_cfg = self.cfg["output"]
        if not out_cfg.get("save_last", True):
            return
        cach = int(out_cfg.get("save_last_every", 1))
        if not xong and cach > 1 and epoch % cach != 0:
            return

        _luu_an_toan(
            {
                "epoch": epoch,
                "xong": xong,
                "model": self.model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "scheduler": scheduler.state_dict(),
                "scaler": scaler.state_dict(),
                "best_macro_f1": best_macro_f1,
                "patience_left": patience_left,
                "thoi_gian_da_chay": da_chay,
                "ngau_nhien": _trang_thai_ngau_nhien(),
                "config_hash": config_hash(self.cfg),
                "exp_name": self.exp_name,
                "seed": self.seed,
            },
            self.last_path,
        )

    def _tiep_tuc(
        self, optimizer: torch.optim.Optimizer, scheduler: Any, scaler: Any
    ) -> Tuple[int, float, int]:
        """Nap last.pt vao optimizer/scheduler/scaler/RNG, tra ve
        (epoch bat dau, best_macro_f1, kien nhan con lai)."""
        mac_dinh = (1, -1.0, self.cfg["train"]["early_stop_patience"])

        if not self.last_path.exists():
            self.logger.info(
                f"Yeu cau chay tiep nhung chua co {self.last_path} — chay tu dau."
            )
            return mac_dinh

        goi = torch.load(self.last_path, map_location=self.device, weights_only=False)

        # Tiep tuc bang mot cau hinh KHAC se cho ra ket qua lai giua hai cau
        # hinh — khong tai lap duoc, va config_hash trong metrics.json se noi doi.
        # Tha dung han con hon de so do di vao bao cao.
        hash_moi = config_hash(self.cfg)
        if goi.get("config_hash") != hash_moi:
            raise ValueError(
                "Khong the chay tiep: cau hinh da doi.\n"
                f"  last.pt sinh boi config_hash = {goi.get('config_hash')}\n"
                f"  config hien tai            = {hash_moi}\n"
                "Tiep tuc se tron hai cau hinh vao mot ket qua khong tai lap duoc.\n"
                "Chon mot trong hai: doi config ve nhu cu, hoac xoa "
                f"{self.last_path} de chay lai tu dau."
            )

        self.model.load_state_dict(goi["model"])
        self.model.to(self.device)
        optimizer.load_state_dict(goi["optimizer"])
        scheduler.load_state_dict(goi["scheduler"])
        scaler.load_state_dict(goi["scaler"])
        _nap_trang_thai_ngau_nhien(goi["ngau_nhien"])
        self.thoi_gian_phien_truoc = float(goi.get("thoi_gian_da_chay", 0.0))

        epoch_da_xong = int(goi["epoch"])
        if goi.get("xong"):
            self.logger.info(
                f"Lan chay truoc DA KET THUC o epoch {epoch_da_xong} — khong con gi de "
                f"chay tiep. Se danh gia lai tu {self.ckpt_path}."
            )
        else:
            self.logger.info(
                f"Chay tiep tu epoch {epoch_da_xong + 1}/{self.cfg['train']['epochs']} "
                f"(da chay {self.thoi_gian_phien_truoc / 60:.1f} phut, "
                f"best dev_macro_f1 = {goi['best_macro_f1']:.4f}, "
                f"kien nhan con {goi['patience_left']})"
            )
        return epoch_da_xong + 1, float(goi["best_macro_f1"]), int(goi["patience_left"])
