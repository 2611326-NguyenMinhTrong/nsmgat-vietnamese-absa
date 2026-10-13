"""[CD1.12b] Đối chiếu số liệu của Chương 4 với dữ liệu và file kết quả.

Tính lại từng con số từ data/processed/, results/<exp>/seed<N>/ và các file thống kê, dựng lại
đúng dòng bảng hoặc cụm chữ mà chương phải có, rồi tìm trong bản nháp. In ra những chỗ KHÔNG
tìm thấy. Không sửa gì trong bản nháp.

    python scripts/doi_chieu_chuong4.py                 # kiểm bản nháp mặc định
    python scripts/doi_chieu_chuong4.py --in-bang       # in thêm các bảng tính lại, để chép khi cần
    python scripts/doi_chieu_chuong4.py --do-cat        # đo thêm tỉ lệ mẫu bị cắt ở 128 subword (cần bộ tách từ PhoBERT)

Mã thoát 0 khi mọi con số đều khớp, 1 khi có chỗ lệch.

Phạm vi: Bảng 4.1, 4.2, 4.5 đến 4.9 và các con số trong lời văn suy ra từ chúng. Các con số lấy
từ bài báo khác, và các con số về tập chẩn đoán, không thuộc phạm vi của công cụ này.
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


def chuan(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đối chiếu số liệu Chương 4 với dữ liệu và file kết quả.")
    ap.add_argument("--goc", type=Path, default=Path("."), help="thư mục gốc của repo")
    ap.add_argument("--nhap", type=Path, default=NHAP_MAC_DINH, help="bản nháp Chương 4")
    ap.add_argument("--in-bang", action="store_true", help="in các bảng tính lại")
    ap.add_argument("--do-cat", action="store_true", help="đo thêm tỉ lệ mẫu bị cắt ở 128 subword")
    a = ap.parse_args(argv)

    van = chuan((a.goc / a.nhap).read_text(encoding="utf-8"))
    kiem, tho = so_lieu_du_lieu(a.goc)
    k2, bang = so_lieu_ket_qua(a.goc, tho)
    kiem += k2
    if a.do_cat:
        kiem += do_ti_le_cat(a.goc)
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
