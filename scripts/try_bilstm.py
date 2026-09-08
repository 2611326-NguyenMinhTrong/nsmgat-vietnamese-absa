"""[CD1.4b] Cong cu thu tay BiLSTMModel — go mot cau, xem mo hinh nhin vao dau.

VI SAO CAN
----------
`try_lexicon.py` tra loi "mo hinh cham diem tung tu the nao". Cong cu nay tra
loi cau khac va quan trong hon voi luan van:

    "Doi khia canh thi mo hinh co nhin sang cho khac trong cau khong?"

Do la CAU HOI CHINH cua bai toan ACSA. LexiconModel MU KHIA CANH — cung mot
cau thi moi khia canh cho cung mot du doan, nen bi chan o tran 80,2% accuracy
(do duoc o CD1.4a). BiLSTM nhin thay khia canh o hai cho (luc ma hoa va luc
gop). Che do `--doi-khia-canh` cho THAY dieu do bang mat, khong phai tin loi.

QUAN TRONG: script goi DUNG code that (`model.ma_hoa()`, `model._chu_y()`,
`ACSADataset`, `collate_fn`), KHONG viet lai. Do la ly do bilstm.py tach rieng
hai ham do — de cong cu va mo hinh khong the lech nhau.

DOC BANG ATTENTION THE NAO
--------------------------
Trong so attention cong lai bang 1 tren toan cau. Token nao trong so cao la
token mo hinh dua vao de quyet dinh. Ba luu y khi doc:

  - PhoBERT tach subword, nen mot tu goc co the gom nhieu manh. Bang o day da
    CONG trong so cac manh lai theo tu goc (dung `word_ids` trong batch), nen
    doc theo tu cho de.
  - <s> va </s> la token dac biet, khong phai tu that. Chung van an trong so
    va thuong an kha nhieu — day la hien tuong binh thuong cua attention, coi
    nhu "khong nhin vao dau ca".
  - Attention cao KHONG dong nghia "day la ly do". No chi noi mo hinh doc o
    do. Ket luan nhan qua can them thi nghiem (se lam o CD1.9).

DUNG
----
    .venv\\Scripts\\python.exe scripts/try_bilstm.py                  # tuong tac
    .venv\\Scripts\\python.exe scripts/try_bilstm.py --text "pin trau nhung man hinh toi" --aspect BATTERY
    .venv\\Scripts\\python.exe scripts/try_bilstm.py --doi-khia-canh "pin trau nhung man hinh toi"
    .venv\\Scripts\\python.exe scripts/try_bilstm.py --uid visfd-test-00042-BATTERY
    .venv\\Scripts\\python.exe scripts/try_bilstm.py --sai 10
    .venv\\Scripts\\python.exe scripts/try_bilstm.py --lop 1        # xem mo hinh doan gi cho lop trung tinh

Phai chay bang Python cua moi truong ao (.venv) — xem GAP-010.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

# Console Windows mac dinh la cp1252, khong in duoc chu tieng Viet co dau ->
# UnicodeEncodeError. Ep stdout ve UTF-8 ngay dau chuong trinh.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import torch  # noqa: E402

from nsmgat.data.dataset import ACSADataset, collate_fn  # noqa: E402
from nsmgat.models.bilstm import BiLSTMModel  # noqa: E402
from nsmgat.utils.io import load_config, read_jsonl  # noqa: E402

TEN_NHAN = ["tiêu cực", "trung tính", "tích cực"]
CKPT = REPO_ROOT / "checkpoints" / "bilstm" / "seed42" / "best.pt"


# --- Nap mo hinh --------------------------------------------------------------


def nap_mo_hinh() -> tuple[BiLSTMModel, dict]:
    cfg = load_config(REPO_ROOT / "configs" / "bilstm.yaml")
    print("  Dang xay bang tra subword tu tap train (mat ~20s) ...")
    model = BiLSTMModel(cfg)

    if CKPT.exists():
        model.load_state_dict(torch.load(CKPT, map_location="cpu"))
        print(f"  Da nap trong so da huan luyen: {CKPT.relative_to(REPO_ROOT)}")
    else:
        print(f"  ! Chua co {CKPT.relative_to(REPO_ROOT)} — dung trong so NGAU NHIEN.")
        print("    Ket qua duoi day vo nghia. Chay truoc:")
        print("      .venv\\Scripts\\python.exe -m nsmgat.train "
              "--config configs/bilstm.yaml --model bilstm --seed 42")
    model.eval()
    return model, cfg


# --- Dung batch bang DUNG duong ong that ---------------------------------------


def lam_batch(records: list[dict], cfg: dict) -> dict:
    """Ghi record ra file tam roi cho ACSADataset doc.

    Vong qua file tam nghe thua, nhung doi lai la dung DUNG ACSADataset +
    collate_fn ma luc huan luyen dung — ke ca cat bot theo max_seq_len va
    cach suy word_ids. Neu tu tokenize o day thi cong cu va huan luyen co the
    lech nhau, dung loai loi ca repo nay dang chong.
    """
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(cfg["model"]["encoder_name"])
    max_len = cfg.get("train", {}).get("max_seq_len", 128)

    with tempfile.NamedTemporaryFile(
        "w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        tam = Path(f.name)
    try:
        ds = ACSADataset(tam, tokenizer, max_seq_len=max_len)
        return collate_fn([ds[i] for i in range(len(ds))])
    finally:
        tam.unlink(missing_ok=True)


def lam_record(uid: str, tokens: list[str], aspect: str, label: int = 0) -> dict:
    n = len(tokens)
    return {
        "uid": uid,
        "text": " ".join(tokens),
        "tokens": tokens,
        "pos": ["X"] * n,
        "heads": [-1] * n,
        "deprels": ["root"] * n,
        "aspect": aspect,
        "label": label,
        "domain": "visfd",
        "split": "test",
    }


def chay(model: BiLSTMModel, batch: dict) -> tuple[torch.Tensor, torch.Tensor]:
    """Goi DUNG duong code that: ma_hoa() -> _chu_y() -> classifier.

    Tra ve (xac suat (B,3), trong so attention (B,L)).
    """
    with torch.no_grad():
        h, a_lap, mask = model.ma_hoa(batch)
        trong_so = model._chu_y(h, a_lap, mask)
        gop = torch.bmm(trong_so.unsqueeze(1), h).squeeze(1)
        logits = model.classifier(gop)  # eval() nen dropout da tat
    return torch.softmax(logits, dim=-1), trong_so


def gop_theo_tu(
    trong_so: list[float], word_ids: list[int | None], tokens: list[str]
) -> list[tuple[str, float]]:
    """Cong trong so cac subword lai theo tu goc. Subword dac biet -> '<dac biet>'."""
    tong: dict[int | None, float] = {}
    for w, ts in zip(word_ids, trong_so):
        tong[w] = tong.get(w, 0.0) + ts
    ket: list[tuple[str, float]] = []
    if None in tong:
        ket.append(("<dac biet>", tong.pop(None)))
    for w in sorted(tong):
        ten = tokens[w] if w < len(tokens) else f"<cat #{w}>"
        ket.append((ten, tong[w]))
    return ket


# --- Cac che do ---------------------------------------------------------------


def in_mot_ca(
    model: BiLSTMModel,
    cfg: dict,
    tokens: list[str],
    aspect: str,
    tieu_de: str,
    nhan_vang: int | None = None,
) -> None:
    batch = lam_batch([lam_record("__thu_tay__", tokens, aspect)], cfg)
    prob, trong_so = chay(model, batch)

    print(f"\n{'=' * 74}\n{tieu_de}\n{'=' * 74}")
    if aspect not in model.aspect_to_idx:
        print(f"  ! Khia canh {aspect!r} chua tung thay luc huan luyen -> lui ve chi so 0.")
        print(f"    Khia canh hop le: {', '.join(sorted(model.aspect_to_idx))}")
    print(f"  Khia canh: {aspect}")
    print(f"  Token ({len(tokens)}): {' '.join(tokens)}\n")

    cap = gop_theo_tu(trong_so[0].tolist(), batch["word_ids"][0], tokens)
    dinh = max(ts for _, ts in cap) or 1.0

    print(f"  {'Tu':<22} {'Chu y':>7}")
    print(f"  {'-' * 22} {'-' * 7}   {'-' * 30}")
    for ten, ts in cap:
        thanh = "█" * int(round(ts / dinh * 30))
        print(f"  {ten:<22} {ts:>6.1%}   {thanh}")

    nhan = int(torch.argmax(prob[0]).item())
    print(f"\n  >> DU DOAN : {TEN_NHAN[nhan].upper()}")
    print("     Xac suat : " + "  ".join(f"{TEN_NHAN[i]}={prob[0][i]:.3f}" for i in range(3)))
    if nhan_vang is not None:
        print(f"     Nhan vang: {TEN_NHAN[nhan_vang].upper()}   "
              f"-> {'DUNG' if nhan == nhan_vang else 'SAI'}")


def doi_khia_canh(model: BiLSTMModel, cfg: dict, tokens: list[str]) -> None:
    """Chay CUNG MOT CAU voi MOI khia canh — che do dang gia nhat cua cong cu.

    LexiconModel se cho ra 11 dong Y HET NHAU (mu khia canh). BiLSTM phai cho
    ra khac nhau; neu khong thi thiet ke aspect-aware da that bai.
    """
    aspects = sorted(model.aspect_to_idx)
    records = [lam_record(f"__ac_{a}__", tokens, a) for a in aspects]
    batch = lam_batch(records, cfg)
    prob, trong_so = chay(model, batch)

    print(f"\n{'=' * 74}\n  Cung mot cau, doi khia canh: {' '.join(tokens)}\n{'=' * 74}")
    print(f"  {'Khia canh':<14} {'Du doan':<12} {'tieu':>6} {'trung':>6} {'tich':>6}   Nhin nhieu nhat")
    print(f"  {'-' * 14} {'-' * 12} {'-' * 6} {'-' * 6} {'-' * 6}   {'-' * 26}")

    for i, a in enumerate(aspects):
        cap = [(t, w) for t, w in gop_theo_tu(trong_so[i].tolist(), batch["word_ids"][i], tokens)
               if t != "<dac biet>"]
        top = ", ".join(t for t, _ in sorted(cap, key=lambda x: -x[1])[:3])
        nhan = int(torch.argmax(prob[i]).item())
        print(f"  {a:<14} {TEN_NHAN[nhan]:<12} "
              f"{prob[i][0]:>6.3f} {prob[i][1]:>6.3f} {prob[i][2]:>6.3f}   {top}")

    khac = len({int(torch.argmax(prob[i]).item()) for i in range(len(aspects))})
    print(f"\n  {khac} du doan khac nhau tren {len(aspects)} khia canh.")
    if khac == 1:
        print("  -> Cau nay mo hinh doan giong nhau het. Chua ket luan duoc gi:")
        print("     co the cau khong co y kien trai chieu. Thu cau co 'nhung'.")
    else:
        print("  -> Mo hinh CO doi du doan theo khia canh — dieu LexiconModel khong lam duoc.")


def xem_uid(model: BiLSTMModel, cfg: dict, uid: str) -> None:
    for split in ("test", "dev", "train"):
        path = REPO_ROOT / "data" / "processed" / f"visfd_{split}.jsonl"
        if not path.exists():
            continue
        for r in read_jsonl(path):
            if r["uid"] == uid:
                in_mot_ca(model, cfg, r["tokens"], r["aspect"],
                          f"{uid}  (tap {split})", r["label"])
                print(f"\n  Cau goc: {r['text'][:200]}")
                return
    print(f"  Khong tim thay uid {uid!r}")


def _du_doan_tap_test(model: BiLSTMModel, cfg: dict) -> tuple[list[dict], torch.Tensor]:
    path = REPO_ROOT / "data" / "processed" / "visfd_test.jsonl"
    if not path.exists():
        raise SystemExit("  Chua co data/processed/visfd_test.jsonl")
    records = read_jsonl(path)
    print(f"  Dang chay tren {len(records):,} Example cua tap test ...")

    phan: list[torch.Tensor] = []
    for i in range(0, len(records), 64):
        batch = lam_batch(records[i:i + 64], cfg)
        prob, _ = chay(model, batch)
        phan.append(prob)
    return records, torch.cat(phan)


def xem_ca_sai(model: BiLSTMModel, cfg: dict, k: int) -> None:
    """Ca doan SAI — nguyen lieu cho muc 5.3 (phan tich loi) cua bao cao."""
    records, prob = _du_doan_tap_test(model, cfg)
    doan = prob.argmax(dim=-1).tolist()

    sai = [(r, d, prob[i]) for i, (r, d) in enumerate(zip(records, doan)) if d != r["label"]]
    print(f"\n  Doan sai {len(sai):,}/{len(records):,} ({len(sai) / len(records):.1%}). "
          f"{min(k, len(sai))} ca dau:\n")
    for r, d, p in sai[:k]:
        print(f"  [{r['uid']}]  khia canh={r['aspect']}")
        print(f"    vang={TEN_NHAN[r['label']]:<11} doan={TEN_NHAN[d]:<11} "
              f"tin={p[d]:.3f}")
        print(f"    {r['text'][:110]}\n")


def xem_lop(model: BiLSTMModel, cfg: dict, lop: int) -> None:
    """Mo hinh doan gi cho cac Example thuoc MOT lop vang.

    Dung de kiem gia thuyet (3) cua CD1.4a: "NEU bi nuot boi NEG". Voi
    LexiconModel, lop 1 (trung tinh) co F1 = 0,000 — khong Example nao duoc
    doan la trung tinh. Xem BiLSTM co pha duoc san khong.
    """
    records, prob = _du_doan_tap_test(model, cfg)
    doan = prob.argmax(dim=-1).tolist()

    trong_lop = [(r, d) for r, d in zip(records, doan) if r["label"] == lop]
    if not trong_lop:
        print(f"  Khong co Example nao nhan vang = {lop}")
        return

    dem = [0, 0, 0]
    for _, d in trong_lop:
        dem[d] += 1
    print(f"\n  {len(trong_lop):,} Example co nhan vang = {TEN_NHAN[lop].upper()}, "
          f"mo hinh doan thanh:")
    for i in range(3):
        thanh = "█" * int(round(dem[i] / len(trong_lop) * 40))
        dau = "  <== dung" if i == lop else ""
        print(f"    {TEN_NHAN[i]:<11} {dem[i]:>5,} ({dem[i] / len(trong_lop):>5.1%})  {thanh}{dau}")

    tong_doan = sum(1 for d in doan if d == lop)
    print(f"\n  Tren toan tap test, mo hinh doan {TEN_NHAN[lop]} {tong_doan:,} lan.")
    if tong_doan == 0:
        print(f"  -> Mo hinh KHONG BAO GIO doan lop nay => F1 = 0, giong het LexiconModel.")


# --- Che do tuong tac ---------------------------------------------------------

HUONG_DAN = """
  Go cau tieng Viet DA TACH TU (dung '_' cho tu ghep: 'man_hinh', 'tuyet_voi').
  Mac dinh chay voi khia canh dang chon.

    :ac <ten>       doi khia canh dang chon        vi du  :ac SCREEN
    :ac             liet ke khia canh hop le
    :moi <cau>      chay cau do voi MOI khia canh  <- che do dang xem nhat
    :uid <uid>      chay tren mot Example that
    :sai [N]        N ca mo hinh doan sai tren tap test
    :lop [0|1|2]    mo hinh doan gi cho mot lop vang (mac dinh 1 = trung tinh)
    :help           in lai huong dan
    :q              thoat
