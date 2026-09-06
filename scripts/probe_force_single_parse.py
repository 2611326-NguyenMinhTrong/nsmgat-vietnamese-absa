"""[CD1.3 / GAP-007] Do hau qua cua viec EP VnCoreNLP parse ca binh luan mot lan.

CAU HOI CAN TRA LOI
-------------------
GAP-007: 52,2% Example co do thi cu phap bi chia cat, vi UIT-ViSFD "cau" thuc
ra la binh luan nhieu cau va VnCoreNLP tach cau truoc khi parse.

Hoc vien hoi (02/09/2026): "khong co cach nao phan tich cu phap cho tung binh
luan 1 lan a? hoac tach theo moi binh luan chu khong tach cau?"

Cau tra loi ngan: LAM DUOC (bo dau cham cau -> parser coi ca binh luan la mot
cau, do thi lien thong hoan toan), NHUNG lam hong cau truc.

CACH DO
-------
Voi moi binh luan nhieu cau:
  A. Parse binh thuong (giu dau cham) -> nhieu cau, nhieu root -> bo token dau
     cham va anh xa lai chi so
  B. Parse sau khi thay dau cham bang khoang trang -> mot cau, mot root
Hai ben co cung day token, nen so sanh duoc head cua tung token.

Ti le token BI DOI head = muc do cau truc bi viet lai khi ep parse mot lan.
Vi ban A la parser chay DUNG mien du lieu no duoc huan luyen (tung cau roi),
con ban B la chay ngoai mien do, phan bi doi gan nhu chac chan la XAU DI.

Ket qua ghi ra results/force_single_parse_probe.json

Dung:
    python scripts/probe_force_single_parse.py
    python scripts/probe_force_single_parse.py --n 300
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

DATA_PATH = REPO_ROOT / "data" / "processed" / "visfd_train.jsonl"
OUT_PATH = REPO_ROOT / "results" / "force_single_parse_probe.json"

PUNCT_KET_CAU = {".", "!", "?", ";"}
RE_PUNCT = re.compile(r"[.!?;]")


def parse_phang(raw_model, text: str) -> tuple[list[str], list[int], list[str]]:
    """Parse va noi phang moi cau, giong het VnCorePipeline.annotate()."""
    sentences = raw_model.annotate_text(text)
    tokens, heads, deprels, offset = [], [], [], 0
    for idx in sorted(sentences):
        for w in sentences[idx]:
            tokens.append(w["wordForm"])
            deprels.append(w["depLabel"])
            head = int(w["head"])
            heads.append(-1 if head == 0 else offset + head - 1)
        offset += len(sentences[idx])
    return tokens, heads, deprels


def bo_token_dau_cau(tokens, heads, deprels):
    """Bo token dau cham/cham than va anh xa lai chi so head.

    Can thiet de hai ban parse co cung day token, moi so sanh head duoc.
    """
    giu = [i for i, t in enumerate(tokens) if t not in PUNCT_KET_CAU]
    anh_xa = {cu: moi for moi, cu in enumerate(giu)}
    t2, h2, d2 = [], [], []
    for cu in giu:
        t2.append(tokens[cu])
        d2.append(deprels[cu])
        h = heads[cu]
        # head tro vao mot dau cham da bi bo -> coi nhu root
        h2.append(-1 if h == -1 else anh_xa.get(h, -1))
    return t2, h2, d2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n", type=int, default=150, help="So binh luan nhieu cau can thu")
    parser.add_argument("-o", "--out", type=Path, default=OUT_PATH)
    args = parser.parse_args(argv)

    if not DATA_PATH.exists():
        print(f"Khong thay {DATA_PATH} — chay scripts/prepare_data.py truoc", file=sys.stderr)
        return 1

    from nsmgat.data.preprocess import VnCorePipeline

    raw_model = VnCorePipeline()._model

    # Lay cac binh luan NHIEU CAU, khong trung nhau
    rows = [json.loads(line) for line in DATA_PATH.open(encoding="utf-8")]
    da_thay, mau = set(), []
    for r in rows:
        if r["text"] in da_thay:
            continue
        da_thay.add(r["text"])
        if sum(1 for h in r["heads"] if h == -1) >= 2 and 10 <= len(r["tokens"]) <= 40:
            mau.append(r["text"])
        if len(mau) >= args.n:
            break

    tong = giong = lech_token = 0
    for text in mau:
        t_a, h_a, _ = bo_token_dau_cau(*parse_phang(raw_model, text))
        t_b, h_b, _ = parse_phang(raw_model, RE_PUNCT.sub(" ", text))
        if t_a != t_b:
            # Bo dau cham doi khi lam doi ca ket qua tach tu -> khong so sanh duoc
            lech_token += 1
            continue
        for a, b in zip(h_a, h_b):
            tong += 1
            giong += a == b

    doi = tong - giong
    ket_qua = {
        "so_binh_luan_da_thu": len(mau),
        "so_binh_luan_lech_token_bo_qua": lech_token,
        "so_token_so_sanh_duoc": tong,
        "token_giu_nguyen_head": giong,
        "token_bi_doi_head": doi,
        "ti_le_bi_doi_head": round(doi / tong * 100, 1) if tong else 0.0,
    }

    print(f"\n{'=' * 66}")
    print("Ep VnCoreNLP parse ca binh luan MOT LAN — hau qua len cau truc")
    print(f"{'=' * 66}")
    print(f"  Binh luan nhieu cau da thu : {ket_qua['so_binh_luan_da_thu']}"
          f"  ({lech_token} lech token, bo qua)")
    print(f"  Token so sanh duoc         : {tong:,}")
    print(f"  Giu nguyen head            : {giong:,}  ({giong / tong * 100:.1f}%)")
    print(f"  >> BI DOI head             : {doi:,}  ({ket_qua['ti_le_bi_doi_head']}%)")
    print()
    print("  Dien giai: ban parse tung cau la parser chay DUNG mien du lieu no")
    print("  duoc huan luyen. Phan bi doi khi ep parse mot lan gan nhu chac chan")
    print("  la XAU DI, khong phai tot len.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(ket_qua, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nOK -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
