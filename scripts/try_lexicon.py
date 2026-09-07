"""[CD1.4a] Cong cu thu tay LexiconModel — go mot cau, xem mo hinh nghi gi.

VI SAO CAN
----------
pytest chi tra loi "code co dung khong". Cong cu nay tra loi cau khac:
"mo hinh THUC SU nghi gi ve cau nay, va vi sao". Dung de:
  - Hieu mo hinh bang cach nghich, khong phai bang cach doc code
  - Tim ca that bai lam vi du cho muc 5.3 (ca dien hinh) cua bao cao
  - Kiem tra bang mat xem tu dien co hop ly khong

QUAN TRONG: script nay goi DUNG code that cua LexiconModel (._dac_trung(),
.calibrate, .explain()), KHONG viet lai logic. Neu viet lai, cong cu va mo
hinh co the lech nhau va bao cao sai — dung loai loi ma ca repo nay dang chong.

TACH TU
-------
Tu dien dung tu da tach ("tuyet_voi"), nen cau go tay phai duoc tach tu thi
moi tra cuu dung. Script tu dung VnCoreNLP neu co (chinh xac, khoi dong ~5s),
neu khong thi tach theo khoang trang va BAO RO la ket qua kem chinh xac.

DUNG
----
    python scripts/try_lexicon.py                      # che do tuong tac
    python scripts/try_lexicon.py --text "pin rat trau"
    python scripts/try_lexicon.py --word tuyet_voi
    python scripts/try_lexicon.py --top 15
    python scripts/try_lexicon.py --uid visfd-test-00042-BATTERY
    python scripts/try_lexicon.py --sai 10                # 10 ca mo hinh doan SAI
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import torch  # noqa: E402

from nsmgat.models.lexicon import LexiconModel  # noqa: E402
from nsmgat.train import load_config  # noqa: E402
from nsmgat.utils.io import read_jsonl  # noqa: E402

TEN_NHAN = ["tiêu cực", "trung tính", "tích cực"]
CKPT = REPO_ROOT / "checkpoints" / "lexicon" / "seed42" / "best.pt"


# --- Tach tu ------------------------------------------------------------------


class BoTachTu:
    """Tach tu bang VnCoreNLP neu co; neu khong thi tach theo khoang trang."""

    def __init__(self) -> None:
        self._model = None
        self.co_vncorenlp = False
        try:
            from nsmgat.data.preprocess import VnCorePipeline

            self._model = VnCorePipeline()
            self.co_vncorenlp = True
        except Exception as exc:  # thieu Java / thieu model / bat ky loi nao
            print(f"  (khong dung duoc VnCoreNLP: {type(exc).__name__} — tach theo khoang trang)")

    def tach(self, text: str) -> list[str]:
        if self._model is not None:
            tokens, _, _, _ = self._model.annotate(text)
            return tokens
        return text.split()


# --- Nap mo hinh --------------------------------------------------------------


def nap_mo_hinh() -> LexiconModel:
    cfg = load_config(REPO_ROOT / "configs" / "lexicon.yaml")
    model = LexiconModel(cfg)
    if CKPT.exists():
        model.load_state_dict(torch.load(CKPT, map_location="cpu"))
        print(f"  Da nap trong so da huan luyen: {CKPT.relative_to(REPO_ROOT)}")
    else:
        print(f"  ! Chua co {CKPT.relative_to(REPO_ROOT)} — dung trong so ngau nhien.")
        print("    Chay truoc: python -m nsmgat.train --config configs/lexicon.yaml "
              "--model lexicon --seed 42")
    model.eval()
    return model


def du_doan(model: LexiconModel, uid: str) -> tuple[int, list[float], float, float]:
    """Chay dung duong code that: _dac_trung() -> calibrate()."""
    mean_score, coverage = model._dac_trung(uid)
    with torch.no_grad():
        logits = model.calibrate(torch.tensor([[mean_score, coverage]], dtype=torch.float))
        prob = torch.softmax(logits, dim=-1)[0].tolist()
    return int(torch.argmax(logits, dim=-1).item()), prob, mean_score, coverage


# --- Cac che do ---------------------------------------------------------------


def xem_cau(model: LexiconModel, tokens: list[str], tieu_de: str, nhan_vang: int | None = None) -> None:
    """In bang token + diem, roi du doan. Dung uid tam de goi dung code that."""
    uid = "__thu_tay__"
    model.uid_to_tokens[uid] = tokens
    model._cache.pop(uid, None)  # xoa cache cu neu go cau khac

    print(f"\n{'=' * 74}\n{tieu_de}\n{'=' * 74}")
    print(f"  Token ({len(tokens)}): {' '.join(tokens)}\n")

    print(f"  {'Token':<20} {'Diem':>8}   Ghi chu")
    print(f"  {'-' * 20} {'-' * 8}   {'-' * 28}")
    tra_duoc = 0
    for tok in tokens:
        key = tok.lower()
        if key in model.lexicon:
            diem = model.lexicon[key]
            tra_duoc += 1
            manh = "  <== manh" if abs(diem) > 0.3 else ""
            print(f"  {tok:<20} {diem:>+8.4f}   {'duong' if diem > 0 else 'am'}{manh}")
        else:
            print(f"  {tok:<20} {'—':>8}   KHONG co trong tu dien")

    nhan, prob, mean_score, coverage = du_doan(model, uid)
    print(f"\n  mean_score = {mean_score:+.4f}   (trung binh {tra_duoc} token tra cuu duoc)")
    print(f"  coverage   = {coverage:.4f}   ({tra_duoc}/{len(tokens)} token)")
    print(f"\n  >> DU DOAN : {TEN_NHAN[nhan].upper()}")
    print("     Xac suat : " + "  ".join(f"{TEN_NHAN[i]}={prob[i]:.3f}" for i in range(3)))
    if nhan_vang is not None:
        dung = "DUNG" if nhan == nhan_vang else "SAI"
        print(f"     Nhan vang: {TEN_NHAN[nhan_vang].upper()}   -> {dung}")

    del model.uid_to_tokens[uid]
    model._cache.pop(uid, None)


def bo_dau(s: str) -> str:
    """'tuyệt_vời' -> 'tuyet_voi'. De nguoi dung go khong dau van tra duoc."""
    import unicodedata

    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()


def tra_tu(model: LexiconModel, tu: str) -> None:
    key = tu.lower().strip()
    print(f"\n  Tra tu: {key!r}")

    if key in model.lexicon:
        diem = model.lexicon[key]
        print(f"    diem = {diem:+.4f}  ({'tich cuc' if diem > 0 else 'tieu cuc'})")
        return

    # Go khong dau van phai tra duoc — nguoi Viet hay go tat.
    khong_dau = bo_dau(key)
    trung = [(k, v) for k, v in model.lexicon.items() if bo_dau(k) == khong_dau]
    if trung:
        print("    (go khong dau — tim thay trong tu dien:)")
        for k, v in trung:
            print(f"    {k:<24} diem = {v:+.4f}  ({'tich cuc' if v > 0 else 'tieu cuc'})")
        return

    print("    KHONG co trong tu dien.")
    # Chi goi y tu du dai va thuc su chua chuoi con — tranh tra ve rac nhu '_', 'e'
    gan = [k for k in model.lexicon if len(k) >= 3 and (khong_dau in bo_dau(k) or bo_dau(k) in khong_dau)]
    if gan:
        print(f"    Tu gan giong: {', '.join(sorted(gan, key=len)[:8])}")
    elif "_" not in key:
        print("    Goi y: tu ghep trong tu dien dung dau '_', vi du 'tuyet_voi'.")


def xem_top(model: LexiconModel, k: int) -> None:
    sap = sorted(model.lexicon.items(), key=lambda x: -x[1])
    print(f"\n  {k} tu DUONG nhat:")
    for tu, diem in sap[:k]:
        print(f"    {diem:+.4f}  {tu}")
    print(f"\n  {k} tu AM nhat:")
    for tu, diem in sap[-k:][::-1]:
        print(f"    {diem:+.4f}  {tu}")


def xem_uid(model: LexiconModel, uid: str) -> None:
    for split in ("test", "dev", "train"):
        path = REPO_ROOT / "data" / "processed" / f"visfd_{split}.jsonl"
        if not path.exists():
            continue
        for r in read_jsonl(path):
            if r["uid"] == uid:
                xem_cau(model, r["tokens"], f"{uid}  (khia canh = {r['aspect']})", r["label"])
                print(f"\n  Cau goc: {r['text'][:200]}")
                return
    print(f"  Khong tim thay uid {uid!r}")


def xem_ca_sai(model: LexiconModel, k: int) -> None:
    """Liet ke ca mo hinh doan SAI — nguyen lieu cho muc 5.3 cua bao cao."""
    path = REPO_ROOT / "data" / "processed" / "visfd_test.jsonl"
    if not path.exists():
        print("  Chua co data/processed/visfd_test.jsonl")
        return

    sai = []
    for r in read_jsonl(path):
        model.uid_to_tokens.setdefault(r["uid"], r["tokens"])
        nhan, _, mean_score, coverage = du_doan(model, r["uid"])
        if nhan != r["label"]:
            sai.append((r, nhan, mean_score, coverage))
        if len(sai) >= k:
            break

    print(f"\n  {len(sai)} ca dau tien mo hinh doan SAI tren tap test:\n")
    for r, nhan, mean_score, coverage in sai:
        print(f"  [{r['uid']}]  khia canh={r['aspect']}")
        print(f"    vang={TEN_NHAN[r['label']]:<11} doan={TEN_NHAN[nhan]:<11} "
              f"mean={mean_score:+.3f} cov={coverage:.2f}")
        print(f"    {r['text'][:110]}\n")


# --- Che do tuong tac ---------------------------------------------------------

HUONG_DAN = """
  Go mot cau tieng Viet de xem mo hinh nghi gi. Cac lenh khac:

    :tu <tu>        tra mot tu trong tu dien       vi du  :tu tuyet_voi
    :top [N]        N tu duong/am nhat             vi du  :top 15
    :uid <uid>      chay tren mot Example that     vi du  :uid visfd-test-00000-BATTERY
    :sai [N]        N ca mo hinh doan sai
    :help           in lai huong dan nay
    :q              thoat
