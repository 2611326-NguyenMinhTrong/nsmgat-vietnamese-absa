"""[CD1.3] Chan doan chat luong do thi cu phap truoc khi chay ASGCN / Sentic-GCN.

VI SAO CAN SCRIPT NAY
---------------------
Rui ro R3 trong pLan/chuyende1/PLAN_CHUYENDE1.md: "Sentic-GCN thua PhoBERT qua
nhieu -> kiem tra do thi cu phap TRUOC khi ket luan. Day gan nhu luon la loi
cai dat, khong phai ket luan khoa hoc."

Neu khong do truoc, khi asgcn/senticgcn cho ket qua thap se co HAI cach giai
thich khong phan biet duoc:
  (a) phuong phap do thi khong hop voi bai toan  -> ket luan khoa hoc
  (b) cay phu thuoc dau vao qua kem                -> loi du lieu

Script nay bien (b) thanh con so do duoc, de loai tru truoc khi ket luan (a).

CHI SO QUAN TRONG NHAT: ti le Example co do thi BI CHIA CAT (>1 thanh phan
lien thong). GCN lan truyen theo canh — neu token khia canh va tu cam xuc nam
o hai thanh phan roi nhau thi them bao nhieu lop GCN cung khong noi duoc chung.

GAP-007 phuong an C (chot 06/09/2026): script cung do luon chi phi cua bien the
`asgcn_linked` (link_roots=True) so voi `asgcn` (link_roots=False), de biet truoc
bien the noi root "dat" hon bao nhieu canh.

Ket qua ghi ra results/syntactic_graph_stats.json (KHONG phai metrics.json —
schema do da dong bang o S0.4, xem PLAN_CHUYENDE1.md muc 6.4).

Dung:
    python scripts/diagnose_syntactic_graph.py
    python scripts/diagnose_syntactic_graph.py --split train --show 5
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nsmgat.graphs.syntactic import ETYPE_SELF, SyntacticGraphBuilder  # noqa: E402
from nsmgat.schema import Example  # noqa: E402

DATA_DIR = REPO_ROOT / "data" / "processed"
OUT_PATH = REPO_ROOT / "results" / "syntactic_graph_stats.json"
SPLITS = ("train", "dev", "test")


def load_split(split: str) -> list[Example]:
    path = DATA_DIR / f"visfd_{split}.jsonl"
    with path.open(encoding="utf-8") as fh:
        return [Example.from_dict(json.loads(line)) for line in fh]


def count_components(heads: list[int]) -> int:
    """So thanh phan lien thong khi coi cay phu thuoc la do thi vo huong."""
    n = len(heads)
    if n == 0:
        return 0

    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for dep, head in enumerate(heads):
        if head == -1 or not (0 <= head < n) or head == dep:
            continue
        a, b = find(dep), find(head)
        if a != b:
            parent[a] = b

    return len({find(i) for i in range(n)})


def analyse(examples: list[Example], builder: SyntacticGraphBuilder) -> dict:
    n_tokens, n_edges, n_roots, n_comps = [], [], [], []
    n_edges_linked = []
    deprels: Counter[str] = Counter()
    head_ngoai_pham_vi = self_head = 0

    # GAP-007 phuong an C: do luon chi phi cua bien the noi root, de biet
    # asgcn_linked "dat" hon asgcn bao nhieu truoc khi chay that.
    builder_linked = SyntacticGraphBuilder(link_roots=True)

    for ex in examples:
        n = len(ex.tokens)
        edges = builder.build(ex)

        n_tokens.append(n)
        n_edges.append(len(edges))
        n_edges_linked.append(len(builder_linked.build(ex)))
        n_roots.append(sum(1 for h in ex.heads if h == -1))
        n_comps.append(count_components(ex.heads))
        deprels.update(ex.deprels)

        for dep, head in enumerate(ex.heads):
            if head != -1 and not (0 <= head < n):
                head_ngoai_pham_vi += 1
            elif head == dep:
                self_head += 1

        # Bat bien: moi token dung mot self-loop
        assert sum(1 for e in edges if e.etype == ETYPE_SELF) == n, ex.uid

    tong = len(examples)
    phan_bo_comp = Counter(n_comps)
    bi_chia_cat = sum(v for k, v in phan_bo_comp.items() if k > 1)

    return {
        "so_example": tong,
        "token": {
            "trung_binh": round(statistics.mean(n_tokens), 2),
            "trung_vi": statistics.median(n_tokens),
            "lon_nhat": max(n_tokens),
        },
        "canh": {
            "trung_binh": round(statistics.mean(n_edges), 2),
            "tong": sum(n_edges),
        },
        "canh_bien_the_noi_root": {
            "trung_binh": round(statistics.mean(n_edges_linked), 2),
            "tong": sum(n_edges_linked),
            "canh_them_vao": sum(n_edges_linked) - sum(n_edges),
            "ti_le_tang": round((sum(n_edges_linked) / sum(n_edges) - 1) * 100, 1),
        },
        "root_moi_example": {
            "trung_binh": round(statistics.mean(n_roots), 2),
            "lon_nhat": max(n_roots),
            "phan_bo": dict(sorted(Counter(n_roots).items())[:10]),
        },
        "thanh_phan_lien_thong": {
            "trung_binh": round(statistics.mean(n_comps), 2),
            "lon_nhat": max(n_comps),
            "phan_bo": dict(sorted(phan_bo_comp.items())[:10]),
            "so_example_bi_chia_cat": bi_chia_cat,
            "ti_le_bi_chia_cat": round(bi_chia_cat / tong * 100, 1),
        },
        "du_lieu_bat_thuong": {
            "head_ngoai_pham_vi": head_ngoai_pham_vi,
            "token_tu_tro_vao_minh": self_head,
        },
        "deprel_pho_bien": dict(deprels.most_common(15)),
        "so_loai_deprel": len(deprels),
    }


def show_examples(examples: list[Example], k: int) -> None:
    """In vai cay phu thuoc de xac minh bang mat — phan con lai cua rui ro R3."""
    print(f"\n{'=' * 78}\n{k} CAY PHU THUOC DAU TIEN — xac minh bang mat\n{'=' * 78}")
    for ex in examples[:k]:
        print(f"\n[{ex.uid}]  khia canh={ex.aspect}  nhan={ex.label}")
        print(f"  {ex.text[:150]}")
        print(f"  so thanh phan lien thong: {count_components(ex.heads)}")
        for i, (tok, head, rel) in enumerate(zip(ex.tokens, ex.heads, ex.deprels)):
            muc_tieu = "ROOT" if head == -1 else f"{head}:{ex.tokens[head]}"
            print(f"    {i:3d} {tok:<18} --{rel:<10}--> {muc_tieu}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--split", choices=(*SPLITS, "all"), default="all")
    parser.add_argument("--show", type=int, default=0, help="In N cay phu thuoc de xem bang mat")
    parser.add_argument("-o", "--out", type=Path, default=OUT_PATH)
    args = parser.parse_args(argv)

    builder = SyntacticGraphBuilder()
    splits = SPLITS if args.split == "all" else (args.split,)
    ket_qua = {}

    for split in splits:
        path = DATA_DIR / f"visfd_{split}.jsonl"
        if not path.exists():
            print(f"Khong thay {path} — chay scripts/prepare_data.py truoc", file=sys.stderr)
            return 1

        examples = load_split(split)
        stats = analyse(examples, builder)
        ket_qua[split] = stats

        tp = stats["thanh_phan_lien_thong"]
        print(f"\n--- {split} ---")
        print(f"  Example              : {stats['so_example']:,}")
        print(f"  Token trung binh     : {stats['token']['trung_binh']}")
        linked = stats["canh_bien_the_noi_root"]
        print(f"  Canh trung binh      : {stats['canh']['trung_binh']}"
              f"   (bien the noi root: {linked['trung_binh']}, +{linked['ti_le_tang']}%)")
        print(f"  Root trung binh      : {stats['root_moi_example']['trung_binh']}")
        print(f"  Thanh phan lien thong: {tp['trung_binh']} (toi da {tp['lon_nhat']})")
        print(f"  >> BI CHIA CAT       : {tp['so_example_bi_chia_cat']:,} / {stats['so_example']:,}"
              f"  ({tp['ti_le_bi_chia_cat']}%)")
        bat_thuong = stats["du_lieu_bat_thuong"]
        if any(bat_thuong.values()):
            print(f"  ! Bat thuong         : {bat_thuong}")

        if args.show:
            show_examples(examples, args.show)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(ket_qua, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nOK -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
