"""[CD1.10] Đo chi phí suy luận của các mô hình trong CÙNG MỘT điều kiện.

Không huấn luyện gì. Với mỗi thí nghiệm: dựng mô hình từ file cấu hình, nạp
checkpoints/<exp>/seed<N>/best.pt, cho chạy qua tập kiểm tra và đo thời gian cùng bộ nhớ GPU đỉnh.

    python scripts/profile_cost.py                              # sáu mô hình, seed 42, ghi results/cost_profile.json
    python scripts/profile_cost.py --exp phobert asgcn          # chỉ vài mô hình; mục cũ của mô hình khác được giữ
    python scripts/profile_cost.py --so-mau 64 --lap 1 --chi-in # thử nhanh ở máy, không ghi file

ĐIỀU KIỆN ĐO, GIỐNG NHAU CHO MỌI MÔ HÌNH
----------------------------------------
- Cùng thiết bị (GPU nếu có), cùng tập mẫu (tập kiểm tra, theo đúng thứ tự file), cùng kích thước lô.
- Không dùng độ chính xác hỗn hợp, vì hàm đánh giá đã sinh ra các con số của báo cáo cũng không dùng.
- Đầu vào được tách subword và gộp lô TRƯỚC khi bấm giờ. Thời gian đo là thời gian của mô hình:
  chuyển lô sang thiết bị, lan truyền xuôi, lấy nhãn. Với ba mô hình đồ thị, phần này gồm cả việc
  dựng ma trận kề cho từng lô. Thời gian phân tích cú pháp bằng VnCoreNLP KHÔNG nằm trong đó.
- Mỗi cấu hình chạy vài lô khởi động rồi lặp `--lap` lần; con số báo cáo là trung vị.
- Mô hình từ điển có bộ nhớ đệm đặc trưng theo mẫu; bộ nhớ đệm đó được xoá trước mỗi lần lặp.

HAI CHỖ PHẢI ĐỌC KỸ TRONG FILE KẾT QUẢ
--------------------------------------
- `trong_so`: "best.pt" là bộ trọng số đã huấn luyện; "khoi_tao" là không tìm thấy best.pt nên mô hình
  mang trọng số lúc khởi tạo. Thời gian và bộ nhớ không phụ thuộc giá trị trọng số, nhưng khi đó
  không kiểm được dự đoán, và báo cáo phải ghi rõ.
- `so_du_doan_khac`: số mẫu mà nhãn dự đoán ở lần đo khác với results/<exp>/seed<N>/predictions.jsonl.
  Bằng 0 là mô hình đang đo đúng là mô hình đã cho các con số của báo cáo.
"""

from __future__ import annotations

import argparse
import datetime
import gc
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

for _luong in (sys.stdout, sys.stderr):  # thong bao loi cung phai in duoc tieng Viet tren console Windows
    if hasattr(_luong, "reconfigure"):
        _luong.reconfigure(encoding="utf-8", errors="replace")

# exp -> (file cấu hình, tên mô hình trong MODEL_REGISTRY)
THI_NGHIEM = {
    "lexicon": ("configs/lexicon.yaml", "lexicon"),
    "bilstm": ("configs/bilstm.yaml", "bilstm"),
    "phobert": ("configs/phobert.yaml", "phobert"),
    "asgcn": ("configs/asgcn.yaml", "asgcn"),
    "asgcn_linked": ("configs/asgcn_linked.yaml", "asgcn"),
    "senticgcn": ("configs/senticgcn.yaml", "senticgcn"),
}
CO_LO_MAC_DINH = (1, 32)
RA_MAC_DINH = Path("results/cost_profile.json")


def moi_truong(device) -> Dict[str, Any]:
    """Ghi lại nơi phép đo diễn ra, để hai lần đo ở hai nơi khác nhau không bị trộn mà không ai biết."""
    import torch
    import transformers

    mt: Dict[str, Any] = {
        "thoi_diem": datetime.datetime.now().isoformat(timespec="seconds"),
        "thiet_bi": str(device),
        "ten_gpu": None,
        "bo_nho_gpu_mb": None,
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "python": platform.python_version(),
        "he_dieu_hanh": platform.platform(),
        "bo_xu_ly": platform.processor() or platform.machine(),
        "commit": None,
    }
    if device.type == "cuda":
        mt["ten_gpu"] = torch.cuda.get_device_name(device)
        mt["bo_nho_gpu_mb"] = round(torch.cuda.get_device_properties(device).total_memory / 2**20)
    try:
        mt["commit"] = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                                      timeout=10).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        pass
    return mt


def chia_lo(items: Sequence[dict], co_lo: int, collate) -> List[dict]:
    return [collate(list(items[i:i + co_lo])) for i in range(0, len(items), co_lo)]