"""


def tuong_tac(model: LexiconModel, tach_tu: BoTachTu) -> None:
    print(HUONG_DAN)
    while True:
        try:
            dong = input("\n  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not dong:
            continue
        if dong in (":q", ":quit", ":exit"):
            return
        if dong == ":help":
            print(HUONG_DAN)
        elif dong.startswith(":tu "):
            tra_tu(model, dong[4:])
        elif dong.startswith(":top"):
            phan = dong.split()
            xem_top(model, int(phan[1]) if len(phan) > 1 else 10)
        elif dong.startswith(":uid "):
            xem_uid(model, dong[5:].strip())
        elif dong.startswith(":sai"):
            phan = dong.split()
            xem_ca_sai(model, int(phan[1]) if len(phan) > 1 else 5)
        elif dong.startswith(":"):
            print(f"  Khong hieu lenh {dong!r}. Go :help de xem huong dan.")
        else:
            xem_cau(model, tach_tu.tach(dong), f"Cau ban go: {dong}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--text", help="Chay tren mot cau roi thoat")
    parser.add_argument("--word", help="Tra mot tu trong tu dien roi thoat")
    parser.add_argument("--top", type=int, help="In N tu duong/am nhat roi thoat")
    parser.add_argument("--uid", help="Chay tren mot Example that roi thoat")
    parser.add_argument("--sai", type=int, help="In N ca mo hinh doan sai roi thoat")
    args = parser.parse_args(argv)

    print("\n  Dang nap LexiconModel ...")
    model = nap_mo_hinh()
    print(f"  Tu dien: {len(model.lexicon):,} token")

    if args.word:
        tra_tu(model, args.word)
    elif args.top:
        xem_top(model, args.top)
    elif args.uid:
        xem_uid(model, args.uid)
    elif args.sai:
        xem_ca_sai(model, args.sai)
    elif args.text:
        xem_cau(model, BoTachTu().tach(args.text), f"Cau: {args.text}")
    else:
        tuong_tac(model, BoTachTu())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
