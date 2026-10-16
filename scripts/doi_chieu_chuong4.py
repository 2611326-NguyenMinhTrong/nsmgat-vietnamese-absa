"""[CD1.12b] Đối chiếu số liệu của Chương 4 với dữ liệu và file kết quả.

Tính lại từng con số từ data/processed/, results/<exp>/seed<N>/ và các file thống kê, dựng lại
đúng dòng bảng hoặc cụm chữ mà chương phải có, rồi tìm trong bản nháp. In ra những chỗ KHÔNG
tìm thấy. Không sửa gì trong bản nháp.

    python scripts/doi_chieu_chuong4.py                 # kiểm bản chính (bản rút gọn): Chương 4, Phụ lục và phần tóm tắt
    python scripts/doi_chieu_chuong4.py --ban day_du    # kiểm bản đầy đủ (bản lưu)
    python scripts/doi_chieu_chuong4.py --in-bang       # in thêm các bảng tính lại, để chép khi cần
    python scripts/doi_chieu_chuong4.py --do-cat        # đo thêm tỉ lệ mẫu bị cắt ở 128 subword (cần bộ tách từ PhoBERT)
    python scripts/doi_chieu_chuong4.py --do-mau-so     # đo thêm mẫu số chuẩn hoá không dương của Sentic-GCN ở mục 4.3 (cần torch)

Mã thoát 0 khi mọi con số đều khớp, 1 khi có chỗ lệch.

HAI BẢN CỦA BÁO CÁO
-------------------
Từ 13/10/2026 bản chính là bản rút gọn. Nó chia nội dung của Chương 4 ra hai file (Chuong4_ThucNghiem.md
và PhuLuc.md), đánh số bảng lại và viết lại một số câu. Trong mã, mỗi bảng được gọi bằng số của bản đầy
đủ ("Bảng 4.5"); SO_BANG_RUT_GON đổi sang số của bản chính khi tìm và khi in. Câu nào hai bản viết khác
nhau thì có hai cụm chữ, chọn bằng theo_ban(). Câu chỉ có ở một bản thì bản kia bỏ qua.

CÁCH TÌM
--------
- Hàng của bảng: phải nằm trong ĐÚNG bảng mang số đó, và tên của bảng đó phải chứa từ khoá ở
  TU_KHOA_BANG. Một hàng đúng số nhưng nằm dưới bảng khác thì bị báo lệch.
- Cụm chữ của lời văn: tìm trong toàn bộ các file của bản.
- Câu định tính (hàm neu): chỉ được có trong báo cáo khi số liệu còn đỡ được câu đó.

Phạm vi: các bảng số liệu của Chương 4 (mười bốn bảng, kể cả bảng đã chuyển sang Phụ lục C) và các con
số trong lời văn suy ra từ chúng; số tham số ở bảng thang mô hình; độ phủ của từ điển và tỉ lệ đồ thị bị
chia cắt ở mục 4.3; ở bản chính, mô tả mốc GPT-4o ở mục 4.3 (từ configs/llm.yaml và danh sách mẫu của tập con)
và cách đo chi phí suy luận ở mục 4.5 (từ results/cost_profile.json, chưa có file thì từ giá trị mặc định của
scripts/profile_cost.py). Các con số lấy từ bài báo khác không thuộc phạm vi của công cụ này, và các con số về
từ khoá phủ định ở cuối mục 4.1.2 chưa có chỗ kiểm.

Phần tập chẩn đoán (mục 4.1.2 và 4.6) cần ba file chỉ có trên máy học viên:
data/diagnostic/candidates.csv, data/diagnostic/kappa.json và results/diagnostic_eval.json. Thiếu một
trong ba thì phần này được bỏ qua và công cụ in rõ là đã bỏ qua. Thành phần tập và giá trị điểm của
accuracy, macro-F1 được tính lại từ predictions.jsonl; khoảng tin cậy và p lấy từ diagnostic_eval.json.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).parent))

import compare_baselines as cb  # noqa: E402

for _luong in (sys.stdout, sys.stderr):
    if hasattr(_luong, "reconfigure"):
        _luong.reconfigure(encoding="utf-8", errors="replace")

# Các file của từng bản. Bản chính (rut_gon) là mặc định từ 13/10/2026.
TEP_THEO_BAN = {
    "rut_gon": (Path("chuyende1/report/nhap_rut_gon/Chuong4_ThucNghiem.md"), Path("chuyende1/report/nhap_rut_gon/PhuLuc.md")),
    "day_du": (Path("chuyende1/report/nhap/Chuong4_ThucNghiem.md"),),
}
TEP_TRANG_DAU = Path("chuyende1/report/nhap_rut_gon/TrangDau.md")
TIEU_DE_TOM_TAT = "TÓM TẮT"
DAU_TOM_TAT = "Tóm tắt, "  # mô tả của các chỗ kiểm chỉ tìm trong phần tóm tắt
# Số bảng của bản đầy đủ -> số bảng của bản chính.
SO_BANG_RUT_GON = {"4.1": "4.1", "4.2": "C.1", "4.4": "4.2", "4.5": "4.3", "4.6": "4.4", "4.7": "C.3", "4.8": "4.5",
                   "4.9": "4.6", "4.10": "4.7", "4.11": "4.8", "4.12": "C.4", "4.13": "4.9", "4.14": "C.5",
                   "4.15": "C.6", "4.16": "C.7"}
# Tên bảng phải chứa cụm này: bắt trường hợp hai bảng cùng dạng hàng bị đổi chỗ cho nhau.
TU_KHOA_BANG = {
    "4.1": "Quy mô và phân bố nhãn", "4.2": "Phân bố mẫu theo khía cạnh và nhãn", "4.4": "Thang mô hình",
    "4.5": "Kết quả trên tập kiểm tra", "4.6": "Kiểm định bootstrap ghép cặp", "4.7": "Macro-F1 từng",
    "4.8": "Hành vi trên lớp trung tính", "4.9": "Số tham số và thời gian huấn luyện",
    "4.10": "Thành phần của tập chẩn đoán", "4.11": "Accuracy trên bốn nhóm", "4.12": "Macro-F1 trên bốn nhóm",
    "4.13": "Hiệu số so với nhóm thường", "4.14": "Accuracy theo từng dấu hiệu",
    "4.15": "Hiệu số accuracy so với PhoBERT", "4.16": "mà người chú thích đồng ý với nhãn gốc",
}
MAU_MO_TA_BANG = re.compile(r"^Bảng (\d+\.\d+), ")
MAU_TEN_BANG = re.compile(r"^Bảng ((?:\d+|[A-Z])\.\d+): (.*)$")
MAU_SO = re.compile(r"\d[\d.,]*\d|\d")
MO_HINH = ("lexicon", "bilstm", "phobert", "asgcn", "asgcn_linked", "senticgcn")
TEN = cb.TEN_HIEN_THI
KHIA_CANH = ("GENERAL", "PERFORMANCE", "BATTERY", "FEATURES", "SER&ACC", "CAMERA", "PRICE", "DESIGN", "SCREEN", "STORAGE")
# Số bình luận gốc của từng phần, đếm trên file của tác giả (Train.csv, Dev.csv, Test.csv). Không suy được từ
# data/processed vì bình luận chỉ có nhãn OTHERS không sinh mẫu.
BINH_LUAN_GOC = {"train": 7786, "dev": 1112, "test": 2224}


def nghin(n: float) -> str:
    return f"{int(round(n)):,}".replace(",", ".")


def tp(x: float, chu_so: int = 2) -> str:
    return f"{x:.{chu_so}f}".replace(".", ",")


def doc_jsonl(p: Path) -> List[dict]:
    with p.open(encoding="utf-8") as fh:
        return [json.loads(d) for d in fh]


def ma_cau(uid: str) -> str:
    return uid.rsplit("-", 1)[0]


def so_lieu_du_lieu(goc: Path) -> Tuple[List[Tuple[str, str]], dict]:
    """Bảng 4.1, 4.2 và các con số về câu nhiều khía cạnh. Trả về (danh sách (mô tả, chuỗi phải có), số thô)."""
    kiem: List[Tuple[str, str]] = []
    tap = {sp: doc_jsonl(goc / f"data/processed/visfd_{sp}.jsonl") for sp in ("train", "dev", "test")}
    cau = {sp: len({ma_cau(r["uid"]) for r in rows}) for sp, rows in tap.items()}
    nhan = {sp: Counter(int(r["label"]) for r in rows) for sp, rows in tap.items()}
    sp3 = ("train", "dev", "test")
    kiem.append(("Bảng 4.1, số bình luận gốc",
                 "| Số bình luận gốc | " + " | ".join(nghin(BINH_LUAN_GOC[s]) for s in sp3) + f" | {nghin(sum(BINH_LUAN_GOC.values()))} |"))
    kiem.append(("Bảng 4.1, số bình luận sinh mẫu",
                 "| Số bình luận sinh ra ít nhất một mẫu | " + " | ".join(nghin(cau[s]) for s in sp3) + f" | {nghin(sum(cau.values()))} |"))
    kiem.append(("Bảng 4.1, số mẫu", "| Số mẫu | " + " | ".join(nghin(len(tap[s])) for s in sp3) + f" | {nghin(sum(len(v) for v in tap.values()))} |"))
    kiem.append(("Bảng 4.1, khía cạnh trung bình",
                 "| Số khía cạnh trung bình mỗi bình luận | " + " | ".join(tp(len(tap[s]) / cau[s]) for s in sp3) + " | |"))
    for i, ten in enumerate(("Tiêu cực", "Trung tính", "Tích cực")):
        kiem.append((f"Bảng 4.1, lớp {ten}", f"| {ten} | " + " | ".join(
            f"{nghin(nhan[s][i])} ({tp(nhan[s][i] / len(tap[s]) * 100)} %)" for s in sp3) + f" | {nghin(sum(nhan[s][i] for s in sp3))} |"))

    test = tap["test"]
    bang = defaultdict(Counter)
    for r in test:
        bang[r["aspect"]][int(r["label"])] += 1
    assert set(bang) == set(KHIA_CANH), sorted(bang)
    for a in KHIA_CANH:
        c = bang[a]
        kiem.append((f"Bảng 4.2, {a}", f"| {a} | {nghin(c[0])} | {nghin(c[1])} | {nghin(c[2])} | {nghin(sum(c.values()))} |"))
    kiem.append(("Bảng 4.2, tổng", f"| Tổng | {nghin(nhan['test'][0])} | {nghin(nhan['test'][1])} | {nghin(nhan['test'][2])} | {nghin(len(test))} |"))

    theo_cau = defaultdict(list)
    for r in test:
        theo_cau[ma_cau(r["uid"])].append(int(r["label"]))
    da = sum(len(v) >= 2 for v in theo_cau.values())
    trai = sum(len(set(v)) >= 2 for v in theo_cau.values())
    tran = sum(max(Counter(v).values()) for v in theo_cau.values()) / len(test)
    n_cau = len(theo_cau)
    kiem += [
        ("Lời văn, câu nhiều khía cạnh", f"{nghin(da)} trong {nghin(n_cau)} bình luận, tức {tp(da / n_cau * 100, 1)} %"),
        ("Lời văn, câu trái nhãn", f"{nghin(trai)} bình luận, tức {tp(trai / n_cau * 100, 1)} %"),
        ("Lời văn, trần mù khía cạnh", f"{tp(tran * 100)} %"),
        ("Lời văn, trung tính ở PRICE", f"{nghin(bang['PRICE'][1])} trong {nghin(nhan['test'][1])} mẫu trung tính của tập kiểm tra, tức {tp(bang['PRICE'][1] / nhan['test'][1] * 100, 1)} %"),
        ("Lời văn, luôn đoán tích cực", f"accuracy {tp(nhan['test'][2] / len(test) * 100)} %"),
    ]
    return kiem, {"so_mau_test": len(test), "so_cau_test": n_cau, "tran": tran, "trung_tinh_test": nhan["test"][1]}


def neu(dung_khong: bool, cau: str, mo_ta: str) -> Tuple[str, str]:
    """Câu định tính: chỉ đòi có trong chương khi số liệu còn đúng như vậy."""
    return (mo_ta, cau if dung_khong else f"SỐ LIỆU KHÔNG CÒN ĐỠ CÂU: {cau}")


def p_loi(p: float) -> str:
    """Giá trị p viết trong lời văn: 'p bằng 0,205' hoặc 'p nhỏ hơn 0,001'."""
    return "p nhỏ hơn 0,001" if p < 0.001 else f"p bằng {cb.p_chu(p)}"


def so_lieu_ket_qua(goc: Path, tho: dict, ban: str = "rut_gon") -> Tuple[List[Tuple[str, Optional[str]]], Dict[str, str]]:
    """Bảng 4.4 đến 4.9 (số của bản đầy đủ) và các con số của mục 4.4, 4.5, 4.7 trong lời văn."""
    kiem: List[Tuple[str, Optional[str]]] = []
    bang: Dict[str, List[str]] = defaultdict(list)
    m = {e: [json.loads((goc / f"results/{e}/seed{s}/metrics.json").read_text(encoding="utf-8")) for s in cb.SEEDS] for e in MO_HINH}

    def tb_lech(e: str, lay) -> Tuple[float, float]:
        v = [lay(x) * 100 for x in m[e]]
        return st.mean(v), st.stdev(v)

    def o(e: str, lay) -> str:
        a, b = tb_lech(e, lay)
        return f"{tp(a)} ± {tp(b)}"

    acc = {e: tb_lech(e, lambda x: x["test"]["accuracy"]) for e in MO_HINH}
    f1 = {e: tb_lech(e, lambda x: x["test"]["macro_f1"]) for e in MO_HINH}
    for e in MO_HINH:
        dong = (f"| {TEN[e]} | {o(e, lambda x: x['test']['accuracy'])} | {o(e, lambda x: x['test']['macro_f1'])} | "
                + " | ".join(o(e, lambda x, i=i: x["test"]["f1_per_class"][i]) for i in range(3)) + " |")
        kiem.append((f"Bảng 4.5, {e}", dong))
        bang["4.5"].append(dong)
    for e in ("phobert", "asgcn", "asgcn_linked", "senticgcn"):
        dong = f"| {TEN[e]} | " + " | ".join(tp(x["test"]["macro_f1"] * 100) for x in m[e]) + " |"
        kiem.append((f"Bảng 4.7, {e}", dong))
        bang["4.7"].append(dong)

    # Bảng 4.8: hành vi trên lớp trung tính, từ predictions.jsonl
    loi_tb, so_doan_tt, pre_tt, rec_tt = {}, {}, {}, {}
    for e in MO_HINH:
        doan_tt, dung_tt, loi = [], [], []
        for s in cb.SEEDS:
            _, vang, doan = cb.doc_du_doan(goc / f"results/{e}/seed{s}/predictions.jsonl")
            doan_tt.append(int((doan == 1).sum()))
            dung_tt.append(int(((doan == 1) & (vang == 1)).sum()))
            loi.append(int((doan != vang).sum()))
        n_tt = tho["trung_tinh_test"]
        p = st.mean(d / n * 100 for d, n in zip(dung_tt, doan_tt)) if all(doan_tt) else None
        r = st.mean(d / n_tt * 100 for d in dung_tt)
        loi_tb[e] = st.mean(loi)
        so_doan_tt[e], pre_tt[e], rec_tt[e] = doan_tt, p, r
        so_doan = nghin(st.mean(doan_tt)) if not any(doan_tt) else tp(st.mean(doan_tt), 1)
        dong = f"| {TEN[e]} | {so_doan} | {'' if p is None else tp(p)} | {tp(r)} | {tp(loi_tb[e], 1) if loi_tb[e] < 1000 else nghin(int(loi_tb[e])) + ',' + str(round(loi_tb[e] % 1 * 10))} |"
        kiem.append((f"Bảng 4.8, {e}", dong))
        bang["4.8"].append(dong)

    for bac, e in zip(("1", "2", "3", "4", "4b", "5"), MO_HINH):
        ts = {x["n_params"] for x in m[e]}
        assert len(ts) == 1, (e, ts)
        so_ts = nghin(ts.pop())
        phut = st.mean(x["train_time_sec"] for x in m[e]) / 60
        kiem.append((f"Bảng 4.9, {e}", f"| {TEN[e]} | {so_ts} | {tp(phut, 1)} |"))
        bang["4.9"].append(kiem[-1][1])
        tho.setdefault("tham_so", {})[bac] = so_ts  # cho kiem_thang_mo_hinh

    kq = json.loads((goc / "results/compare_baselines.json").read_text(encoding="utf-8"))
    for r in kq["ket_qua"]:
        f, a = r["macro_f1"], r["accuracy"]
        dong = (f"| {TEN[r['a']]} | {TEN[r['b']]} | {cb.so(f['hieu_so'])} | {cb.so(f['ci95_duoi'])} đến {cb.so(f['ci95_tren'])} | {cb.p_chu(f['p'])} | "
                f"{cb.so(a['hieu_so'])} | {cb.so(a['ci95_duoi'])} đến {cb.so(a['ci95_tren'])} | {cb.p_chu(a['p'])} |")
        kiem.append((f"Bảng 4.6, {r['a']} trừ {r['b']}", dong))
        bang["4.6"].append(dong)

    def hieu(d: dict, a: str, b: str) -> float:
        return d[a][0] - d[b][0]

    f1s = {e: [x["test"]["macro_f1"] * 100 for x in m[e]] for e in MO_HINH}
    tt = {e: st.mean(x["test"]["f1_per_class"][1] * 100 for x in m[e]) for e in MO_HINH}
    ts = {e: m[e][0]["n_params"] for e in MO_HINH}
    kiem += [
        ("Lời văn, BiLSTM vượt trần", f"vượt trần đó {tp(acc['bilstm'][0] - tho['tran'] * 100)} điểm"),
        ("Lời văn, PhoBERT hơn BiLSTM", f"{tp(hieu(acc, 'phobert', 'bilstm'))} điểm accuracy và {tp(hieu(f1, 'phobert', 'bilstm'))} điểm macro-F1"),
        ("Lời văn, F1 trung tính tăng", f"F1 lớp trung tính tăng {tp(tt['phobert'] - tt['bilstm'])} điểm"),
        ("Lời văn, ASGCN kém PhoBERT", f"thấp hơn PhoBERT {tp(-hieu(acc, 'asgcn', 'phobert'))} điểm accuracy và {tp(-hieu(f1, 'asgcn', 'phobert'))} điểm macro-F1"),
        ("Lời văn, ASGCN từng seed", f"nhỉnh hơn PhoBERT {tp(f1s['asgcn'][0] - f1s['phobert'][0])} điểm, ở hai {theo_ban(ban, day_du='hạt giống', rut_gon='seed')} còn lại nó thấp hơn "
                                     f"{tp(f1s['phobert'][1] - f1s['asgcn'][1])} và {tp(f1s['phobert'][2] - f1s['asgcn'][2])} điểm"),
        ("Lời văn, nối gốc hơn ASGCN", f"cao hơn ASGCN {tp(hieu(f1, 'asgcn_linked', 'asgcn'))} điểm"),
        ("Lời văn, nối gốc lấy lại", f"khoảng {tp(hieu(f1, 'asgcn_linked', 'asgcn') / -hieu(f1, 'asgcn', 'phobert') * 100, 0)} %"),
        ("Lời văn, Sentic hơn ASGCN", theo_ban(
            ban,
            day_du=f"cao hơn ASGCN {tp(hieu(f1, 'senticgcn', 'asgcn'))} điểm và gần bằng PhoBERT, thấp hơn {tp(-hieu(f1, 'senticgcn', 'phobert'))} điểm",
            rut_gon=f"Sentic-GCN đạt macro-F1 {tp(f1['senticgcn'][0])} %, cao hơn ASGCN {tp(hieu(f1, 'senticgcn', 'asgcn'))} điểm và thấp hơn PhoBERT {tp(-hieu(f1, 'senticgcn', 'phobert'))} điểm")),
        ("Lời văn, Sentic accuracy", f"chỉ hơn ASGCN {tp(hieu(acc, 'senticgcn', 'asgcn'))} điểm và vẫn thấp hơn PhoBERT {tp(-hieu(acc, 'senticgcn', 'phobert'))} điểm"),
        ("Lời văn, Sentic từng seed", "âm " + tp(f1s["asgcn"][0] - f1s["senticgcn"][0]) + " điểm, dương " + tp(f1s["senticgcn"][1] - f1s["asgcn"][1])
         + " điểm và dương " + tp(f1s["senticgcn"][2] - f1s["asgcn"][2]) + " điểm"),
        ("Lời văn, Sentic sai nhiều hơn", f"nhiều hơn PhoBERT khoảng {tp(loi_tb['senticgcn'] - loi_tb['phobert'], 0)} mẫu"),
        ("Lời văn, tham số thêm", f"{nghin(ts['asgcn'] - ts['phobert'])} tham số so với PhoBERT, tức {tp((ts['asgcn'] - ts['phobert']) / ts['phobert'] * 100)} %"),
        ("Lời văn, F1 trung tính cao nhất", f"F1 cao nhất đạt được là {tp(max(tt.values()))} %"),
    ]
    if ban == "rut_gon":
        kiem += cau_cua_ban_chinh(m, acc, f1, f1s, tt, tho, loi_tb, so_doan_tt, pre_tt, rec_tt, kq)
    return kiem, {k: "\n".join(v) for k, v in bang.items()}


def cau_cua_ban_chinh(m, acc, f1, f1s, tt, tho, loi_tb, so_doan_tt, pre_tt, rec_tt, kq) -> List[Tuple[str, Optional[str]]]:
    """Các câu có số ở mục 4.4 và 4.7 của bản chính mà trước 13/10/2026 chưa có chỗ kiểm.

    Chỉ áp cho bản chính: bản đầy đủ là bản lưu, lời văn của nó không còn được dò theo.
    """
    hoc = [e for e in MO_HINH if e != "lexicon"]
    dung_phobert = ("phobert", "asgcn", "asgcn_linked", "senticgcn")
    cap = {(r["a"], r["b"]): r for r in kq["ket_qua"]}
    lop = {e: [st.mean(x["test"]["f1_per_class"][i] * 100 for x in m[e]) for i in range(3)] for e in MO_HINH}
    n_tt = tho["trung_tinh_test"]

    def hs(d: dict, a: str, b: str) -> float:
        return d[a][0] - d[b][0]

    def tung_seed(a: str, b: str) -> List[float]:
        return [x - y for x, y in zip(f1s[a], f1s[b])]

    def doi_dau(ds: List[float]) -> bool:
        return min(ds) < 0 < max(ds)

    tot = max(tt, key=tt.get)  # mô hình có F1 lớp trung tính cao nhất
    ng_pb, sg_ag, sg_pb = cap[("asgcn_linked", "phobert")], cap[("senticgcn", "asgcn")], cap[("senticgcn", "phobert")]
    nho_nhat_f1 = min(hoc, key=lambda e: f1[e][1])
    kho_nhat = all(lop[e][1] < min(lop[e][0], lop[e][2]) for e in MO_HINH)  # F1 lớp trung tính thấp nhất ở mọi mô hình
    return [
        ("4.4, mô hình từ điển", f"Mô hình từ điển đạt accuracy {tp(acc['lexicon'][0])} % nhưng macro-F1 chỉ {tp(f1['lexicon'][0])} %"),
        neu(not any(so_doan_tt["lexicon"]), "vì nó không đoán lớp trung tính một lần nào trong cả ba lần chạy", "4.4, mô hình từ điển không đoán trung tính"),
        neu(acc["lexicon"][0] < tho["tran"] * 100, f"Accuracy của nó nằm dưới trần {tp(tho['tran'] * 100)} % của mô hình mù khía cạnh", "4.4, mô hình từ điển dưới trần"),
        ("4.4, BiLSTM", f"BiLSTM đạt accuracy {tp(acc['bilstm'][0])} %, vượt trần đó {tp(acc['bilstm'][0] - tho['tran'] * 100)} điểm"),
        neu(all(hs(f1, "phobert", "bilstm") > abs(hs(f1, a, b)) for a, b in (("asgcn", "phobert"), ("senticgcn", "asgcn"))),
            "Tri thức tiền huấn luyện đem lại mức tăng lớn nhất trong các bậc có nhìn khía cạnh", "4.4, bậc tăng lớn nhất"),
        ("4.4, độ lệch chuẩn BiLSTM và PhoBERT", f"Độ lệch chuẩn của macro-F1 giảm từ {tp(f1['bilstm'][1])} xuống {tp(f1['phobert'][1])}"),
        ("4.4, F1 trung tính so với hai lớp còn lại", f"nhưng vẫn thấp hơn hai lớp còn lại hơn {math.floor(min(lop['phobert'][0], lop['phobert'][2]) - lop['phobert'][1])} điểm"),
        ("4.4, độ lệch chuẩn ASGCN", f"độ lệch chuẩn của macro-F1 tăng lên {tp(f1['asgcn'][1])}"),
        neu(doi_dau(tung_seed("asgcn", "phobert")), "Vì dấu của hiệu số đổi theo seed", "4.4, ASGCN đổi dấu theo seed"),
        ("4.4, nối gốc", f"Biến thể nối gốc đạt macro-F1 {tp(f1['asgcn_linked'][0])} %, cao hơn ASGCN {tp(hs(f1, 'asgcn_linked', 'asgcn'))} điểm"),
        ("4.4, độ lệch chuẩn nối gốc", f"độ lệch chuẩn giảm từ {tp(f1['asgcn'][1])} xuống {tp(f1['asgcn_linked'][1])}"),
        neu(tung_seed("asgcn_linked", "asgcn")[0] < 0 and all(x > 0 for x in tung_seed("asgcn_linked", "asgcn")[1:]),
            "Hiệu số này cũng đổi dấu ở seed 42", "4.4, nối gốc đổi dấu ở seed 42"),
        neu(ng_pb["macro_f1"]["p"] >= 0.05 and ng_pb["accuracy"]["p"] >= 0.05,
            f"biến thể nối gốc không khác biệt có ý nghĩa ở cả hai độ đo (p bằng {cb.p_chu(ng_pb['macro_f1']['p'])} và {cb.p_chu(ng_pb['accuracy']['p'])})",
            "4.4, nối gốc so với PhoBERT"),
        neu(sg_ag["macro_f1"]["p"] < 0.05 <= sg_ag["accuracy"]["p"] and sg_pb["macro_f1"]["p"] >= 0.05 > sg_pb["accuracy"]["p"],
            f"So với ASGCN, hiệu số macro-F1 có ý nghĩa ({p_loi(sg_ag['macro_f1']['p'])}) còn hiệu số accuracy thì không ({p_loi(sg_ag['accuracy']['p'])}); "
            f"so với PhoBERT, macro-F1 không khác biệt ({p_loi(sg_pb['macro_f1']['p'])}) còn accuracy thấp hơn có ý nghĩa ({p_loi(sg_pb['accuracy']['p'])})",
            "4.4, kiểm định của Sentic-GCN"),
        neu([e for e in MO_HINH if st.mean(so_doan_tt[e]) > n_tt] == ["senticgcn"],
            "Sentic-GCN là mô hình duy nhất đoán trung tính nhiều hơn số mẫu trung tính thật", "4.4, Sentic-GCN đoán trung tính nhiều"),
        neu(max(rec_tt, key=rec_tt.get) == "senticgcn" and min(dung_phobert, key=lambda e: pre_tt[e]) == "senticgcn",
            f"Recall của lớp này tăng lên {tp(rec_tt['senticgcn'])} %, cao nhất trong các mô hình, nhưng precision giảm còn {tp(pre_tt['senticgcn'])} %, "
            f"thấp nhất trong bốn mô hình dùng PhoBERT, và tổng số mẫu đoán sai là {tp(loi_tb['senticgcn'], 0)}",
            "4.4, recall và precision của Sentic-GCN"),
        neu(max(acc, key=lambda e: acc[e][0]) == "phobert" and max(f1, key=lambda e: f1[e][0]) == "phobert" and nho_nhat_f1 == "phobert",
            "Trên cả accuracy lẫn macro-F1, PhoBERT tinh chỉnh là mô hình đứng đầu; trong năm mô hình học, nó cũng có độ lệch chuẩn của macro-F1 "
            f"nhỏ nhất giữa các seed ({tp(f1['phobert'][1])})", "4.7, mô hình đứng đầu"),
        neu(sorted(hoc, key=lambda e: -f1[e][0])[:3] == ["phobert", "senticgcn", "asgcn_linked"],
            f"Sentic-GCN và ASGCN nối gốc đứng sát sau về macro-F1, cách PhoBERT lần lượt {tp(-hs(f1, 'senticgcn', 'phobert'))} và {tp(-hs(f1, 'asgcn_linked', 'phobert'))} điểm",
            "4.7, hai mô hình đứng sau"),
        neu(sg_pb["macro_f1"]["p"] >= 0.05 and ng_pb["macro_f1"]["p"] >= 0.05,
            f"Kiểm định không bác bỏ được giả thuyết hai khoảng cách này bằng không (p bằng {cb.p_chu(sg_pb['macro_f1']['p'])} và {cb.p_chu(ng_pb['macro_f1']['p'])})",
            "4.7, kiểm định hai khoảng cách"),
        neu(sg_pb["accuracy"]["p"] < 0.05,
            f"Về accuracy, PhoBERT cao hơn Sentic-GCN {tp(hs(acc, 'phobert', 'senticgcn'))} điểm và hiệu số này có ý nghĩa (p bằng {cb.p_chu(sg_pb['accuracy']['p'])})",
            "4.7, accuracy của PhoBERT và Sentic-GCN"),
        neu(all(x > 0 for x in tung_seed("bilstm", "lexicon") + tung_seed("phobert", "bilstm")),
            f"tăng {tp(hs(f1, 'bilstm', 'lexicon'))} điểm macro-F1, và bước thêm tri thức tiền huấn luyện, tăng {tp(hs(f1, 'phobert', 'bilstm'))} điểm",
            "4.7, hai bước có hiệu số lớn"),
        neu(max(abs(hs(f1, "asgcn", "phobert")), abs(hs(f1, "senticgcn", "asgcn"))) < 1.3
            and doi_dau(tung_seed("asgcn", "phobert")) and doi_dau(tung_seed("senticgcn", "asgcn")),
            "cho hiệu số nhỏ hơn 1,3 điểm và đổi dấu theo seed", "4.7, hai bước thêm cấu trúc"),
        ("4.7, lớp trung tính so với hai lớp còn lại", f"F1 cao nhất đạt được là {tp(tt[tot])} %, thấp hơn lớp tiêu cực {round(lop[tot][0] - lop[tot][1])} điểm và lớp tích cực {round(lop[tot][2] - lop[tot][1])} điểm"),
        neu([e for e in dung_phobert if rec_tt[e] > rec_tt["phobert"]] == ["senticgcn"] and pre_tt["senticgcn"] < pre_tt["phobert"],
            "Mô hình duy nhất nâng được recall của lớp này làm điều đó bằng cách giảm precision", "4.7, recall đổi lấy precision"),
        neu(kho_nhat, "Lớp trung tính là lớp khó nhất ở mọi mô hình", "4.7, lớp trung tính khó nhất"),
        # Phần tóm tắt: các cụm dưới đây chỉ được tìm trong mục TÓM TẮT của TrangDau.md.
        ("Tóm tắt, số bình luận", f"trên tập UIT-ViSFD gồm {nghin(sum(BINH_LUAN_GOC.values()))} bình luận"),
        # Viết lại 16/10/2026 cho dễ đọc: bỏ 85,43, 86,50, p 0,630, 71,31 và kappa khỏi phần tóm tắt (vẫn kiểm ở thân bài).
        neu(max(f1, key=lambda e: f1[e][0]) == "phobert", f"PhoBERT tinh chỉnh cho kết quả tốt nhất, với macro-F1 {tp(f1['phobert'][0])} %", "Tóm tắt, PhoBERT đứng đầu"),
        neu(hs(f1, "asgcn", "phobert") < 0 and hs(f1, "senticgcn", "phobert") < 0,
            "ASGCN và Sentic-GCN không tốt hơn PhoBERT", "Tóm tắt, hai mô hình đồ thị không tốt hơn PhoBERT"),
        neu(kho_nhat, "Ở mọi mô hình, cảm xúc trung tính là lớp khó nhận đúng nhất", "Tóm tắt, lớp trung tính"),
    ]


def so_lieu_thong_ke(goc: Path) -> List[Tuple[str, Optional[str]]]:
    """Độ phủ của từ điển và tỉ lệ đồ thị bị chia cắt ở mục 4.3, đọc từ hai file thống kê trong results/."""
    kiem: List[Tuple[str, Optional[str]]] = []
    tep_td, tep_dt = goc / "results/lexicon_stats.json", goc / "results/syntactic_graph_stats.json"
    if tep_td.is_file():
        td = json.loads(tep_td.read_text(encoding="utf-8"))
        kiem.append(("4.3, từ điển", f"với hệ số làm mượt {tp(td['smoothing'], 0)}; từ có mặt trong dưới {td['min_freq']} mẫu huấn luyện bị loại. "
                                     f"Từ điển thu được có {nghin(td['so_token_vao_tu_dien'])} mục, phủ {tp(td['do_phu_tren_train']['ti_le_phu_token'], 1)} % số lượt từ trong các mẫu huấn luyện"))
    else:
        print(f"BỎ QUA số liệu từ điển ở mục 4.3, thiếu: {tep_td}")
    if tep_dt.is_file():
        dt = json.loads(tep_dt.read_text(encoding="utf-8"))
        cat = {sp: dt[sp]["thanh_phan_lien_thong"]["ti_le_bi_chia_cat"] for sp in ("train", "test")}
        kiem.append(("4.3, đồ thị bị chia cắt", f"Hiện tượng này xảy ra ở {tp(cat['train'], 1)} % số mẫu huấn luyện và {tp(cat['test'], 1)} % số mẫu kiểm tra"))
        kiem.append(("4.3, số cạnh thêm", f"làm số cạnh tăng {tp(dt['train']['canh_bien_the_noi_root']['ti_le_tang'], 1)} % trên tập huấn luyện"))
    else:
        print(f"BỎ QUA số liệu đồ thị ở mục 4.3, thiếu: {tep_dt}")
    return kiem


CHU_SO = {1: "một", 2: "hai", 3: "ba", 4: "bốn", 5: "năm", 6: "sáu"}


def so_lieu_llm(goc: Path) -> List[Tuple[str, Optional[str]]]:
    """Mô tả mốc GPT-4o ở mục 4.3: tên mô hình, nhiệt độ, cách hỏi và thành phần tập con.

    Đọc configs/llm.yaml và danh sách mẫu của tập con; thành phần tập con đếm lại trên tập kiểm tra.
    """
    import eval_llm as el
    import yaml

    cfg = yaml.safe_load((goc / el.CAU_HINH).read_text(encoding="utf-8"))
    tep = goc / cfg["tap_con"]["tep_uid"]
    if not tep.is_file():
        print(f"BỎ QUA mô tả mốc GPT-4o ở mục 4.3, thiếu: {tep}")
        return []
    uid = json.loads(tep.read_text(encoding="utf-8"))["uid"]
    test = {r["uid"]: r for r in doc_jsonl(goc / cfg["du_lieu"]["test"])}
    nhan = Counter(int(test[u]["label"]) for u in uid)
    v = cfg["vi_du"]
    # Hai cụm đầu có dấu câu đứng sau: "bằng 0" là chuỗi con của "bằng 0,7", "gpt-4o" là chuỗi con của "gpt-4o-mini".
    return [
        ("4.3, tên mô hình ngôn ngữ lớn", f"tên gọi trên giao diện lập trình là {cfg['mo_hinh']},"),
        ("4.3, nhiệt độ", f"với nhiệt độ bằng {cfg['tham_so']['temperature']:g}".replace(".", ",") + "."),
        ("4.3, zero-shot", "zero-shot, chỉ có lời dặn, chạy một lần"),
        ("4.3, few-shot", f"thêm {CHU_SO[v['moi_lop']]} ví dụ cho mỗi lớp là các bình luận dài {v['tu_toi_thieu']} đến {v['tu_toi_da']} từ "
                          f"rút từ tập huấn luyện, chạy {CHU_SO[len(el.SEED_VI_DU)]} lần với {CHU_SO[len(el.SEED_VI_DU)]} bộ ví dụ khác nhau"),
        ("4.3, tập con", f"một tập con {nghin(len(uid))} mẫu rút phân tầng theo nhãn từ tập kiểm tra ({nghin(nhan[0])} tiêu cực, "
                         f"{nghin(nhan[1])} trung tính, {nghin(nhan[2])} tích cực, thuộc {nghin(len({ma_cau(u) for u in uid}))} bình luận)"),
        ("4.3, chấm lại trên tập con", f"sáu mô hình còn lại được chấm lại trên đúng {nghin(len(uid))} mẫu đó"),
    ]


def so_lieu_chi_phi(goc: Path, so_mau_test: int) -> List[Tuple[str, Optional[str]]]:
    """Cách đo chi phí suy luận ở mục 4.5. Có results/cost_profile.json thì so với file đó; chưa có thì so với giá trị mặc
    định của scripts/profile_cost.py, tức là cách đo sẽ được dùng."""
    import profile_cost as pc

    tep = goc / pc.RA_MAC_DINH
    if tep.is_file():
        mh = json.loads(tep.read_text(encoding="utf-8"))["mo_hinh"]
        co_lo = sorted({int(c) for r in mh.values() for c in r["theo_co_lo"]})
        lap = sorted({r["so_lan_lap"] for r in mh.values()})
        so_mau = sorted({r["so_mau"] for r in mh.values()})
        seed = sorted({r["seed"] for r in mh.values()})
        if len(lap) > 1 or len(so_mau) > 1 or len(seed) > 1:
            return [("4.5, cách đo", f"[các mô hình trong {tep} đo khác điều kiện: số lần lặp {lap}, số mẫu {so_mau}, seed {seed}]")]
        lap, so_mau, seed = lap[0], so_mau[0], seed[0]
    else:
        print(f"CHÚ Ý: chưa có {tep}; cách đo ở mục 4.5 được so với giá trị mặc định của scripts/profile_cost.py")
        co_lo, lap, so_mau, seed = list(pc.CO_LO_MAC_DINH), pc.LAP_MAC_DINH, so_mau_test, 42
    lo = " và ".join(map(str, co_lo))
    ra = [
        ("4.5, số mẫu và kích thước lô", f"toàn bộ {nghin(so_mau)} mẫu của tập kiểm tra ở {CHU_SO[len(co_lo)]} kích thước lô, {lo}, "
                                         "không dùng độ chính xác hỗn hợp"),
        ("4.5, số lần lặp", f"mỗi cấu hình lặp {CHU_SO[lap]} lần và lấy trung vị"),
        ("4.5, seed đối chiếu", f"dự đoán của seed {seed} đã dùng cho Bảng {SO_BANG_RUT_GON['4.5']}"),
    ]
    if tep.is_file():
        thieu = [e for e in MO_HINH if e not in mh]
        # File thiếu mô hình thì đòi một cụm không thể có, để chỗ này bị báo lệch thay vì làm dừng công cụ
        ra += ket_qua_chi_phi(goc, mh) if not thieu else [("4.5, kết quả chi phí", f"[{tep.name} thiếu mô hình: {', '.join(thieu)}]")]
    return ra


def ket_qua_chi_phi(goc: Path, mh: Dict[str, dict]) -> List[Tuple[str, Optional[str]]]:
    """Các con số và câu so sánh trong hai đoạn kết quả của mục 4.5, tính lại từ results/cost_profile.json."""
    ms = {e: {c: mh[e]["theo_co_lo"][c]["ms_moi_mau"] for c in ("1", "32")} for e in MO_HINH}
    mb = {e: mh[e]["theo_co_lo"]["32"]["bo_nho_dinh_mb"] for e in MO_HINH}
    khac = {e: {c: mh[e]["theo_co_lo"][c]["so_du_doan_khac"] for c in ("1", "32")} for e in MO_HINH}
    f1 = {e: st.mean(json.loads((goc / f"results/{e}/seed{s}/metrics.json").read_text(encoding="utf-8"))["test"]["macro_f1"]
                     for s in cb.SEEDS) for e in MO_HINH}
    do_thi = ("asgcn", "asgcn_linked", "senticgcn")
    cham = {c: [(ms[e][c] / ms["phobert"][c] - 1) * 100 for e in do_thi] for c in ("1", "32")}
    them_mb = sorted({round(mb[e] - mb["phobert"], 1) for e in do_thi})
    khoi_tao = sorted(e for e in MO_HINH if mh[e]["trong_so"] != "best.pt")
    gpu = {r["moi_truong"]["ten_gpu"] for r in mh.values()}
    so_mau = mh["bilstm"]["so_mau"]
    return [
        ("4.5, GPU", f"Phép đo chạy trên GPU {gpu.pop() if len(gpu) == 1 else sorted(gpu)}"),
        neu(khoi_tao == ["asgcn", "phobert"], "PhoBERT và ASGCN được đo với trọng số lúc khởi tạo", "4.5, mô hình đo với trọng số lúc khởi tạo"),
        neu(all(khac[e][c] == 0 for e in ("lexicon", "asgcn_linked", "senticgcn") for c in ("1", "32")),
            "Mô hình từ điển, ASGCN nối gốc và Sentic-GCN cho đúng từng dự đoán đã công bố ở cả hai kích thước lô", "4.5, dự đoán trùng"),
        ("4.5, BiLSTM khác dự đoán", f"BiLSTM khác {khac['bilstm']['1']} trong {nghin(so_mau)} dự đoán ở lô 1 và {khac['bilstm']['32']} ở lô 32"),
        ("4.5, mô hình đồ thị chậm hơn", f"chậm hơn PhoBERT từ {min(cham['1']):.0f} đến {max(cham['1']):.0f} % ở lô 1 và từ {min(cham['32']):.0f} "
                                         f"đến {max(cham['32']):.0f} % ở lô 32"),
        ("4.5, bộ nhớ thêm", f"bộ nhớ đỉnh chỉ cao hơn {tp(them_mb[0], 1)} MB" if len(them_mb) == 1 else f"[bộ nhớ thêm khác nhau: {them_mb}]"),
        ("4.5, Sentic-GCN so với ASGCN", f"Sentic-GCN chỉ chậm hơn ASGCN {tp(ms['senticgcn']['1'] - ms['asgcn']['1'])} ms một mẫu ở lô 1"),
        ("4.5, mô hình nhẹ nhanh hơn", f"mô hình từ điển nhanh hơn PhoBERT khoảng {ms['phobert']['1'] / ms['lexicon']['1']:.0f} lần và BiLSTM "
                                       f"khoảng {tp(ms['phobert']['1'] / ms['bilstm']['1'], 1)} lần"),
        neu(all(ms[e][c] > ms["phobert"][c] for e in do_thi for c in ("1", "32")) and all(f1[e] < f1["phobert"] for e in do_thi),
            "ba mô hình đồ thị tốn thêm thời gian suy luận mà không đạt macro-F1 cao hơn PhoBERT", "4.5, đánh đổi"),
    ]


def kiem_cot_chi_phi(cac_bang: Dict[str, dict], ban: str, goc: Path) -> List[Tuple[str, Optional[str]]]:
    """Hai cột cuối của bảng chi phí: hàng của mỗi mô hình phải kết thúc bằng thời gian suy luận và bộ nhớ đỉnh đã đo.

    Bảng này mang số 4.9 ở bản đầy đủ; bản đầy đủ không có hai cột này nên chỉ kiểm bản chính.
    """
    import profile_cost as pc

    tep = goc / pc.RA_MAC_DINH
    if ban != "rut_gon" or not tep.is_file():
        return []
    mh = json.loads(tep.read_text(encoding="utf-8"))["mo_hinh"]
    hang = cac_bang.get(so_bang_cua(ban, "4.9"), {}).get("hang", [])
    ra: List[Tuple[str, Optional[str]]] = []
    for e in MO_HINH:
        lo = mh.get(e, {}).get("theo_co_lo", {})
        if (lo.get("1", {}).get("ms_moi_mau") is None or lo.get("32", {}).get("ms_moi_mau") is None
                or lo.get("32", {}).get("bo_nho_dinh_mb") is None):
            ra.append((f"Bảng 4.9, chi phí suy luận của {e}", f"[{tep.name} không có số đo lô 1 và 32 của {e}, hoặc không có bộ nhớ GPU]"))
            continue
        m = mh[e]["theo_co_lo"]
        duoi = f"| {tp(m['1']['ms_moi_mau'])} / {tp(m['32']['ms_moi_mau'])} | {tp(m['32']['bo_nho_dinh_mb'], 1)} |"
        ung = [h for h in hang if h.startswith(f"| {TEN[e]} |")]
        dung = len(ung) == 1 and ung[0].endswith(duoi)
        ra.append((f"Bảng 4.9, chi phí suy luận của {e}", ung[0] if dung else f"| {TEN[e]} | ... {duoi}"))
    return ra


def do_ti_le_cat(goc: Path, do_dai: int = 128) -> List[Tuple[str, str]]:
    """Tỉ lệ mẫu dài hơn `do_dai` subword, đo bằng đúng ACSADataset của chương trình huấn luyện (dạng cặp câu)."""
    sys.path.insert(0, str(goc / "src"))
    from transformers import AutoTokenizer

    from nsmgat.data.dataset import ACSADataset

    tok = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    ra = {}
    for sp in ("train", "dev", "test"):
        ds = ACSADataset(goc / f"data/processed/visfd_{sp}.jsonl", tok, max_seq_len=100_000, pair_mode=True)
        dai = sum(len(ds[i]["input_ids"]) > do_dai for i in range(len(ds)))
        ra[sp] = (dai, len(ds))
        print(f"  {sp}: {dai} trong {len(ds)} mẫu dài hơn {do_dai} subword, tức {tp(dai / len(ds) * 100)} %")
    return [
        ("Lời văn, mẫu kiểm tra bị cắt", f"{nghin(ra['test'][0])} trong {nghin(ra['test'][1])} mẫu kiểm tra dài hơn giới hạn này, tức {tp(ra['test'][0] / ra['test'][1] * 100)} %"),
        ("Lời văn, mẫu huấn luyện bị cắt", f"Tỉ lệ ở tập huấn luyện là {tp(ra['train'][0] / ra['train'][1] * 100)} %"),
        ("Lời văn, mẫu phát triển bị cắt", f"ở tập phát triển là {tp(ra['dev'][0] / ra['dev'][1] * 100)} %"),
    ]


def so_lieu_chan_doan(goc: Path, ban: str = "rut_gon"):
    """Số liệu của mục 4.1.2 và 4.6. Trả về None nếu máy không có các file của tập chẩn đoán.

    Thành phần tập và giá trị điểm của accuracy, macro-F1 được TÍNH LẠI từ candidates.csv và
    predictions.jsonl, rồi so với results/diagnostic_eval.json; khoảng tin cậy và p lấy từ file đó.
    """
    import chu_thich_chan_doan as ct
    import finalize_diagnostic as fd

    csv_path, kappa_path, eval_path = goc / ct.CSV_MAC_DINH, goc / fd.KAPPA_MAC_DINH, goc / "results/diagnostic_eval.json"
    thieu = [str(p) for p in (csv_path, kappa_path, eval_path) if not p.exists()]
    if thieu:
        print("BỎ QUA phần tập chẩn đoán, thiếu: " + ", ".join(thieu))
        return None
    rows = ct.doc_csv(csv_path)
    dung = [r for r in rows if r["phenomenon"] in fd.NHOM_CHAM]
    kp = json.loads(kappa_path.read_text(encoding="utf-8"))
    ev = json.loads(eval_path.read_text(encoding="utf-8"))
    if ev["so_bo"]:
        raise SystemExit("results/diagnostic_eval.json còn ghi là số sơ bộ: chạy lại finalize_diagnostic.py cham")

    def dem(ds, nhom):
        return [r for r in ds if r["phenomenon"] in nhom]

    def tp1(x: float) -> str:
        return tp(x * 100, 1)

    def dau(x: float) -> str:
        return cb.so(x, 1)

    def kc(x: dict) -> str:
        return f"{tp1(x['gia_tri'])} ({tp1(x['ci95_duoi'])} đến {tp1(x['ci95_tren'])})"

    # --- Tính lại giá trị điểm từ predictions.jsonl, so với file kết quả ---
    du_doan = {e: [dict(zip(u, zip(g.tolist(), d.tolist()))) for u, g, d in
                   (cb.doc_du_doan(goc / "results" / e / f"seed{s}" / "predictions.jsonl") for s in cb.SEEDS)] for e in MO_HINH}

    def diem(e: str, ds) -> Tuple[float, float]:
        acc, f1 = [], []
        for tra in du_doan[e]:
            cap = [tra[r["uid"]] for r in ds]
            acc.append(sum(g == d for g, d in cap) / len(cap))
            f = []
            for lop in range(3):
                tp_ = sum(g == lop and d == lop for g, d in cap)
                mau = sum(g == lop for g, _ in cap) + sum(d == lop for _, d in cap)
                f.append(2 * tp_ / mau if mau else 0.0)
            f1.append(sum(f) / 3)
        return st.mean(acc), st.mean(f1)

    tap = {"tat_ca": dung, "chi_dong_y": [r for r in dung if r["nhan_kiem_tra"] == "dong_y"]}
    for ten, ds in tap.items():
        for e in MO_HINH:
            for nhom, thanh_phan, khoa in ([(g, (g,), "ket_qua") for g in fd.NHOM_CHAM] + [(g, tp_, "ket_qua_gop") for g, tp_ in fd.NHOM_GOP.items()]):
                a, f = diem(e, dem(ds, thanh_phan))
                x = ev[khoa][ten][e][nhom]
                if abs(a - x["accuracy"]["gia_tri"]) > 1e-9 or abs(f - x["macro_f1"]["gia_tri"]) > 1e-9 or x["n"] != len(dem(ds, thanh_phan)):
                    raise SystemExit(f"diagnostic_eval.json lệch với số tính lại: {ten} {e} {nhom}")

    ten_nhom = {"regular": "Thường", "negation": "Phủ định", "contrast": "Chuyển ý", "both": "Cả hai"}
    ten_lop = ("negative", "neutral", "positive")
    kq, gop, moc = ev["ket_qua"], ev["ket_qua_gop"], ev["so_voi_mo_hinh_moc"]
    bang: Dict[str, List[str]] = defaultdict(list)

    def kdy(ds) -> int:
        return sum(r["nhan_kiem_tra"] != "dong_y" for r in ds)

    for g in fd.NHOM_CHAM:
        ds = dem(dung, (g,))
        bang["4.10"].append(f"| {ten_nhom[g]} | {len(ds)} | " + " | ".join(str(sum(r['nhan_goc'] == k for r in ds)) for k in ten_lop)
                            + f" | {kdy(ds)} ({tp(kdy(ds) / len(ds) * 100, 1)} %) |")
    bang["4.10"].append(f"| Tổng | {len(dung)} | " + " | ".join(str(sum(r['nhan_goc'] == k for r in dung)) for k in ten_lop)
                        + f" | {kdy(dung)} ({tp(kdy(dung) / len(dung) * 100, 1)} %) |")
    for e in MO_HINH:
        r = kq["tat_ca"][e]
        bang["4.11"].append(f"| {TEN[e]} | " + " | ".join(kc(r[g]["accuracy"]) for g in fd.NHOM_CHAM) + " |")
        bang["4.12"].append(f"| {TEN[e]} | " + " | ".join(kc(r[g]["macro_f1"]) for g in fd.NHOM_CHAM) + " |")
        bang["4.13"].append(f"| {TEN[e]} | " + " | ".join(f"{dau(r[g][dd]['hieu_voi_moc'])} ({cb.p_chu(r[g][dd]['p'])})"
                                                           for dd in ("accuracy", "macro_f1") for g in fd.NHOM_CHAM[1:]) + " |")
        rg = gop["tat_ca"][e]
        bang["4.14"].append(f"| {TEN[e]} | {kc(rg['regular']['accuracy'])} | " + " | ".join(
            f"{kc(rg[g]['accuracy'])} | {dau(rg[g]['accuracy']['hieu_voi_moc'])} ({cb.p_chu(rg[g]['accuracy']['p'])})" for g in ("co_phu_dinh", "co_chuyen_y")) + " |")
        rd = kq["chi_dong_y"][e]
        bang["4.16"].append(f"| {TEN[e]} | {tp1(rd['regular']['accuracy']['gia_tri'])} | " + " | ".join(
            f"{tp1(rd[g]['accuracy']['gia_tri'])} ({dau(rd[g]['accuracy']['hieu_voi_moc'])}; p {cb.p_chu(rd[g]['accuracy']['p'])})" for g in fd.NHOM_CHAM[1:]) + " |")
        if e != ev["mo_hinh_moc"]:
            bang["4.15"].append(f"| {TEN[e]} | " + " | ".join(
                f"{dau(x['hieu'])} ({dau(x['ci95_duoi'])} đến {dau(x['ci95_tren'])}); p {cb.p_chu(x['p'])}"
                for x in (moc["tat_ca"][e][g]["accuracy"] for g in fd.NHOM_CHAM)) + " |")
    kiem = [(f"Bảng {b}, dòng {i + 1}", d) for b, ds in bang.items() for i, d in enumerate(ds)]

    # --- Lời văn mục 4.1.2 ---
    n = {g: len(dem(dung, (g,))) for g in fd.NHOM_CHAM}
    kho_pd = [r for r in rows if r["nhom_ung_vien"] == "phu_dinh"]
    kho_dc = [r for r in rows if r["nhom_ung_vien"] == "doi_chung"]
    co_pd = len(dem(kho_pd, fd.DAU_HIEU["phu_dinh"]))
    dc_co = len(dem(kho_dc, ("negation", "contrast", "both")))
    ph, cx = kp["phenomenon"], kp["nhan_cam_xuc"]
    lech_ch_pd = ph["bang"].get("both->negation", 0) + ph["bang"].get("negation->both", 0)
    kd = cx["khong_dong_y_nhan_goc"]
    ti_le_kdy = {g: tp(kdy(dem(dung, (g,))) / n[g] * 100, 1) for g in fd.NHOM_CHAM}
    khong_ro = sum(r["nhan_kiem_tra"] == "khong_ro" for r in dung)
    gn = ph["giu_nguyen"]
    kiem += [
        ("4.1.2, cỡ tập", f"Còn lại {len(dung)} mẫu thuộc {len({ma_cau(r['uid']) for r in dung})} bình luận"),
        ("4.1.2, bốn nhóm", f"{n['regular']} mẫu thuộc nhóm thường, {n['negation']} mẫu thuộc nhóm phủ định, {n['contrast']} mẫu thuộc nhóm chuyển ý và {n['both']} mẫu thuộc nhóm cả hai"),
        ("4.1.2, kho phủ định", f"Trong {len(kho_pd)} mẫu của kho có từ phủ định, chỉ {co_pd} mẫu, tức {tp(co_pd / len(kho_pd) * 100, 1)} %"),
        ("4.1.2, kho đối chứng", f"{dc_co} trong {len(kho_dc)} mẫu của kho đối chứng"),
        ("4.1.2, cỡ mẫu gán lại theo nhóm", f"bốn nhóm có {gn['negation']['lan_1']}, {gn['contrast']['lan_1']}, {gn['both']['lan_1']} và {gn['regular']['lan_1']} mẫu"),
        ("4.1.2, kappa", f"là {tp(ph['kappa'], 3)}, với {round(ph['ti_le_trung'] * kp['so_dong'])} trên {kp['so_dong']} mẫu trùng nhau, tức {tp(ph['ti_le_trung'] * 100, 1)} %"),
        ("4.1.2, khoảng cách", f"cách nhau không quá {kp['khoang_cach_toi_da_ngay']} ngày"),
        ("4.1.2, cận trên", f"nên {tp(ph['kappa'], 3)} là cận trên của độ nhất quán thật"),
        ("4.1.2, lệch dồn", f"{lech_ch_pd} trong {len(kp['uid_lech'])} mẫu lệch là lệch giữa nhóm cả hai và nhóm phủ định"),
        ("4.1.2, nhóm cả hai giữ nguyên", f"nhóm cả hai chỉ giữ nguyên nhãn ở {gn['both']['giu']} trên {gn['both']['lan_1']} mẫu"),
        ("4.1.2, kappa từng dấu hiệu", f"cho kappa {tp(kp['dau_hieu']['phu_dinh']['kappa'], 3)}, còn việc xét mẫu có chuyển ý hay không cho kappa {tp(kp['dau_hieu']['chuyen_y']['kappa'], 3)}"),
        ("4.1.2, không đồng ý nhãn gốc", f"{kdy(dung)} trên {len(dung)} mẫu, tức {tp(kdy(dung) / len(dung) * 100, 1)} %"),
        ("4.1.2, mẫu không quyết được", f"gồm {khong_ro} mẫu người chú thích không quyết được"),
        ("4.1.2, không đồng ý theo nhóm", f"{ti_le_kdy['regular']} % ở nhóm thường, {ti_le_kdy['negation']} % ở nhóm phủ định, {ti_le_kdy['contrast']} % ở nhóm chuyển ý và {ti_le_kdy['both']} % ở nhóm cả hai"),
        ("4.1.2, kappa nhãn cảm xúc", f"kappa giữa hai lần gán là {tp(cx['kappa'], 3)}"),
        ("4.1.2, không đồng ý hai lần", f"lần đầu người chú thích không đồng ý với nhãn gốc ở {kd['lan_1']} mẫu, lần hai ở {kd['lan_2']} mẫu, và chỉ {kd['ca_hai']} mẫu ở cả hai lần"),
        ("4.1.2, tập con đồng ý", f"{len(tap['chi_dong_y'])} mẫu mà người chú thích đồng ý với nhãn gốc"),
    ]

    # --- Lời văn mục 4.6 và 4.7 ---
    hoc = [e for e in MO_HINH if e != "lexicon"]
    do_thi = ("asgcn", "asgcn_linked", "senticgcn")
    co_hien_tuong = fd.NHOM_CHAM[1:]

    def o(e, g, dd="accuracy", nguon=kq, ten="tat_ca"):
        return nguon[ten][e][g][dd]

    def tri(x: float) -> str:
        """Trị tuyệt đối của một hiệu số, một chữ số thập phân."""
        return tp(abs(x) * 100, 1)

    def khoang(ds) -> str:
        return f"{tri(min(abs(x) for x in ds))} đến {tri(max(abs(x) for x in ds))}"

    pb, sg = moc["tat_ca"], moc["chi_dong_y"]
    lexicon_tt = sum(tra[r["uid"]][1] == 1 for tra in du_doan["lexicon"] for r in dung)
    tt = {g: sum(r["nhan_goc"] == "neutral" for r in dem(dung, (g,))) / n[g] for g in fd.NHOM_CHAM}
    p_pd = [o(e, "negation")["p"] for e in hoc]
    f1_pd = {e: o(e, "negation", "macro_f1") for e in MO_HINH}
    gop_pd = {e: o(e, "co_phu_dinh", nguon=gop) for e in MO_HINH}
    gop_cy = {e: o(e, "co_chuyen_y", nguon=gop) for e in MO_HINH}
    st_ = pb["senticgcn"]
    rong = (o("phobert", "both")["ci95_tren"] - o("phobert", "both")["ci95_duoi"]) * 100
    cau_tang = neu(all(o(e, g, ten="chi_dong_y")["gia_tri"] > o(e, g)["gia_tri"] for e in MO_HINH for g in fd.NHOM_CHAM),
                   "Trên tập con này mọi con số đều tăng", "4.6, tập con đồng ý tăng")[1]
    kiem += [
        ("4.6, số bình luận", f"trên {ev['so_cau']['tat_ca']} bình luận của tập"),
        ("4.6, tỉ lệ trung tính", f"chiếm {tp(tt['negation'] * 100, 1)} % ở nhóm phủ định so với {tp(tt['regular'] * 100, 1)} % ở nhóm thường"),
        ("4.6, nhóm cả hai", f"nhóm cả hai thấp hơn nhóm thường từ {khoang([o(e, 'both')['hieu_voi_moc'] for e in MO_HINH])} điểm accuracy, "
                             f"với p không vượt quá {cb.p_chu(max(o(e, 'both')['p'] for e in MO_HINH))}"),
        neu(max(o(e, "both")["gia_tri"] for e in MO_HINH) < 0.75, "Không mô hình nào đạt 75 % accuracy trên nhóm này", "4.6, trần ở nhóm cả hai"),
        ("4.6, nhóm chuyển ý", f"Nhóm chuyển ý thấp hơn từ {khoang([o(e, 'contrast')['hieu_voi_moc'] for e in MO_HINH])} điểm, "
                               f"với p không vượt quá {cb.p_chu(max(o(e, 'contrast')['p'] for e in MO_HINH))}"),
        neu(all(o(e, g, "macro_f1")["p"] < 0.05 and o(e, g, "macro_f1")["hieu_voi_moc"] < 0 for e in MO_HINH for g in ("contrast", "both")),
            "Hai kết quả này giữ nguyên khi đo bằng macro-F1", "4.6, macro-F1 ở hai nhóm khó"),
        ("4.6, nhóm phủ định, accuracy", f"với p từ {cb.p_chu(min(p_pd))} đến {cb.p_chu(max(p_pd))}"),
        ("4.6, nhóm phủ định, macro-F1", f"BiLSTM thấp hơn {tri(f1_pd['bilstm']['hieu_voi_moc'])} điểm, ASGCN {tri(f1_pd['asgcn']['hieu_voi_moc'])} điểm và ASGCN nối gốc "
                                         f"{tri(f1_pd['asgcn_linked']['hieu_voi_moc'])} điểm"
                                         + theo_ban(ban, day_du=f" (p lần lượt bằng {cb.p_chu(f1_pd['bilstm']['p'])}, {cb.p_chu(f1_pd['asgcn']['p'])} và {cb.p_chu(f1_pd['asgcn_linked']['p'])})", rut_gon=".")),
        ("4.6, PhoBERT và Sentic-GCN ở nhóm phủ định", theo_ban(ban, day_du=f"PhoBERT và Sentic-GCN thì không (p bằng {cb.p_chu(f1_pd['phobert']['p'])} và {cb.p_chu(f1_pd['senticgcn']['p'])})")),
        ("4.6, mô hình từ điển ở nhóm phủ định", f"cao hơn nhóm thường {tri(o('lexicon', 'negation')['hieu_voi_moc'])} điểm"),
        neu(lexicon_tt == 0 and o("lexicon", "negation")["hieu_voi_moc"] > 0, "không đoán lớp trung tính ở mẫu nào của tập chẩn đoán", "4.6, mô hình từ điển không đoán trung tính"),
        ("4.6, trần của mô hình từ điển", f"là {tp((1 - tt['regular']) * 100, 1)} % ở nhóm thường và {tp((1 - tt['negation']) * 100, 1)} % ở nhóm phủ định"),
        neu(all(gop_pd[e]["p"] < 0.05 and gop_pd[e]["hieu_voi_moc"] < 0 for e in hoc), "mẫu có phủ định thấp hơn nhóm thường ở cả năm mô hình học", "4.6, có phủ định, năm mô hình học"),
        ("4.6, có phủ định, PhoBERT", f"PhoBERT thấp hơn nhóm thường {tri(gop_pd['phobert']['hieu_voi_moc'])} điểm (p bằng {cb.p_chu(gop_pd['phobert']['p'])}), "
                                      f"các mô hình còn lại từ {khoang([gop_pd[e]['hieu_voi_moc'] for e in hoc if e != 'phobert'])} điểm"),
        ("4.6, có chuyển ý", f"Mẫu có chuyển ý thấp hơn từ {khoang([gop_cy[e]['hieu_voi_moc'] for e in hoc])} điểm ở năm mô hình học, trong đó PhoBERT thấp hơn {tri(gop_cy['phobert']['hieu_voi_moc'])} điểm"),
        neu(all(gop_cy[e]["p"] < 0.05 for e in hoc), "mẫu có chuyển ý khó hơn mẫu thường, và mẫu có phủ định nói chung cũng khó hơn", "4.6, kết luận theo dấu hiệu"),
        neu(all(pb[e][g]["accuracy"]["p"] >= 0.05 for e in do_thi for g in fd.NHOM_CHAM if pb[e][g]["accuracy"]["hieu"] > 0),
            "Không mô hình đồ thị nào cao hơn PhoBERT có ý nghĩa ở bất kỳ nhóm nào", "4.6, mô hình đồ thị so với PhoBERT"),
        ("4.6, Sentic-GCN so với PhoBERT", f"Sentic-GCN cao hơn PhoBERT {tri(st_['negation']['accuracy']['hieu'])} điểm ở nhóm phủ định, {tri(st_['contrast']['accuracy']['hieu'])} điểm ở nhóm chuyển ý "
                                           f"và {tri(st_['both']['accuracy']['hieu'])} điểm ở nhóm cả hai"),
        ("4.6, p của Sentic-GCN so với PhoBERT", "(p bằng " + ", ".join(cb.p_chu(st_[g]["accuracy"]["p"]) for g in co_hien_tuong[:2]) + f" và {cb.p_chu(st_['both']['accuracy']['p'])})"),
        ("4.6, Sentic-GCN trên tập con đồng ý", "ba hiệu số này còn " + ", ".join(dau(sg["senticgcn"][g]["accuracy"]["hieu"]) for g in co_hien_tuong[:2])
                                                + f" và {dau(sg['senticgcn']['both']['accuracy']['hieu'])} điểm"),
        ("4.6, ASGCN so với PhoBERT", f"ASGCN thấp hơn PhoBERT {tri(pb['asgcn']['regular']['accuracy']['hieu'])} điểm ở nhóm thường (p bằng {cb.p_chu(pb['asgcn']['regular']['accuracy']['p'])}) "
                                      f"và {tri(pb['asgcn']['negation']['accuracy']['hieu'])} điểm ở nhóm phủ định (p bằng {cb.p_chu(pb['asgcn']['negation']['accuracy']['p'])})"),
        ("4.6, BiLSTM so với PhoBERT ở nhóm cả hai", f"BiLSTM chỉ thấp hơn PhoBERT {tri(pb['bilstm']['both']['accuracy']['hieu'])} điểm (p bằng {cb.p_chu(pb['bilstm']['both']['accuracy']['p'])}), tức với {n['both']} mẫu của nhóm này"),
        ("4.6, số phép so ở Bảng 4.15", theo_ban(ban, day_du=f"Bảng 4.15 gồm {len(pb) * len(fd.NHOM_CHAM)} phép so")),
        ("4.6, không đồng ý ở hai nhóm khó", f"{ti_le_kdy['contrast']} % số mẫu của nhóm chuyển ý và {ti_le_kdy['both']} % của nhóm cả hai"),
        ("4.6, tập con đồng ý tăng", theo_ban(ban, day_du=cau_tang)),
        ("4.6, PhoBERT trên tập con đồng ý", theo_ban(ban, day_du="PhoBERT đạt " + ", ".join(f"{tp1(o('phobert', g, ten='chi_dong_y')['gia_tri'])} %" for g in fd.NHOM_CHAM[:3])
                                                                       + f" và {tp1(o('phobert', 'both', ten='chi_dong_y')['gia_tri'])} % ở bốn nhóm")),
        ("4.6, khoảng cách còn lại trên tập con", f"ở PhoBERT còn {tri(o('phobert', 'contrast', ten='chi_dong_y')['hieu_voi_moc'])} điểm ở nhóm chuyển ý (p bằng {cb.p_chu(o('phobert', 'contrast', ten='chi_dong_y')['p'])}) "
                                                  f"và {tri(o('phobert', 'both', ten='chi_dong_y')['hieu_voi_moc'])} điểm ở nhóm cả hai (p bằng {cb.p_chu(o('phobert', 'both', ten='chi_dong_y')['p'])})"),
        neu(all(o(e, "both", ten="chi_dong_y")["hieu_voi_moc"] < 0 and o(e, "both", ten="chi_dong_y")["p"] < 0.05 for e in hoc),
            f"Nhóm cả hai vẫn thấp hơn nhóm thường có ý nghĩa ở cả năm mô hình học, với p không vượt quá {cb.p_chu(max(o(e, 'both', ten='chi_dong_y')['p'] for e in hoc))}",
            "4.6, nhóm cả hai trên tập con"),
        ("4.6, độ rộng khoảng tin cậy ở nhóm cả hai", f"chỉ có {n['both']} mẫu, và khoảng tin cậy của accuracy ở nhóm này rộng khoảng {round(rong)} điểm"),
        ("4.7, nhóm cả hai", f"thấp hơn nhóm thường từ {khoang([o(e, 'both')['hieu_voi_moc'] for e in MO_HINH])} điểm accuracy ở cả sáu mô hình"),
        ("4.7, kappa", theo_ban(ban, day_du=f"hệ số kappa {tp(ph['kappa'], 3)} đo khi hai lần gán cách nhau không quá {kp['khoang_cach_toi_da_ngay']} ngày")),
    ]
    if ban == "rut_gon":
        co_y_nghia_pd = {e for e in MO_HINH if f1_pd[e]["p"] < 0.05 and f1_pd[e]["hieu_voi_moc"] < 0}
        cd_pb = {g: o("phobert", g, ten="chi_dong_y") for g in ("contrast", "both")}
        kiem += [
            ("4.1.2, số ứng viên", f"{len(rows)} mẫu thuộc {len({ma_cau(r['uid']) for r in rows})} bình luận được lọc theo từ khoá phủ định và chuyển ý"),
            neu(len(rows) - len(dung) == 1, f"Sau khi loại một mẫu, tập gồm {len(dung)} mẫu thuộc {len({ma_cau(r['uid']) for r in dung})} bình luận", "4.1.2, cỡ tập ở bản chính"),
            ("4.1.2, cỡ mẫu gán lại", f"{kp['so_dong']} mẫu được gán lại mà không xem nhãn cũ"),
            ("4.1.2, khoảng cách so với quy ước", f"cách nhau không quá {kp['khoang_cach_toi_da_ngay']} ngày, ngắn hơn mức {fd.SO_NGAY_CHO} ngày mà chuyên đề dự định"),
            neu(all(o(e, "negation")["p"] >= 0.05 for e in hoc), "không mô hình học nào cho hiệu số có ý nghĩa giữa nhóm phủ định và nhóm thường", "4.6, nhóm phủ định không có ý nghĩa về accuracy"),
            neu(co_y_nghia_pd == {"bilstm", "asgcn", "asgcn_linked"}, "Về macro-F1, ba mô hình thấp hơn có ý nghĩa ở nhóm phủ định", "4.6, ba mô hình thấp hơn về macro-F1"),
            neu(all(st_[g]["accuracy"]["ci95_duoi"] < 0 < st_[g]["accuracy"]["ci95_tren"] for g in co_hien_tuong), "nhưng cả ba khoảng tin cậy đều chứa số 0", "4.6, khoảng tin cậy của Sentic-GCN so với PhoBERT"),
            neu(all(abs(cd_pb[g]["hieu_voi_moc"]) < abs(o("phobert", g)["hieu_voi_moc"]) for g in cd_pb), "Trên tập con này, khoảng cách với nhóm thường thu hẹp lại", "4.6, khoảng cách thu hẹp trên tập con"),
            neu(all(gop_cy[e]["hieu_voi_moc"] < 0 for e in MO_HINH), "mẫu có chuyển ý cũng thấp hơn mẫu thường ở mọi mô hình", "4.7, mẫu có chuyển ý ở mọi mô hình"),
            ("Tóm tắt, cỡ tập chẩn đoán", f"một tập chẩn đoán gồm {len(dung)} mẫu lấy từ tập kiểm tra"),
            neu(len(MO_HINH) == 6 and all(o(e, "both")["hieu_voi_moc"] < 0 for e in MO_HINH),
                f"Ở cả sáu mô hình, nhóm có cả phủ định lẫn chuyển ý khó hơn hẳn: accuracy thấp hơn nhóm thường từ "
                f"{khoang([o(e, 'both')['hieu_voi_moc'] for e in MO_HINH])} điểm", "Tóm tắt, nhóm cả hai"),
        ]
    return kiem, {k: "\n".join(v) for k, v in bang.items()}


def do_mau_so(goc: Path) -> List[Tuple[str, str]]:
    """Mẫu số chuẩn hoá không dương của Sentic-GCN trên tập huấn luyện, đo bằng chính lớp mô hình (GAP-033)."""
    import build_lexicon_external as ble

    r = ble.thong_ke_mau_so(goc / "data/lexicon_from_train.json", goc / "data/processed", phan=("train",))["train"]
    print(f"  train: {r['tu_mau_so_khong_duong']} trong {r['so_tu']} lượt từ có mẫu số <= 0, thuộc {r['mau_dinh']} trong {r['so_mau']} mẫu")
    return [("Lời văn 4.3, mẫu số không dương", f"có {tp(r['tu_mau_so_khong_duong'] / r['so_tu'] * 100, 3)} % số từ rơi vào trường hợp đó, "
                                                 f"thuộc {tp(r['mau_dinh'] / r['so_mau'] * 100)} % số mẫu")]


def chuan(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def theo_ban(ban: str, *, day_du: Optional[str] = None, rut_gon: Optional[str] = None) -> Optional[str]:
    """Cụm chữ của một câu mà hai bản viết khác nhau. None: bản đó không có câu này, bỏ qua chỗ kiểm."""
    return {"day_du": day_du, "rut_gon": rut_gon}[ban]


def tach_bang(van_ban: str) -> Dict[str, dict]:
    """{số bảng: {"ten": tên bảng, "van": các hàng nối lại, "hang": danh sách hàng}}, khoảng trắng đã chuẩn hoá."""
    ra: Dict[str, dict] = {}
    dong = van_ban.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(dong):
        m = MAU_TEN_BANG.match(dong[i].strip())
        i += 1
        if not m:
            continue
        if m.group(1) in ra:
            raise ValueError(f"Bảng {m.group(1)} có hai lần trong bản nháp")
        while i < len(dong) and not dong[i].strip():
            i += 1
        hang = []
        while i < len(dong) and dong[i].strip().startswith("|"):
            hang.append(chuan(dong[i]))
            i += 1
        ra[m.group(1)] = {"ten": m.group(2).strip(), "van": " ".join(hang), "hang": hang}
    return ra


def so_bang_cua(ban: str, so_goc: str) -> str:
    return SO_BANG_RUT_GON[so_goc] if ban == "rut_gon" else so_goc


def doi_so_bang(ban: str, mo_ta: str) -> str:
    """Đổi số bảng trong lời mô tả sang số của bản đang kiểm, để người đọc tìm được bảng."""
    if ban != "rut_gon":
        return mo_ta
    return re.sub(r"Bảng (\d+\.\d+)", lambda m: f"Bảng {SO_BANG_RUT_GON.get(m.group(1), m.group(1))}", mo_ta)


def tim(kiem: Sequence[Tuple[str, Optional[str]]], van: str, cac_bang: Dict[str, dict], ban: str, tom_tat: Optional[str] = None):
    """Trả về (số chỗ đã kiểm, danh sách (mô tả, cụm chữ, lý do) không thấy, số chỗ bỏ qua vì bản này không có câu đó).

    Chỗ kiểm có mô tả bắt đầu bằng DAU_TOM_TAT chỉ được tìm trong phần tóm tắt; chưa có phần tóm tắt thì bỏ qua.
    """
    lech, bo_qua, da_kiem = [], 0, 0
    van_tom_tat = chuan(tom_tat) if tom_tat else None
    for mo_ta, chuoi in kiem:
        if chuoi is None or (mo_ta.startswith(DAU_TOM_TAT) and van_tom_tat is None):
            bo_qua += 1
            continue
        da_kiem += 1
        if mo_ta.startswith(DAU_TOM_TAT):
            if chuan(chuoi) not in van_tom_tat:
                lech.append((mo_ta, chuoi, "không thấy cụm chữ này trong phần tóm tắt"))
            continue
        m = MAU_MO_TA_BANG.match(mo_ta)
        if not m:
            if chuan(chuoi) not in van:
                lech.append((doi_so_bang(ban, mo_ta), chuoi, "không thấy cụm chữ này trong lời văn"))
            continue
        so = so_bang_cua(ban, m.group(1))
        bang = cac_bang.get(so)
        if bang is None:
            lech.append((doi_so_bang(ban, mo_ta), chuoi, f"bản nháp không có Bảng {so}"))
        elif chuan(chuoi) not in bang["van"]:
            o_dau = [k for k, b in cac_bang.items() if chuan(chuoi) in b["van"]]
            ly_do = f"hàng này nằm ở Bảng {', '.join(o_dau)} chứ không ở Bảng {so}" if o_dau else f"Bảng {so} không có hàng này"
            lech.append((doi_so_bang(ban, mo_ta), chuoi, ly_do))
    return da_kiem, lech, bo_qua


def kiem_ten_bang(cac_bang: Dict[str, dict], ban: str, so_goc_can: Sequence[str]) -> List[Tuple[str, Optional[str]]]:
    """Mỗi bảng có hàng được kiểm thì tên của nó phải chứa từ khoá. Trả về dạng chỗ kiểm lời văn."""
    ra: List[Tuple[str, Optional[str]]] = []
    for so_goc in so_goc_can:
        so = so_bang_cua(ban, so_goc)
        ten = cac_bang.get(so, {}).get("ten", "")
        tu = TU_KHOA_BANG[so_goc]
        # Cụm chữ đòi có là chính dòng tên bảng; nếu tên không chứa từ khoá thì đòi một chuỗi không thể có.
        ra.append((f"Tên của Bảng {so}", f"Bảng {so}: {ten}" if tu in ten else f"Bảng {so}: [tên phải chứa '{tu}', đang là '{ten}']"))
    return ra


def kiem_thang_mo_hinh(cac_bang: Dict[str, dict], ban: str, tham_so: Dict[str, str]) -> List[Tuple[str, Optional[str]]]:
    """Bảng thang mô hình: hàng của mỗi bậc phải kết thúc bằng đúng số tham số đọc từ metrics.json."""
    hang = cac_bang.get(so_bang_cua(ban, "4.4"), {}).get("hang", [])
    ra: List[Tuple[str, Optional[str]]] = []
    for bac, so_ts in tham_so.items():
        ung = [h for h in hang if h.startswith(f"| {bac} |")]
        dung = len(ung) == 1 and ung[0].endswith(f"| {so_ts} |")
        ra.append((f"Bảng 4.4, số tham số của bậc {bac}", ung[0] if dung else f"| {bac} | ... | {so_ts} |"))
    return ra


def doc_tom_tat(tep: Path) -> Optional[str]:
    """Phần TÓM TẮT trong file các trang đầu của bản chính, hoặc None nếu chưa có."""
    if not tep.is_file():
        return None
    than, trong = [], False
    for d in tep.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n"):
        if d.startswith("# "):
            trong = d[2:].strip() == TIEU_DE_TOM_TAT
        elif trong:
            than.append(d)
    return "\n".join(than).strip() or None


def so_la_trong_tom_tat(tom_tat: str, than_bai: str) -> List[str]:
    """Con số có trong phần tóm tắt mà không có trong thân bài. Phần tóm tắt không được đưa ra số mới."""
    co = set(MAU_SO.findall(than_bai))
    return sorted({s for s in MAU_SO.findall(tom_tat) if s not in co})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đối chiếu số liệu Chương 4 với dữ liệu và file kết quả.")
    ap.add_argument("--goc", type=Path, default=Path("."), help="thư mục gốc của repo")
    ap.add_argument("--ban", choices=sorted(TEP_THEO_BAN), default="rut_gon",
                    help="bản của báo cáo: rut_gon là bản chính (mặc định), day_du là bản lưu")
    ap.add_argument("--nhap", type=Path, nargs="+", default=None,
                    help="các file bản nháp cần kiểm, thay cho các file mặc định của --ban")
    ap.add_argument("--in-bang", action="store_true", help="in các bảng tính lại")
    ap.add_argument("--do-cat", action="store_true", help="đo thêm tỉ lệ mẫu bị cắt ở 128 subword")
    ap.add_argument("--do-mau-so", action="store_true", help="đo thêm tỉ lệ từ và mẫu có mẫu số chuẩn hoá không dương ở Sentic-GCN (cần torch)")
    a = ap.parse_args(argv)

    cac_tep = list(a.nhap) if a.nhap else list(TEP_THEO_BAN[a.ban])
    tho_van = "\n\n".join((a.goc / p).read_text(encoding="utf-8") for p in cac_tep)
    cac_bang = tach_bang(tho_van)
    tom_tat = doc_tom_tat(a.goc / TEP_TRANG_DAU) if a.ban == "rut_gon" and not a.nhap else None
    van = chuan(tho_van + ("\n\n" + tom_tat if tom_tat else ""))

    kiem, tho = so_lieu_du_lieu(a.goc)
    k2, bang = so_lieu_ket_qua(a.goc, tho, a.ban)
    kiem += k2
    kiem += kiem_thang_mo_hinh(cac_bang, a.ban, tho["tham_so"])
    kiem += kiem_cot_chi_phi(cac_bang, a.ban, a.goc)
    if a.ban == "rut_gon":
        kiem += so_lieu_thong_ke(a.goc)
        kiem += so_lieu_llm(a.goc)
        kiem += so_lieu_chi_phi(a.goc, tho["so_mau_test"])
    cd =so_lieu_chan_doan(a.goc, a.ban)
    if cd is not None:
        kiem += cd[0]
        bang.update(cd[1])
    if a.do_cat:
        kiem += do_ti_le_cat(a.goc)
    if a.do_mau_so:
        kiem += do_mau_so(a.goc)
    co_hang = sorted({m.group(1) for mo_ta, chuoi in kiem if chuoi is not None and (m := MAU_MO_TA_BANG.match(mo_ta))},
                     key=lambda s: tuple(int(x) for x in s.split(".")))
    kiem += kiem_ten_bang(cac_bang, a.ban, co_hang)
    if a.in_bang:
        for ten, noi_dung in bang.items():
            print(f"--- Bảng {so_bang_cua(a.ban, ten)}\n{noi_dung}\n")

    da_kiem, lech, bo_qua = tim(kiem, van, cac_bang, a.ban, tom_tat)
    for mo_ta, chuoi, ly_do in lech:
        print(f"KHÔNG THẤY  {mo_ta}: {ly_do}\n            cần có: {chuoi}")
    so_la: List[str] = []
    if tom_tat:
        thu_muc = (a.goc / TEP_TRANG_DAU).parent
        than_bai = "\n".join(p.read_text(encoding="utf-8") for p in sorted(thu_muc.glob("Chuong*.md")) + [thu_muc / "PhuLuc.md"] if p.is_file())
        so_la = so_la_trong_tom_tat(tom_tat, than_bai)
    elif a.ban == "rut_gon" and not a.nhap:
        print(f"BỎ QUA phần tóm tắt: chưa có {TEP_TRANG_DAU} hoặc file chưa có mục {TIEU_DE_TOM_TAT}")
    for s in so_la:
        print(f"SỐ LẠ TRONG TÓM TẮT  {s}: con số này không có trong chương nào hay trong phụ lục")
    ten_ban = "bản chính" if a.ban == "rut_gon" else "bản đầy đủ"
    print(f"Đã kiểm {da_kiem} chỗ trong {ten_ban} ({', '.join(p.name for p in cac_tep)}"
          f"{', phần tóm tắt' if tom_tat else ''}): {da_kiem - len(lech)} khớp, {len(lech)} lệch."
          + (f" Bỏ qua {bo_qua} chỗ vì bản này không có câu tương ứng hoặc chưa có phần tóm tắt." if bo_qua else "")
          + (f" Phần tóm tắt có {len(so_la)} con số lạ." if so_la else ""))
    return 1 if lech or so_la else 0


if __name__ == "__main__":
    raise SystemExit(main())
