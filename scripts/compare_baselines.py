"""[CD1.10] Kiểm định bootstrap ghép cặp cho các cặp mô hình của thang baseline.

Đọc results/<exp>/seed<N>/predictions.jsonl của các thí nghiệm đã chạy, KHÔNG huấn luyện
lại gì. Với mỗi cặp mô hình (A, B) trả lời: hiệu số macro-F1 (và accuracy) giữa A và B
có đứng vững khi tập kiểm tra đổi đi không.

    python scripts/compare_baselines.py                    # 10.000 lần lấy mẫu, ghi file
    python scripts/compare_baselines.py --chi-in           # chỉ in bảng, không ghi
    python scripts/compare_baselines.py --so-lan 2000      # chạy nhanh để thử

CÁCH LÀM, VÀ HAI CHỖ PHẢI NÓI RÕ KHI ĐƯA VÀO BÁO CÁO
---------------------------------------------------
1. Đơn vị lấy mẫu là CÂU (bình luận), không phải mẫu. Một câu sinh ra trung bình ba mẫu
   (ba khía cạnh) có chung văn bản nên không độc lập với nhau; lấy mẫu theo mẫu sẽ cho
   khoảng tin cậy hẹp giả tạo. Mỗi lần lấy mẫu rút có hoàn lại đủ số câu của tập kiểm
   tra, mọi mẫu của câu được rút đi theo câu.
2. Mỗi mô hình có ba lần chạy (ba seed). Thống kê được kiểm định là TRUNG BÌNH BA SEED
   của độ đo, tính trên cùng một tập câu được rút. Vì vậy kiểm định này chỉ trả lời về
   độ bất định do TẬP KIỂM TRA; nó coi ba bộ trọng số đã huấn luyện là cố định và không
   tính tới việc huấn luyện lại với seed khác sẽ ra mô hình khác. Độ dao động giữa các
   seed xem ở cột độ lệch chuẩn của bảng kết quả chính.

p hai phía = 2 x min(tỉ lệ lần hiệu số <= 0, tỉ lệ lần hiệu số >= 0), có cộng một để
không bao giờ bằng không. Hiệu số "có ý nghĩa ở mức 0,05" khi p < 0,05, tương đương
khoảng tin cậy 95 % không chứa số 0.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEEDS = (42, 1337, 2024)
SO_LOP = 3
# (A, B): kiểm định hiệu số A − B. Nửa đầu là các bậc liền nhau của thang, nửa sau là
# so với mốc chính `phobert`.
CAP_MAC_DINH: Tuple[Tuple[str, str], ...] = (
    ("bilstm", "lexicon"),
    ("phobert", "bilstm"),
    ("asgcn", "phobert"),
    ("asgcn_linked", "asgcn"),
    ("senticgcn", "asgcn"),
    ("asgcn_linked", "phobert"),
    ("senticgcn", "phobert"),
)
TEN_HIEN_THI = {"lexicon": "Từ điển cảm xúc", "bilstm": "BiLSTM với attention", "phobert": "PhoBERT tinh chỉnh",
                "asgcn": "ASGCN", "asgcn_linked": "ASGCN nối gốc", "senticgcn": "Sentic-GCN"}


def ma_cau(uid: str) -> str:
    return uid.rsplit("-", 1)[0]


def doc_du_doan(duong_dan: Path) -> Tuple[List[str], np.ndarray, np.ndarray]:
    uid, vang, doan = [], [], []
    with duong_dan.open(encoding="utf-8") as fh:
        for dong in fh:
            r = json.loads(dong)
            uid.append(r["uid"])
            vang.append(int(r["y_true"]))
            doan.append(int(r["y_pred"]))
    return uid, np.asarray(vang), np.asarray(doan)


def dem_theo_cau(uid: Sequence[str], vang: np.ndarray, doan: np.ndarray) -> Tuple[List[str], np.ndarray]:
    """Ma trận (số câu, 9): số mẫu của từng câu rơi vào từng ô (nhãn thật, nhãn đoán)."""
    cau = sorted({ma_cau(u) for u in uid})
    vi_tri = {c: i for i, c in enumerate(cau)}
    dem = np.zeros((len(cau), SO_LOP * SO_LOP), dtype=np.float64)
    for u, g, d in zip(uid, vang, doan):
        dem[vi_tri[ma_cau(u)], g * SO_LOP + d] += 1
    return cau, dem


def do_do(o: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Từ ô đếm (..., 9) ra (macro-F1, accuracy). Lớp không có mẫu nào và không được đoán: F1 = 0."""
    m = o.reshape(o.shape[:-1] + (SO_LOP, SO_LOP))
    tp = np.einsum("...ii->...i", m)
    that = m.sum(axis=-1)
    doan = m.sum(axis=-2)
    mau = that + doan
    f1 = np.divide(2 * tp, mau, out=np.zeros_like(tp), where=mau > 0)
    return f1.mean(axis=-1), tp.sum(axis=-1) / m.sum(axis=(-1, -2))


def nap(goc: Path, thi_nghiem: Sequence[str]) -> Tuple[List[str], Dict[str, np.ndarray]]:
    """{thí nghiệm: mảng (3 seed, số câu, 9)}. Dừng nếu các file không cùng tập uid và nhãn thật."""
    chuan_uid, chuan_vang, cau = None, None, None
    ra: Dict[str, np.ndarray] = {}
    for exp in thi_nghiem:
        lop = []
        for s in SEEDS:
            p = goc / exp / f"seed{s}" / "predictions.jsonl"
            uid, vang, doan = doc_du_doan(p)
            if chuan_uid is None:
                chuan_uid, chuan_vang = uid, vang
            elif uid != chuan_uid or not np.array_equal(vang, chuan_vang):
                raise ValueError(f"{p} không cùng thứ tự uid hoặc nhãn thật với các file khác")
            cau, dem = dem_theo_cau(uid, vang, doan)
            lop.append(dem)
        ra[exp] = np.stack(lop)
    return cau, ra


