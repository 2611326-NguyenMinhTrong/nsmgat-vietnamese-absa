"""[CD1.6a'] Soi predictions.jsonl theo khía cạnh.

Trả lời một câu hỏi: khi macro-F1 tụt, nó tụt ở **khía cạnh nào** và ở **lớp nào**.
Con số tổng không nói được điều đó, vì UIT-ViSFD lệch rất nặng: 40 % câu trung lập
của tập test thuộc riêng khía cạnh PRICE.

Chỉ đọc `results/<exp>/seed<N>/predictions.jsonl`, không nạp mô hình, không cần GPU.
Mỗi dòng của file đó có đủ `aspect`, `y_true`, `y_pred`, nên mọi chỉ số phân lớp đều
tính lại được mà không cần trọng số.

ĐÂY LÀ CÔNG CỤ TẠM, KHÔNG PHẢI `scripts/error_analysis.py`
----------------------------------------------------------
`error_analysis.py` thuộc S5.4, làm phân tích lỗi đầy đủ kèm ca minh hoạ khả năng
giải thích. File này chỉ làm phần bảng số, dựng ở CD1.6a' để đọc kết quả `asgcn` và
`asgcn_linked`. Giữ trong kho vì mọi con số ở `chuyende1/notes/CD1.6a_asgcn-linked-
va-soi-khia-canh.md` sinh ra từ đây và phải tính lại được. Tới S5.4 thì xem lại có
gộp vào `error_analysis.py` không.

Bốn bảng:
    phan-bo   tập test có gì — nhãn thật theo từng khía cạnh
    f1        F1 của một lớp, tách theo khía cạnh, trung bình nhiều seed
    nham      câu thuộc một lớp bị đoán nhầm thành lớp nào
    loi       số câu sai của một lớp, theo khía cạnh, để so hai mô hình

Dùng:
    python scripts/soi_khia_canh.py phan-bo
    python scripts/soi_khia_canh.py f1 --exp phobert asgcn asgcn_linked
    python scripts/soi_khia_canh.py nham --exp phobert asgcn asgcn_linked
    python scripts/soi_khia_canh.py loi --exp asgcn asgcn_linked --lop 1
    python scripts/soi_khia_canh.py f1 --exp asgcn --lop 0 --seeds 42
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

# Console Windows mac dinh la cp1252, khong in duoc chu tieng Viet co dau ->
# UnicodeEncodeError. Ep stdout ve UTF-8 ngay dau chuong trinh.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = REPO_ROOT / "results"
DEFAULT_SEEDS = (42, 1337, 2024)

# Khop schema.LABEL_NAMES = ["negative", "neutral", "positive"]
TEN_LOP = ("tiêu cực", "trung lập", "tích cực")

Dong = Dict[str, object]


# --- Doc du lieu --------------------------------------------------------------

def doc_du_doan(goc: Path, exp: str, seed: int) -> List[Dong]:
    """Doc predictions.jsonl cua mot lan chay."""
    p = goc / exp / f"seed{seed}" / "predictions.jsonl"
    if not p.exists():
        raise FileNotFoundError(
            f"Không thấy {p}\n"
            f"  Lần chạy {exp}/seed{seed} chưa có kết quả, hoặc chưa tải từ Colab về."
        )
    with p.open(encoding="utf-8") as fh:
        return [json.loads(dong) for dong in fh]


def _nhieu_seed(goc: Path, exp: str, seeds: Sequence[int]) -> List[List[Dong]]:
    return [doc_du_doan(goc, exp, s) for s in seeds]


def _tb_lech(gia_tri: Sequence[float]) -> Tuple[float, float]:
    """Trung binh va do lech chuan. Mot seed thi do lech bang 0, khong phai loi."""
    tb = statistics.mean(gia_tri)
    return tb, statistics.stdev(gia_tri) if len(gia_tri) > 1 else 0.0


# --- Chi so -------------------------------------------------------------------

def f1_cua_lop(rows: Sequence[Dong], lop: int) -> float:
    """F1 cua rieng mot lop, tinh truc tiep tu dem.

    Khong dung sklearn de khong them phu thuoc chi vi mot cong thuc ba dong, va de
    thay ro F1 o day la F1 nhi phan "lop nay vs phan con lai", dung dinh nghia ma
    macro-F1 trong metrics.json lay trung binh.
    """
    tp = sum(1 for r in rows if r["y_true"] == lop and r["y_pred"] == lop)
    fp = sum(1 for r in rows if r["y_true"] != lop and r["y_pred"] == lop)
    fn = sum(1 for r in rows if r["y_true"] == lop and r["y_pred"] != lop)
    if tp == 0:
        # Khong doan dung ca nao -> F1 = 0 theo quy uoc thong thuong. Xay ra that
        # o nhung khia canh rat mong, vd SER&ACC chi co 27 cau trung lap.
        return 0.0
    pre, rec = tp / (tp + fp), tp / (tp + fn)
    return 2 * pre * rec / (pre + rec)


def ho_tro_theo_khia_canh(rows: Sequence[Dong]) -> Dict[str, List[int]]:
    """Dem nhan THAT theo tung khia canh. Khong phu thuoc mo hinh nao."""
    d: Dict[str, List[int]] = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        d[str(r["aspect"])][int(r["y_true"])] += 1
    return dict(d)


# --- Bon bang -----------------------------------------------------------------

def bang_phan_bo(goc: Path, exp: str, seed: int) -> int:
    rows = doc_du_doan(goc, exp, seed)
    ho_tro = ho_tro_theo_khia_canh(rows)
    thu_tu = sorted(ho_tro, key=lambda k: -ho_tro[k][1])

    print(f"TẬP TEST CÓ GÌ — nhãn thật theo từng khía cạnh (đọc từ {exp}/seed{seed})")
    print("Nhãn thật nên bảng này giống nhau ở mọi mô hình và mọi seed.\n")
    print(f"{'khía cạnh':12} {'tổng':>6} {'tiêu cực':>9} {'trung lập':>10} {'tích cực':>9} {'% trung lập':>12}")
    for k in thu_tu:
        n = ho_tro[k]
        print(f"{k:12} {sum(n):>6} {n[0]:>9} {n[1]:>10} {n[2]:>9} {n[1] / sum(n) * 100:>11.1f}%")
    tong = [sum(ho_tro[k][i] for k in ho_tro) for i in range(3)]
    print(f"{'TỔNG':12} {sum(tong):>6} {tong[0]:>9} {tong[1]:>10} {tong[2]:>9} "
          f"{tong[1] / sum(tong) * 100:>11.1f}%")
    return 0


def bang_f1(goc: Path, exps: Sequence[str], seeds: Sequence[int], lop: int) -> int:
    ho_tro = ho_tro_theo_khia_canh(doc_du_doan(goc, exps[0], seeds[0]))
    thu_tu = sorted(ho_tro, key=lambda k: -ho_tro[k][lop])
    du_lieu = {e: _nhieu_seed(goc, e, seeds) for e in exps}

    print(f"F1 LỚP {TEN_LOP[lop].upper()} theo từng khía cạnh "
          f"(trung bình {len(seeds)} seed: {', '.join(map(str, seeds))})\n")
    print(f"{'khía cạnh':12} {'n':>5} " + " ".join(f"{e:>16}" for e in exps))
    for k in thu_tu:
        o = []
        for e in exps:
            v = [f1_cua_lop([r for r in rows if r["aspect"] == k], lop) for rows in du_lieu[e]]
            tb, sd = _tb_lech(v)
            o.append(f"{tb:>9.4f}±{sd:<6.4f}")
        print(f"{k:12} {ho_tro[k][lop]:>5} " + " ".join(o))
    return 0


def bang_nham(goc: Path, exps: Sequence[str], seeds: Sequence[int], lop: int) -> int:
    print(f"CÂU THẬT SỰ {TEN_LOP[lop].upper()} BỊ ĐOÁN NHẦM THÀNH GÌ "
          f"(trung bình {len(seeds)} seed)\n")
    khac = [i for i in range(3) if i != lop]
    print(f"{'mô hình':14} {'đúng':>15} " + " ".join(f"{'→ ' + TEN_LOP[i]:>17}" for i in khac))
    for e in exps:
        dem = []
        for rows in _nhieu_seed(goc, e, seeds):
            d = [0, 0, 0]
            for r in rows:
                if r["y_true"] == lop:
                    d[int(r["y_pred"])] += 1
            dem.append(d)
        tb = [statistics.mean(d[j] for d in dem) for j in range(3)]
        n = sum(tb)
        print(f"{e:14} {tb[lop]:>8.1f} ({tb[lop] / n * 100:4.1f}%) "
              + " ".join(f"{tb[i]:>10.1f} ({tb[i] / n * 100:4.1f}%)" for i in khac))
    return 0


def bang_loi(goc: Path, exps: Sequence[str], seeds: Sequence[int], lop: int) -> int:
    ho_tro = ho_tro_theo_khia_canh(doc_du_doan(goc, exps[0], seeds[0]))
    thu_tu = sorted(ho_tro, key=lambda k: -ho_tro[k][lop])
    du_lieu = {e: _nhieu_seed(goc, e, seeds) for e in exps}

    print(f"SỐ CÂU {TEN_LOP[lop].upper()} BỊ SAI, theo khía cạnh "
          f"(trung bình {len(seeds)} seed)\n")
    cot_hieu = f"{exps[-1]} − {exps[0]}" if len(exps) > 1 else ""
    print(f"{'khía cạnh':12} {'n':>5} " + " ".join(f"{e:>13}" for e in exps)
          + (f" {cot_hieu:>22}" if cot_hieu else ""))
    for k in thu_tu:
        loi = []
        for e in exps:
            v = [sum(1 for r in rows if r["aspect"] == k and r["y_true"] == lop
                     and r["y_pred"] != lop) for rows in du_lieu[e]]
            loi.append(statistics.mean(v))
        dong = f"{k:12} {ho_tro[k][lop]:>5} " + " ".join(f"{x:>13.1f}" for x in loi)
        if cot_hieu:
            dong += f" {loi[-1] - loi[0]:>+22.1f}"
        print(dong)
    return 0


# --- CLI ----------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Soi predictions.jsonl theo khía cạnh — không nạp mô hình, không cần GPU.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Lớp: 0 = tiêu cực, 1 = trung lập, 2 = tích cực.",
    )
    parser.add_argument("lenh", choices=("phan-bo", "f1", "nham", "loi"),
                        help="phan-bo: nhãn thật theo khía cạnh | f1: F1 một lớp theo khía "
                             "cạnh | nham: lớp đó bị đoán nhầm thành gì | loi: số câu sai")
    parser.add_argument("--exp", nargs="+", default=["phobert", "asgcn", "asgcn_linked"],
                        help="Tên thí nghiệm, theo thứ tự muốn in (mặc định: 3 mô hình của CD1.6a)")
    parser.add_argument("--seeds", nargs="+", type=int, default=list(DEFAULT_SEEDS),
                        help="Các seed lấy trung bình (mặc định: 42 1337 2024)")
    parser.add_argument("--lop", type=int, default=1, choices=(0, 1, 2),
                        help="Lớp cần soi (mặc định 1 = trung lập, lớp thiểu số)")
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS,
                        help="Thư mục results/ (mặc định: results/ của kho)")
    args = parser.parse_args(argv)

    try:
        if args.lenh == "phan-bo":
            return bang_phan_bo(args.results, args.exp[0], args.seeds[0])
        if args.lenh == "f1":
            return bang_f1(args.results, args.exp, args.seeds, args.lop)
        if args.lenh == "nham":
            return bang_nham(args.results, args.exp, args.seeds, args.lop)
        return bang_loi(args.results, args.exp, args.seeds, args.lop)
    except FileNotFoundError as err:
        print(err, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
