"""[CD1.9 / CD1.12] Vẽ các hình của báo cáo Chuyên đề 1 từ dữ liệu và file kết quả.

Mọi hình đều vẽ từ số đã đo, không có con số nào gõ tay trong file này:

    Hình 2.1  trọng số tự chú ý của PhoBERT trên một đoạn bình luận  <- chạy PhoBERT-base v2 chưa tinh chỉnh
    Hình 4.1  phân bố nhãn theo khía cạnh trên tập kiểm tra      <- data/processed/visfd_test.jsonl
    Hình 5.1  ma trận nhầm lẫn của sáu mô hình                    <- results/error_analysis.json
    Hình 5.2  accuracy theo độ dài câu                            <- results/error_analysis.json
    Hình 5.3  accuracy theo loại câu                              <- results/error_analysis.json
    Hình 5.4  số mẫu theo số mô hình luôn sai                     <- results/error_analysis.json

    python scripts/make_figures.py                 # vẽ hết vào chuyende1/figures/
    python scripts/make_figures.py --chi 4.1 5.2   # chỉ vẽ vài hình

Chạy scripts/error_analysis.py trước nếu results/error_analysis.json chưa có hoặc đã cũ.
Hình 2.1 cần tải trọng số PhoBERT-base v2 (khoảng 540 MB, một lần); không tải được thì hình này bị bỏ qua.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))

import compare_baselines as cb  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

THU_MUC_MAC_DINH = Path("chuyende1/figures")
NHAN = ("Tiêu cực", "Trung tính", "Tích cực")
MAU_NHAN = ("#b2182b", "#bdbdbd", "#2166ac")
NET_NHAN = ("//", "", "..")  # nét gạch để ba lớp vẫn phân biệt được khi in đen trắng
MAU_MO_HINH = {"lexicon": "#999999", "bilstm": "#e69f00", "phobert": "#0072b2", "asgcn": "#d55e00", "asgcn_linked": "#cc79a7", "senticgcn": "#009e73"}
DAU_MO_HINH = {"lexicon": "x", "bilstm": "s", "phobert": "o", "asgcn": "^", "asgcn_linked": "v", "senticgcn": "D"}
TEN_DO_DAI = {"den_20": "Đến 20 từ", "21_40": "21 đến 40 từ", "41_80": "41 đến 80 từ", "tren_80": "Trên 80 từ"}
TEN_LOAI_CAU = {"da_cung": "Nhiều khía cạnh,\ncùng nhãn", "mot": "Một khía cạnh", "da_trai": "Nhiều khía cạnh,\ntrái nhãn"}

plt.rcParams.update({"font.family": ["Times New Roman", "DejaVu Serif"], "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.dpi": 200, "savefig.bbox": "tight"})


def nghin(n: float) -> str:
    return f"{int(round(n)):,}".replace(",", ".")


CAU_HINH_2_1 = ("pin", "4500", "nhưng", "nhanh", "hết", "quá")  # trích từ bình luận visfd-test-01805
LOP_HINH_2_1 = 1  # lớp thứ nhất: ở các lớp sâu, phần lớn trọng số dồn về hai ký hiệu đầu và cuối chuỗi


def hinh_2_1(out: Path) -> None:
    """Trọng số tự chú ý THẬT của PhoBERT-base v2 chưa tinh chỉnh, trung bình các đầu của một lớp."""
    import torch
    from transformers import AutoModel, AutoTokenizer

    ten = "vinai/phobert-base-v2"
    tok = AutoTokenizer.from_pretrained(ten)
    model = AutoModel.from_pretrained(ten, output_attentions=True, attn_implementation="eager")
    model.eval()
    enc = tok(list(CAU_HINH_2_1), is_split_into_words=True, return_tensors="pt")
    with torch.no_grad():
        chu_y = model(**enc).attentions[LOP_HINH_2_1 - 1][0].mean(dim=0).numpy()  # (n, n), mỗi hàng cộng lại bằng 1
    manh = tok.convert_ids_to_tokens(enc["input_ids"][0])
    fig, ax = plt.subplots(figsize=(5.6, 4.8))
    anh = ax.imshow(chu_y, cmap="Blues", vmin=0, vmax=float(chu_y.max()))
    for i in range(len(manh)):
        for j in range(len(manh)):
            ax.text(j, i, f"{chu_y[i, j]:.2f}".replace(".", ","), ha="center", va="center", fontsize=8,
                    color="white" if chu_y[i, j] > chu_y.max() * 0.6 else "black")
    ax.set_xticks(range(len(manh)), manh, rotation=45, ha="right")
    ax.set_yticks(range(len(manh)), manh)
    ax.set_xlabel("Subword được nhìn tới")
    ax.set_ylabel("Subword đang được biểu diễn")
    ax.spines[:].set_visible(False)
    fig.colorbar(anh, ax=ax, fraction=0.046, pad=0.04, format=matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ",")))
    fig.savefig(out)
    plt.close(fig)


def hinh_4_1(test_path: Path, out: Path) -> None:
    bang: Dict[str, Counter] = defaultdict(Counter)
    with test_path.open(encoding="utf-8") as fh:
        for d in fh:
            r = json.loads(d)
            bang[r["aspect"]][int(r["label"])] += 1
    kc = sorted(bang, key=lambda a: sum(bang[a].values()))
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    trai = np.zeros(len(kc))
    for i, ten in enumerate(NHAN):
        v = np.array([bang[a][i] for a in kc])
        ax.barh(kc, v, left=trai, color=MAU_NHAN[i], hatch=NET_NHAN[i], edgecolor="white", linewidth=0.5, label=ten)
        trai += v
    for y, a in enumerate(kc):
        ax.text(trai[y] + 12, y, nghin(trai[y]), va="center", fontsize=10)
    ax.set_xlabel("Số mẫu trên tập kiểm tra")
    ax.set_xlim(0, trai.max() * 1.1)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: nghin(v)))
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(out)
    plt.close(fig)


def hinh_5_1(kq: dict, out: Path) -> None:
    fig, truc = plt.subplots(2, 3, figsize=(8.4, 5.6))
    for ax, e in zip(truc.flat, kq["mo_hinh"]):
        m = np.array(kq["ma_tran"][e]["ma_tran"])
        ti_le = m / m.sum(axis=1, keepdims=True) * 100
        ax.imshow(ti_le, cmap="Blues", vmin=0, vmax=100)
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{ti_le[i, j]:.1f}".replace(".", ","), ha="center", va="center",
                        color="white" if ti_le[i, j] > 55 else "black", fontsize=10)
        ax.set_xticks(range(3), NHAN, fontsize=9)
        ax.set_yticks(range(3), NHAN, fontsize=9, rotation=90, va="center")
        ax.set_title(cb.TEN_HIEN_THI.get(e, e), fontsize=11)
        ax.spines[:].set_visible(False)
    fig.supxlabel("Nhãn mô hình đoán", fontsize=11)
    fig.supylabel("Nhãn thật", fontsize=11)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def _ve_theo_nhom(kq_nhom: dict, mo_hinh: List[str], nhom: List[str], ten_nhom: Dict[str, str], out: Path, kieu: str) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    x = np.arange(len(nhom))
    rong = 0.8 / len(mo_hinh)
    for k, e in enumerate(mo_hinh):
        gia = np.array([kq_nhom[e][g]["accuracy"]["gia_tri"] for g in nhom]) * 100
        duoi = gia - np.array([kq_nhom[e][g]["accuracy"]["ci95_duoi"] for g in nhom]) * 100
        tren = np.array([kq_nhom[e][g]["accuracy"]["ci95_tren"] for g in nhom]) * 100 - gia
        ten = cb.TEN_HIEN_THI.get(e, e)
        if kieu == "duong":
            ax.errorbar(x + (k - len(mo_hinh) / 2 + 0.5) * 0.06, gia, yerr=[duoi, tren], marker=DAU_MO_HINH[e], color=MAU_MO_HINH[e],
                        capsize=2, linewidth=1.2, markersize=5, label=ten)
        else:
            ax.bar(x + (k - len(mo_hinh) / 2 + 0.5) * rong, gia, rong * 0.92, yerr=[duoi, tren], color=MAU_MO_HINH[e], capsize=1.5,
                   error_kw={"linewidth": 0.8}, label=ten)
    so_mau = [kq_nhom[mo_hinh[0]][g]["n"] for g in nhom]
    ax.set_xticks(x, [f"{ten_nhom[g]}\n(n = {nghin(n)})" for g, n in zip(nhom, so_mau)])
    ax.set_ylabel("Accuracy (%)")
    thap = min(kq_nhom[e][g]["accuracy"]["ci95_duoi"] for e in mo_hinh for g in nhom) * 100
    ax.set_ylim(max(0, np.floor(thap / 10) * 10), 100)
    ax.legend(frameon=False, fontsize=9, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0))  # đặt ngoài vùng vẽ để không đè lên cột
    fig.savefig(out)
    plt.close(fig)


def hinh_5_2(kq: dict, out: Path) -> None:
    _ve_theo_nhom(kq["do_dai"], kq["mo_hinh"], list(TEN_DO_DAI), TEN_DO_DAI, out, "duong")


def hinh_5_3(kq: dict, out: Path) -> None:
    _ve_theo_nhom(kq["loai_cau"], kq["mo_hinh"], list(TEN_LOAI_CAU), TEN_LOAI_CAU, out, "cot")


def hinh_5_4(kq: dict, out: Path) -> None:
    g = kq["giao_loi"]
    so = [str(k) for k in range(1, len(g["mo_hinh_xet"]) + 1)]
    v = [g["theo_so_mo_hinh_luon_sai"][k] for k in so]
    fig, ax = plt.subplots(figsize=(5.6, 3.8))
    cot = ax.bar(so, v, color=["#bdbdbd"] * (len(so) - 1) + ["#b2182b"], width=0.6)
    for c, n in zip(cot, v):
        ax.text(c.get_x() + c.get_width() / 2, n + max(v) * 0.015, nghin(n), ha="center", fontsize=10)
    ax.set_xlabel(f"Số mô hình luôn sai trên mẫu (trong {len(so)} mô hình dùng PhoBERT)")
    ax.set_ylabel("Số mẫu kiểm tra")
    fig.savefig(out)
    plt.close(fig)


HINH = {
    "2.1": ("hinh_2_1_tu_chu_y_phobert.png", "phobert"),
    "4.1": ("hinh_4_1_phan_bo_nhan_theo_khia_canh.png", "du_lieu"),
    "5.1": ("hinh_5_1_ma_tran_nham_lan.png", hinh_5_1),
    "5.2": ("hinh_5_2_accuracy_theo_do_dai.png", hinh_5_2),
    "5.3": ("hinh_5_3_accuracy_theo_loai_cau.png", hinh_5_3),
    "5.4": ("hinh_5_4_so_mo_hinh_luon_sai.png", hinh_5_4),
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Vẽ các hình của báo cáo từ dữ liệu và file kết quả.")
    ap.add_argument("--test", type=Path, default=Path("data/processed/visfd_test.jsonl"))
    ap.add_argument("--loi", type=Path, default=Path("results/error_analysis.json"), help="kết quả của scripts/error_analysis.py")
    ap.add_argument("--out", type=Path, default=THU_MUC_MAC_DINH, help=f"thư mục ghi hình (mặc định {THU_MUC_MAC_DINH})")
    ap.add_argument("--chi", nargs="+", choices=sorted(HINH), help="chỉ vẽ các hình này (mặc định: tất cả)")
    a = ap.parse_args(argv)

    a.out.mkdir(parents=True, exist_ok=True)
    kq = json.loads(a.loi.read_text(encoding="utf-8")) if any(callable(HINH[h][1]) for h in (a.chi or HINH)) else None
    for so in a.chi or sorted(HINH):
        ten, ham = HINH[so]
        if ham == "phobert":
            try:
                hinh_2_1(a.out / ten)
            except Exception as loi:  # noqa: BLE001 - thiếu mạng hoặc thiếu trọng số thì bỏ hình này, các hình khác vẫn vẽ
                print(f"BỎ QUA Hình {so}: không chạy được PhoBERT ({type(loi).__name__}: {loi})")
                continue
        elif ham == "du_lieu":
            hinh_4_1(a.test, a.out / ten)
        else:
            ham(kq, a.out / ten)
        print(f"Hình {so}: {a.out / ten}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