def do_thoi_gian(model, lo: List[dict], device, lap: int, khoi_dong: int) -> Dict[str, Any]:
    """Chạy `lap` lần qua mọi lô. Trả về thời gian từng lần (giây), nhãn dự đoán và bộ nhớ GPU đỉnh (byte)."""
    import torch

    from nsmgat.evaluate import move_batch_to_device

    cuda = device.type == "cuda"

    def dong_bo():
        if cuda:
            torch.cuda.synchronize(device)

    model.eval()
    thoi_gian: List[float] = []
    nhan: List[int] = []
    with torch.no_grad():
        for b in lo[:khoi_dong]:
            model(move_batch_to_device(b, device))
        dong_bo()
        if cuda:
            torch.cuda.reset_peak_memory_stats(device)
        for _ in range(lap):
            if hasattr(model, "_cache"):
                model._cache.clear()
            ra = []
            dong_bo()
            t0 = time.perf_counter()
            for b in lo:
                ra.append(model(move_batch_to_device(b, device)).argmax(dim=-1))
            dong_bo()
            thoi_gian.append(time.perf_counter() - t0)
            nhan = [int(x) for r in ra for x in r.cpu().tolist()]
    return {"thoi_gian": thoi_gian, "nhan": nhan,
            "dinh": int(torch.cuda.max_memory_allocated(device)) if cuda else None,
            "dinh_giu_cho": int(torch.cuda.max_memory_reserved(device)) if cuda else None}


def doc_du_doan_cu(goc: Path, exp: str, seed: int) -> Optional[Dict[str, int]]:
    """Dự đoán đã công bố của thí nghiệm, để đối chiếu với lần đo.

    Tìm ở results/ rồi results_local/: trên Colab, notebook nối results/ sang Drive và đổi tên thư mục
    results/ của repo thành results_local/, nên dự đoán của hai mô hình chạy ở máy nằm ở thư mục sau.
    """
    for thu_muc in ("results", "results_local"):
        p = goc / thu_muc / exp / f"seed{seed}" / "predictions.jsonl"
        if p.exists():
            with p.open(encoding="utf-8") as fh:
                return {r["uid"]: int(r["y_pred"]) for r in map(json.loads, fh)}
    return None


def do_mot(exp: str, seed: int, device, co_lo: Sequence[int], so_mau: Optional[int], lap: int, khoi_dong: int,
           goc: Path) -> Dict[str, Any]:
    """Đo một thí nghiệm. Lỗi ở một kích thước lô được ghi vào kết quả chứ không làm dừng các phép đo khác."""
    import torch
    from transformers import AutoTokenizer

    from nsmgat.data.dataset import ACSADataset, collate_fn
    from nsmgat.train import build_model
    from nsmgat.utils.io import load_config
    from nsmgat.utils.seed import set_seed

    tep_cau_hinh, ten_mo_hinh = THI_NGHIEM[exp]
    cfg = load_config(goc / tep_cau_hinh)
    cfg["seed"] = seed
    cfg.setdefault("model", {})["name"] = ten_mo_hinh
    set_seed(seed)

    tokenizer = AutoTokenizer.from_pretrained(cfg["model"].get("encoder_name", "vinai/phobert-base-v2"))
    ds = ACSADataset(cfg["data"]["test_path"], tokenizer, cfg["train"]["max_seq_len"],
                     bool(cfg["data"].get("pair_mode", False)))
    n = len(ds) if so_mau is None else min(so_mau, len(ds))

    t0 = time.perf_counter()
    items = [ds[i] for i in range(n)]
    tach_subword_ms = (time.perf_counter() - t0) / n * 1000

    model = build_model(ten_mo_hinh, cfg)
    ckpt = Path(cfg["output"]["ckpt_dir"]) / exp / f"seed{seed}" / "best.pt"
    if ckpt.exists():
        model.load_state_dict(torch.load(ckpt, map_location="cpu"))
        trong_so = "best.pt"
    else:
        trong_so = "khoi_tao"
        print(f"  CHÚ Ý: không thấy {ckpt}; {exp} được đo với trọng số lúc khởi tạo, không kiểm được dự đoán.")
    model.to(device)

    ra: Dict[str, Any] = {
        "exp": exp, "seed": seed, "so_tham_so": model.count_params(), "trong_so": trong_so, "so_mau": n,
        "ca_tap_kiem_tra": n == len(ds), "do_dai_toi_da": cfg["train"]["max_seq_len"], "so_lan_lap": lap,
        "tach_subword_ms_moi_mau": round(tach_subword_ms, 4), "theo_co_lo": {},
    }
    if device.type == "cuda":
        ra["bo_nho_trong_so_mb"] = round(torch.cuda.memory_allocated(device) / 2**20, 1)

    cu = doc_du_doan_cu(goc, exp, seed) if trong_so == "best.pt" else None
    vang = [it["label"] for it in items]
    for c in co_lo:
        try:
            kq = do_thoi_gian(model, chia_lo(items, c, collate_fn), device, lap, khoi_dong)
        except Exception as e:  # ghi lỗi rồi đo tiếp: một mô hình hỏng không được làm mất số của mô hình khác
            ra["theo_co_lo"][str(c)] = {"loi": f"{type(e).__name__}: {e}"}
            print(f"  LỖI ở {exp}, lô {c}: {type(e).__name__}: {e}")
            continue
        ms = [t / n * 1000 for t in kq["thoi_gian"]]
        muc = {
            "ms_moi_mau": round(statistics.median(ms), 4), "ms_nho_nhat": round(min(ms), 4),
            "ms_lon_nhat": round(max(ms), 4), "mau_moi_giay": round(1000 / statistics.median(ms), 1),
            "bo_nho_dinh_mb": None if kq["dinh"] is None else round(kq["dinh"] / 2**20, 1),
            "bo_nho_giu_cho_dinh_mb": None if kq["dinh_giu_cho"] is None else round(kq["dinh_giu_cho"] / 2**20, 1),
            "accuracy": round(sum(int(a == b) for a, b in zip(kq["nhan"], vang)) / n, 6),
            "so_du_doan_khac": None,
        }
        if cu is not None:
            muc["so_du_doan_khac"] = sum(int(cu.get(it["uid"]) != y) for it, y in zip(items, kq["nhan"]))
        ra["theo_co_lo"][str(c)] = muc
    return ra


