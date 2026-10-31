"""[CD1.11d] Chấm thí nghiệm can thiệp `phobert_luat` theo các điều kiện đã đặt ở mục 5.6.2 của báo cáo.

Lệnh KHÔNG huấn luyện, chỉ đọc dự đoán đã lưu. Tiêu chí viết ở đây và ở phiếu chuyende1/notes/CD1.11d_tin-hieu-luat.md TRƯỚC khi
có kết quả; commit chứa file này là bằng chứng về thứ tự đó. Đừng sửa tiêu chí sau khi đã xem số: muốn đo thêm thì thêm phép đo
mới và ghi là phân tích sau khi xem.

    do-phu   Luật bắt được bao nhiêu trên tập huấn luyện (mặc định). Không cần kết quả huấn luyện.
    cham     Chấm và ghi results/tin_hieu_luat.json.

    python scripts/phan_tich_tin_hieu_luat.py do-phu
    python scripts/phan_tich_tin_hieu_luat.py cham --chi-in

BỐN CÂU HỎI, THEO THỨ TỰ
------------------------
1. Có cải thiện không. Phép chính duy nhất: macro-F1 trên toàn tập kiểm tra của `phobert_luat` so với đối chứng chính. Được công
   nhận khi hiệu số dương, p bootstrap nhỏ hơn 0,05, cùng dấu ở mọi seed (tiêu chí mục 4.2) VÀ p hoán vị seed nhỏ hơn 0,05 (điều
   kiện 2 ở mục 5.6.2). Mọi phép khác là phép phụ, nhiều phép so và không hiệu chỉnh, chỉ đọc như dấu hiệu.

2. Phần cải thiện có đến từ chỗ luật tác động không (điều kiện 3). Hiệu của hiệu số: mức tăng ở nơi có hiện tượng trừ mức tăng ở
   nơi không có, trong đó khoảng tin cậy bootstrap phải nằm hẳn trên 0. Hai cách chia:
     - theo từ khoá trên toàn tập kiểm tra: bình luận luật bắt được với bình luận không có từ khoá nào. Bình luận không có từ khoá
       có đầu vào y hệt `phobert` (models/phobert_luat.py), nên đây là nhóm đối chứng tự nhiên, đủ lớn để phép so có lực.
     - theo nhãn của người chú thích trên tập chẩn đoán: mẫu có hiện tượng với nhóm thường, trên mọi dòng và trên các dòng đồng ý
       với nhãn gốc. Các nhóm này nhỏ, khoảng tin cậy sẽ rộng.

3. Tăng ở đâu. Các nhóm mục 5.6.2 nêu tên: F1 lớp trung tính, bình luận trái nhãn, nhóm chuyển ý và nhóm cả hai của tập chẩn đoán.
   Thêm số lỗi ước lượng cho quần thể theo ô (phan_tich_bo_sung.py), để so với dư địa tối đa đã in ở mục 5.6.2.

4. Thành phần nào đem lại phần tăng (điều kiện 4), nếu có chạy hai biến thể chỉ bật một kênh.

ĐIỀU KIỆN CHƯA LÀM ĐƯỢC Ở ĐÂY
-----------------------------
Người chú thích thứ hai (điều kiện 3) và bộ cặp câu tối thiểu (điều kiện 5) chưa có: các phép trên phần đồng ý với nhãn gốc vì vậy
vẫn dựa trên nhận định của một người.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

_GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(_GOC / "src"))

import build_diagnostic_candidates as bd  # noqa: E402
import compare_baselines as cb  # noqa: E402
import doi_chung_do_thi as dct  # noqa: E402
import phan_tich_bo_sung as pb  # noqa: E402
import probe_oracle_rules as po  # noqa: E402
from nsmgat.data import tin_hieu_luat as thl  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEP_KET_QUA = Path("results/tin_hieu_luat.json")
MO_HINH = "phobert_luat"
BIEN_THE = ("phobert_luat_phu_dinh", "phobert_luat_chuyen_y")
# Đối chứng chính cùng phiên, cùng seed, cùng nền tảng; "phobert" và "asgcn_khong_gcn" là hai mốc mục 5.6.2 nêu tên.
DOI_CHUNG_CHINH = "phobert_cung_phien"
DOI_CHUNG_PHU = ("phobert", "asgcn_khong_gcn")
NHOM_TOAN_TAP = ("toan_bo", "trai_nhan", "khong_trai_nhan", "co_tu_khoa", "co_tu_phu_dinh", "co_tu_chuyen_y", "khong_tu_khoa",
                 "nhan_trung_tinh")
NHOM_CHAN_DOAN = ("regular", "negation", "contrast", "both", "co_hien_tuong")
LOP_TRUNG_TINH = 1
NGUONG_P = 0.05


# --- Độ phủ của luật ------------------------------------------------------------------------------------------------


def do_phu(ds: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """Thống kê trên các bình luận khác nhau của một tập: luật bắt bao nhiêu, phạm vi phủ định dài bao nhiêu."""
    cau = {tuple(r["tokens"]) for r in ds}  # type: ignore[arg-type]
    dem = {"co_phu_dinh": 0, "co_chuyen_y": 0, "ca_hai": 0, "khong_tu_khoa": 0, "co_noi_nhuong_bo": 0}
    tu = {"tong": 0, "tu_phu_dinh": 0, "pham_vi": 0, "tu_noi": 0, "ve_nhuong": 0, "ve_nhan": 0}
    do_dai_pham_vi: List[int] = []
    for tokens in cau:
        th = thl.tin_hieu_cua(tokens)
        pd, cy = th["phu_dinh"], th["chuyen_y"]
        co_pd, co_cy = thl.PD_TU in pd, thl.CY_TU in cy
        dem["co_phu_dinh"] += co_pd
        dem["co_chuyen_y"] += co_cy
        dem["ca_hai"] += co_pd and co_cy
        dem["khong_tu_khoa"] += not (co_pd or co_cy)
        dem["co_noi_nhuong_bo"] += any(t.lower() in thl.NHUONG_BO for t in tokens)
        tu["tong"] += len(tokens)
        tu["tu_phu_dinh"] += pd.count(thl.PD_TU)
        tu["pham_vi"] += pd.count(thl.PD_PHAM_VI)
        tu["tu_noi"] += cy.count(thl.CY_TU)
        tu["ve_nhuong"] += cy.count(thl.CY_VE_NHUONG)
        tu["ve_nhan"] += cy.count(thl.CY_VE_NHAN)
        dai = None
        for n in pd:
            if n == thl.PD_TU:
                if dai is not None:
                    do_dai_pham_vi.append(dai)
                dai = 0
            elif n == thl.PD_PHAM_VI and dai is not None:
                dai += 1
            elif dai is not None:
                do_dai_pham_vi.append(dai)
                dai = None
        if dai is not None:
            do_dai_pham_vi.append(dai)
    pv = np.array(do_dai_pham_vi) if do_dai_pham_vi else np.zeros(1)
    return {"so_mau": len(ds), "so_binh_luan": len(cau), "binh_luan": dem,
            "ti_le_binh_luan": {k: v / len(cau) for k, v in dem.items()}, "tu": tu,
            "ti_le_tu": {k: v / tu["tong"] for k, v in tu.items() if k != "tong"},
            "pham_vi_phu_dinh": {"luot": len(do_dai_pham_vi), "trung_vi": float(np.median(pv)),
                                 "p90": float(np.percentile(pv, 90)), "lon_nhat": int(pv.max()),
                                 "ti_le_rong": float((pv == 0).mean())}}


# --- Nhóm mẫu -------------------------------------------------------------------------------------------------------


def mat_na_toan_tap(uid: Sequence[str], vang: np.ndarray, test: Sequence[Dict[str, object]]) -> Dict[str, np.ndarray]:
    con = pb.mat_na_nhom_con(uid, vang, test)
    tk = [bd.tim_tu_khoa(r["tokens"]) for r in test]  # type: ignore[arg-type]
    pd = np.array([bool(x[0]) for x in tk])
    cy = np.array([bool(x[1]) for x in tk])
    return {"toan_bo": con["toan_bo"], "trai_nhan": con["trai_nhan"], "khong_trai_nhan": con["khong_trai_nhan"],
            "co_tu_khoa": pd | cy, "co_tu_phu_dinh": pd, "co_tu_chuyen_y": cy, "khong_tu_khoa": ~(pd | cy),
            "nhan_trung_tinh": vang == LOP_TRUNG_TINH}


def mat_na_chan_doan(uid: Sequence[str], chan_doan: Sequence[Dict[str, object]], chi_dong_y: bool) -> Dict[str, np.ndarray]:
    ht = {str(r["uid"]): r["phenomenon"] for r in chan_doan if not chi_dong_y or r["nhan_kiem_tra"] == "dong_y"}
    nhan = [ht.get(u) for u in uid]
    ra = {g: np.array([h == g for h in nhan]) for g in ("regular", "negation", "contrast", "both")}
    ra["co_hien_tuong"] = ra["negation"] | ra["contrast"] | ra["both"]
    return ra


def o_canh_cau(uid: Sequence[str], vang: np.ndarray, doan: np.ndarray, chon: np.ndarray) -> np.ndarray:
    """(seed, số bình luận của cả tập, 9): mọi nhóm cùng một trục bình luận, để rút một mẫu bootstrap dùng chung cho hai nhóm."""
    cau = sorted({cb.ma_cau(u) for u in uid})
    vi_tri = {c: i for i, c in enumerate(cau)}
    ra = np.zeros((doan.shape[0], len(cau), cb.SO_LOP ** 2), dtype=np.float64)
    i_cau = np.array([vi_tri[cb.ma_cau(u)] for u in uid])
    for s in range(doan.shape[0]):
        np.add.at(ra[s], (i_cau[chon], vang[chon] * cb.SO_LOP + doan[s][chon]), 1)
    return ra


# --- Phép kiểm --------------------------------------------------------------------------------------------------------


def f1_lop(o: np.ndarray, lop: int) -> np.ndarray:
    """F1 của một lớp từ ô đếm (..., 9)."""
    m = o.reshape(o.shape[:-1] + (cb.SO_LOP, cb.SO_LOP))
    tp = m[..., lop, lop]
    mau = m[..., lop, :].sum(axis=-1) + m[..., :, lop].sum(axis=-1)
    return np.divide(2 * tp, mau, out=np.zeros_like(tp), where=mau > 0)


def _bootstrap(so_cau: int, ham: Callable[[np.ndarray], np.ndarray], so_lan: int, rng: np.random.Generator, khoi: int = 500) -> np.ndarray:
    """Giá trị của thống kê trên từng mẫu bootstrap. `ham` nhận trọng số (n, số bình luận), trả về mảng (n,)."""
    ra, con = [], so_lan
    while con > 0:
        n = min(khoi, con)
        ra.append(ham(rng.multinomial(so_cau, np.full(so_cau, 1.0 / so_cau), size=n).astype(np.float64)))
        con -= n
    return np.concatenate(ra)


def _p_hai_phia(d: np.ndarray) -> float:
    return float(min(1.0, 2 * min((np.sum(d <= 0) + 1) / (len(d) + 1), (np.sum(d >= 0) + 1) / (len(d) + 1))))


def _cung_dau(hieu: np.ndarray) -> bool:
    return bool((hieu > 0).all() or (hieu < 0).all())


def kiem_cap(a: np.ndarray, b: np.ndarray, so_lan: int, rng: np.random.Generator) -> Dict[str, Dict[str, object]]:
    """So A với B trên một nhóm: bootstrap, hoán vị seed, và cùng dấu ở mọi seed. a, b: (seed, câu, 9), cùng thứ tự seed."""
    r: Dict[str, Dict[str, object]] = cb.kiem_dinh(a, b, so_lan, rng)  # type: ignore[assignment]
    fa, aa = cb.do_do(a.sum(axis=1))
    fb, ab = cb.do_do(b.sum(axis=1))
    for do, x, y in (("macro_f1", fa, fb), ("accuracy", aa, ab)):
        r[do]["p_hoan_vi_seed"] = dct.hoan_vi_seed(x, y)
        r[do]["cung_dau"] = _cung_dau(x - y)
        r[do]["hieu_tung_seed"] = (x - y).tolist()
    return r


def kiem_f1_lop(a: np.ndarray, b: np.ndarray, lop: int, so_lan: int, rng: np.random.Generator) -> Dict[str, object]:
    fa, fb = f1_lop(a.sum(axis=1), lop), f1_lop(b.sum(axis=1), lop)

    def ham(w: np.ndarray) -> np.ndarray:
        return f1_lop(np.einsum("nc,sck->nsk", w, a), lop).mean(axis=1) - f1_lop(np.einsum("nc,sck->nsk", w, b), lop).mean(axis=1)

    d = _bootstrap(a.shape[1], ham, so_lan, rng)
    return {"a": float(fa.mean()), "b": float(fb.mean()), "hieu_so": float((fa - fb).mean()), "ci95_duoi": float(np.percentile(d, 2.5)),
            "ci95_tren": float(np.percentile(d, 97.5)), "p": _p_hai_phia(d), "p_hoan_vi_seed": dct.hoan_vi_seed(fa, fb),
            "cung_dau": _cung_dau(fa - fb), "hieu_tung_seed": (fa - fb).tolist()}


def hieu_cua_hieu(a1: np.ndarray, b1: np.ndarray, a2: np.ndarray, b2: np.ndarray, so_lan: int, rng: np.random.Generator) -> Dict[str, Dict[str, float]]:
    """(A - B ở nhóm 1) - (A - B ở nhóm 2), cho macro-F1 và accuracy. Bốn mảng (seed, số bình luận, 9), cùng trục bình luận."""
    ra: Dict[str, Dict[str, float]] = {}
    for vi_tri, do in enumerate(("macro_f1", "accuracy")):
        def ham(w: np.ndarray) -> np.ndarray:
            ket = [cb.do_do(np.einsum("nc,sck->nsk", w, x))[vi_tri].mean(axis=1) for x in (a1, b1, a2, b2)]
            return (ket[0] - ket[1]) - (ket[2] - ket[3])

        d = _bootstrap(a1.shape[1], ham, so_lan, rng)
        t = [cb.do_do(x.sum(axis=1))[vi_tri].mean() for x in (a1, b1, a2, b2)]
        ra[do] = {"nhom_1": float(t[0] - t[1]), "nhom_2": float(t[2] - t[3]), "hieu_cua_hieu": float((t[0] - t[1]) - (t[2] - t[3])),
                  "ci95_duoi": float(np.percentile(d, 2.5)), "ci95_tren": float(np.percentile(d, 97.5))}
    return ra


def ket_luan(chinh: Dict[str, object], hdh_tu_khoa: Dict[str, float]) -> Dict[str, object]:
    """Câu trả lời cho hai câu hỏi đầu, đúng theo tiêu chí đặt trước."""
    dat_4_2 = bool(chinh["p"] < NGUONG_P and chinh["cung_dau"])  # type: ignore[operator]
    qua_hoan_vi = bool(chinh["p_hoan_vi_seed"] < NGUONG_P)  # type: ignore[operator]
    cong_nhan = bool(chinh["hieu_so"] > 0 and dat_4_2 and qua_hoan_vi)  # type: ignore[operator]
    return {"dat_tieu_chi_4_2": dat_4_2, "qua_hoan_vi_seed": qua_hoan_vi, "cong_nhan_cai_thien": cong_nhan,
            "quy_duoc_cho_hien_tuong": bool(cong_nhan and hdh_tu_khoa["ci95_duoi"] > 0)}


# --- Chấm -------------------------------------------------------------------------------------------------------------


def uoc_luong_loi(chan_doan: Sequence[Dict[str, object]], test: Sequence[Dict[str, object]], vi_tri: Dict[str, int], vang: np.ndarray,
                  a: np.ndarray, b: np.ndarray, so_lan: int, rng: np.random.Generator) -> Dict[str, Dict[str, object]]:
    """Số lỗi mỗi seed ước lượng cho quần thể theo ô, ở mẫu có hiện tượng và mẫu thường, cho A và B."""
    so_mau = Counter(o for o in map(po.o_cua, test) if o is not None)
    cac_o = pb.theo_o(chan_doan)
    da, db = [(vang, d) for d in a], [(vang, d) for d in b]
    mau = [pb.rut_lai(cac_o, rng) for _ in range(so_lan)]
    ra: Dict[str, Dict[str, object]] = {}
    for ten in ("co_hien_tuong", "thuong"):
        ht = pb.NHOM_UOC_LUONG[ten]
        la = pb.so_loi(pb.uoc_luong(cac_o, so_mau, ht, vi_tri, da)[1])
        lb = pb.so_loi(pb.uoc_luong(cac_o, so_mau, ht, vi_tri, db)[1])
        d = [pb.so_loi(pb.uoc_luong(x, so_mau, ht, vi_tri, da)[1]) - pb.so_loi(pb.uoc_luong(x, so_mau, ht, vi_tri, db)[1]) for x in mau]
        ra[ten] = {"loi_a": la, "loi_b": lb, "thay_doi": la - lb, "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}
    return ra


def _co_du_seed(goc: Path, exp: str, seeds: Sequence[int]) -> bool:
    return all((goc / exp / f"seed{s}" / "predictions.jsonl").exists() for s in seeds)


def cham(goc: Path, seeds: Sequence[int], doi_chung_chinh: str, so_lan: int, seed: int) -> Dict[str, object]:
    ket_qua = goc / "results"
    test = po.doc_jsonl(goc / "data/processed/visfd_test.jsonl")
    chan_doan = po.doc_jsonl(goc / "data/diagnostic/diagnostic_300.jsonl")
    for exp in (MO_HINH, doi_chung_chinh):
        if not _co_du_seed(ket_qua, exp, seeds):
            raise FileNotFoundError(f"thiếu dự đoán của {exp} ở một trong các seed {list(seeds)}")
    doi_chung = [doi_chung_chinh] + [e for e in DOI_CHUNG_PHU if e != doi_chung_chinh and _co_du_seed(ket_qua, e, seeds)]
    bien_the = [e for e in BIEN_THE if _co_du_seed(ket_qua, e, seeds)]
    tn = {e: tuple(seeds) for e in [MO_HINH] + doi_chung + bien_the}
    uid, vang, doan = dct.nap(ket_qua, tn)
    if uid != [r["uid"] for r in test]:
        raise ValueError("thứ tự uid của dự đoán khác tập kiểm tra")
    vi_tri = {str(r["uid"]): i for i, r in enumerate(test)}
    rng = np.random.default_rng(seed)

    mat_na_tt = mat_na_toan_tap(uid, vang, test)
    mat_na_cd = {"tat_ca": mat_na_chan_doan(uid, chan_doan, False), "dong_y": mat_na_chan_doan(uid, chan_doan, True)}

    def so(a: str, b: str, chon: np.ndarray) -> Dict[str, object]:
        return kiem_cap(dct.o_dem(uid, vang, doan[a], chon), dct.o_dem(uid, vang, doan[b], chon), so_lan, rng)

    cac_cap: Dict[str, dict] = {}
    for b in doi_chung:
        cac_cap[b] = {"toan_tap": {g: so(MO_HINH, b, mat_na_tt[g]) | {"so_mau": int(mat_na_tt[g].sum())} for g in NHOM_TOAN_TAP if mat_na_tt[g].any()},
                      "chan_doan": {ph: {g: so(MO_HINH, b, m[g]) | {"so_mau": int(m[g].sum())} for g in NHOM_CHAN_DOAN if m[g].any()} for ph, m in mat_na_cd.items()}}

    canh = {e: {g: o_canh_cau(uid, vang, doan[e], mat_na_tt[g]) for g in ("toan_bo", "co_tu_khoa", "khong_tu_khoa")} for e in (MO_HINH, doi_chung_chinh)}
    hdh = {"tu_khoa": hieu_cua_hieu(canh[MO_HINH]["co_tu_khoa"], canh[doi_chung_chinh]["co_tu_khoa"], canh[MO_HINH]["khong_tu_khoa"],
                                    canh[doi_chung_chinh]["khong_tu_khoa"], so_lan, rng)}
    for ph, m in mat_na_cd.items():
        o1 = {e: o_canh_cau(uid, vang, doan[e], m["co_hien_tuong"]) for e in (MO_HINH, doi_chung_chinh)}
        o2 = {e: o_canh_cau(uid, vang, doan[e], m["regular"]) for e in (MO_HINH, doi_chung_chinh)}
        hdh[f"chan_doan_{ph}"] = hieu_cua_hieu(o1[MO_HINH], o1[doi_chung_chinh], o2[MO_HINH], o2[doi_chung_chinh], so_lan, rng)

    tt = canh[MO_HINH]["toan_bo"], canh[doi_chung_chinh]["toan_bo"]
    f1_cac_lop = {str(lop): kiem_f1_lop(tt[0], tt[1], lop, so_lan, rng) for lop in range(cb.SO_LOP)}
    khac = {"cung_seed_voi_doi_chung": float(np.mean([(x != y).mean() for x, y in zip(doan[MO_HINH], doan[doi_chung_chinh])])),
            "doi_chung_voi_chinh_no": pb.ti_le_khac(doan[doi_chung_chinh]), "mo_hinh_voi_chinh_no": pb.ti_le_khac(doan[MO_HINH])}
    dung_sai = {"luat_dung_doi_chung_sai": pb.dung_het_sai_het(vang, doan[MO_HINH], doan[doi_chung_chinh]),
                "doi_chung_dung_luat_sai": pb.dung_het_sai_het(vang, doan[doi_chung_chinh], doan[MO_HINH])}
    loi = uoc_luong_loi(chan_doan, test, vi_tri, vang, doan[MO_HINH], doan[doi_chung_chinh], min(so_lan, 2000), rng)
    loai_bo = {e: so(e, doi_chung_chinh, mat_na_tt["toan_bo"]) | {"so_voi_ca_hai_kenh": so(MO_HINH, e, mat_na_tt["toan_bo"])} for e in bien_the}

    chinh = cac_cap[doi_chung_chinh]["toan_tap"]["toan_bo"]["macro_f1"]
    return {"mo_hinh": MO_HINH, "doi_chung_chinh": doi_chung_chinh, "seeds": list(seeds), "so_lan": so_lan, "seed": seed,
            "ket_luan": ket_luan(chinh, hdh["tu_khoa"]["macro_f1"]),
            "cap": cac_cap, "hieu_cua_hieu": hdh, "f1_tung_lop": f1_cac_lop, "khac_du_doan": khac, "dung_het_sai_het": dung_sai,
            "loi_uoc_luong": loi, "loai_bo": loai_bo,
            "do_phu_tap_kiem_tra": do_phu(test)}


# --- In ---------------------------------------------------------------------------------------------------------------


def _d(x: float) -> str:
    return f"{x * 100:+.2f}"


def _dong_cap(ten: str, r: Dict[str, Dict[str, object]], so_mau: Optional[int] = None) -> str:
    f, a = r["macro_f1"], r["accuracy"]
    n = f" ({so_mau} mẫu)" if so_mau is not None else ""
    return (f"  {ten}{n}: macro-F1 {_d(f['hieu_so'])} [{_d(f['ci95_duoi'])}; {_d(f['ci95_tren'])}] p {f['p']:.3f}, hoán vị {f['p_hoan_vi_seed']:.3f}, "  # type: ignore[arg-type]
            f"cùng dấu {'có' if f['cung_dau'] else 'không'}; accuracy {_d(a['hieu_so'])} p {a['p']:.3f}, hoán vị {a['p_hoan_vi_seed']:.3f}")  # type: ignore[arg-type]


def in_do_phu(k: Dict[str, object], ten_tap: str) -> str:
    tl, tu, pv = k["ti_le_binh_luan"], k["ti_le_tu"], k["pham_vi_phu_dinh"]
    return "\n".join([
        f"Độ phủ của luật trên tập {ten_tap}: {k['so_binh_luan']} bình luận, {k['so_mau']} mẫu",
        f"  bình luận có từ phủ định {tl['co_phu_dinh'] * 100:.1f} %, có từ nối chuyển ý {tl['co_chuyen_y'] * 100:.1f} %, "  # type: ignore[index]
        f"cả hai {tl['ca_hai'] * 100:.1f} %, không từ khoá nào {tl['khong_tu_khoa'] * 100:.1f} %, có từ nối nhượng bộ {tl['co_noi_nhuong_bo'] * 100:.1f} %",  # type: ignore[index]
        f"  tỉ lệ từ được gán nhãn: từ phủ định {tu['tu_phu_dinh'] * 100:.1f} %, phạm vi {tu['pham_vi'] * 100:.1f} %, từ nối {tu['tu_noi'] * 100:.1f} %, "  # type: ignore[index]
        f"vế nhượng {tu['ve_nhuong'] * 100:.1f} %, vế nhấn {tu['ve_nhan'] * 100:.1f} %",  # type: ignore[index]
        f"  phạm vi phủ định: {pv['luot']} lượt, trung vị {pv['trung_vi']:.0f} từ, phân vị 90 {pv['p90']:.0f} từ, dài nhất {pv['lon_nhat']} từ, "  # type: ignore[index]
        f"rỗng {pv['ti_le_rong'] * 100:.1f} %",  # type: ignore[index]
    ])


def in_ket_qua(kq: Dict[str, object]) -> str:
    dc = kq["doi_chung_chinh"]
    kl = kq["ket_luan"]
    dong = [f"{kq['mo_hinh']} so với {dc}, seed {kq['seeds']}, {kq['so_lan']} lần lấy mẫu", "",
            "KẾT LUẬN THEO TIÊU CHÍ ĐẶT TRƯỚC",
            f"  đạt tiêu chí mục 4.2 (p < 0,05 và cùng dấu mọi seed): {kl['dat_tieu_chi_4_2']}",  # type: ignore[index]
            f"  qua phép hoán vị seed: {kl['qua_hoan_vi_seed']}",  # type: ignore[index]
            f"  công nhận cải thiện: {kl['cong_nhan_cai_thien']}",  # type: ignore[index]
            f"  quy được cho hai hiện tượng: {kl['quy_duoc_cho_hien_tuong']}", ""]  # type: ignore[index]
    for b, c in kq["cap"].items():  # type: ignore[attr-defined]
        dong.append(f"So với {b}, toàn tập kiểm tra:")
        dong += [_dong_cap(g, r, r["so_mau"]) for g, r in c["toan_tap"].items() if g != "nhan_trung_tinh"]
        # Nhóm chỉ có một nhãn thật nên macro-F1 vô nghĩa: accuracy ở đây chính là độ phủ của lớp trung tính.
        x = c["toan_tap"]["nhan_trung_tinh"]["accuracy"]
        dong.append(f"  độ phủ lớp trung tính: {_d(x['hieu_so'])} [{_d(x['ci95_duoi'])}; {_d(x['ci95_tren'])}] p {x['p']:.3f}, hoán vị {x['p_hoan_vi_seed']:.3f}")
        for ph, nhom in c["chan_doan"].items():
            dong.append(f"So với {b}, tập chẩn đoán ({ph}):")
            dong += [_dong_cap(g, r, r["so_mau"]) for g, r in nhom.items()]
        dong.append("")
    dong.append("Hiệu của hiệu số (nơi có hiện tượng trừ nơi không có):")
    for ten, h in kq["hieu_cua_hieu"].items():  # type: ignore[attr-defined]
        for do, x in h.items():
            dong.append(f"  {ten}, {do}: {_d(x['nhom_1'])} trừ {_d(x['nhom_2'])} = {_d(x['hieu_cua_hieu'])} [{_d(x['ci95_duoi'])}; {_d(x['ci95_tren'])}]")
    dong.append("F1 từng lớp (0 tiêu cực, 1 trung tính, 2 tích cực):")
    for lop, x in kq["f1_tung_lop"].items():  # type: ignore[attr-defined]
        dong.append(f"  lớp {lop}: {x['a'] * 100:.2f} so với {x['b'] * 100:.2f}, hiệu {_d(x['hieu_so'])} [{_d(x['ci95_duoi'])}; {_d(x['ci95_tren'])}] "
                    f"p {x['p']:.3f}, hoán vị {x['p_hoan_vi_seed']:.3f}, cùng dấu {'có' if x['cung_dau'] else 'không'}")
    k = kq["khac_du_doan"]
    dong.append(f"Dự đoán khác nhau: với đối chứng cùng seed {k['cung_seed_voi_doi_chung'] * 100:.2f} %; đối chứng với chính nó "  # type: ignore[index]
                f"{k['doi_chung_voi_chinh_no'] * 100:.2f} %; mô hình với chính nó {k['mo_hinh_voi_chinh_no'] * 100:.2f} %")  # type: ignore[index]
    dong.append(f"Đúng hết, sai hết: {kq['dung_het_sai_het']}")
    dong.append("Số lỗi mỗi seed ước lượng cho quần thể theo ô:")
    for ten, x in kq["loi_uoc_luong"].items():  # type: ignore[attr-defined]
        dong.append(f"  {ten}: {x['loi_a']:.1f} so với {x['loi_b']:.1f}, thay đổi {x['thay_doi']:+.1f} [{x['ci95'][0]:+.1f}; {x['ci95'][1]:+.1f}]")
    if kq["loai_bo"]:
        dong.append("Thí nghiệm loại bỏ, chỉ bật một kênh, toàn tập kiểm tra:")
        for e, r in kq["loai_bo"].items():  # type: ignore[attr-defined]
            dong.append(_dong_cap(f"{e} so với {dc}", r))
            dong.append(_dong_cap(f"{MO_HINH} so với {e}", r["so_voi_ca_hai_kenh"]))
    dong += ["", in_do_phu(kq["do_phu_tap_kiem_tra"], "kiểm tra")]  # type: ignore[arg-type]
    return "\n".join(dong)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Chấm thí nghiệm can thiệp phobert_luat theo các điều kiện đặt trước.")
    ap.add_argument("--goc", type=Path, default=Path("."), help="thư mục gốc của repo")
    con = ap.add_subparsers(dest="lenh", required=True)
    p_phu = con.add_parser("do-phu", help="luật bắt được bao nhiêu, không cần kết quả huấn luyện")
    p_phu.add_argument("--tap", choices=("train", "dev", "test"), default="train", help="tập để đếm (mặc định train)")
    p_cham = con.add_parser("cham", help="chấm và ghi results/tin_hieu_luat.json")
    p_cham.add_argument("--doi-chung", default=DOI_CHUNG_CHINH, help=f"đối chứng chính (mặc định {DOI_CHUNG_CHINH})")
    p_cham.add_argument("--seeds", type=int, nargs="+", default=list(cb.SEEDS), help="các seed của thí nghiệm (mặc định đúng các seed của Chương 4)")
    p_cham.add_argument("--so-lan", type=int, default=10_000, help="số lần lấy mẫu của bootstrap (mặc định 10000)")
    p_cham.add_argument("--seed", type=int, default=20261101, help="seed của bộ sinh số ngẫu nhiên cho bootstrap")
    p_cham.add_argument("--chi-in", action="store_true", help="chỉ in, không ghi file")
    a = ap.parse_args(argv)

    if a.lenh == "do-phu":
        print(in_do_phu(do_phu(po.doc_jsonl(a.goc / f"data/processed/visfd_{a.tap}.jsonl")), a.tap))
        return 0
    kq = cham(a.goc, a.seeds, a.doi_chung, a.so_lan, a.seed)
    print(in_ket_qua(kq))
    if not a.chi_in:
        p = a.goc / TEP_KET_QUA
        p.write_text(json.dumps(kq, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Đã ghi {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
