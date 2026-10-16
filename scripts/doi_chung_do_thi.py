"""[CD1.12i / GAP-040] Kiểm định các thí nghiệm đối chứng cho mô hình đồ thị, 5 seed.

Đọc results/<exp>/seed<N>/predictions.jsonl, KHÔNG huấn luyện gì. Trả lời câu hỏi đã chốt với học viên ngày
16/10/2026: phần ĐỒ THỊ có đem lại một hiệu số dương có ý nghĩa không, khi đã tách nó khỏi hai biến lẫn:

    phobert        -> phobert_fp32      : fp16 -> fp32 (cùng mô hình)
    phobert_fp32   -> asgcn_khong_gcn   : cách đọc ra, token <s> -> gộp attention theo khía cạnh (cùng fp32)
    asgcn_khong_gcn -> asgcn            : thêm GCN trên cây phụ thuộc
    asgcn_khong_gcn -> asgcn_linked     : thêm GCN trên cây nối gốc
    asgcn_khong_gcn -> senticgcn        : thêm GCN có trọng số cảm xúc

    python scripts/doi_chung_do_thi.py                 # 10.000 lần lấy mẫu, ghi results/doi_chung_do_thi.json
    python scripts/doi_chung_do_thi.py --chi-in        # chỉ in, không ghi
    python scripts/doi_chung_do_thi.py --so-lan 2000   # chạy nhanh để thử

HAI PHÉP KIỂM ĐỊNH, VÌ HAI NGUỒN BẤT ĐỊNH
---------------------------------------
1. Bootstrap ghép cặp theo bình luận: dùng nguyên `kiem_dinh` của compare_baselines.py (cùng phép với Bảng 4.4).
   Nó coi các bộ trọng số đã huấn luyện là cố định, chỉ đo độ bất định do TẬP KIỂM TRA.
2. Hoán vị trên điểm của từng seed: liệt kê MỌI cách chia lại các lần chạy của hai mô hình thành hai nhóm cùng cỡ
   (5 với 5 là 252 cách, 5 với 3 là 56 cách). Nó đo xem hiệu số trung bình có lớn hơn dao động giữa các lần HUẤN
   LUYỆN không. p nhỏ nhất đạt được là 2/252 (khoảng 0,008) với 5 và 5, và 1/56 (khoảng 0,018) với 5 và 3 (hai
   nhóm khác cỡ thì không có cách chia "đảo" cho cùng hiệu số). Với ít seed như vậy, phép này kém nhạy; đọc nó như
   phép kiểm tra phụ, không như phép chính.

Tiêu chí "đồ thị có ích" (học viên chốt 16/10/2026, phiếu CD1.12j mục 8): một hiệu số DƯƠNG có ý nghĩa ở phép 1
(p < 0,05) giữa một mô hình đồ thị và đối chứng không đồ thị (asgcn_khong_gcn, phobert hoặc phobert_fp32), trên toàn
tập kiểm tra, nhóm bình luận trái cảm xúc, hoặc một nhóm của tập chẩn đoán. Script in thêm cột phép 2 và nhắc rằng số
phép so là nhiều, chưa hiệu chỉnh.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_baselines as cb  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEED_GOC = (42, 1337, 2024)
SEED_MOI = (7, 123)
# Ghi rõ từng thí nghiệm dùng seed nào, không tự quét thư mục: một thư mục seed lạ lọt vào sẽ đổi kết quả
# mà không ai thấy.
SEED_THI_NGHIEM: Dict[str, Tuple[int, ...]] = {
    "phobert": SEED_GOC + SEED_MOI,
    "phobert_fp32": SEED_GOC,
    "asgcn_khong_gcn": SEED_GOC + SEED_MOI,
    "asgcn": SEED_GOC + SEED_MOI,
    "asgcn_linked": SEED_GOC + SEED_MOI,
    "senticgcn": SEED_GOC + SEED_MOI,
}
DO_THI = ("asgcn", "asgcn_linked", "senticgcn")
DOI_CHUNG = ("asgcn_khong_gcn", "phobert", "phobert_fp32")
# (A, B, ý nghĩa của hiệu số A - B)
CAP: Tuple[Tuple[str, str, str], ...] = (
    ("phobert_fp32", "phobert", "tắt fp16"),
    ("asgcn_khong_gcn", "phobert_fp32", "cách đọc ra"),
    ("asgcn", "asgcn_khong_gcn", "GCN, cây phụ thuộc"),
    ("asgcn_linked", "asgcn_khong_gcn", "GCN, cây nối gốc"),
    ("senticgcn", "asgcn_khong_gcn", "GCN, trọng số cảm xúc"),
    ("asgcn", "phobert_fp32", "cả đầu đồ thị, cùng fp32"),
    ("asgcn_linked", "phobert_fp32", "cả đầu đồ thị, cùng fp32"),
    ("senticgcn", "phobert_fp32", "cả đầu đồ thị, cùng fp32"),
    ("asgcn", "phobert", "như Bảng 4.4, 5 seed"),
    ("asgcn_linked", "phobert", "như Bảng 4.4, 5 seed"),
    ("senticgcn", "phobert", "như Bảng 4.4, 5 seed"),
)
TEN = {"phobert": "PhoBERT", "phobert_fp32": "PhoBERT fp32", "asgcn_khong_gcn": "Gộp attention, không GCN",
       "asgcn": "ASGCN", "asgcn_linked": "ASGCN nối gốc", "senticgcn": "Sentic-GCN"}
NHOM = ("toan_bo", "trai_cam_xuc", "co_phu_dinh", "co_chuyen_y", "ca_hai")
TEN_NHOM = {"toan_bo": "Toàn tập kiểm tra", "trai_cam_xuc": "Bình luận trái cảm xúc",
            "co_phu_dinh": "Chẩn đoán: có phủ định", "co_chuyen_y": "Chẩn đoán: có chuyển ý",
            "ca_hai": "Chẩn đoán: cả hai"}


def doc_jsonl(p: Path) -> List[dict]:
    with p.open(encoding="utf-8") as fh:
        return [json.loads(d) for d in fh if d.strip()]


def mat_na_nhom(uid: Sequence[str], vang: np.ndarray, chan_doan: Sequence[dict]) -> Dict[str, np.ndarray]:
    """Mặt nạ (số mẫu,) cho từng nhóm.

    Trái cảm xúc: các khía cạnh của cùng bình luận không cùng một nhãn (giống `loai_cau` = da_trai của
    error_analysis.py). Nhóm chẩn đoán gộp theo DẤU HIỆU như Bảng C.5: có phủ định = negation hoặc both,
    có chuyển ý = contrast hoặc both.
    """
    nhan_cau: Dict[str, set] = {}
    for u, y in zip(uid, vang):
        nhan_cau.setdefault(cb.ma_cau(u), set()).add(int(y))
    hien_tuong = {r["uid"]: r["phenomenon"] for r in chan_doan}
    la = [u for u in hien_tuong if u not in set(uid)]
    if la:
        raise ValueError(f"{len(la)} uid của tập chẩn đoán không có trong tập kiểm tra, ví dụ {la[0]}")
    ht = [hien_tuong.get(u) for u in uid]
    return {
        "toan_bo": np.ones(len(uid), dtype=bool),
        "trai_cam_xuc": np.array([len(nhan_cau[cb.ma_cau(u)]) > 1 for u in uid]),
        "co_phu_dinh": np.array([h in ("negation", "both") for h in ht]),
        "co_chuyen_y": np.array([h in ("contrast", "both") for h in ht]),
        "ca_hai": np.array([h == "both" for h in ht]),
    }


def nap(goc: Path, seed_tn: Dict[str, Tuple[int, ...]]) -> Tuple[List[str], np.ndarray, Dict[str, np.ndarray]]:
    """uid, nhãn thật, {thí nghiệm: dự đoán (seed, mẫu)}. Dừng nếu các file không cùng uid hoặc nhãn thật."""
    chuan_uid, chuan_vang = None, None
    doan: Dict[str, np.ndarray] = {}
    for exp, seeds in seed_tn.items():
        lop = []
        for s in seeds:
            p = goc / exp / f"seed{s}" / "predictions.jsonl"
            u, v, d = cb.doc_du_doan(p)
            if chuan_uid is None:
                chuan_uid, chuan_vang = u, v
            elif u != chuan_uid or not np.array_equal(v, chuan_vang):
                raise ValueError(f"{p} không cùng thứ tự uid hoặc nhãn thật với các file khác")
            lop.append(d)
        doan[exp] = np.stack(lop)
    return chuan_uid, chuan_vang, doan


def o_dem(uid: Sequence[str], vang: np.ndarray, doan: np.ndarray, chon: np.ndarray) -> np.ndarray:
    """(seed, câu, 9) chỉ trên các mẫu được chọn, gộp theo bình luận."""
    u = [x for x, c in zip(uid, chon) if c]
    return np.stack([cb.dem_theo_cau(u, vang[chon], d[chon])[1] for d in doan])


def hoan_vi_seed(a: np.ndarray, b: np.ndarray) -> float:
    """p hai phía của hiệu số trung bình a - b, liệt kê mọi cách chia lại len(a) + len(b) giá trị."""
    gop = np.concatenate([a, b])
    quan_sat = abs(a.mean() - b.mean())
    na, tong = len(a), gop.sum()
    dem = n = 0
    for chon in combinations(range(len(gop)), na):
        sa = gop[list(chon)].sum()
        hieu = sa / na - (tong - sa) / (len(gop) - na)
        dem += abs(hieu) >= quan_sat - 1e-12
        n += 1
    return dem / n


def phan_tich(goc: Path, test_path: Path, chan_doan_path: Path, so_lan: int, seed: int) -> dict:
    uid, vang, doan = nap(goc, SEED_THI_NGHIEM)
    test_uid = [r["uid"] for r in doc_jsonl(test_path)]
    if test_uid != uid:
        raise ValueError(f"thứ tự uid của dự đoán khác {test_path}")
    nhom = mat_na_nhom(uid, vang, doc_jsonl(chan_doan_path))
    rng = np.random.default_rng(seed)

    kq: dict = {"so_lan": so_lan, "seed": seed, "don_vi_lay_mau": "cau",
                "seed_thi_nghiem": {k: list(v) for k, v in SEED_THI_NGHIEM.items()},
                "nhom": {}, "mo_hinh": {}, "cap": []}
    o = {g: {e: o_dem(uid, vang, doan[e], nhom[g]) for e in doan} for g in NHOM}
    for g in NHOM:
        kq["nhom"][g] = {"so_mau": int(nhom[g].sum()), "so_cau": int(o[g]["phobert"].shape[1])}
        kq["mo_hinh"][g] = {}
        for e in doan:
            f, a = cb.do_do(o[g][e].sum(axis=1))
            kq["mo_hinh"][g][e] = {"macro_f1_tung_seed": f.tolist(), "accuracy_tung_seed": a.tolist()}
    for g in NHOM:
        for ma, mb, y in CAP:
            r = {"nhom": g, "a": ma, "b": mb, "y_nghia": y}
            r.update(cb.kiem_dinh(o[g][ma], o[g][mb], so_lan, rng))
            fa = np.array(kq["mo_hinh"][g][ma]["macro_f1_tung_seed"])
            fb = np.array(kq["mo_hinh"][g][mb]["macro_f1_tung_seed"])
            r["macro_f1"]["p_hoan_vi_seed"] = hoan_vi_seed(fa, fb)
            kq["cap"].append(r)
    kq["do_thi_co_ich"] = [
        {k: r[k] for k in ("nhom", "a", "b")} | {"hieu_so": r[do]["hieu_so"], "p": r[do]["p"], "do_do": do}
        for r in kq["cap"] for do in ("macro_f1", "accuracy")
        if r["a"] in DO_THI and r["b"] in DOI_CHUNG and r[do]["hieu_so"] > 0 and r[do]["p"] < 0.05
    ]
    kq["so_phep_so"] = len(kq["cap"]) * 2
    return kq


def _so(x: float) -> str:
    return f"{x * 100:+.2f}".replace(".", ",")


def _p(p: float) -> str:
    return "< 0,001" if p < 0.001 else f"{p:.3f}".replace(".", ",")


def in_ket_qua(kq: dict) -> str:
    dong = []
    for g in NHOM:
        n = kq["nhom"][g]
        dong.append(f"\n## {TEN_NHOM[g]} ({n['so_mau']} mẫu, {n['so_cau']} bình luận)\n")
        dong.append("| Mô hình | Số seed | Macro-F1 trung bình | Độ lệch chuẩn | Accuracy trung bình |")
        dong.append("|---|---|---|---|---|")
        for e, v in kq["mo_hinh"][g].items():
            f, a = np.array(v["macro_f1_tung_seed"]), np.array(v["accuracy_tung_seed"])
            sd = f"{f.std(ddof=1) * 100:.2f}" if len(f) > 1 else ""
            dong.append(f"| {TEN[e]} | {len(f)} | {f.mean() * 100:.2f} | {sd} | {a.mean() * 100:.2f} |")
        dong.append("")
        dong.append("| A | B | Ý nghĩa | Hiệu số macro-F1 | KTC 95 % | p bootstrap | p hoán vị seed | Hiệu số accuracy | p |")
        dong.append("|---|---|---|---|---|---|---|---|---|")
        for r in kq["cap"]:
            if r["nhom"] != g:
                continue
            f, a = r["macro_f1"], r["accuracy"]
            dong.append(f"| {TEN[r['a']]} | {TEN[r['b']]} | {r['y_nghia']} | {_so(f['hieu_so'])} | "
                        f"{_so(f['ci95_duoi'])} đến {_so(f['ci95_tren'])} | {_p(f['p'])} | {_p(f['p_hoan_vi_seed'])} | "
                        f"{_so(a['hieu_so'])} | {_p(a['p'])} |")
    dong.append(f"\n## Tiêu chí đồ thị có ích ({kq['so_phep_so']} phép so, chưa hiệu chỉnh so nhiều lần)\n")
    if kq["do_thi_co_ich"]:
        for r in kq["do_thi_co_ich"]:
            dong.append(f"- ĐẠT: {TEN[r['a']]} hơn {TEN[r['b']]} ở {TEN_NHOM[r['nhom']]}, {r['do_do']} "
                        f"{_so(r['hieu_so'])} điểm, p bootstrap {_p(r['p'])}")
    else:
        dong.append("- KHÔNG ĐẠT ở nhóm nào: không mô hình đồ thị nào hơn một đối chứng không đồ thị có ý nghĩa.")
    return "\n".join(dong) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm định thí nghiệm đối chứng cho mô hình đồ thị (5 seed).")
    ap.add_argument("--results", type=Path, default=Path("results"))
    ap.add_argument("--test", type=Path, default=Path("data/processed/visfd_test.jsonl"))
    ap.add_argument("--chan-doan", type=Path, default=Path("data/diagnostic/diagnostic_300.jsonl"))
    ap.add_argument("--so-lan", type=int, default=10_000, help="số lần lấy mẫu bootstrap (mặc định 10000)")
    ap.add_argument("--seed", type=int, default=20261017, help="seed của bộ sinh số ngẫu nhiên cho bootstrap")
    ap.add_argument("--out-json", type=Path, default=Path("results/doi_chung_do_thi.json"))
    ap.add_argument("--chi-in", action="store_true", help="chỉ in, không ghi file")
    a = ap.parse_args(argv)

    kq = phan_tich(a.results, a.test, a.chan_doan, a.so_lan, a.seed)
    print(in_ket_qua(kq))
    if not a.chi_in:
        a.out_json.write_text(json.dumps(kq, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Đã ghi {a.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
