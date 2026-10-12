"""[CD1.9 / S5.3 + S5.4] Phân tích lỗi của thang baseline trên tập kiểm tra UIT-ViSFD.

Đọc results/<exp>/seed<N>/predictions.jsonl của các lần chạy đã có và data/processed/, KHÔNG
chạy mô hình nào. Năm lát cắt:

    1. Ma trận nhầm lẫn: lỗi dồn vào cặp lớp nào.
    2. Theo khía cạnh: khía cạnh nào khó, có đi cùng tần suất trong tập huấn luyện không.
    3. Theo độ dài câu (số từ sau tách từ).
    4. Theo loại câu: một khía cạnh, nhiều khía cạnh cùng nhãn, nhiều khía cạnh trái nhãn;
       kèm tỉ lệ "sụp nhãn" (câu trái nhãn mà mô hình đoán một nhãn cho mọi khía cạnh).
    5. Giao lỗi: bao nhiêu mẫu mọi mô hình mạnh cùng sai ở cả ba seed, chúng có đặc điểm gì.

Lát cắt theo hiện tượng ngôn ngữ (phủ định, chuyển ý) nằm ở `finalize_diagnostic.py cham`.

    python scripts/error_analysis.py                # ghi results/error_analysis.json và bảng
    python scripts/error_analysis.py --chi-in       # chỉ in
    python scripts/error_analysis.py --ca 10        # ghi thêm 10 ca cùng sai ra file nháp (không đưa lên GitHub)

Mọi độ đo là TRUNG BÌNH BA SEED. Khoảng tin cậy và giá trị p lấy bằng bootstrap theo CÂU, như
compare_baselines.py. "Luôn sai" nghĩa là sai ở cả ba seed.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import compare_baselines as cb  # noqa: E402
import finalize_diagnostic as fd  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MO_HINH = fd.MO_HINH
MANH = ("phobert", "asgcn", "asgcn_linked", "senticgcn")  # bốn mô hình dùng PhoBERT, xét giao lỗi
NHAN = ("tiêu cực", "trung tính", "tích cực")
DO_DAI = (("den_20", "Đến 20 từ", 0, 20), ("21_40", "21 đến 40 từ", 21, 40), ("41_80", "41 đến 80 từ", 41, 80), ("tren_80", "Trên 80 từ", 81, 10**9))
LOAI_CAU = (("da_cung", "Nhiều khía cạnh, cùng nhãn"), ("mot", "Một khía cạnh"), ("da_trai", "Nhiều khía cạnh, trái nhãn"))
CA_MAC_DINH = Path("chuyende1/report/nhap/ca_cung_sai.md")


def nap(goc: Path, test_path: Path, mo_hinh: Sequence[str]):
    """Trả về (bản ghi tập kiểm tra, nhãn thật (N,), {mô hình: dự đoán (seed, N)}). Dừng nếu lệch uid hoặc nhãn."""
    test = [json.loads(d) for d in test_path.open(encoding="utf-8")]
    uid = [r["uid"] for r in test]
    vang = np.asarray([int(r["label"]) for r in test])
    doan: Dict[str, np.ndarray] = {}
    for exp in mo_hinh:
        lop = []
        for s in cb.SEEDS:
            p = goc / exp / f"seed{s}" / "predictions.jsonl"
            u, g, d = cb.doc_du_doan(p)
            if u != uid or not np.array_equal(g, vang):
                raise ValueError(f"{p} không cùng thứ tự uid hoặc nhãn thật với {test_path}")
            lop.append(d)
        doan[exp] = np.stack(lop)
    return test, vang, doan


def chi_so_cau(test: Sequence[dict]):
    cau = sorted({cb.ma_cau(r["uid"]) for r in test})
    vi_tri = {c: i for i, c in enumerate(cau)}
    return cau, np.asarray([vi_tri[cb.ma_cau(r["uid"])] for r in test])


def dem(nhom: np.ndarray, so_nhom: int, cau_idx: np.ndarray, so_cau: int, vang: np.ndarray, doan: np.ndarray) -> np.ndarray:
    """Ô đếm (nhóm, seed, câu, 9). `nhom` là chỉ số nhóm của từng mẫu, âm thì bỏ qua mẫu đó."""
    o = np.zeros((so_nhom, doan.shape[0], so_cau, cb.SO_LOP * cb.SO_LOP))
    chon = nhom >= 0
    for s in range(doan.shape[0]):
        np.add.at(o, (nhom[chon], s, cau_idx[chon], vang[chon] * cb.SO_LOP + doan[s][chon]), 1)
    return o


def loai_cau(cau_idx: np.ndarray, vang: np.ndarray) -> np.ndarray:
    """Chỉ số trong LOAI_CAU cho từng mẫu, theo số khía cạnh và số nhãn khác nhau của câu chứa nó."""
    so_kc = np.bincount(cau_idx)
    so_nhan = np.zeros(len(so_kc), dtype=int)
    for c in range(cb.SO_LOP):
        so_nhan += np.bincount(cau_idx[vang == c], minlength=len(so_kc)) > 0
    return np.where(so_kc[cau_idx] == 1, 1, np.where(so_nhan[cau_idx] > 1, 2, 0))


def lat_ma_tran(vang: np.ndarray, doan: Dict[str, np.ndarray]) -> Dict[str, dict]:
    ra = {}
    for exp, d in doan.items():
        m = np.zeros((cb.SO_LOP, cb.SO_LOP))
        for s in range(d.shape[0]):
            np.add.at(m, (vang, d[s]), 1)
        m /= d.shape[0]
        loi = m.sum() - np.trace(m)
        ra[exp] = {"ma_tran": m.tolist(), "so_loi": float(loi),
                   "ti_le_tim_lai": (np.diag(m) / m.sum(axis=1)).tolist(),
                   "phan_loi_theo_cap": {f"{i}->{j}": float(m[i, j] / loi) if loi else 0.0 for i in range(cb.SO_LOP) for j in range(cb.SO_LOP) if i != j}}
    return ra


def lat_sup_nhan(cau_idx: np.ndarray, vang: np.ndarray, doan: Dict[str, np.ndarray], loai: np.ndarray) -> Dict[str, dict]:
    """Trên các câu trái nhãn: tỉ lệ câu bị đoán một nhãn duy nhất, và lỗi có chạy sang nhãn khác đang có trong câu không."""
    so_cau = cau_idx.max() + 1
    trai = np.zeros(so_cau, dtype=bool)
    trai[cau_idx[loai == 2]] = True
    co_nhan = np.zeros((so_cau, cb.SO_LOP), dtype=bool)
    co_nhan[cau_idx, vang] = True
    hai_nhan = co_nhan.sum(axis=1) == 2
    ra = {}
    for exp, d in doan.items():
        sup, sang, tong = [], [], []
        for s in range(d.shape[0]):
            co_doan = np.zeros((so_cau, cb.SO_LOP), dtype=bool)
            co_doan[cau_idx, d[s]] = True
            sup.append(float((co_doan.sum(axis=1) == 1)[trai].mean()))
            loi = (d[s] != vang) & hai_nhan[cau_idx]  # câu có đúng hai nhãn: lỗi rơi vào nhãn kia hay nhãn thứ ba
            sang.append(int(co_nhan[cau_idx[loi], d[s][loi]].sum()))
            tong.append(int(loi.sum()))
        ra[exp] = {"ti_le_sup_nhan": float(np.mean(sup)), "so_loi_o_cau_hai_nhan": float(np.mean(tong)),
                   "phan_loi_sang_nhan_kia": float(np.sum(sang) / np.sum(tong)) if np.sum(tong) else 0.0}
    return {"so_cau_trai_nhan": int(trai.sum()), "so_cau_dung_hai_nhan": int(hai_nhan.sum()), "mo_hinh": ra}


def lat_giao_loi(test: Sequence[dict], vang: np.ndarray, doan: Dict[str, np.ndarray], loai: np.ndarray, manh: Sequence[str]) -> dict:
    luon_sai = {exp: (d != vang).all(axis=0) for exp, d in doan.items()}
    co_sai = {exp: (d != vang).any(axis=0) for exp, d in doan.items()}
    so_mh = np.sum([luon_sai[e] for e in manh], axis=0)
    cung = so_mh == len(manh)
    kc = np.asarray([r["aspect"] for r in test])
    tat_ca_doan = np.concatenate([doan[e] for e in manh])  # (4 mô hình x 3 seed, N)
    nhan_doan = np.asarray([Counter(c).most_common(1)[0][0] for c in tat_ca_doan[:, cung].T], dtype=int)
    cap = Counter(zip(vang[cung].tolist(), nhan_doan.tolist()))
    return {
        "mo_hinh_xet": list(manh), "so_mau": int(len(vang)),
        "luon_sai": {e: int(v.sum()) for e, v in luon_sai.items()},
        "sai_it_nhat_mot_seed": {e: int(v.sum()) for e, v in co_sai.items()},
        "theo_so_mo_hinh_luon_sai": {str(k): int((so_mh == k).sum()) for k in range(len(manh) + 1)},
        "cung_sai": int(cung.sum()),
        "khong_lan_chay_nao_sai": int((~np.any([co_sai[e] for e in manh], axis=0)).sum()),
        "cung_sai_theo_nhan": {NHAN[c]: int((vang[cung] == c).sum()) for c in range(cb.SO_LOP)},
        "tat_ca_theo_nhan": {NHAN[c]: int((vang == c).sum()) for c in range(cb.SO_LOP)},
        "cung_sai_theo_khia_canh": dict(Counter(kc[cung].tolist()).most_common()),
        "tat_ca_theo_khia_canh": dict(Counter(kc.tolist()).most_common()),
        "cung_sai_o_cau_trai_nhan": int((loai[cung] == 2).sum()), "tat_ca_o_cau_trai_nhan": int((loai == 2).sum()),
        "cung_sai_nhan_that_sang_nhan_doan": {f"{NHAN[g]} -> {NHAN[d]}": n for (g, d), n in cap.most_common()},
        "chi_so_cung_sai": np.flatnonzero(cung).tolist(),
    }


def pt(x: float, chu_so: int = 1) -> str:
    return f"{x * 100:.{chu_so}f}".replace(".", ",")


def bang_tat_ca(kq: dict, so_lan: int) -> str:
    ten = lambda e: cb.TEN_HIEN_THI.get(e, e)  # noqa: E731
    nghin = lambda n: f"{n:,}".replace(",", ".")  # noqa: E731
    cau = kq["so_cau"]
    chu = (f"Mỗi ô: trung bình ba seed (%), khoảng tin cậy 95 % trong ngoặc vuông; nhóm khác nhóm đầu có thêm hiệu so với nhóm đầu "
           f"(điểm phần trăm) và p hai phía. Bootstrap {nghin(so_lan)} lần theo câu ({nghin(cau)} câu).")
    k = []

    k.append("Bảng A. Lỗi theo cặp lớp, trung bình ba seed. Sáu cột giữa là phần trăm trên tổng số lỗi của mô hình; "
             "ba cột cuối là tỉ lệ tìm lại của từng lớp (%).\n")
    cap = [(i, j) for i in range(3) for j in range(3) if i != j]
    k.append("| Mô hình | Số lỗi | " + " | ".join(f"{NHAN[i]} thành {NHAN[j]}" for i, j in cap) + " | " + " | ".join(f"Tìm lại {x}" for x in NHAN) + " |")
    k.append("|---|---|" + "---|" * 9)
    for e, r in kq["ma_tran"].items():
        k.append(f"| {ten(e)} | {pt(r['so_loi'] / 100, 0)} | " + " | ".join(pt(r["phan_loi_theo_cap"][f"{i}->{j}"]) for i, j in cap)
                 + " | " + " | ".join(pt(x) for x in r["ti_le_tim_lai"]) + " |")

    kc = kq["khia_canh"]
    k.append("\nBảng B. Macro-F1 theo khía cạnh (%), trung bình ba seed, xếp theo số mẫu huấn luyện giảm dần.\n")
    k.append("| Khía cạnh | Mẫu huấn luyện | Mẫu kiểm tra | Trung tính trong kiểm tra (%) | " + " | ".join(ten(e) for e in kq["mo_hinh"]) + " |")
    k.append("|---|---|---|---|" + "---|" * len(kq["mo_hinh"]))
    for a in kc["thu_tu"]:
        k.append(f"| {a} | {nghin(kc['so_huan_luyen'][a])} | {nghin(kc['so_kiem_tra'][a])} | {pt(kc['ti_le_trung_tinh'][a])} | "
                 + " | ".join(pt(kc["ket_qua"][e][a]["macro_f1"]["gia_tri"]) for e in kq["mo_hinh"]) + " |")
    k.append("\nTương quan hạng Spearman giữa số mẫu huấn luyện của khía cạnh và macro-F1 trên khía cạnh đó (10 khía cạnh): "
             + "; ".join(f"{ten(e)} rho = {v['rho']:.2f}".replace(".", ",") + f", p = {v['p']:.3f}".replace(".", ",") for e, v in kc["spearman"].items()) + ".")

    k.append("\n" + fd.bang_cham(kq["do_dai"], "accuracy", "Bảng C. Accuracy theo độ dài câu. " + chu, [x[0] for x in DO_DAI], {x[0]: x[1] for x in DO_DAI}))
    k.append(fd.bang_cham(kq["loai_cau"], "accuracy", "Bảng D. Accuracy theo loại câu. " + chu, [x[0] for x in LOAI_CAU], dict(LOAI_CAU)))
    # Không in macro-F1 theo loại câu: câu cùng nhãn gần như không có mẫu trung tính, nên macro-F1 giữa ba loại câu
    # không so được với nhau. Số vẫn có trong file .json.

    sn = kq["sup_nhan"]
    k.append(f"Bảng E. Câu trái nhãn ({nghin(sn['so_cau_trai_nhan'])} câu). Sụp nhãn: câu bị đoán cùng một nhãn cho mọi khía cạnh. "
             f"Hai cột cuối chỉ tính trên {nghin(sn['so_cau_dung_hai_nhan'])} câu có đúng hai nhãn khác nhau: trong các lỗi ở đó, "
             "bao nhiêu phần trăm rơi vào nhãn còn lại đang có trong câu chứ không phải nhãn thứ ba.\n")
    k.append("| Mô hình | Câu sụp nhãn (%) | Số lỗi ở câu hai nhãn | Lỗi rơi vào nhãn kia của câu (%) |")
    k.append("|---|---|---|---|")
    for e, r in sn["mo_hinh"].items():
        k.append(f"| {ten(e)} | {pt(r['ti_le_sup_nhan'])} | {pt(r['so_loi_o_cau_hai_nhan'] / 100, 0)} | {pt(r['phan_loi_sang_nhan_kia'])} |")

    g = kq["giao_loi"]
    n = g["so_mau"]
    k.append(f"\nBảng F. Số mẫu sai trên {nghin(n)} mẫu kiểm tra. Luôn sai: sai ở cả ba seed.\n")
    k.append("| Mô hình | Luôn sai | Sai ở ít nhất một seed |")
    k.append("|---|---|---|")
    for e in g["luon_sai"]:
        k.append(f"| {ten(e)} | {nghin(g['luon_sai'][e])} ({pt(g['luon_sai'][e] / n)} %) | {nghin(g['sai_it_nhat_mot_seed'][e])} ({pt(g['sai_it_nhat_mot_seed'][e] / n)} %) |")
    bon = ", ".join(ten(e) for e in g["mo_hinh_xet"])
    c = g["cung_sai"]
    k.append(f"\nBảng G. Giao lỗi của bốn mô hình dùng PhoBERT ({bon}).\n")
    k.append("| Số mô hình luôn sai trên mẫu | " + " | ".join(g["theo_so_mo_hinh_luon_sai"]) + " |")
    k.append("|---|" + "---|" * len(g["theo_so_mo_hinh_luon_sai"]))
    k.append("| Số mẫu | " + " | ".join(nghin(v) for v in g["theo_so_mo_hinh_luon_sai"].values()) + " |")
    k.append(f"\nCả bốn mô hình luôn sai trên {nghin(c)} mẫu ({pt(c / n)} % tập kiểm tra). "
             f"Không lần chạy nào trong 12 lần sai trên {nghin(g['khong_lan_chay_nao_sai'])} mẫu ({pt(g['khong_lan_chay_nao_sai'] / n)} %).")
    k.append(f"\nBảng H. Đặc điểm của {nghin(c)} mẫu cả bốn mô hình luôn sai, so với toàn tập kiểm tra.\n")
    k.append("| Đặc điểm | Trong nhóm cùng sai | Tỉ lệ trong nhóm (%) | Tỉ lệ trong toàn tập (%) |")
    k.append("|---|---|---|---|")
    for x in NHAN:
        k.append(f"| Nhãn thật {x} | {g['cung_sai_theo_nhan'][x]} | {pt(g['cung_sai_theo_nhan'][x] / c)} | {pt(g['tat_ca_theo_nhan'][x] / n)} |")
    k.append(f"| Thuộc câu trái nhãn | {g['cung_sai_o_cau_trai_nhan']} | {pt(g['cung_sai_o_cau_trai_nhan'] / c)} | {pt(g['tat_ca_o_cau_trai_nhan'] / n)} |")
    for a, v in g["tat_ca_theo_khia_canh"].items():
        m = g["cung_sai_theo_khia_canh"].get(a, 0)
        k.append(f"| Khía cạnh {a} | {m} | {pt(m / c)} | {pt(v / n)} |")
    k.append(f"\nBảng I. Trong {nghin(c)} mẫu đó, nhãn thật bị đoán thành nhãn nào (nhãn được đoán nhiều nhất trong 12 lần chạy).\n")
    k.append("| Nhãn thật thành nhãn đoán | Số mẫu | Tỉ lệ (%) |")
    k.append("|---|---|---|")
    for cp, v in g["cung_sai_nhan_that_sang_nhan_doan"].items():
        k.append(f"| {cp.replace(' -> ', ' thành ')} | {v} | {pt(v / c)} |")
    return "\n".join(k) + "\n"


def ghi_ca(test: Sequence[dict], doan: Dict[str, np.ndarray], chi_so: Sequence[int], so_ca: int, seed: int, out: Path) -> None:
    chon = sorted(random.Random(seed).sample(list(chi_so), min(so_ca, len(chi_so))))
    dong = [f"# {len(chon)} ca rút ngẫu nhiên (seed {seed}) từ {len(chi_so)} mẫu cả bốn mô hình dùng PhoBERT luôn sai", "",
            "File nháp, chứa câu của UIT-ViSFD: không đưa lên GitHub.", ""]
    for i in chon:
        r = test[i]
        dong += [f"## {r['uid']}", "", f"- Câu: {r.get('text') or ' '.join(r['tokens'])}", f"- Khía cạnh: {r['aspect']}",
                 f"- Nhãn thật: {NHAN[int(r['label'])]}",
                 "- Dự đoán ba seed: " + "; ".join(f"{cb.TEN_HIEN_THI.get(e, e)}: " + ", ".join(NHAN[int(x)] for x in doan[e][:, i]) for e in MANH), ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(dong), encoding="utf-8")


def phan_tich(goc: Path, test_path: Path, train_path: Path, so_lan: int, seed: int):
    from scipy.stats import spearmanr

    test, vang, doan = nap(goc, test_path, MO_HINH)
    cau, cau_idx = chi_so_cau(test)
    rng = np.random.default_rng(seed)
    kq: dict = {"so_lan": so_lan, "seed": seed, "seeds_mo_hinh": list(cb.SEEDS), "don_vi_lay_mau": "cau", "so_cau": len(cau),
                "so_mau": len(test), "mo_hinh": list(MO_HINH)}
    kq["ma_tran"] = lat_ma_tran(vang, doan)

    kc_test = np.asarray([r["aspect"] for r in test])
    dem_train = Counter(json.loads(d)["aspect"] for d in train_path.open(encoding="utf-8"))
    thu_tu = sorted(set(kc_test.tolist()), key=lambda a: -dem_train[a])
    nhom_kc = np.asarray([thu_tu.index(a) for a in kc_test])
    kq["khia_canh"] = {"thu_tu": thu_tu, "so_huan_luyen": {a: dem_train[a] for a in thu_tu},
                       "so_kiem_tra": {a: int((kc_test == a).sum()) for a in thu_tu},
                       "ti_le_trung_tinh": {a: float((vang[kc_test == a] == 1).mean()) for a in thu_tu}, "ket_qua": {}, "spearman": {}}
    do_dai = np.asarray([len(r["tokens"]) for r in test])
    nhom_dd = np.asarray([next(i for i, x in enumerate(DO_DAI) if x[2] <= n <= x[3]) for n in do_dai])
    loai = loai_cau(cau_idx, vang)
    kq["do_dai"], kq["loai_cau"] = {}, {}
    for exp in MO_HINH:
        r = fd.cham_mot_mo_hinh(dem(nhom_kc, len(thu_tu), cau_idx, len(cau), vang, doan[exp]), so_lan, rng, ten_nhom=thu_tu)
        for a in thu_tu:  # so với khía cạnh đứng đầu không có nghĩa, bỏ
            for k in ("macro_f1", "accuracy"):
                r[a][k] = {x: r[a][k][x] for x in ("gia_tri", "ci95_duoi", "ci95_tren")}
        kq["khia_canh"]["ket_qua"][exp] = r
        f1 = [r[a]["macro_f1"]["gia_tri"] for a in thu_tu]
        rho, p = spearmanr([dem_train[a] for a in thu_tu], f1) if len(set(f1)) > 1 else (0.0, 1.0)  # dãy hằng: không xác định
        kq["khia_canh"]["spearman"][exp] = {"rho": float(rho), "p": float(p)}
        kq["do_dai"][exp] = fd.cham_mot_mo_hinh(dem(nhom_dd, len(DO_DAI), cau_idx, len(cau), vang, doan[exp]), so_lan, rng, ten_nhom=[x[0] for x in DO_DAI])
        kq["loai_cau"][exp] = fd.cham_mot_mo_hinh(dem(loai, len(LOAI_CAU), cau_idx, len(cau), vang, doan[exp]), so_lan, rng, ten_nhom=[x[0] for x in LOAI_CAU])
    kq["sup_nhan"] = lat_sup_nhan(cau_idx, vang, doan, loai)
    kq["giao_loi"] = lat_giao_loi(test, vang, doan, loai, MANH)
    return kq, test, doan


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Phân tích lỗi của các mô hình baseline theo năm lát cắt.")
    ap.add_argument("--results", type=Path, default=Path("results"))
    ap.add_argument("--test", type=Path, default=Path("data/processed/visfd_test.jsonl"))
    ap.add_argument("--train", type=Path, default=Path("data/processed/visfd_train.jsonl"))
    ap.add_argument("--so-lan", type=int, default=10_000, help="số lần lấy mẫu bootstrap (mặc định 10000)")
    ap.add_argument("--seed", type=int, default=20261014, help="hạt giống của bộ sinh số ngẫu nhiên")
    ap.add_argument("--out-json", type=Path, default=Path("results/error_analysis.json"))
    ap.add_argument("--out-md", type=Path, default=Path("chuyende1/tables/bang_5_phan_tich_loi.md"))
    ap.add_argument("--chi-in", action="store_true", help="chỉ in bảng, không ghi file")
    ap.add_argument("--ca", type=int, default=0, help="số ca cùng sai rút ra file nháp để đọc tay (mặc định 0: không ghi)")
    ap.add_argument("--out-ca", type=Path, default=CA_MAC_DINH, help="file nháp chứa các ca; có câu của bộ dữ liệu, không đưa lên GitHub")
    a = ap.parse_args(argv)

    kq, test, doan = phan_tich(a.results, a.test, a.train, a.so_lan, a.seed)
    bang = bang_tat_ca(kq, a.so_lan)
    print(bang)
    if a.ca:
        ghi_ca(test, doan, kq["giao_loi"]["chi_so_cung_sai"], a.ca, a.seed, a.out_ca)
        print(f"Đã ghi {a.out_ca}")
    if not a.chi_in:
        kq["giao_loi"]["uid_cung_sai"] = [test[i]["uid"] for i in kq["giao_loi"].pop("chi_so_cung_sai")]
        a.out_json.write_text(json.dumps(kq, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        a.out_md.write_text(bang, encoding="utf-8")
        print(f"Đã ghi {a.out_json} và {a.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