def kiem_dinh(a: np.ndarray, b: np.ndarray, so_lan: int, rng: np.random.Generator, khoi: int = 500) -> Dict[str, Dict[str, float]]:
    """a, b: (seed, câu, 9). Trả về hiệu số quan sát, khoảng tin cậy 95 % và p cho macro-F1 và accuracy."""
    so_cau = a.shape[1]
    f_a, acc_a = do_do(a.sum(axis=1))  # mỗi cái là mảng (seed,)
    f_b, acc_b = do_do(b.sum(axis=1))
    quan_sat = {"macro_f1": float(f_a.mean() - f_b.mean()), "accuracy": float(acc_a.mean() - acc_b.mean())}
    hieu = {"macro_f1": [], "accuracy": []}
    con = so_lan
    while con > 0:
        n = min(khoi, con)
        w = rng.multinomial(so_cau, np.full(so_cau, 1.0 / so_cau), size=n).astype(np.float64)  # (n, cau)
        oa = np.einsum("nc,sck->nsk", w, a)
        ob = np.einsum("nc,sck->nsk", w, b)
        fa, aa = do_do(oa)
        fb, ab = do_do(ob)
        hieu["macro_f1"].append(fa.mean(axis=1) - fb.mean(axis=1))
        hieu["accuracy"].append(aa.mean(axis=1) - ab.mean(axis=1))
        con -= n
    ra = {}
    for k, v in hieu.items():
        d = np.concatenate(v)
        p = 2 * min((np.sum(d <= 0) + 1) / (len(d) + 1), (np.sum(d >= 0) + 1) / (len(d) + 1))
        ra[k] = {"hieu_so": quan_sat[k], "ci95_duoi": float(np.percentile(d, 2.5)),
                 "ci95_tren": float(np.percentile(d, 97.5)), "p": float(min(1.0, p))}
    return ra


def so(x: float, chu_so: int = 2) -> str:
    return f"{x * 100:+.{chu_so}f}".replace(".", ",")


def p_chu(p: float) -> str:
    return "< 0,001" if p < 0.001 else f"{p:.3f}".replace(".", ",")


def bang_markdown(kq: List[dict], so_lan: int, so_cau: int) -> str:
    nghin = lambda n: f"{n:,}".replace(",", ".")  # noqa: E731
    dong = [f"Kiểm định bootstrap ghép cặp: {nghin(so_lan)} lần lấy mẫu theo câu ({nghin(so_cau)} câu), "
            "trên trung bình ba seed. Hiệu số tính bằng điểm phần trăm, A trừ B.",
            "",
            "| A | B | Hiệu số macro-F1 | Khoảng tin cậy 95 % | p | Hiệu số accuracy | Khoảng tin cậy 95 % | p |",
            "|---|---|---|---|---|---|---|---|"]
    for r in kq:
        f, a = r["macro_f1"], r["accuracy"]
        dong.append(f"| {TEN_HIEN_THI.get(r['a'], r['a'])} | {TEN_HIEN_THI.get(r['b'], r['b'])} | {so(f['hieu_so'])} | "
                    f"{so(f['ci95_duoi'])} đến {so(f['ci95_tren'])} | {p_chu(f['p'])} | {so(a['hieu_so'])} | "
                    f"{so(a['ci95_duoi'])} đến {so(a['ci95_tren'])} | {p_chu(a['p'])} |")
    return "\n".join(dong) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm định bootstrap ghép cặp giữa các mô hình baseline.")
    ap.add_argument("--results", type=Path, default=Path("results"))
    ap.add_argument("--so-lan", type=int, default=10_000, help="số lần lấy mẫu (mặc định 10000)")
    ap.add_argument("--seed", type=int, default=20261011, help="hạt giống của bộ sinh số ngẫu nhiên")
    ap.add_argument("--out-json", type=Path, default=Path("results/compare_baselines.json"))
    ap.add_argument("--out-md", type=Path, default=Path("chuyende1/tables/bang_4_kiem_dinh.md"))
    ap.add_argument("--chi-in", action="store_true", help="chỉ in bảng, không ghi file")
    a = ap.parse_args(argv)

    thi_nghiem = sorted({x for cap in CAP_MAC_DINH for x in cap})
    cau, du_lieu = nap(a.results, thi_nghiem)
    rng = np.random.default_rng(a.seed)
    kq = []
    for ma, mb in CAP_MAC_DINH:
        r = {"a": ma, "b": mb}
        r.update(kiem_dinh(du_lieu[ma], du_lieu[mb], a.so_lan, rng))
        kq.append(r)
    bang = bang_markdown(kq, a.so_lan, len(cau))
    print(bang)
    if not a.chi_in:
        a.out_json.write_text(json.dumps({"so_lan": a.so_lan, "seed": a.seed, "so_cau": len(cau), "seeds_mo_hinh": list(SEEDS),
                                          "don_vi_lay_mau": "cau", "ket_qua": kq}, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
        a.out_md.write_text(bang, encoding="utf-8")
        print(f"Đã ghi {a.out_json} và {a.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
