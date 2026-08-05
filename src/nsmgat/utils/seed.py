"""Khoa seed ngau nhien de dam bao tai lap duoc giua cac lan chay."""

import os
import random

import numpy as np
import torch


def set_seed(seed: int) -> None:
    """Khoa seed cho random, numpy, torch (CPU + CUDA) va bat che do deterministic."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
