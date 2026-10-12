"""[CD1.8d / S6.4] Đo độ nhất quán của nhãn tập chẩn đoán bằng cách gán lại một mẫu.

Chưa có người chú thích thứ hai, nên dùng phương án đã ghi trong plan: chính người chú
thích gán lại một mẫu sau ít nhất hai tuần, không xem nhãn cũ. Con số thu được là độ
NHẤT QUÁN CỦA MỘT NGƯỜI (intra-annotator), không được gọi là độ đồng thuận giữa hai người.
Nếu sau này có người thứ hai thì đưa đúng file .xlsx này cho họ gán; lệnh `kappa` không đổi.

    python scripts/finalize_diagnostic.py rut-mau     # rút 60 dòng, ghi file .xlsx TRỐNG nhãn để gán lại
    python scripts/finalize_diagnostic.py kappa       # sau khi gán lại xong: tính kappa, in các dòng lệch

Mẫu được rút PHÂN TẦNG theo nhãn hiện tượng của lần gán đầu, mỗi nhóm số dòng bằng nhau
(mặc định 15 x 4 nhóm), không rút theo tỉ lệ thật. Lý do: rút theo tỉ lệ thật thì nhóm
`both` chỉ được khoảng 6 dòng, không đủ để biết quy tắc của nhóm đó có lặp lại được không.
Khi báo cáo phải nói rõ mẫu là phân tầng.

Lệnh chốt file tập chẩn đoán và chấm các mô hình trên đó thuộc bước sau, chưa có ở đây.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).parent))

import chu_thich_chan_doan as ct  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

XLSX_MAC_DINH = Path("data/diagnostic/gan_lai_60.xlsx")
SO_NGAY_CHO = 14
NGUONG_KAPPA = 0.70
NHOM_RUT = ("negation", "contrast", "both", "regular")
DINH_DANG_NGAY = "%d/%m/%Y"

Dong = Dict[str, str]


def file_so(xlsx: Path) -> Path:
    return xlsx.with_suffix(".json")


def rut_phan_tang(rows: Sequence[Dong], moi_nhom: int, seed: int) -> List[Dong]:
    """Rút `moi_nhom` dòng cho mỗi nhãn hiện tượng, rồi xáo thứ tự chung. Tất định theo seed."""
    rng = random.Random(seed)
    chon: List[Dong] = []
    for nhom in NHOM_RUT:
        kho = sorted((r for r in rows if r["phenomenon"] == nhom), key=lambda r: r["uid"])
        if len(kho) < moi_nhom:
            raise ValueError(f"Nhóm {nhom} chỉ có {len(kho)} dòng đã gán, không đủ {moi_nhom}")
        chon.extend(rng.sample(kho, moi_nhom))
    rng.shuffle(chon)
    return chon


def kappa_cohen(a: Sequence[str], b: Sequence[str]) -> Tuple[float, float, float]:
    """Trả về (kappa, p_o, p_e). Hai dãy cùng độ dài, khác rỗng."""
    if len(a) != len(b) or not a:
        raise ValueError("Hai dãy nhãn phải cùng độ dài và khác rỗng")
    n = len(a)
    p_o = sum(x == y for x, y in zip(a, b)) / n
    da, db = Counter(a), Counter(b)
    p_e = sum(da[k] * db[k] for k in set(da) | set(db)) / (n * n)
    if p_e == 1.0:  # cả hai lần chỉ dùng đúng một nhãn: kappa không xác định, quy ước 1 nếu trùng hết
        return (1.0 if p_o == 1.0 else 0.0), p_o, p_e
    return (p_o - p_e) / (1 - p_e), p_o, p_e


def nhan_cam_xuc(r: Dong) -> str:
    """Nhãn cảm xúc mà người chú thích cho là đúng: `dong_y` nghĩa là nhãn gốc."""
    return r["nhan_goc"] if r["nhan_kiem_tra"] == "dong_y" else r["nhan_kiem_tra"]


def doc_xlsx(xlsx: Path) -> List[Dong]:
    from openpyxl import load_workbook

    ws = load_workbook(xlsx, read_only=True, data_only=True)[ct.TEN_SHEET]
    hang = ws.iter_rows(values_only=True)
    tieu_de = tuple(str(x) for x in next(hang))
    if tieu_de != ct.COT_XLSX:
        raise ValueError(f"Dòng tiêu đề của {xlsx} đã bị đổi: {tieu_de}")
    ra = []
    for h in hang:
        r = {c: ("" if v is None else str(v).strip()) for c, v in zip(ct.COT_XLSX, h)}
        if r["uid"]:
            ra.append(r)
    return ra


def cmd_rut_mau(csv_path: Path, xlsx: Path, moi_nhom: int, seed: int, ghi_de: bool) -> int:
    if xlsx.exists() and not ghi_de:
        print(f"DỪNG: {xlsx} đã tồn tại. Rút lại là đổi mẫu và mất phần đã gán lại. Chắc chắn thì thêm --ghi-de.")
        return 2
    rows = ct.doc_csv(csv_path)
    loi = ct.loi_gia_tri(rows)
    if loi:
        print("CSV có giá trị không hợp lệ, sửa trước:\n  " + "\n  ".join(loi[:10]))
        return 1
    chon = rut_phan_tang(rows, moi_nhom, seed)
    trong = [{**r, **{c: "" for c in ct.COT_CHU_THICH}} for r in chon]  # xoá nhãn cũ khỏi file gán lại
    xlsx.parent.mkdir(parents=True, exist_ok=True)
    ct.luu_workbook(trong, xlsx)
    hom_nay = dt.date.today()
    som_nhat = hom_nay + dt.timedelta(days=SO_NGAY_CHO)
    file_so(xlsx).write_text(json.dumps({
        "ngay_rut": hom_nay.strftime(DINH_DANG_NGAY), "som_nhat_duoc_gan_lai": som_nhat.strftime(DINH_DANG_NGAY),
        "seed": seed, "moi_nhom": moi_nhom, "phan_tang_theo": "phenomenon cua lan gan dau",
        "uid": [r["uid"] for r in chon]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Đã rút {len(chon)} dòng ({moi_nhom} dòng mỗi nhóm {', '.join(NHOM_RUT)}) ra {xlsx}.\n"
          f"Ba cột chú thích trong file này để TRỐNG.\n"
          f"Không mở file trước ngày {som_nhat.strftime(DINH_DANG_NGAY)}. Khi gán lại: không mở candidates.csv, "
          f"không mở candidates_chu_thich.xlsx; chỉ dùng docs/annotation_guideline.md.")
    return 0


def cmd_kappa(csv_path: Path, xlsx: Path, bo_qua_ngay: bool, out_json: Path) -> int:
    so = json.loads(file_so(xlsx).read_text(encoding="utf-8"))
    som_nhat = dt.datetime.strptime(so["som_nhat_duoc_gan_lai"], DINH_DANG_NGAY).date()
    if dt.date.today() < som_nhat and not bo_qua_ngay:
        print(f"DỪNG: mẫu rút ngày {so['ngay_rut']}, sớm nhất {so['som_nhat_duoc_gan_lai']} mới được gán lại "
              f"(cách {SO_NGAY_CHO} ngày để quên nhãn cũ). Nếu người gán là NGƯỜI THỨ HAI thì thêm --bo-qua-ngay.")
        return 2
    lan2 = {r["uid"]: r for r in doc_xlsx(xlsx)}
    lan1 = {r["uid"]: r for r in ct.doc_csv(csv_path)}
    if set(lan2) != set(so["uid"]):
        print("DỪNG: tập uid trong file gán lại không trùng với mẫu đã rút.")
        return 1
    loi = ct.loi_gia_tri(list(lan2.values()))
    thieu = [u for u, r in lan2.items() if not ct.da_xong(r)]
    if loi or thieu:
        print(f"DỪNG: còn {len(thieu)} dòng chưa gán đủ hai ô, {len(loi)} lỗi giá trị.\n  " + "\n  ".join((loi + thieu)[:15]))
        return 1
    uid = so["uid"]
    h1, h2 = [lan1[u]["phenomenon"] for u in uid], [lan2[u]["phenomenon"] for u in uid]
    k, p_o, p_e = kappa_cohen(h1, h2)
    c1, c2 = [nhan_cam_xuc(lan1[u]) for u in uid], [nhan_cam_xuc(lan2[u]) for u in uid]
    kc, pc, _ = kappa_cohen(c1, c2)
    print(f"Hiện tượng (`phenomenon`), {len(uid)} dòng: kappa = {k:.3f} | trùng {p_o * 100:.1f} % | "
          f"trùng do ngẫu nhiên kỳ vọng {p_e * 100:.1f} %")
    print(f"Ngưỡng {NGUONG_KAPPA:.2f}: {'ĐẠT' if k >= NGUONG_KAPPA else 'CHƯA ĐẠT'}")
    nhan = [x for x in ct.HIEN_TUONG if x in set(h1) | set(h2)]
    print("\nLần 1 (hàng) so với lần 2 (cột):")
    print(f"{'':<10}" + "".join(f"{x:>10}" for x in nhan))
    bang = Counter(zip(h1, h2))
    for x in nhan:
        print(f"{x:<10}" + "".join(f"{bang[(x, y)]:>10}" for y in nhan))
    print(f"\nNhãn cảm xúc sau kiểm tra: kappa = {kc:.3f} | trùng {pc * 100:.1f} %")
    lech = [u for u, x, y in zip(uid, h1, h2) if x != y]
    if lech:
        print(f"\n{len(lech)} dòng lệch về hiện tượng (lần 1 -> lần 2):")
        for u in lech:
            print(f"  {u.replace('visfd-test-', '')}: {lan1[u]['phenomenon']} -> {lan2[u]['phenomenon']} | {lan1[u]['text'][:110]}")
    out_json.write_text(json.dumps({
        "loai": "nhat_quan_mot_nguoi" if not bo_qua_ngay else "can_ghi_ro_ai_gan_lan_hai",
        "ngay_rut": so["ngay_rut"], "ngay_tinh": dt.date.today().strftime(DINH_DANG_NGAY), "so_dong": len(uid),
        "phan_tang": True, "moi_nhom": so["moi_nhom"],
        "phenomenon": {"kappa": k, "ti_le_trung": p_o, "ti_le_trung_ngau_nhien": p_e,
                       "bang": {f"{x}->{y}": bang[(x, y)] for x in nhan for y in nhan if bang[(x, y)]}},
        "nhan_cam_xuc": {"kappa": kc, "ti_le_trung": pc}, "uid_lech": lech}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nĐã ghi {out_json}")
    return 0 if k >= NGUONG_KAPPA else 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Rút mẫu gán lại và tính kappa cho tập chẩn đoán.")
    sub = ap.add_subparsers(dest="lenh", required=True)
    p = sub.add_parser("rut-mau", help="rút mẫu phân tầng, ghi file .xlsx trống nhãn")
    p.add_argument("--csv", type=Path, default=ct.CSV_MAC_DINH)
    p.add_argument("--xlsx", type=Path, default=XLSX_MAC_DINH)
    p.add_argument("--moi-nhom", type=int, default=15, help="số dòng mỗi nhóm hiện tượng (mặc định 15, tức 60 dòng)")
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--ghi-de", action="store_true")
    p = sub.add_parser("kappa", help="tính kappa giữa lần gán đầu (CSV) và lần gán lại (.xlsx)")
    p.add_argument("--csv", type=Path, default=ct.CSV_MAC_DINH)
    p.add_argument("--xlsx", type=Path, default=XLSX_MAC_DINH)
    p.add_argument("--out", type=Path, default=Path("data/diagnostic/kappa.json"))
    p.add_argument("--bo-qua-ngay", action="store_true", help="bỏ kiểm tra khoảng cách 14 ngày (khi người gán là người thứ hai)")
    a = ap.parse_args(argv)
    if a.lenh == "rut-mau":
        return cmd_rut_mau(a.csv, a.xlsx, a.moi_nhom, a.seed, a.ghi_de)
    return cmd_kappa(a.csv, a.xlsx, a.bo_qua_ngay, a.out)


if __name__ == "__main__":
    raise SystemExit(main())