def in_bang(ket_qua: Dict[str, Dict[str, Any]], co_lo: Sequence[int]) -> None:
    dau = f"{'mô hình':<14}{'trọng số':<10}{'tham số':>12}"
    for c in co_lo:
        dau += f"{'ms/mẫu lô ' + str(c):>16}{'đỉnh MB':>10}{'khác':>6}"
    print(dau)
    for exp, r in ket_qua.items():
        dong = f"{exp:<14}{r['trong_so']:<10}{r['so_tham_so']:>12,}"
        for c in co_lo:
            m = r["theo_co_lo"].get(str(c), {})
            if "loi" in m or not m:
                dong += f"{'LỖI':>16}{'':>10}{'':>6}"
                continue
            dinh = "" if m["bo_nho_dinh_mb"] is None else f"{m['bo_nho_dinh_mb']:.0f}"
            khac = "" if m["so_du_doan_khac"] is None else str(m["so_du_doan_khac"])
            dong += f"{m['ms_moi_mau']:>16.3f}{dinh:>10}{khac:>6}"
        print(dong)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đo thời gian suy luận và bộ nhớ GPU đỉnh của các mô hình trong cùng một điều kiện.")
    ap.add_argument("--exp", nargs="+", default=list(THI_NGHIEM), choices=list(THI_NGHIEM), help="thí nghiệm cần đo (mặc định cả sáu)")
    ap.add_argument("--seed", type=int, default=42, help="lấy best.pt của seed nào (mặc định 42)")
    ap.add_argument("--co-lo", nargs="+", type=int, default=list(CO_LO_MAC_DINH), help="các kích thước lô cần đo (mặc định 1 và 32)")
    ap.add_argument("--so-mau", type=int, default=None, help="chỉ đo trên N mẫu đầu của tập kiểm tra (mặc định cả tập)")
    ap.add_argument("--lap", type=int, default=3, help="số lần lặp cho mỗi cấu hình, lấy trung vị (mặc định 3)")
    ap.add_argument("--khoi-dong", type=int, default=5, help="số lô chạy khởi động trước khi bấm giờ (mặc định 5)")
    ap.add_argument("--device", default="auto", help="auto, cuda hoặc cpu (mặc định auto: có GPU thì dùng)")
    ap.add_argument("--goc", type=Path, default=Path("."), help="thư mục gốc của repo")
    ap.add_argument("--out", type=Path, default=RA_MAC_DINH, help=f"file kết quả (mặc định {RA_MAC_DINH})")
    ap.add_argument("--chi-in", action="store_true", help="chỉ in bảng, không ghi file")
    a = ap.parse_args(argv)

    import torch

    device = torch.device("cuda" if (a.device == "auto" and torch.cuda.is_available()) else ("cpu" if a.device == "auto" else a.device))
    mt = moi_truong(device)
    print(f"Thiết bị: {mt['ten_gpu'] or mt['thiet_bi']} | torch {mt['torch']} | transformers {mt['transformers']}")

    ket_qua: Dict[str, Dict[str, Any]] = {}
    for exp in a.exp:
        print(f"Đang đo {exp} ...")
        r = do_mot(exp, a.seed, device, a.co_lo, a.so_mau, a.lap, a.khoi_dong, a.goc)
        r["moi_truong"] = mt
        ket_qua[exp] = r
        gc.collect()
        if device.type == "cuda":
            torch.cuda.empty_cache()
    print()
    in_bang(ket_qua, a.co_lo)

    if a.chi_in:
        return 0
    ra = a.goc / a.out
    cu = json.loads(ra.read_text(encoding="utf-8")) if ra.exists() else {"mo_hinh": {}}
    cu["mo_hinh"].update(ket_qua)
    cu["mo_hinh"] = {k: cu["mo_hinh"][k] for k in THI_NGHIEM if k in cu["mo_hinh"]}
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_text(json.dumps(cu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"\nĐã ghi {ra} ({len(cu['mo_hinh'])} mô hình)")
    thieu = [e for e, r in ket_qua.items() if r["trong_so"] != "best.pt"]
    if thieu:
        print(f"CHÚ Ý: {', '.join(thieu)} được đo với trọng số lúc khởi tạo vì không có best.pt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
