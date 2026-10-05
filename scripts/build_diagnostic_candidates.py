"""[CD1.8a / S6.1] Lọc Example ứng viên cho tập chẩn đoán phủ định và chuyển ý.

TẬP CHẨN ĐOÁN LÀ TẬP CON CỦA TẬP TEST
-------------------------------------
Mọi ứng viên lấy từ `data/processed/visfd_test.jsonl`, không một dòng nào từ train hay
dev. Lấy từ train là rò rỉ: mô hình đã thấy câu đó kèm nhãn, nên điểm trên tập chẩn đoán
sẽ đo trí nhớ chứ không đo khả năng xử lý phủ định. Hàm `doc_tap_test` chặn điều này ở
ngay cửa vào, không dựa vào việc người chạy trỏ đúng file.

Đơn vị ứng viên là **Example**, tức một cặp (câu, khía cạnh), không phải câu. Lý do:
phủ định trong câu "pin trâu nhưng camera không đẹp" tác động lên CAMERA chứ không lên
BATTERY, nên hiện tượng phải được gán riêng cho từng khía cạnh.

KHÁC ĐẶC TẢ GỐC Ở MỘT CHỖ, CÓ CHỦ Ý
-----------------------------------
`PLAN_NSMGAT.md` mục S6.1 lọc theo **luật** được kích hoạt, tức cần bộ luật của S2.2.
Bộ luật đó thuộc Chuyên đề 2 và chưa tồn tại. `PLAN_CHUYENDE1.md` đã đổi thành lọc theo
**từ khoá**. Cột `luật_kích_hoạt` của đặc tả gốc vì vậy thành `tu_khoa_kich_hoat`.

Danh sách từ khoá nằm ngay trong file này, **không** nằm ở `src/nsmgat/rules/`: thư mục
đó thuộc Chuyên đề 2 (xem `chuyende1/MODULE.md` mục 2.3).

BA BẬC TỪ KHOÁ
--------------
    PHU_DINH, CHUYEN_Y   bậc "chắc" — quyết định Example vào nhóm ứng viên nào
    NGO                  bậc "ngờ"  — không đưa câu vào nhóm nào, chỉ LOẠI câu khỏi nhóm
                         đối chứng

Bậc "ngờ" tồn tại để giữ nhóm đối chứng sạch. Từ "mà" xuất hiện ở 411 câu test, khi thì
chuyển ý ("pin 4500 mà hao quá nhanh"), khi thì không ("nghĩ mà chán"). Coi nó là từ
khoá chắc thì nhóm chuyển ý ngập ca sai; bỏ hẳn nó đi thì nhóm đối chứng lẫn câu chuyển
ý. Cho câu chỉ chứa từ ngờ ra khỏi cả hai phía là cách duy nhất giữ được cả hai nhóm.

Mọi từ khoá được chọn sau khi đếm trên chính tập test, số đếm ở
`chuyende1/notes/CD1.8a_loc-ung-vien.md`. Lệnh `--chi-thong-ke` in lại toàn bộ.

KHÔNG GHI ĐÈ CÔNG CHÚ THÍCH
---------------------------
File đầu ra là thứ học viên sẽ ngồi điền tay 20–25 giờ. Chạy lại lệnh này mà ghi đè lên
file đã điền dở là mất hết, đúng mẫu hỏng của GAP-017. Nên: file đích mà đã có ô chú
thích nào được điền thì lệnh **dừng**, trừ khi có `--ghi-de`, và khi đó nó sao lưu trước.

Dùng:
    python scripts/build_diagnostic_candidates.py                  # sinh candidates.csv
    python scripts/build_diagnostic_candidates.py --chi-thong-ke   # chỉ in số, không ghi
    python scripts/build_diagnostic_candidates.py --seed 7 --so-doi-chung 300
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import random
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# Console Windows mac dinh la cp1252, khong in duoc chu tieng Viet co dau ->
# UnicodeEncodeError. Ep stdout ve UTF-8 ngay dau chuong trinh.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEST = REPO_ROOT / "data" / "processed" / "visfd_test.jsonl"
DEFAULT_OUT = REPO_ROOT / "data" / "diagnostic" / "candidates.csv"

# Khop schema.LABEL_NAMES. Khong import nsmgat de cong cu nho khong keo theo ca
# goi (bai hoc GAP-010); co test canh hai noi khong lech nhau.
TEN_LOP = ("negative", "neutral", "positive")

# Thu tu nay cung la thu tu in va thu tu sap xep file dau ra.
NHOM = ("phu_dinh", "chuyen_y", "ca_hai", "doi_chung")
CHI_TIEU_MAC_DINH = {"phu_dinh": 250, "chuyen_y": 200, "ca_hai": 150, "doi_chung": 200}
DO_DAI_MAC_DINH = (5, 40)

COT = ("uid", "text", "aspect", "nhan_goc", "nhom_ung_vien", "tu_khoa_kich_hoat",
       "so_token", "phenomenon", "nhan_kiem_tra", "ghi_chu")
COT_CHU_THICH = ("phenomenon", "nhan_kiem_tra", "ghi_chu")

# --- Tu khoa ------------------------------------------------------------------
# So sanh theo TOKEN da tach tu, viet thuong, khop NGUYEN token. Khop theo token
# chu khong theo chuoi con la co chu y: "không_khí" va "không_tưởng" la token
# rieng nen khong bi nham thanh phu dinh, con "không_thể" thi duoc liet ke han.

PHU_DINH = frozenset({
    "không", "chẳng", "chả", "chưa",
    "không_thể", "không_thể_nào", "không_nổi",
    # Dang viet tat va khong dau. VnCoreNLP KHONG nhan ra chung la pho tu phu
    # dinh: "ko" bi gan V hoac N. Nen phai khop theo mat chu, khong theo tu loai.
    "ko", "k", "kh", "kg", "khong", "hok", "kô", "éo",
})
# Tap con cua PHU_DINH, chi de in thong ke "dang chuan / dang viet tat".
PHU_DINH_VIET_TAT = frozenset({"ko", "k", "kh", "kg", "khong", "hok", "kô", "éo"})

CHUYEN_Y = frozenset({
    "nhưng", "nhưng_mà", "nhưg", "cơ_mà", "song", "ngược_lại", "vậy_mà",
    "tuy", "tuy_nhiên", "tuy_rằng", "mặc_dù", "dù",
    # Chuyen y kieu "moi thu on, tru X" va "duoc cai X": dac trung cua binh luan
    # san pham, khong co trong danh sach lien tu cua sach ngu phap.
    "trừ", "ngoại_trừ", "có_điều", "mỗi_tội", "chỉ_tội", "được_cái", "được_mỗi_cái",
})

NGO = frozenset({
    "mà", "còn", "chứ",              # lien tu da nghia, xem docstring
    "đâu",                           # "không ... đâu" hoac "ở đâu"
    "đừng", "khỏi",                  # "đừng mua", "khỏi chê": gan phu dinh nhung khong phai phu dinh cam xuc
    "hông",                          # "hông có" (= không) hoac "bên hông"
    "nhung",                         # "nhưng" go khong dau, hoac ten rieng
    "riêng", "tiếc", "dù_sao", "chẳng_lẽ",
})

Dong = Dict[str, object]


# --- Doc du lieu --------------------------------------------------------------

def doc_tap_test(duong_dan: Path) -> List[Dong]:
    """Doc file Example va CHAN moi dong khong thuoc tap test.

    Kiem ca truong `split` lan tien to uid: hai dau hieu doc lap, trat mot la dung.
    Day la chot chong ro ri cua ca tap chan doan, nen no nam o cua vao chu khong
    phai o mot buoc kiem ve sau.
    """
    if not duong_dan.exists():
        raise FileNotFoundError(
            f"Không thấy {duong_dan}\n"
            f"  File này không nằm trong git. Sinh lại bằng scripts/prepare_data.py."
        )
    rows: List[Dong] = []
    with duong_dan.open(encoding="utf-8") as fh:
        for so, dong in enumerate(fh, 1):
            r = json.loads(dong)
            uid = str(r.get("uid", ""))
            if r.get("split") != "test" or not uid.startswith("visfd-test-"):
                raise ValueError(
                    f"{duong_dan.name} dòng {so}: uid = {uid!r}, split = {r.get('split')!r}.\n"
                    f"  Tập chẩn đoán CHỈ được lấy từ tập test. Lấy từ train hay dev là rò rỉ dữ liệu."
                )
            rows.append(r)
    return rows


def ma_cau(uid: str) -> str:
    """'visfd-test-00042-BATTERY' -> 'visfd-test-00042'. Ten khia canh khong chua dau '-'."""
    return uid.rsplit("-", 1)[0]


# --- Tu khoa va nhom ----------------------------------------------------------

def tim_tu_khoa(tokens: Sequence[str]) -> Tuple[List[str], List[str], List[str]]:
    """Tra ve (phu_dinh, chuyen_y, ngo): tu khoa khop, theo thu tu xuat hien, khong lap."""
    pd: List[str] = []
    cy: List[str] = []
    ngo: List[str] = []
    for tok in tokens:
        t = tok.lower()
        for tap, dich in ((PHU_DINH, pd), (CHUYEN_Y, cy), (NGO, ngo)):
            if t in tap and t not in dich:
                dich.append(t)
    return pd, cy, ngo


def xep_nhom(pd: Sequence[str], cy: Sequence[str], ngo: Sequence[str]) -> Optional[str]:
    """Nhom ung vien cua mot cau. None = cau chi co tu "ngo", bi loai khoi moi nhom."""
    if pd and cy:
        return "ca_hai"
    if pd:
        return "phu_dinh"
    if cy:
        return "chuyen_y"
    return None if ngo else "doi_chung"


# --- Chon mau -----------------------------------------------------------------

def chia_chi_tieu(co_san: Sequence[int], chi_tieu: int) -> List[int]:
    """Chia `chi_tieu` cho cac lop sao cho can bang nhat co the.

    Kieu "do nuoc": moi vong chia deu phan con lai cho cac lop con hang. Lop nao
    can truoc thi dung, phan du don sang cac lop khac o vong sau. Vi du co_san =
    [123, 62, 235] va chi_tieu = 200 cho [69, 62, 69] chu khong phai [66, 62, 66].
    """
    lay = [0] * len(co_san)
    con = chi_tieu
    while con > 0:
        mo = [i for i in range(len(co_san)) if lay[i] < co_san[i]]
        if not mo:
            break
        phan = max(1, con // len(mo))
        for i in mo:
            them = min(phan, co_san[i] - lay[i], con)
            lay[i] += them
            con -= them
            if con == 0:
                break
    return lay


def _ngoai_bao_xa(so_token: int, do_dai: Tuple[int, int]) -> int:
    """0 neu trong khoang; nguoc lai la so token lech khoi mep gan nhat."""
    lo, hi = do_dai
    if so_token < lo:
        return lo - so_token
    if so_token > hi:
        return so_token - hi
    return 0


def chon_ung_vien(
    rows: Sequence[Dong],
    chi_tieu: Dict[str, int],
    seed: int,
    do_dai: Tuple[int, int] = DO_DAI_MAC_DINH,
    lay_ngoai_do_dai: bool = True,
) -> Tuple[List[Dong], Dict[str, object]]:
    """Chon Example ung vien, can bang nhan trong tung nhom.

    Thu tu uu tien khi hai yeu cau cua dac ta va cham nhau: CAN BANG NHAN thang UU
    TIEN CAU NGAN. Lop nao thieu cau trong khoang do dai thi lay them cau ngoai
    khoang, cau lech it nhat truoc, de du phan cua lop do.

    Tra ve (danh sach dong da chon, thong ke de in).
    """
    rng = random.Random(seed)
    # nhom -> lop -> [trong khoang, ngoai khoang]
    kho: Dict[str, List[List[List[Dong]]]] = {g: [[[], []] for _ in TEN_LOP] for g in NHOM}
    so_cau: Dict[str, set] = defaultdict(set)
    bi_loai_vi_ngo: set = set()

    for r in sorted(rows, key=lambda x: str(x["uid"])):
        tokens = r["tokens"]
        pd, cy, ngo = tim_tu_khoa(tokens)  # type: ignore[arg-type]
        g = xep_nhom(pd, cy, ngo)
        if g is None:
            bi_loai_vi_ngo.add(ma_cau(str(r["uid"])))
            continue
        n = len(tokens)  # type: ignore[arg-type]
        ung_vien = {
            "uid": r["uid"],
            # Chi de NGUOI doc: gop moi khoang trang, ke ca xuong dong, thanh mot dau
            # cach. Van ban goc tra lai duoc tu uid trong visfd_test.jsonl.
            "text": " ".join(str(r["text"]).split()),
            "aspect": r["aspect"],
            "nhan_goc": TEN_LOP[int(r["label"])],  # type: ignore[arg-type]
            "nhom_ung_vien": g,
            "tu_khoa_kich_hoat": "; ".join(pd + cy),
            "so_token": n,
            "phenomenon": "",
            "nhan_kiem_tra": "",
            "ghi_chu": "",
        }
        trong = _ngoai_bao_xa(n, do_dai) == 0
        kho[g][int(r["label"])][0 if trong else 1].append(ung_vien)  # type: ignore[arg-type]
        so_cau[g].add(ma_cau(str(r["uid"])))

    chon: List[Dong] = []
    thong_ke: Dict[str, object] = {
        "kho": {g: [(len(a), len(b)) for a, b in kho[g]] for g in NHOM},
        "so_cau_trong_kho": {g: len(so_cau[g]) for g in NHOM},
        "so_cau_bi_loai_vi_ngo": len(bi_loai_vi_ngo),
        "lay": {},
        "ngoai_do_dai": {},
    }
    for g in NHOM:
        co_san = [len(a) + (len(b) if lay_ngoai_do_dai else 0) for a, b in kho[g]]
        lay = chia_chi_tieu(co_san, chi_tieu.get(g, 0))
        ngoai = []
        for lop, so_lay in enumerate(lay):
            trong, ngoai_khoang = kho[g][lop]
            tu_trong = min(so_lay, len(trong))
            chon.extend(rng.sample(trong, tu_trong))
            thieu = so_lay - tu_trong
            # Cau ngoai khoang: lech it nhat truoc, hoa thi theo uid cho on dinh.
            ngoai_khoang = sorted(
                ngoai_khoang,
                key=lambda u: (_ngoai_bao_xa(int(u["so_token"]), do_dai), str(u["uid"])),  # type: ignore[arg-type]
            )
            chon.extend(ngoai_khoang[:thieu])
            ngoai.append(thieu)
        thong_ke["lay"][g] = lay  # type: ignore[index]
        thong_ke["ngoai_do_dai"][g] = ngoai  # type: ignore[index]

    chon.sort(key=lambda u: (NHOM.index(str(u["nhom_ung_vien"])), str(u["uid"])))
    return chon, thong_ke


# --- Ghi file, khong ghi de cong chu thich ------------------------------------

def dem_dong_da_chu_thich(duong_dan: Path) -> int:
    """So dong ma it nhat mot o chu thich da duoc dien. 0 neu file chua co."""
    if not duong_dan.exists():
        return 0
    with duong_dan.open(encoding="utf-8-sig", newline="") as fh:
        return sum(
            1 for r in csv.DictReader(fh)
            if any((r.get(c) or "").strip() for c in COT_CHU_THICH)
        )


def ghi_csv(duong_dan: Path, chon: Sequence[Dong], ghi_de: bool = False) -> Optional[Path]:
    """Ghi file ung vien. Tra ve duong dan ban sao luu neu co tao.

    utf-8-sig de Excel doc dung chu tieng Viet. Dau phan cach van la dau phay: may
    Windows tieng Viet mac dinh dung dau cham phay, nen mo bang cach nhap du lieu
    (Data > From Text/CSV) chu dung bam dup vao file.
    """
    da_dien = dem_dong_da_chu_thich(duong_dan)
    sao_luu: Optional[Path] = None
    if da_dien:
        if not ghi_de:
            raise FileExistsError(
                f"{duong_dan} đã có {da_dien} dòng được chú thích.\n"
                f"  Ghi đè là mất công chú thích. Lệnh DỪNG ở đây, chưa đổi gì.\n"
                f"  Muốn sinh ra chỗ khác : thêm --out <đường dẫn khác>\n"
                f"  Chắc chắn muốn ghi đè : thêm --ghi-de (tự sao lưu file cũ trước)"
            )
        dau = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        # Duoi .csv.bak de khop quy tac *.csv.bak da co trong .gitignore.
        sao_luu = duong_dan.with_name(f"{duong_dan.stem}.{dau}.csv.bak")
        shutil.copy2(duong_dan, sao_luu)

    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    with duong_dan.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COT, lineterminator="\r\n")
        w.writeheader()
        w.writerows(chon)
    return sao_luu


# --- Thong ke -----------------------------------------------------------------

def in_tu_khoa_tren_tap_test(rows: Sequence[Dong]) -> None:
    """Moi tu khoa co mat o bao nhieu CAU cua tap test. Dem theo cau, khong theo Example."""
    cau: Dict[str, Dong] = {}
    for r in rows:
        cau.setdefault(ma_cau(str(r["uid"])), r)
    dem: Counter = Counter()
    chuan = viet_tat = ca_hai = 0
    for r in cau.values():
        tk = {str(t).lower() for t in r["tokens"]}  # type: ignore[union-attr]
        for t in tk & (PHU_DINH | CHUYEN_Y | NGO):
            dem[t] += 1
        co_vt = bool(tk & PHU_DINH_VIET_TAT)
        co_ch = bool(tk & (PHU_DINH - PHU_DINH_VIET_TAT))
        chuan += co_ch and not co_vt
        viet_tat += co_vt and not co_ch
        ca_hai += co_ch and co_vt

    print(f"TỪ KHOÁ TRÊN TẬP TEST — số CÂU chứa từ đó, trên tổng {len(cau):,} câu\n")
    for ten, tap in (("PHỦ ĐỊNH (chắc)", PHU_DINH), ("CHUYỂN Ý (chắc)", CHUYEN_Y),
                     ("NGỜ — chỉ để loại khỏi nhóm đối chứng", NGO)):
        co = sorted(((dem[t], t) for t in tap), reverse=True)
        print(f"  {ten}")
        print("    " + ", ".join(f"{t} {c}" for c, t in co))
    tong = chuan + viet_tat + ca_hai
    print(f"\n  Câu có từ phủ định: {tong:,}")
    print(f"    chỉ dạng chuẩn    : {chuan:,}")
    print(f"    chỉ dạng viết tắt : {viet_tat:,}   ← bộ tách từ gán nhầm từ loại cho nhóm này")
    print(f"    có cả hai dạng    : {ca_hai:,}")


def in_thong_ke(chon: Sequence[Dong], tk: Dict[str, object], chi_tieu: Dict[str, int],
                do_dai: Tuple[int, int]) -> None:
    kho = tk["kho"]
    lay = tk["lay"]
    ngoai = tk["ngoai_do_dai"]
    print(f"\nKHO ỨNG VIÊN — số Example theo nhóm và nhãn "
          f"(trong khoảng {do_dai[0]}–{do_dai[1]} token + ngoài khoảng)\n")
    print(f"  {'nhóm':10} {'số câu':>7}  " + "  ".join(f"{t:>12}" for t in TEN_LOP))
    for g in NHOM:
        o = "  ".join(f"{a:>6}+{b:<5}" for a, b in kho[g])  # type: ignore[index]
        print(f"  {g:10} {tk['so_cau_trong_kho'][g]:>7}  {o}")  # type: ignore[index]
    print(f"\n  Câu bị loại vì chỉ chứa từ khoá ngờ: {tk['so_cau_bi_loai_vi_ngo']}")

    print("\nĐÃ CHỌN — cân bằng nhãn trong từng nhóm\n")
    print(f"  {'nhóm':10} {'chỉ tiêu':>8} {'lấy':>5}  " + "  ".join(f"{t:>9}" for t in TEN_LOP)
          + f"  {'số câu':>7}  {'ngoài khoảng':>12}")
    for g in NHOM:
        l = lay[g]  # type: ignore[index]
        sc = len({ma_cau(str(u["uid"])) for u in chon if u["nhom_ung_vien"] == g})
        canh_bao = "" if sum(l) == chi_tieu[g] else "   ← THIẾU, kho không đủ"
        print(f"  {g:10} {chi_tieu[g]:>8} {sum(l):>5}  " + "  ".join(f"{x:>9}" for x in l)
              + f"  {sc:>7}  {sum(ngoai[g]):>12}{canh_bao}")  # type: ignore[index]
    so_cau = len({ma_cau(str(u["uid"])) for u in chon})
    print(f"  {'TỔNG':10} {sum(chi_tieu.values()):>8} {len(chon):>5}  "
          + "  ".join(f"{sum(1 for u in chon if u['nhan_goc'] == t):>9}" for t in TEN_LOP)
          + f"  {so_cau:>7}")

    print("\nĐÃ CHỌN — theo khía cạnh\n")
    theo_kc: Dict[str, Counter] = defaultdict(Counter)
    for u in chon:
        theo_kc[str(u["aspect"])][str(u["nhan_goc"])] += 1
    print(f"  {'khía cạnh':12} {'tổng':>5}  " + "  ".join(f"{t:>9}" for t in TEN_LOP))
    for kc in sorted(theo_kc, key=lambda k: -sum(theo_kc[k].values())):
        c = theo_kc[kc]
        print(f"  {kc:12} {sum(c.values()):>5}  " + "  ".join(f"{c[t]:>9}" for t in TEN_LOP))


# --- CLI ----------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lọc Example ứng viên cho tập chẩn đoán phủ định / chuyển ý, CHỈ từ tập test.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Bốn nhóm ứng viên: phu_dinh, chuyen_y, ca_hai, doi_chung. Nhóm là theo TỪ KHOÁ "
               "trong câu;\nhiện tượng thật của từng Example do người chú thích quyết ở cột phenomenon.",
    )
    parser.add_argument("--test", type=Path, default=DEFAULT_TEST,
                        help="File Example của tập test (mặc định: data/processed/visfd_test.jsonl)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="File CSV đầu ra (mặc định: data/diagnostic/candidates.csv)")
    parser.add_argument("--seed", type=int, default=42, help="Hạt giống chọn mẫu (mặc định 42)")
    for g, ten in (("phu_dinh", "phủ định"), ("chuyen_y", "chuyển ý"),
                   ("ca_hai", "cả phủ định lẫn chuyển ý"), ("doi_chung", "đối chứng, không từ khoá nào")):
        parser.add_argument(f"--so-{g.replace('_', '-')}", type=int, default=CHI_TIEU_MAC_DINH[g],
                            metavar="N", help=f"Số Example nhóm {ten} (mặc định {CHI_TIEU_MAC_DINH[g]})")
    parser.add_argument("--do-dai", type=int, nargs=2, default=list(DO_DAI_MAC_DINH), metavar=("MIN", "MAX"),
                        help="Khoảng số token ưu tiên của câu (mặc định 5 40)")
    parser.add_argument("--khong-lay-ngoai-do-dai", action="store_true",
                        help="Không lấy câu ngoài khoảng độ dài, kể cả khi vì thế mà nhãn mất cân bằng")
    parser.add_argument("--chi-thong-ke", action="store_true",
                        help="Chỉ in thống kê, KHÔNG ghi file")
    parser.add_argument("--ghi-de", action="store_true",
                        help="Ghi đè dù file đích đã có chú thích (tự sao lưu file cũ trước)")
    args = parser.parse_args(argv)

    chi_tieu = {g: getattr(args, f"so_{g}") for g in NHOM}
    do_dai = (args.do_dai[0], args.do_dai[1])
    try:
        rows = doc_tap_test(args.test)
    except (FileNotFoundError, ValueError) as err:
        print(err, file=sys.stderr)
        return 1

    chon, tk = chon_ung_vien(rows, chi_tieu, args.seed, do_dai,
                             lay_ngoai_do_dai=not args.khong_lay_ngoai_do_dai)
    in_tu_khoa_tren_tap_test(rows)
    in_thong_ke(chon, tk, chi_tieu, do_dai)

    if args.chi_thong_ke:
        print("\n(--chi-thong-ke: không ghi file)")
        return 0
    try:
        sao_luu = ghi_csv(args.out, chon, ghi_de=args.ghi_de)
    except FileExistsError as err:
        print(f"\n{err}", file=sys.stderr)
        return 1
    if sao_luu is not None:
        print(f"\nĐã sao lưu file cũ: {sao_luu}")
    print(f"\nĐã ghi {len(chon)} Example ứng viên vào {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
