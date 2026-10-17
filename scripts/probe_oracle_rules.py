"""[CD1.11] Ba phép thăm dò trần cải tiến cho hướng xử lý phủ định và chuyển ý, từ dữ liệu đã có.

Gói CD1.11 của plan: trước khi cài mô hình đề xuất (Chuyên đề 2), đo xem hướng "xử lý tường minh phủ định
và chuyển ý" đáng giá bao nhiêu trên chính dữ liệu này. Lệnh KHÔNG huấn luyện, KHÔNG chạy mô hình: nó chỉ
đọc dự đoán đã công bố trong results/<exp>/seed<N>/predictions.jsonl, nhãn hiện tượng của tập chẩn đoán
và cây cú pháp VnCoreNLP đã lưu sẵn trong data/processed/visfd_test.jsonl.

P1. Trần của luật lật cực
------------------------
Cách xử lý phủ định quen thuộc nhất là lật cực của ý kiến: tích cực thành tiêu cực và ngược lại. Một luật
như vậy chỉ sửa được lỗi NGƯỢC CỰC (nhãn thật tích cực mà đoán tiêu cực, hoặc ngược lại); nó không sửa được
lỗi có lớp trung tính ở một đầu. Phép thăm dò dùng một "luật lý tưởng" biết trước nhãn thật: lật đúng mọi
lỗi ngược cực trong phạm vi, không lật nhầm chỗ nào. Hai phạm vi:
  - tập chẩn đoán: các dòng người chú thích xác định có phủ định (hoặc chuyển ý, hoặc cả hai) tác động lên
    khía cạnh đang xét, đúng như plan ghi "dùng nhãn vàng để xác định phạm vi";
  - toàn tập kiểm tra: mọi mẫu thuộc câu có từ khoá phủ định. Phạm vi này rộng hơn thật (câu có "không"
    chưa chắc phủ định ý về khía cạnh đó), nên con số là cận trên.
Kèm hai cận trên lỏng hơn để đặt con số vào khung: sửa mọi lỗi ngược cực ở bất cứ đâu, và sửa MỌI lỗi (kể
cả lỗi có lớp trung tính) ở câu có từ khoá phủ định hoặc chuyển ý.

P2. Độ chính xác và độ phủ của luật thô
--------------------------------------
Luật tối giản: một mẫu (câu, khía cạnh) được coi là có phủ định nếu câu có từ khoá phủ định, có chuyển ý nếu
câu có từ nối chuyển ý, đúng danh sách từ khoá đã dùng để lọc ứng viên (build_diagnostic_candidates.py). So
với nhãn hiện tượng của người chú thích:
  - độ chính xác: trong các mẫu luật bắt, bao nhiêu phần thật có hiện tượng tác động lên khía cạnh đó;
  - độ phủ: trong các mẫu thật có hiện tượng, bao nhiêu phần luật bắt được.
Tập chẩn đoán được rút cân bằng nhãn trong từng nhóm từ khoá và ưu tiên câu 5 đến 40 từ, nên tỉ lệ thô trên
tập không đại diện cho tập kiểm tra. Lệnh ước lượng theo Ô (nhóm từ khoá, nhãn gốc): trong mỗi ô các dòng
được rút ngẫu nhiên đều, nên trọng số của ô là số mẫu của ô trên tập kiểm tra chia cho số dòng đã rút. Quần
thể của ước lượng là các mẫu thuộc câu 5 đến 40 từ và không chỉ chứa từ "ngờ"; câu chỉ chứa từ ngờ không
được rút nên không ước lượng được. Khoảng tin cậy 95 % bằng bootstrap trong từng ô.
"Cửa sổ quanh khía cạnh" của plan không làm được ở mức tối giản: khía cạnh của UIT-ViSFD là nhóm (BATTERY,
CAMERA...) không có vị trí trong câu. Muốn biết từ phủ định đứng gần khía cạnh nào thì phải có từ điển cụm
từ của từng khía cạnh, là việc của Chuyên đề 2.

P3. Cây cú pháp có đưa từ phủ định lại gần từ nó phủ định không
---------------------------------------------------------------
Trong tiếng Việt từ phủ định đứng ngay trước vị từ nó phủ định ("không đẹp", "chưa hết"). Lệnh lấy mọi lượt
từ khoá phủ định trong các câu của tập kiểm tra mà ngay sau nó là một từ (không phải dấu câu) thuộc cùng câu,
rồi đo trên cây VnCoreNLP: từ phủ định có được gán nhãn phó từ không, và đường đi trên cây giữa hai từ dài bao
nhiêu cạnh (khoảng cách tuyến tính là 1). Tách dạng chuẩn (không, chưa, chẳng, chả...) với dạng viết tắt (ko,
k, kh...). Từ đứng sau chỉ là xấp xỉ của từ bị phủ định, có thể sai ở câu như "không phải máy này tệ".

KHÔNG PHẢI S2.2
---------------
Luật ở P2 là bản thăm dò dùng một lần. Nó nằm ở đây theo chuyende1/MODULE.md mục 2.3, không ở
src/nsmgat/rules/. Danh sách từ khoá lấy thẳng từ build_diagnostic_candidates.py, không chép thành bản thứ hai.

Dùng:
    python scripts/probe_oracle_rules.py            # in bảng, ghi results/probe_results.json và bảng .md
    python scripts/probe_oracle_rules.py --chi-in   # chỉ in, không ghi file
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import build_diagnostic_candidates as bd  # noqa: E402
import compare_baselines as cb  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

Dong = Dict[str, object]
DuDoan = List[Tuple[np.ndarray, np.ndarray]]  # [(nhãn thật, nhãn đoán)] theo thứ tự cb.SEEDS

MO_HINH_MAC_DINH = "phobert"
NHOM = ("negation", "contrast", "both", "regular")
TEN_NHOM = {"negation": "Phủ định", "contrast": "Chuyển ý", "both": "Cả hai", "regular": "Thường"}
# Luật nào bắt nhóm ứng viên (theo từ khoá) nào, và nhãn hiện tượng nào thì tính là luật bắt đúng.
LUAT_BAT = {"phu_dinh": ("phu_dinh", "ca_hai"), "chuyen_y": ("chuyen_y", "ca_hai")}
CO_HIEN_TUONG = {"phu_dinh": ("negation", "both"), "chuyen_y": ("contrast", "both")}
TEN_LUAT = {"phu_dinh": "Câu có từ khoá phủ định", "chuyen_y": "Câu có từ nối chuyển ý"}
DAU_CAU = "CH"  # nhãn từ loại của dấu câu trong VnCoreNLP
PHO_TU = "R"
TEN_DANG = {"chuan": "Dạng chuẩn", "viet_tat": "Dạng viết tắt"}


def doc_jsonl(p: Path) -> List[Dong]:
    with p.open(encoding="utf-8") as fh:
        return [json.loads(d) for d in fh if d.strip()]


def nguoc_cuc(vang: np.ndarray, doan: np.ndarray) -> np.ndarray:
    """Mặt nạ các lỗi ngược cực: thật tiêu cực mà đoán tích cực, hoặc ngược lại (0 tiêu cực, 2 tích cực)."""
    return ((vang == 0) & (doan == 2)) | ((vang == 2) & (doan == 0))


def sua_theo_mat_na(vang: np.ndarray, doan: np.ndarray, mat_na: np.ndarray) -> np.ndarray:
    """Luật lý tưởng: ở chỗ mặt nạ bật, dự đoán thành nhãn thật. Không sửa mảng đầu vào."""
    ra = doan.copy()
    ra[mat_na] = vang[mat_na]
    return ra


def do_do(vang: np.ndarray, doan: np.ndarray) -> Tuple[float, float]:
    """(macro-F1, accuracy) của một lần chạy, cùng cách tính với compare_baselines."""
    o = np.bincount(vang * cb.SO_LOP + doan, minlength=cb.SO_LOP ** 2).astype(np.float64)
    f, a = cb.do_do(o)
    return float(f), float(a)


def nap_du_doan(goc: Path, exp: str, test: Sequence[Dong]) -> DuDoan:
    """Dự đoán của mọi seed, theo đúng thứ tự dòng của tập kiểm tra. Dừng nếu lệch uid hay nhãn thật."""
    uid_test = [r["uid"] for r in test]
    nhan = np.array([int(r["label"]) for r in test])  # type: ignore[arg-type]
    ra: DuDoan = []
    for s in cb.SEEDS:
        p = goc / exp / f"seed{s}" / "predictions.jsonl"
        uid, vang, doan = cb.doc_du_doan(p)
        if uid != uid_test or not np.array_equal(vang, nhan):
            raise ValueError(f"{p} không cùng thứ tự uid hoặc nhãn thật với tập kiểm tra")
        ra.append((vang, doan))
    return ra


def _tb(x: Sequence[float]) -> float:
    return float(np.mean(x))


# --- P1 -----------------------------------------------------------------------

def p1_tap_chan_doan(chan_doan: Sequence[Dong], test: Sequence[Dong], du_doan: DuDoan) -> Dict[str, dict]:
    """Mỗi nhóm hiện tượng: lỗi mỗi seed, phần ngược cực, phần nhãn gốc trung tính mà đoán có cực, phần ở dòng người
    chú thích không đồng ý nhãn gốc, macro-F1 của nhóm trước và sau khi luật lý tưởng lật mọi lỗi ngược cực."""
    vi_tri = {r["uid"]: i for i, r in enumerate(test)}
    ra: Dict[str, dict] = {}
    for g in NHOM:
        dong = [r for r in chan_doan if r["phenomenon"] == g]
        for r in dong:
            if r["uid"] not in vi_tri or int(test[vi_tri[r["uid"]]]["label"]) != int(r["label"]):  # type: ignore[arg-type]
                raise ValueError(f"{r['uid']}: không có trong tập kiểm tra hoặc khác nhãn gốc")
        chi_so = np.array([vi_tri[r["uid"]] for r in dong], dtype=int)
        dong_y = np.array([r["nhan_kiem_tra"] == "dong_y" for r in dong], dtype=bool)
        loi, nc, tt, kdy, f0, f1 = [], [], [], [], [], []
        for vang, doan in du_doan:
            v, d = vang[chi_so], doan[chi_so]
            sai, m = v != d, nguoc_cuc(v, d)
            loi.append(sai.sum())
            nc.append(m.sum())
            tt.append((sai & (v == 1)).sum())
            kdy.append((sai & ~dong_y).sum())
            f0.append(do_do(v, d)[0])
            f1.append(do_do(v, sua_theo_mat_na(v, d, m))[0])
        ra[g] = {"n": len(dong), "loi": _tb(loi), "loi_nguoc_cuc": _tb(nc), "loi_goc_trung_tinh": _tb(tt),
                 "loi_o_dong_khong_dong_y": _tb(kdy), "macro_f1": _tb(f0), "macro_f1_sau_khi_lat": _tb(f1), "tang": _tb(f1) - _tb(f0)}
    return ra


def p1_toan_tap(test: Sequence[Dong], du_doan: DuDoan) -> Dict[str, object]:
    """Ba cận trên trên toàn tập kiểm tra: luật lý tưởng sửa lỗi trong từng phạm vi, đo macro-F1 tăng bao nhiêu."""
    tk = [bd.tim_tu_khoa(r["tokens"]) for r in test]  # type: ignore[arg-type]
    co_pd = np.array([bool(pd) for pd, _, _ in tk])
    co_cy = np.array([bool(cy) for _, cy, _ in tk])
    pham_vi: Dict[str, Callable[[np.ndarray, np.ndarray], np.ndarray]] = {
        "nguoc_cuc_o_cau_co_phu_dinh": lambda v, d: nguoc_cuc(v, d) & co_pd,
        "nguoc_cuc_moi_cho": nguoc_cuc,
        "moi_loi_o_cau_co_tu_khoa": lambda v, d: (v != d) & (co_pd | co_cy),
    }
    goc = [do_do(v, d) for v, d in du_doan]
    ra: Dict[str, object] = {
        "n": len(test), "mau_o_cau_co_phu_dinh": int(co_pd.sum()), "mau_o_cau_co_tu_khoa": int((co_pd | co_cy).sum()),
        "loi": _tb([(v != d).sum() for v, d in du_doan]), "loi_nguoc_cuc": _tb([nguoc_cuc(v, d).sum() for v, d in du_doan]),
        "macro_f1": _tb([f for f, _ in goc]), "accuracy": _tb([a for _, a in goc]),
    }
    for ten, ham in pham_vi.items():
        sua, df, da = [], [], []
        for (v, d), (f0, a0) in zip(du_doan, goc):
            m = ham(v, d)
            f1, a1 = do_do(v, sua_theo_mat_na(v, d, m))
            sua.append(m.sum())
            df.append(f1 - f0)
            da.append(a1 - a0)
        ra[ten] = {"so_loi_sua": _tb(sua), "tang_macro_f1": _tb(df), "tang_accuracy": _tb(da)}
    return ra


# --- P2 -----------------------------------------------------------------------

def o_cua(r: Dong) -> Optional[Tuple[str, int]]:
    """(nhóm từ khoá, nhãn gốc) nếu mẫu thuộc quần thể ước lượng: câu 5 đến 40 từ, không chỉ chứa từ ngờ."""
    tokens = r["tokens"]
    g = bd.xep_nhom(*bd.tim_tu_khoa(tokens))  # type: ignore[arg-type]
    if g is None or bd._ngoai_bao_xa(len(tokens), bd.DO_DAI_MAC_DINH):  # type: ignore[arg-type]
        return None
    return g, int(r["label"])  # type: ignore[arg-type]


def p2_luat_tho(chan_doan: Sequence[Dong], test: Sequence[Dong], so_lan: int, rng: np.random.Generator) -> Dict[str, object]:
    """Độ chính xác và độ phủ của luật từ khoá, ước lượng theo ô cho quần thể của tập kiểm tra."""
    so_mau = Counter(o for o in map(o_cua, test) if o is not None)
    hien_tuong: Dict[Tuple[str, int], List[str]] = defaultdict(list)
    ngoai = 0
    for r in chan_doan:
        o = o_cua(r)
        if o is None:
            ngoai += 1
        else:
            hien_tuong[o].append(str(r["phenomenon"]))
    thieu = sorted(o for o in so_mau if o not in hien_tuong)
    if thieu:
        raise ValueError(f"Không ước lượng được: các ô {thieu} không có dòng nào trong tập chẩn đoán")
    o_ds = sorted(so_mau)
    N = np.array([so_mau[o] for o in o_ds], dtype=np.float64)
    n = np.array([len(hien_tuong[o]) for o in o_ds])
    chi_ngo = sum(bd.xep_nhom(*bd.tim_tu_khoa(r["tokens"])) is None for r in test)  # type: ignore[arg-type]
    ra: Dict[str, object] = {"quan_the": int(N.sum()), "mau_cau_chi_co_tu_ngo": int(chi_ngo),
                             "mau_ngoai_do_dai": len(test) - int(N.sum()) - int(chi_ngo),
                             "dong_dung_de_uoc_luong": int(n.sum()), "dong_ngoai_quan_the": ngoai}
    for luat in ("phu_dinh", "chuyen_y"):
        bat = np.array([o[0] in LUAT_BAT[luat] for o in o_ds])
        trung = np.array([sum(h in CO_HIEN_TUONG[luat] for h in hien_tuong[o]) for o in o_ds])

        def uoc(p: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
            co = p * N  # số mẫu có hiện tượng ước lượng cho từng ô
            dung = co[..., bat].sum(axis=-1)
            with np.errstate(invalid="ignore", divide="ignore"):  # luật không bắt ô nào: nan, không phải lỗi
                return dung / N[bat].sum(), dung / co.sum(axis=-1)

        cx, dp = uoc(trung / n)
        cx_b, dp_b = uoc(rng.binomial(n, trung / n, size=(so_lan, len(o_ds))) / n)
        # Dòng có hiện tượng mà luật bỏ sót, đếm trên cả tập chẩn đoán: bao nhiêu dòng có từ ngờ ("mà", "còn"...).
        bo_sot = [bd.tim_tu_khoa(r["tokens"]) for r in chan_doan if r["phenomenon"] in CO_HIEN_TUONG[luat]]  # type: ignore[arg-type]
        bo_sot = [ngo for pd, cy, ngo in bo_sot if not (pd if luat == "phu_dinh" else cy)]
        ra[luat] = {
            "bo_sot_tren_tap_chan_doan": {"dong": len(bo_sot), "co_tu_ngo": sum(bool(x) for x in bo_sot)},
            "do_chinh_xac": float(cx), "do_chinh_xac_ci95": [float(np.percentile(cx_b, 2.5)), float(np.percentile(cx_b, 97.5))],
            "do_phu": float(dp), "do_phu_ci95": [float(np.percentile(dp_b, 2.5)), float(np.percentile(dp_b, 97.5))],
            "mau_luat_bat_tren_tap_kiem_tra": int(N[bat].sum()),
            "tho": {"dong_luat_bat": int(n[bat].sum()), "dong_luat_bat_dung": int(trung[bat].sum()),
                    "dong_co_hien_tuong": int(trung.sum())},
        }
    return ra


# --- P3 -----------------------------------------------------------------------

def to_tien(heads: Sequence[int], i: int) -> List[int]:
    """i và các tổ tiên của nó tới gốc (head -1). Dừng nếu head ngoài khoảng hoặc có vòng."""
    ds = [i]
    while heads[i] != -1:
        i = heads[i]
        if not 0 <= i < len(heads) or len(ds) > len(heads):
            raise ValueError(f"Cây cú pháp hỏng: head ngoài khoảng hoặc có vòng ở token {ds[0]}")
        ds.append(i)
    return ds


def khoang_cach_cay(heads: Sequence[int], a: int, b: int) -> Optional[int]:
    """Số cạnh trên đường đi giữa hai token; None nếu chúng thuộc hai câu (hai cây) khác nhau."""
    ta = {x: k for k, x in enumerate(to_tien(heads, a))}
    for k, y in enumerate(to_tien(heads, b)):
        if y in ta:
            return ta[y] + k
    return None


def p3_cu_phap(test: Sequence[Dong]) -> Dict[str, object]:
    """Mỗi dạng từ phủ định: số lượt, phần có từ đứng sau trong cùng câu, và với phần đó: tỉ lệ gán nhãn phó từ,
    tỉ lệ kề nhau trên cây, khoảng cách trên cây tới từ đứng sau."""
    cau: Dict[str, Dong] = {}
    for r in test:
        cau.setdefault(bd.ma_cau(str(r["uid"])), r)
    dem = {d: Counter() for d in TEN_DANG}
    kc: Dict[str, List[int]] = {d: [] for d in TEN_DANG}
    for r in cau.values():
        tok, pos, heads = r["tokens"], r["pos"], r["heads"]
        for i, t in enumerate(tok):  # type: ignore[arg-type]
            t = t.lower()
            if t not in bd.PHU_DINH:
                continue
            dang = "viet_tat" if t in bd.PHU_DINH_VIET_TAT else "chuan"
            dem[dang]["luot"] += 1
            if i + 1 >= len(tok) or pos[i + 1] == DAU_CAU:  # type: ignore[index, arg-type]
                continue
            k = khoang_cach_cay(heads, i, i + 1)  # type: ignore[arg-type]
            if k is None:
                continue
            dem[dang]["co_tu_sau"] += 1
            dem[dang]["pho_tu"] += pos[i] == PHO_TU  # type: ignore[index]
            kc[dang].append(k)
    ra: Dict[str, object] = {"so_cau": len(cau)}
    for d in TEN_DANG:
        k = np.array(kc[d])
        m = max(len(k), 1)
        ra[d] = {"luot": dem[d]["luot"], "co_tu_sau": dem[d]["co_tu_sau"], "ti_le_pho_tu": dem[d]["pho_tu"] / m,
                 "ti_le_ke_nhau": float((k == 1).sum()) / m, "ti_le_tu_3_canh": float((k >= 3).sum()) / m,
                 "khoang_cach_tb": float(k.mean()) if len(k) else 0.0, "khoang_cach_trung_vi": float(np.median(k)) if len(k) else 0.0}
    return ra


# --- Bảng ---------------------------------------------------------------------

def _pt(x: float, chu_so: int = 1) -> str:
    return f"{x * 100:.{chu_so}f}".replace(".", ",")


def _s(x: float, chu_so: int = 1) -> str:
    return f"{x:.{chu_so}f}".replace(".", ",")


def bang(kq: Dict[str, object]) -> str:
    ten = cb.TEN_HIEN_THI.get(str(kq["mo_hinh"]), str(kq["mo_hinh"]))
    seeds = ", ".join(map(str, kq["seeds"]))  # type: ignore[arg-type]
    p1c, p1t, p2, p3 = kq["p1"]["tap_chan_doan"], kq["p1"]["toan_tap_kiem_tra"], kq["p2"], kq["p3"]  # type: ignore[index]
    d = [f"Sinh bởi scripts/probe_oracle_rules.py. Mô hình: {ten}, trung bình {len(kq['seeds'])} seed ({seeds}).", ""]  # type: ignore[arg-type]
    d += ["Bảng P1a. Luật lật cực lý tưởng trên tập chẩn đoán: phạm vi là các dòng người chú thích gán nhóm đó. "
          "Số lỗi là trung bình mỗi seed; macro-F1 tính trong nhóm (%).", "",
          "| Nhóm | Số dòng | Lỗi | Lỗi ngược cực | Lỗi có nhãn gốc trung tính | Lỗi ở dòng không đồng ý nhãn gốc | Macro-F1 | Sau khi lật | Tăng (điểm) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for g in NHOM:
        x = p1c[g]
        d.append(f"| {TEN_NHOM[g]} | {x['n']} | {_s(x['loi'])} | {_s(x['loi_nguoc_cuc'])} | {_s(x['loi_goc_trung_tinh'])} | "
                 f"{_s(x['loi_o_dong_khong_dong_y'])} | {_pt(x['macro_f1'])} | {_pt(x['macro_f1_sau_khi_lat'])} | {_pt(x['tang'], 2)} |")
    d += ["", f"Bảng P1b. Cận trên trên toàn tập kiểm tra ({p1t['n']} mẫu; macro-F1 {_pt(p1t['macro_f1'], 2)} %, "
          f"{_s(p1t['loi'])} lỗi mỗi seed, trong đó {_s(p1t['loi_nguoc_cuc'])} lỗi ngược cực). "
          f"{p1t['mau_o_cau_co_phu_dinh']} mẫu thuộc câu có từ khoá phủ định, {p1t['mau_o_cau_co_tu_khoa']} mẫu thuộc câu có "
          "từ khoá phủ định hoặc chuyển ý.", "",
          "| Luật lý tưởng sửa | Số lỗi sửa mỗi seed | Macro-F1 tăng (điểm) | Accuracy tăng (điểm) |", "|---|---|---|---|"]
    for k, nhan in (("nguoc_cuc_o_cau_co_phu_dinh", "Lỗi ngược cực ở câu có từ khoá phủ định"),
                    ("nguoc_cuc_moi_cho", "Lỗi ngược cực ở mọi chỗ"),
                    ("moi_loi_o_cau_co_tu_khoa", "Mọi lỗi ở câu có từ khoá phủ định hoặc chuyển ý")):
        x = p1t[k]
        d.append(f"| {nhan} | {_s(x['so_loi_sua'])} | {_pt(x['tang_macro_f1'], 2)} | {_pt(x['tang_accuracy'], 2)} |")
    d += ["", f"Bảng P2. Luật từ khoá so với nhãn hiện tượng của người chú thích. Ước lượng theo ô (nhóm từ khoá, nhãn gốc) "
          f"cho {p2['quan_the']} mẫu của tập kiểm tra thuộc câu 5 đến 40 từ và không chỉ chứa từ ngờ "
          f"(ngoài quần thể: {p2['mau_ngoai_do_dai']} mẫu ở câu ngoài độ dài, {p2['mau_cau_chi_co_tu_ngo']} mẫu ở câu chỉ có từ ngờ). "
          f"Dùng {p2['dong_dung_de_uoc_luong']} dòng của tập chẩn đoán ({p2['dong_ngoai_quan_the']} dòng ngoài quần thể). "
          "Khoảng tin cậy 95 % bằng bootstrap trong từng ô.", "",
          "Hai cột cuối đếm trên cả tập chẩn đoán: dòng có hiện tượng mà câu không có từ khoá của luật, và trong đó bao "
          "nhiêu dòng có từ ngờ.", "",
          "| Luật | Độ chính xác (%) | KTC 95 % | Độ phủ (%) | KTC 95 % | Dòng luật bắt | Trong đó đúng | Dòng bị bỏ sót | Có từ ngờ |",
          "|---|---|---|---|---|---|---|---|---|"]
    for luat in ("phu_dinh", "chuyen_y"):
        x = p2[luat]
        d.append(f"| {TEN_LUAT[luat]} | {_pt(x['do_chinh_xac'])} | {_pt(x['do_chinh_xac_ci95'][0])} – {_pt(x['do_chinh_xac_ci95'][1])} | "
                 f"{_pt(x['do_phu'])} | {_pt(x['do_phu_ci95'][0])} – {_pt(x['do_phu_ci95'][1])} | "
                 f"{x['tho']['dong_luat_bat']} | {x['tho']['dong_luat_bat_dung']} | "
                 f"{x['bo_sot_tren_tap_chan_doan']['dong']} | {x['bo_sot_tren_tap_chan_doan']['co_tu_ngo']} |")
    d += ["", f"Bảng P3. Từ khoá phủ định và từ đứng ngay sau nó trên cây VnCoreNLP, {p3['so_cau']} câu của tập kiểm tra. "
          "Ba cột tỉ lệ và khoảng cách tính trên các lượt có từ đứng sau thuộc cùng câu; khoảng cách tuyến tính luôn là 1.", "",
          "| Dạng | Lượt | Có từ đứng sau | Gán nhãn phó từ (%) | Kề nhau trên cây (%) | Cách từ 3 cạnh (%) | Khoảng cách trên cây trung bình |",
          "|---|---|---|---|---|---|---|"]
    for dang, nhan in TEN_DANG.items():
        x = p3[dang]
        d.append(f"| {nhan} | {x['luot']} | {x['co_tu_sau']} | {_pt(x['ti_le_pho_tu'])} | {_pt(x['ti_le_ke_nhau'])} | "
                 f"{_pt(x['ti_le_tu_3_canh'])} | {_s(x['khoang_cach_tb'], 2)} |")
    return "\n".join(d) + "\n"


def tham_do(results: Path, test_jsonl: Path, chan_doan_jsonl: Path, mo_hinh: str, so_lan: int, seed: int) -> Dict[str, object]:
    test = doc_jsonl(test_jsonl)
    chan_doan = doc_jsonl(chan_doan_jsonl)
    du_doan = nap_du_doan(results, mo_hinh, test)
    rng = np.random.default_rng(seed)
    return {"mo_hinh": mo_hinh, "seeds": list(cb.SEEDS), "so_lan": so_lan, "seed": seed,
            "p1": {"tap_chan_doan": p1_tap_chan_doan(chan_doan, test, du_doan), "toan_tap_kiem_tra": p1_toan_tap(test, du_doan)},
            "p2": p2_luat_tho(chan_doan, test, so_lan, rng), "p3": p3_cu_phap(test)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Ba phép thăm dò trần cải tiến (P1, P2, P3) từ dự đoán và nhãn đã có.")
    ap.add_argument("--results", type=Path, default=Path("results"))
    ap.add_argument("--test", type=Path, default=bd.DEFAULT_TEST)
    ap.add_argument("--chan-doan", type=Path, default=Path("data/diagnostic/diagnostic_300.jsonl"))
    ap.add_argument("--mo-hinh", default=MO_HINH_MAC_DINH, help="thí nghiệm dùng cho P1 (mặc định phobert)")
    ap.add_argument("--so-lan", type=int, default=10_000, help="số lần lấy mẫu bootstrap cho P2 (mặc định 10000)")
    ap.add_argument("--seed", type=int, default=20261018, help="hạt giống của bộ sinh số ngẫu nhiên")
    ap.add_argument("--out-json", type=Path, default=Path("results/probe_results.json"))
    ap.add_argument("--out-md", type=Path, default=Path("chuyende1/tables/bang_5_tham_do.md"))
    ap.add_argument("--chi-in", action="store_true", help="chỉ in bảng, không ghi file")
    a = ap.parse_args(argv)

    kq = tham_do(a.results, a.test, a.chan_doan, a.mo_hinh, a.so_lan, a.seed)
    b = bang(kq)
    print(b)
    if not a.chi_in:
        a.out_json.write_text(json.dumps(kq, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        a.out_md.write_text(b, encoding="utf-8")
        print(f"Đã ghi {a.out_json} và {a.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
