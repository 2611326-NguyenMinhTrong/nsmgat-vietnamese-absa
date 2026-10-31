"""[CD1.12r] Các phép đo bổ sung cho Chương 5, trả lời câu hỏi của giảng viên hướng dẫn ngày 31/10/2026.

Lệnh KHÔNG huấn luyện, KHÔNG chạy mô hình: chỉ đọc dự đoán đã công bố trong results/<exp>/seed<N>/predictions.jsonl, tập kiểm
tra và tập chẩn đoán. Tách riêng khỏi doi_chung_do_thi.py và error_analysis.py vì thêm nhóm vào các công cụ đó sẽ đổi dãy số
ngẫu nhiên của bootstrap, làm các giá trị p đã in ở Chương 4 xê dịch.

Ba phần:

1. Loại lỗi của PhoBERT trên từng nhóm hiện tượng (mục 5.2): số lỗi theo cặp nhãn thật, nhãn đoán, và tỉ lệ sai theo từng nhãn
   thật. Tính cả trên phần mẫu người chú thích đồng ý với nhãn gốc, vì hơn một nửa số lỗi nằm ở những mẫu còn lại.

2. Phần lỗi do hai hiện tượng chiếm và mức tăng tối đa (mục 5.6.2): ước lượng theo ô (nhóm từ khoá, nhãn gốc) như phép P2 của
   probe_oracle_rules.py, vì tập chẩn đoán rút cân bằng nhãn và không đại diện cho tập kiểm tra. Quần thể là các mẫu thuộc bình
   luận 5 đến 40 từ và không chỉ chứa từ đa nghĩa; các mẫu còn lại không ước lượng được và được giữ nguyên, nên mức tăng tính
   ra không gồm phần lỗi ở đó. Mức tăng: giả sử một cơ chế sửa đúng mọi lỗi (hoặc một phần lỗi) ở các mẫu có hiện tượng, tính lại
   macro-F1 trên toàn tập kiểm tra từ ma trận nhầm lẫn trung bình năm seed.

3. Vì sao mô hình đồ thị không giúp (mục 5.4): tỉ lệ dự đoán khác nhau giữa các seed và giữa các mô hình; số mẫu mô hình đồ thị
   đúng ở cả năm seed mà đối chứng sai ở cả năm seed; hiệu số giữa mô hình đồ thị và đối chứng trong các nhóm con, gồm phép kiểm
   giả thuyết "chất lượng cây cú pháp kém là nguyên nhân" trên bình luận có và không có dạng viết tắt của từ phủ định. Các
   nhóm con được đặt trước khi xem kết quả, nhưng số phép so nhiều và chưa hiệu chỉnh, nên chỉ đọc như dấu hiệu.

    python scripts/phan_tich_bo_sung.py            # in tóm tắt, ghi results/phan_tich_bo_sung.json
    python scripts/phan_tich_bo_sung.py --chi-in   # chỉ in, không ghi file
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import build_diagnostic_candidates as bd  # noqa: E402
import compare_baselines as cb  # noqa: E402
import doi_chung_do_thi as dct  # noqa: E402
import probe_oracle_rules as po  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

Dong = Dict[str, object]
TEP_KET_QUA = Path("results/phan_tich_bo_sung.json")
NHOM = ("regular", "negation", "contrast", "both")
# Tên nhóm khi ước lượng trên quần thể, và các nhãn hiện tượng thuộc nhóm đó.
NHOM_UOC_LUONG = {"co_hien_tuong": ("negation", "contrast", "both"), "phu_dinh": ("negation", "both"), "chuyen_y": ("contrast", "both"),
                  "ca_hai": ("both",), "thuong": ("regular",)}
DO_THI = ("asgcn", "asgcn_linked", "senticgcn")
MO_HINH_SO = ("phobert", "asgcn_khong_gcn") + DO_THI  # các mô hình đủ năm seed
CAP_DO_THI = (("asgcn", "asgcn_khong_gcn"), ("asgcn_linked", "asgcn_khong_gcn"), ("senticgcn", "asgcn_khong_gcn"),
              ("asgcn", "phobert"), ("senticgcn", "phobert"))
NHOM_CON = ("toan_bo", "trai_nhan", "khong_trai_nhan", "co_viet_tat", "khong_viet_tat", "chi_phu_dinh_chuan")


# --- 1. Loại lỗi theo nhóm hiện tượng -------------------------------------------------------------------------------


def loai_loi(dong: Sequence[Dong], vi_tri: Dict[str, int], du_doan: po.DuDoan) -> Dict[str, object]:
    """Lỗi trung bình mỗi seed của một tập dòng: theo cặp "thật->đoán", và tỉ lệ sai của từng nhãn thật."""
    chi_so = np.array([vi_tri[str(r["uid"])] for r in dong], dtype=int)
    cap: Counter = Counter()
    for vang, doan in du_doan:
        for a, b in zip(vang[chi_so], doan[chi_so]):
            if a != b:
                cap[f"{int(a)}->{int(b)}"] += 1
    so_seed = len(du_doan)
    nhan = np.array([int(r["label"]) for r in dong], dtype=int)  # type: ignore[arg-type]
    so_theo_nhan = [int((nhan == y).sum()) for y in range(cb.SO_LOP)]
    sai = [sum(v for k, v in cap.items() if k.startswith(f"{y}->")) / so_seed for y in range(cb.SO_LOP)]
    return {"n": len(dong), "n_theo_nhan": so_theo_nhan, "loi": sum(cap.values()) / so_seed,
            "cap": {k: v / so_seed for k, v in sorted(cap.items())},
            "ti_le_sai_theo_nhan": [s / n if n else None for s, n in zip(sai, so_theo_nhan)]}


def bang_loai_loi(chan_doan: Sequence[Dong], vi_tri: Dict[str, int], du_doan: po.DuDoan) -> Dict[str, Dict[str, object]]:
    ra: Dict[str, Dict[str, object]] = {"tat_ca": {}, "dong_y": {}}
    for g in NHOM:
        dong = [r for r in chan_doan if r["phenomenon"] == g]
        ra["tat_ca"][g] = loai_loi(dong, vi_tri, du_doan)
        ra["dong_y"][g] = loai_loi([r for r in dong if r["nhan_kiem_tra"] == "dong_y"], vi_tri, du_doan)
    return ra


# --- 2. Phần lỗi do hiện tượng chiếm và mức tăng tối đa --------------------------------------------------------------


def macro_f1_tu_ma_tran(m: np.ndarray) -> float:
    """Macro-F1 từ ma trận nhầm lẫn (có thể là ma trận trung bình, không nguyên)."""
    tp = np.diag(m)
    tu, mau = 2 * tp, m.sum(axis=0) + m.sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        f = np.where(mau > 0, tu / mau, 0.0)
    return float(f.mean())


def ma_tran_trung_binh(du_doan: po.DuDoan) -> np.ndarray:
    m = np.zeros((cb.SO_LOP, cb.SO_LOP))
    for vang, doan in du_doan:
        np.add.at(m, (vang, doan), 1)
    return m / len(du_doan)


def theo_o(chan_doan: Sequence[Dong]) -> Dict[Tuple[str, int], List[Dong]]:
    ra: Dict[Tuple[str, int], List[Dong]] = defaultdict(list)
    for r in chan_doan:
        o = po.o_cua(r)
        if o is not None:
            ra[o].append(r)
    return ra


def uoc_luong(cac_o: Dict[Tuple[str, int], List[Dong]], so_mau: Counter, nhan_ht: Sequence[str], vi_tri: Dict[str, int],
              du_doan: po.DuDoan, chi_dong_y: bool = False) -> Tuple[float, np.ndarray]:
    """(số mẫu có hiện tượng, ma trận thật-đoán của các mẫu đó, trung bình mỗi seed) ước lượng cho quần thể.

    Trọng số của một dòng là số mẫu của ô trên tập kiểm tra chia cho số dòng đã rút trong ô. `chi_dong_y` chỉ tính ma trận trên
    các dòng người chú thích đồng ý với nhãn gốc; số mẫu có hiện tượng vẫn tính trên mọi dòng.
    """
    so = 0.0
    m = np.zeros((cb.SO_LOP, cb.SO_LOP))
    so_seed = len(du_doan)
    for o, dong in cac_o.items():
        w = so_mau[o] / len(dong)
        for r in dong:
            if r["phenomenon"] not in nhan_ht:
                continue
            so += w
            if chi_dong_y and r["nhan_kiem_tra"] != "dong_y":
                continue
            i = vi_tri[str(r["uid"])]
            for _, doan in du_doan:
                m[int(r["label"]), int(doan[i])] += w / so_seed  # type: ignore[arg-type]
    return so, m


def so_loi(m: np.ndarray) -> float:
    return float(m.sum() - np.trace(m))


def tang_khi_sua(goc: np.ndarray, sua: np.ndarray, phan: float = 1.0) -> float:
    """Macro-F1 tăng bao nhiêu khi `phan` số lỗi trong ma trận `sua` được chuyển về đường chéo của ma trận `goc`."""
    moi = goc.copy()
    for a in range(cb.SO_LOP):
        for b in range(cb.SO_LOP):
            if a != b:
                moi[a, b] -= phan * sua[a, b]
                moi[a, a] += phan * sua[a, b]
    return macro_f1_tu_ma_tran(moi) - macro_f1_tu_ma_tran(goc)


def rut_lai(cac_o: Dict[Tuple[str, int], List[Dong]], rng: np.random.Generator) -> Dict[Tuple[str, int], List[Dong]]:
    return {o: [dong[j] for j in rng.integers(0, len(dong), len(dong))] for o, dong in cac_o.items()}


def phan_loi_va_tran(test: Sequence[Dong], chan_doan: Sequence[Dong], vi_tri: Dict[str, int], du_doan: po.DuDoan, so_lan: int,
                     rng: np.random.Generator) -> Dict[str, object]:
    so_mau = Counter(o for o in map(po.o_cua, test) if o is not None)
    cac_o = theo_o(chan_doan)
    thieu = sorted(o for o in so_mau if o not in cac_o)
    if thieu:
        raise ValueError(f"Không ước lượng được: các ô {thieu} không có dòng nào trong tập chẩn đoán")
    trong_qt = np.array([po.o_cua(r) is not None for r in test])
    quan_the = int(trong_qt.sum())
    loi_qt = float(np.mean([(v[trong_qt] != d[trong_qt]).sum() for v, d in du_doan]))
    mt = ma_tran_trung_binh(du_doan)
    mau = [rut_lai(cac_o, rng) for _ in range(so_lan)]

    nhom: Dict[str, dict] = {}
    for ten, ht in NHOM_UOC_LUONG.items():
        n, m = uoc_luong(cac_o, so_mau, ht, vi_tri, du_doan)
        phan = [so_loi(uoc_luong(x, so_mau, ht, vi_tri, du_doan)[1]) / loi_qt for x in mau]
        nhom[ten] = {"so_mau": n, "ti_le_mau": n / quan_the, "loi": so_loi(m), "ti_le_loi": so_loi(m) / loi_qt,
                     "ci95_ti_le_loi": [float(np.percentile(phan, 2.5)), float(np.percentile(phan, 97.5))], "ti_le_sai": so_loi(m) / n}

    tran: Dict[str, dict] = {}
    for ten, ht, dy in (("co_hien_tuong", NHOM_UOC_LUONG["co_hien_tuong"], False), ("co_hien_tuong_dong_y", NHOM_UOC_LUONG["co_hien_tuong"], True)):
        _, m = uoc_luong(cac_o, so_mau, ht, vi_tri, du_doan, chi_dong_y=dy)
        tang = tang_khi_sua(mt, m)
        bs = [tang_khi_sua(mt, uoc_luong(x, so_mau, ht, vi_tri, du_doan, chi_dong_y=dy)[1]) for x in mau]
        tran[ten] = {"tang": tang, "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "so_loi": so_loi(m),
                     "phan_can_de_tang_1_diem": 0.01 / tang if tang > 0 else None}
    return {"quan_the": quan_the, "ngoai_quan_the": len(test) - quan_the, "loi_quan_the": loi_qt, "nhom": nhom, "tran": tran}


# --- 3. Vì sao mô hình đồ thị không giúp -----------------------------------------------------------------------------


def ti_le_khac(a: np.ndarray, b: Optional[np.ndarray] = None) -> float:
    """Tỉ lệ mẫu có dự đoán khác nhau, trung bình mọi cặp lần chạy. a, b: (seed, mẫu); không có b thì so a với chính nó."""
    if b is None:
        return float(np.mean([(x != y).mean() for x, y in combinations(a, 2)]))
    return float(np.mean([(x != y).mean() for x in a for y in b]))


def dung_het_sai_het(vang: np.ndarray, a: np.ndarray, b: np.ndarray) -> int:
    """Số mẫu a đúng ở mọi seed mà b sai ở mọi seed."""
    return int(((a == vang).all(axis=0) & (b != vang).all(axis=0)).sum())


def mat_na_nhom_con(uid: Sequence[str], vang: np.ndarray, test: Sequence[Dong]) -> Dict[str, np.ndarray]:
    nhan_cau: Dict[str, set] = defaultdict(set)
    for u, y in zip(uid, vang):
        nhan_cau[cb.ma_cau(u)].add(int(y))
    trai = np.array([len(nhan_cau[cb.ma_cau(u)]) > 1 for u in uid])
    tu = [[str(t).lower() for t in r["tokens"]] for r in test]  # type: ignore[attr-defined]
    viet_tat = np.array([any(t in bd.PHU_DINH_VIET_TAT for t in ts) for ts in tu])
    chuan = np.array([any(t in bd.PHU_DINH and t not in bd.PHU_DINH_VIET_TAT for t in ts) for ts in tu])
    return {"toan_bo": np.ones(len(uid), dtype=bool), "trai_nhan": trai, "khong_trai_nhan": ~trai, "co_viet_tat": viet_tat,
            "khong_viet_tat": ~viet_tat, "chi_phu_dinh_chuan": chuan & ~viet_tat}


def phan_tich_do_thi(uid: Sequence[str], vang: np.ndarray, doan: Dict[str, np.ndarray], test: Sequence[Dong], so_lan: int,
                     rng: np.random.Generator) -> Dict[str, object]:
    khac = {"phobert_voi_chinh_no": ti_le_khac(doan["phobert"]),
            "phobert_voi_do_thi": {e: ti_le_khac(doan["phobert"], doan[e]) for e in DO_THI}}
    dh = {e: {"do_thi_dung_phobert_sai": dung_het_sai_het(vang, doan[e], doan["phobert"]),
              "phobert_dung_do_thi_sai": dung_het_sai_het(vang, doan["phobert"], doan[e])} for e in DO_THI}
    mat_na = mat_na_nhom_con(uid, vang, test)
    nhom: Dict[str, dict] = {}
    for g in NHOM_CON:
        o = {e: dct.o_dem(uid, vang, doan[e], mat_na[g]) for e in MO_HINH_SO}
        cac_cap = []
        for a, b in CAP_DO_THI:
            r = {"a": a, "b": b}
            r.update(cb.kiem_dinh(o[a], o[b], so_lan, rng))
            fa, aa = cb.do_do(o[a].sum(axis=1))
            fb, ab = cb.do_do(o[b].sum(axis=1))
            r["macro_f1"]["p_hoan_vi_seed"] = dct.hoan_vi_seed(fa, fb)
            r["accuracy"]["p_hoan_vi_seed"] = dct.hoan_vi_seed(aa, ab)
            cac_cap.append(r)
        nhom[g] = {"so_mau": int(mat_na[g].sum()), "cap": cac_cap}
    return {"khac_du_doan": khac, "dung_het_sai_het": dh, "nhom_con": nhom}


def tim_cap(kq_do_thi: dict, nhom: str, a: str, b: str) -> dict:
    return next(r for r in kq_do_thi["nhom_con"][nhom]["cap"] if r["a"] == a and r["b"] == b)


# --- Chạy ------------------------------------------------------------------------------------------------------------


def phan_tich(goc: Path, so_lan: int, seed: int) -> Dict[str, object]:
    test = po.doc_jsonl(goc / "data/processed/visfd_test.jsonl")
    chan_doan = po.doc_jsonl(goc / "data/diagnostic/diagnostic_300.jsonl")
    du_doan = po.nap_du_doan(goc / "results", "phobert", test)
    vi_tri = {str(r["uid"]): i for i, r in enumerate(test)}
    rng = np.random.default_rng(seed)
    seed_tn = {e: dct.SEED_THI_NGHIEM[e] for e in MO_HINH_SO}
    uid, vang, doan = dct.nap(goc / "results", seed_tn)
    if uid != [r["uid"] for r in test]:
        raise ValueError("thứ tự uid của dự đoán khác tập kiểm tra")
    return {"mo_hinh": "phobert", "seeds": list(cb.SEEDS), "so_lan": so_lan, "seed": seed,
            "loai_loi": bang_loai_loi(chan_doan, vi_tri, du_doan),
            "phan_loi": phan_loi_va_tran(test, chan_doan, vi_tri, du_doan, min(so_lan, 2000), rng),
            "do_thi": phan_tich_do_thi(uid, vang, doan, test, so_lan, rng)}


def in_tom_tat(kq: dict) -> str:
    dong = ["Loại lỗi của PhoBERT theo nhóm (lỗi mỗi seed):"]
    for g in NHOM:
        x = kq["loai_loi"]["tat_ca"][g]
        dong.append(f"  {g}: n = {x['n']}, lỗi {x['loi']:.1f}, cặp {x['cap']}, tỉ lệ sai theo nhãn thật {[round(t * 100, 1) for t in x['ti_le_sai_theo_nhan']]}")
    p = kq["phan_loi"]
    dong.append(f"Quần thể {p['quan_the']} mẫu, {p['loi_quan_the']:.1f} lỗi mỗi seed:")
    for ten, x in p["nhom"].items():
        dong.append(f"  {ten}: {x['so_mau']:.0f} mẫu ({x['ti_le_mau'] * 100:.1f} %), {x['ti_le_loi'] * 100:.1f} % số lỗi "
                    f"(KTC {x['ci95_ti_le_loi'][0] * 100:.1f} đến {x['ci95_ti_le_loi'][1] * 100:.1f}), tỉ lệ sai {x['ti_le_sai'] * 100:.1f} %")
    for ten, x in p["tran"].items():
        dong.append(f"  {ten}: tăng tối đa {x['tang'] * 100:.2f} điểm (KTC {x['ci95'][0] * 100:.2f} đến {x['ci95'][1] * 100:.2f}), "
                    f"cần sửa {x['phan_can_de_tang_1_diem'] * 100:.0f} % số lỗi để tăng 1 điểm")
    d = kq["do_thi"]
    dong.append(f"Dự đoán khác nhau: {d['khac_du_doan']}")
    dong.append(f"Đúng hết, sai hết: {d['dung_het_sai_het']}")
    for g, x in d["nhom_con"].items():
        dong.append(f"{g} ({x['so_mau']} mẫu)")
        for r in x["cap"]:
            f, a = r["macro_f1"], r["accuracy"]
            dong.append(f"  {r['a']} - {r['b']}: macro-F1 {f['hieu_so'] * 100:+.2f} (p {f['p']:.3f}, hoán vị {f['p_hoan_vi_seed']:.3f}); "
                        f"accuracy {a['hieu_so'] * 100:+.2f} (p {a['p']:.3f}, hoán vị {a['p_hoan_vi_seed']:.3f})")
    return "\n".join(dong)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Các phép đo bổ sung cho Chương 5, chỉ đọc dự đoán đã công bố.")
    ap.add_argument("--goc", type=Path, default=Path("."), help="thư mục gốc của repo")
    ap.add_argument("--so-lan", type=int, default=10_000, help="số lần lấy mẫu của bootstrap (mặc định 10000)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--chi-in", action="store_true", help="chỉ in, không ghi file")
    a = ap.parse_args(argv)
    kq = phan_tich(a.goc, a.so_lan, a.seed)
    print(in_tom_tat(kq))
    if not a.chi_in:
        p = a.goc / TEP_KET_QUA
        p.write_text(json.dumps(kq, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Đã ghi {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
