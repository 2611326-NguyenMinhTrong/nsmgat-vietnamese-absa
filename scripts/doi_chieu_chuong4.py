"""[CD1.12b] Đối chiếu số liệu của Chương 4 với dữ liệu và file kết quả.

Tính lại từng con số từ data/processed/, results/<exp>/seed<N>/ và các file thống kê, dựng lại
đúng dòng bảng hoặc cụm chữ mà chương phải có, rồi tìm trong bản nháp. In ra những chỗ KHÔNG
tìm thấy. Không sửa gì trong bản nháp.

    python scripts/doi_chieu_chuong4.py                 # kiểm bản nháp mặc định
    python scripts/doi_chieu_chuong4.py --in-bang       # in thêm các bảng tính lại, để chép khi cần
    python scripts/doi_chieu_chuong4.py --do-cat        # đo thêm tỉ lệ mẫu bị cắt ở 128 subword (cần bộ tách từ PhoBERT)
    python scripts/doi_chieu_chuong4.py --do-mau-so     # đo thêm mẫu số chuẩn hoá không dương của Sentic-GCN ở mục 4.3 (cần torch)

Mã thoát 0 khi mọi con số đều khớp, 1 khi có chỗ lệch.

Phạm vi: Bảng 4.1, 4.2, 4.5 đến 4.16 và các con số trong lời văn suy ra từ chúng. Các con số lấy
từ bài báo khác không thuộc phạm vi của công cụ này.

Phần tập chẩn đoán (mục 4.1.2 và 4.6, Bảng 4.10 đến 4.16) cần ba file chỉ có trên máy học viên:
data/diagnostic/candidates.csv, data/diagnostic/kappa.json và results/diagnostic_eval.json. Thiếu một
trong ba thì phần này được bỏ qua và công cụ in rõ là đã bỏ qua. Thành phần tập và giá trị điểm của
accuracy, macro-F1 được tính lại từ predictions.jsonl; khoảng tin cậy và p lấy từ diagnostic_eval.json.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))

import compare_baselines as cb  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Vẫn trỏ vào bản đầy đủ: 153 chỗ kiểm gắn với số bảng và nguyên văn của bản đó. Bản rút gọn (bản chính từ
# 13/10/2026) đánh số bảng lại và viết lại một số câu, nên chưa kiểm thẳng được bằng công cụ này; nó được kiểm
# gián tiếp qua doi_chieu_ban_rut_gon.py (không con số, không hàng bảng nào nằm ngoài bản đầy đủ).
NHAP_MAC_DINH = Path("chuyende1/report/nhap/Chuong4_ThucNghiem.md")
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


def so_lieu_ket_qua(goc: Path, tho: dict) -> Tuple[List[Tuple[str, str]], Dict[str, str]]:
    """Bảng 4.5, 4.7, 4.8, 4.9 và các hiệu số trong lời văn."""
    kiem: List[Tuple[str, str]] = []
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
    loi_tb = {}
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
        so_doan = nghin(st.mean(doan_tt)) if not any(doan_tt) else tp(st.mean(doan_tt), 1)
        dong = f"| {TEN[e]} | {so_doan} | {'' if p is None else tp(p)} | {tp(r)} | {tp(loi_tb[e], 1) if loi_tb[e] < 1000 else nghin(int(loi_tb[e])) + ',' + str(round(loi_tb[e] % 1 * 10))} |"
        kiem.append((f"Bảng 4.8, {e}", dong))
        bang["4.8"].append(dong)

    for e in MO_HINH:
        ts = {x["n_params"] for x in m[e]}
        assert len(ts) == 1, (e, ts)
        phut = st.mean(x["train_time_sec"] for x in m[e]) / 60
        kiem.append((f"Bảng 4.9, {e}", f"| {TEN[e]} | {nghin(ts.pop())} | {tp(phut, 1)} |"))
        bang["4.9"].append(kiem[-1][1])

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
        ("Lời văn, ASGCN từng seed", f"nhỉnh hơn PhoBERT {tp(f1s['asgcn'][0] - f1s['phobert'][0])} điểm, ở hai hạt giống còn lại nó thấp hơn "
                                     f"{tp(f1s['phobert'][1] - f1s['asgcn'][1])} và {tp(f1s['phobert'][2] - f1s['asgcn'][2])} điểm"),
        ("Lời văn, nối gốc hơn ASGCN", f"cao hơn ASGCN {tp(hieu(f1, 'asgcn_linked', 'asgcn'))} điểm"),
        ("Lời văn, nối gốc lấy lại", f"khoảng {tp(hieu(f1, 'asgcn_linked', 'asgcn') / -hieu(f1, 'asgcn', 'phobert') * 100, 0)} %"),
        ("Lời văn, Sentic hơn ASGCN", f"cao hơn ASGCN {tp(hieu(f1, 'senticgcn', 'asgcn'))} điểm và gần bằng PhoBERT, thấp hơn {tp(-hieu(f1, 'senticgcn', 'phobert'))} điểm"),
        ("Lời văn, Sentic accuracy", f"chỉ hơn ASGCN {tp(hieu(acc, 'senticgcn', 'asgcn'))} điểm và vẫn thấp hơn PhoBERT {tp(-hieu(acc, 'senticgcn', 'phobert'))} điểm"),
        ("Lời văn, Sentic từng seed", "âm " + tp(f1s["asgcn"][0] - f1s["senticgcn"][0]) + " điểm, dương " + tp(f1s["senticgcn"][1] - f1s["asgcn"][1])
         + " điểm và dương " + tp(f1s["senticgcn"][2] - f1s["asgcn"][2]) + " điểm"),
        ("Lời văn, Sentic sai nhiều hơn", f"nhiều hơn PhoBERT khoảng {tp(loi_tb['senticgcn'] - loi_tb['phobert'], 0)} mẫu"),
        ("Lời văn, tham số thêm", f"{nghin(ts['asgcn'] - ts['phobert'])} tham số so với PhoBERT, tức {tp((ts['asgcn'] - ts['phobert']) / ts['phobert'] * 100)} %"),
        ("Lời văn, F1 trung tính cao nhất", f"F1 cao nhất đạt được là {tp(max(tt.values()))} %"),
    ]
    return kiem, {k: "\n".join(v) for k, v in bang.items()}


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


def so_lieu_chan_doan(goc: Path):
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

    def neu(dung_khong: bool, cau: str, mo_ta: str) -> Tuple[str, str]:
        """Câu định tính: chỉ đòi có trong chương khi số liệu còn đúng như vậy."""
        return (mo_ta, cau if dung_khong else f"SỐ LIỆU KHÔNG CÒN ĐỠ CÂU: {cau}")

    pb, sg = moc["tat_ca"], moc["chi_dong_y"]
    lexicon_tt = sum(tra[r["uid"]][1] == 1 for tra in du_doan["lexicon"] for r in dung)
    tt = {g: sum(r["nhan_goc"] == "neutral" for r in dem(dung, (g,))) / n[g] for g in fd.NHOM_CHAM}
    p_pd = [o(e, "negation")["p"] for e in hoc]
    f1_pd = {e: o(e, "negation", "macro_f1") for e in MO_HINH}
    gop_pd = {e: o(e, "co_phu_dinh", nguon=gop) for e in MO_HINH}
    gop_cy = {e: o(e, "co_chuyen_y", nguon=gop) for e in MO_HINH}
    st_ = pb["senticgcn"]
    rong = (o("phobert", "both")["ci95_tren"] - o("phobert", "both")["ci95_duoi"]) * 100
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
                                         f"{tri(f1_pd['asgcn_linked']['hieu_voi_moc'])} điểm (p lần lượt bằng {cb.p_chu(f1_pd['bilstm']['p'])}, {cb.p_chu(f1_pd['asgcn']['p'])} và {cb.p_chu(f1_pd['asgcn_linked']['p'])})"),
        ("4.6, PhoBERT và Sentic-GCN ở nhóm phủ định", f"PhoBERT và Sentic-GCN thì không (p bằng {cb.p_chu(f1_pd['phobert']['p'])} và {cb.p_chu(f1_pd['senticgcn']['p'])})"),
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
        ("4.6, số phép so ở Bảng 4.15", f"Bảng 4.15 gồm {len(pb) * len(fd.NHOM_CHAM)} phép so"),
        ("4.6, không đồng ý ở hai nhóm khó", f"{ti_le_kdy['contrast']} % số mẫu của nhóm chuyển ý và {ti_le_kdy['both']} % của nhóm cả hai"),
        neu(all(o(e, g, ten="chi_dong_y")["gia_tri"] > o(e, g)["gia_tri"] for e in MO_HINH for g in fd.NHOM_CHAM), "Trên tập con này mọi con số đều tăng", "4.6, tập con đồng ý tăng"),
        ("4.6, PhoBERT trên tập con đồng ý", "PhoBERT đạt " + ", ".join(f"{tp1(o('phobert', g, ten='chi_dong_y')['gia_tri'])} %" for g in fd.NHOM_CHAM[:3])
                                             + f" và {tp1(o('phobert', 'both', ten='chi_dong_y')['gia_tri'])} % ở bốn nhóm"),
        ("4.6, khoảng cách còn lại trên tập con", f"ở PhoBERT còn {tri(o('phobert', 'contrast', ten='chi_dong_y')['hieu_voi_moc'])} điểm ở nhóm chuyển ý (p bằng {cb.p_chu(o('phobert', 'contrast', ten='chi_dong_y')['p'])}) "
                                                  f"và {tri(o('phobert', 'both', ten='chi_dong_y')['hieu_voi_moc'])} điểm ở nhóm cả hai (p bằng {cb.p_chu(o('phobert', 'both', ten='chi_dong_y')['p'])})"),
        neu(all(o(e, "both", ten="chi_dong_y")["hieu_voi_moc"] < 0 and o(e, "both", ten="chi_dong_y")["p"] < 0.05 for e in hoc),
            f"Nhóm cả hai vẫn thấp hơn nhóm thường có ý nghĩa ở cả năm mô hình học, với p không vượt quá {cb.p_chu(max(o(e, 'both', ten='chi_dong_y')['p'] for e in hoc))}",
            "4.6, nhóm cả hai trên tập con"),
        ("4.6, độ rộng khoảng tin cậy ở nhóm cả hai", f"chỉ có {n['both']} mẫu, và khoảng tin cậy của accuracy ở nhóm này rộng khoảng {round(rong)} điểm"),
        ("4.7, nhóm cả hai", f"thấp hơn nhóm thường từ {khoang([o(e, 'both')['hieu_voi_moc'] for e in MO_HINH])} điểm accuracy ở cả sáu mô hình"),
        ("4.7, kappa", f"hệ số kappa {tp(ph['kappa'], 3)} đo khi hai lần gán cách nhau không quá {kp['khoang_cach_toi_da_ngay']} ngày"),
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đối chiếu số liệu Chương 4 với dữ liệu và file kết quả.")
    ap.add_argument("--goc", type=Path, default=Path("."), help="thư mục gốc của repo")
    ap.add_argument("--nhap", type=Path, default=NHAP_MAC_DINH, help="bản nháp Chương 4")
    ap.add_argument("--in-bang", action="store_true", help="in các bảng tính lại")
    ap.add_argument("--do-cat", action="store_true", help="đo thêm tỉ lệ mẫu bị cắt ở 128 subword")
    ap.add_argument("--do-mau-so", action="store_true", help="đo thêm tỉ lệ từ và mẫu có mẫu số chuẩn hoá không dương ở Sentic-GCN (cần torch)")
    a = ap.parse_args(argv)

    van = chuan((a.goc / a.nhap).read_text(encoding="utf-8"))
    kiem, tho = so_lieu_du_lieu(a.goc)
    k2, bang = so_lieu_ket_qua(a.goc, tho)
    kiem += k2
    cd = so_lieu_chan_doan(a.goc)
    if cd is not None:
        kiem += cd[0]
        bang.update(cd[1])
    if a.do_cat:
        kiem += do_ti_le_cat(a.goc)
    if a.do_mau_so:
        kiem += do_mau_so(a.goc)
    if a.in_bang:
        for ten, noi_dung in bang.items():
            print(f"--- Bảng {ten}\n{noi_dung}\n")
    lech = [(mo_ta, chuoi) for mo_ta, chuoi in kiem if chuan(chuoi) not in van]
    for mo_ta, chuoi in lech:
        print(f"KHÔNG THẤY  {mo_ta}\n            cần có: {chuoi}")
    print(f"Đã kiểm {len(kiem)} chỗ trong {a.nhap}: {len(kiem) - len(lech)} khớp, {len(lech)} lệch.")
    return 1 if lech else 0


if __name__ == "__main__":
    raise SystemExit(main())
