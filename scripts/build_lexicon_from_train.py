"""[CD1.4a] Dung tu dien cam xuc tieng Viet TU TAP TRAIN.

VI SAO KHONG DUNG VietSentiWordNet
-----------------------------------
Ban GVHD duyet (muc 1) yeu cau thuc nghiem lai "mo hinh dua tren tu dien".
Nhung repo CHUA co tu dien cam xuc tieng Viet nao: rules/lexicon.py va
scripts/build_affective_lexicon.py deu la placeholder cua S2.1/S3.2, tuc
thuoc Chuyen de 2.

Thay vi phu thuoc mot tai nguyen ngoai chua kiem chung duoc (VietSentiWordNet),
script nay SINH tu dien tu chinh tap train. Uu diem:
  - Tai lap duoc 100%, khong phu thuoc mang hay giay phep ben thu ba
  - Khop mien du lieu tuyet doi (binh luan dien thoai, co teencode/viet tat)
  - Do duoc: biet chinh xac tu dien phu bao nhieu % token

Day la ky thuat chuan, goi la "corpus-based lexicon induction".

⚠️ LUU Y VE GAP-002: tu dien nay tra loi cau hoi "tin hieu tu vung thuan
di duoc bao xa", NHUNG KHONG tra loi "VietSentiWordNet co du tot cho
Sentic-GCN khong". Hai cau hoi khac nhau — dung nham lan.

CACH TINH DIEM
--------------
Voi moi token t, gom nhan cua MOI Example trong tap train co chua t:

    p_pos(t) = (n_pos + k * P_pos) / (n + k)      <- lam muot, k = smoothing
    p_neg(t) = (n_neg + k * P_neg) / (n + k)
    score(t) = (p_pos(t) - p_neg(t)) - (P_pos - P_neg)
                                        ^^^^^^^^^^^^^ tru ti le nen

Hai chi tiet quan trong:
  - LAM MUOT: tu hiem bi keo ve 0, khong cho tu xuat hien 2 lan co diem
    tuyet doi. Khong co no, tu dien se day nhieu.
  - TRU TI LE NEN: du lieu lech lop, neu khong tru thi mot tu trung tinh
    van co diem duong. Tru xong, diem 0 nghia la "khong khac ti le chung".

CHONG RO RI: chi doc visfd_train.jsonl. KHONG BAO GIO doc dev/test.

Dung:
    python scripts/build_lexicon_from_train.py
    python scripts/build_lexicon_from_train.py --min-freq 5 --smoothing 10
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TRAIN_PATH = REPO_ROOT / "data" / "processed" / "visfd_train.jsonl"
OUT_PATH = REPO_ROOT / "data" / "lexicon_from_train.json"
STATS_PATH = REPO_ROOT / "results" / "lexicon_stats.json"

LABEL_NEG, LABEL_NEU, LABEL_POS = 0, 1, 2

# Token khong mang cam xuc, bo di cho tu dien sach. Khong phai stopword list
# day du — chi bo dau cau va vai tu chuc nang xuat hien day dac.
BO_QUA = {
    ",", ".", "!", "?", ";", ":", "...", "-", "(", ")", '"', "'",
    "và", "là", "của", "cho", "với", "thì", "mà", "ở", "các", "những",
}


def tinh_diem_tu_dien(
    records: list[dict], min_freq: int, smoothing: float
) -> tuple[dict[str, float], dict]:
    """Tra ve (tu_dien, thong_ke). tu_dien: {token_thuong: diem trong [-1,1]}."""
    dem_nhan: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in records:
        label = r["label"]
        # Moi token chi dem MOT LAN cho moi Example, tranh tu lap lai bi
        # khuech dai trong cung mot cau.
        for tok in {t.lower() for t in r["tokens"]}:
            dem_nhan[tok][label] += 1

    tong_nhan = collections.Counter(r["label"] for r in records)
    n_all = sum(tong_nhan.values())
    P_pos = tong_nhan[LABEL_POS] / n_all
    P_neg = tong_nhan[LABEL_NEG] / n_all
    lech_nen = P_pos - P_neg

    tu_dien: dict[str, float] = {}
    bi_loai_it_gap = 0
    for tok, dem in dem_nhan.items():
        if tok in BO_QUA:
            continue
        n = sum(dem.values())
        if n < min_freq:
            bi_loai_it_gap += 1
            continue
        p_pos = (dem[LABEL_POS] + smoothing * P_pos) / (n + smoothing)
        p_neg = (dem[LABEL_NEG] + smoothing * P_neg) / (n + smoothing)
        tu_dien[tok] = round((p_pos - p_neg) - lech_nen, 4)

    duong = sorted(tu_dien.items(), key=lambda x: -x[1])[:15]
    am = sorted(tu_dien.items(), key=lambda x: x[1])[:15]

    thong_ke = {
        "so_token_khac_nhau_trong_train": len(dem_nhan),
        "so_token_vao_tu_dien": len(tu_dien),
        "so_token_bi_loai_vi_it_gap": bi_loai_it_gap,
        "min_freq": min_freq,
        "smoothing": smoothing,
        "ti_le_nen": {
            "P_pos": round(P_pos, 4),
            "P_neg": round(P_neg, 4),
            "lech_nen": round(lech_nen, 4),
        },
        "top_duong": [{"token": t, "diem": d} for t, d in duong],
        "top_am": [{"token": t, "diem": d} for t, d in am],
    }
    return tu_dien, thong_ke


def do_do_phu(records: list[dict], tu_dien: dict[str, float]) -> dict:
    """Do tu dien phu bao nhieu % token — con so cot loi cho Chuong 4."""
    tong_token = trong_tu_dien = 0
    example_khong_co_tu_nao = 0
    for r in records:
        co = 0
        for tok in r["tokens"]:
            tong_token += 1
            if tok.lower() in tu_dien:
                trong_tu_dien += 1
                co += 1
        if co == 0:
            example_khong_co_tu_nao += 1

    return {
        "tong_token": tong_token,
        "token_co_trong_tu_dien": trong_tu_dien,
        "ti_le_phu_token": round(trong_tu_dien / tong_token * 100, 1),
        "example_khong_tra_cuu_duoc_tu_nao": example_khong_co_tu_nao,
        "ti_le_example_khong_tra_cuu_duoc": round(example_khong_co_tu_nao / len(records) * 100, 2),
    }


def do_tran_mu_khia_canh(records: list[dict]) -> dict:
    """TRAN tuyet doi cho moi mo hinh KHONG nhin thay khia canh.

    Nhan khia canh cua UIT-ViSFD la ma pham tru tieng Anh (BATTERY, CAMERA...)
    KHONG xuat hien trong cau tieng Viet, nen mo hinh tu dien khong the phan
    biet cac khia canh cua cung mot cau -> buoc phai doan CUNG MOT nhan cho
    tat ca. Tran = ti le dung neu doan nhan pho bien nhat cua tung cau.

    Day la con so quan trong: no cho biet mo hinh tu dien du tot den may cung
    khong the vuot qua bao nhieu.
    """
    theo_cau: dict[str, list[int]] = collections.defaultdict(list)
    for r in records:
        theo_cau[r["text"]].append(r["label"])

    tong = dung = 0
    for nhan in theo_cau.values():
        tong += len(nhan)
        dung += collections.Counter(nhan).most_common(1)[0][1]

    nhieu_kc = sum(1 for v in theo_cau.values() if len(v) > 1)
    trai_nhan = sum(1 for v in theo_cau.values() if len(set(v)) > 1)

    return {
        "so_cau_duy_nhat": len(theo_cau),
        "cau_co_nhieu_khia_canh": nhieu_kc,
        "cau_co_khia_canh_trai_nhan": trai_nhan,
        "ti_le_cau_trai_nhan": round(trai_nhan / len(theo_cau) * 100, 1),
        "tran_accuracy": round(dung / tong * 100, 1),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--min-freq", type=int, default=5, help="Bo token xuat hien it hon nguong nay")
    parser.add_argument("--smoothing", type=float, default=10.0, help="He so lam muot, keo tu hiem ve 0")
    parser.add_argument("--train", type=Path, default=TRAIN_PATH)
    parser.add_argument("-o", "--out", type=Path, default=OUT_PATH)
    parser.add_argument("--stats", type=Path, default=STATS_PATH)
    args = parser.parse_args(argv)

    if not args.train.exists():
        print(f"Khong thay {args.train} — chay scripts/prepare_data.py truoc", file=sys.stderr)
        return 1

    records = [json.loads(line) for line in args.train.open(encoding="utf-8")]
    tu_dien, thong_ke = tinh_diem_tu_dien(records, args.min_freq, args.smoothing)
    thong_ke["do_phu_tren_train"] = do_do_phu(records, tu_dien)
    thong_ke["tran_mu_khia_canh"] = do_tran_mu_khia_canh(records)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(tu_dien, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    args.stats.parent.mkdir(parents=True, exist_ok=True)
    args.stats.write_text(json.dumps(thong_ke, ensure_ascii=False, indent=2), encoding="utf-8")

    phu = thong_ke["do_phu_tren_train"]
    tran = thong_ke["tran_mu_khia_canh"]
    print(f"\n{'=' * 68}\nTU DIEN CAM XUC SINH TU TAP TRAIN\n{'=' * 68}")
    print(f"  Token khac nhau trong train : {thong_ke['so_token_khac_nhau_trong_train']:,}")
    print(f"  Vao tu dien (>= {args.min_freq} lan)    : {thong_ke['so_token_vao_tu_dien']:,}")
    print(f"  Bi loai vi it gap           : {thong_ke['so_token_bi_loai_vi_it_gap']:,}")
    print(f"\n  DO PHU: {phu['ti_le_phu_token']}% token tra cuu duoc")
    print(f"  Example khong tra cuu duoc tu nao: {phu['example_khong_tra_cuu_duoc_tu_nao']:,}"
          f"  ({phu['ti_le_example_khong_tra_cuu_duoc']}%)")
    print(f"\n  ⚠️ TRAN cho mo hinh MU KHIA CANH: {tran['tran_accuracy']}% accuracy")
    print(f"     ({tran['ti_le_cau_trai_nhan']}% cau co khia canh trai nhan)")
    print(f"\n  Top duong: {', '.join(d['token'] for d in thong_ke['top_duong'][:8])}")
    print(f"  Top am   : {', '.join(d['token'] for d in thong_ke['top_am'][:8])}")
    print(f"\nOK -> {args.out}")
    print(f"OK -> {args.stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