"""


def tuong_tac(model: BiLSTMModel, cfg: dict) -> None:
    print(HUONG_DAN)
    aspect = sorted(model.aspect_to_idx)[0]
    while True:
        try:
            dong = input(f"\n  [{aspect}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not dong:
            continue
        if dong in (":q", ":quit", ":exit"):
            return
        if dong == ":help":
            print(HUONG_DAN)
        elif dong == ":ac":
            print(f"  Khia canh hop le: {', '.join(sorted(model.aspect_to_idx))}")
        elif dong.startswith(":ac "):
            moi = dong[4:].strip().upper()
            if moi in model.aspect_to_idx:
                aspect = moi
                print(f"  Da doi sang {aspect}")
            else:
                print(f"  Khong co khia canh {moi!r}. "
                      f"Hop le: {', '.join(sorted(model.aspect_to_idx))}")
        elif dong.startswith(":moi "):
            doi_khia_canh(model, cfg, dong[5:].split())
        elif dong.startswith(":uid "):
            xem_uid(model, cfg, dong[5:].strip())
        elif dong.startswith(":sai"):
            phan = dong.split()
            xem_ca_sai(model, cfg, int(phan[1]) if len(phan) > 1 else 5)
        elif dong.startswith(":lop"):
            phan = dong.split()
            xem_lop(model, cfg, int(phan[1]) if len(phan) > 1 else 1)
        elif dong.startswith(":"):
            print(f"  Khong hieu lenh {dong!r}. Go :help.")
        else:
            in_mot_ca(model, cfg, dong.split(), aspect, f"Cau ban go: {dong}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--text", help="Chay tren mot cau roi thoat")
    parser.add_argument("--aspect", default=None, help="Khia canh di kem --text")
    parser.add_argument("--doi-khia-canh", dest="doi_ac",
                        help="Chay mot cau voi MOI khia canh roi thoat")
    parser.add_argument("--uid", help="Chay tren mot Example that roi thoat")
    parser.add_argument("--sai", type=int, help="In N ca doan sai roi thoat")
    parser.add_argument("--lop", type=int, choices=[0, 1, 2],
                        help="Mo hinh doan gi cho mot lop vang roi thoat")
    args = parser.parse_args(argv)

    print("\n  Dang nap BiLSTMModel ...")
    model, cfg = nap_mo_hinh()
    print(f"  Bang nhung: {model.emb.num_embeddings:,} o | "
          f"khia canh: {len(model.aspect_to_idx)} | tham so: {model.count_params():,}")

    if args.doi_ac:
        doi_khia_canh(model, cfg, args.doi_ac.split())
    elif args.uid:
        xem_uid(model, cfg, args.uid)
    elif args.sai:
        xem_ca_sai(model, cfg, args.sai)
    elif args.lop is not None:
        xem_lop(model, cfg, args.lop)
    elif args.text:
        aspect = args.aspect or sorted(model.aspect_to_idx)[0]
        in_mot_ca(model, cfg, args.text.split(), aspect, f"Cau: {args.text}")
    else:
        tuong_tac(model, cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
