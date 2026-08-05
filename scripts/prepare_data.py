"""CLI chuan bi du lieu nsmgat.

Vi du:
    python scripts/prepare_data.py
    python scripts/prepare_data.py --with-vlsp
"""

from __future__ import annotations

import argparse
import collections
from pathlib import Path

from nsmgat.data.loaders import load_visfd, load_vlsp
from nsmgat.data.preprocess import VnCorePipeline, process_all
from nsmgat.schema import LABEL_NAMES
from nsmgat.utils.io import read_jsonl
from nsmgat.utils.logging import get_logger

logger = get_logger(__name__)


def print_stats(domain: str, splits=("train", "dev", "test"), processed_dir: str | Path = "data/processed") -> None:
    processed_dir = Path(processed_dir)
    print(f"\n=== Thong ke {domain} ===")
    for split in splits:
        path = processed_dir / f"{domain}_{split}.jsonl"
        if not path.exists():
            continue
        examples = read_jsonl(path)
        label_counts = collections.Counter(ex["label"] for ex in examples)
        aspect_counts = collections.Counter(ex["aspect"] for ex in examples)
        label_str = ", ".join(
            f"{LABEL_NAMES[k]}={v}" for k, v in sorted(label_counts.items())
        )
        print(f"-- {split}: {len(examples)} Example")
        print(f"   phan bo nhan: {label_str}")
        print(f"   top-10 aspect: {aspect_counts.most_common(10)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chuan bi du lieu nsmgat")
    parser.add_argument(
        "--with-vlsp",
        action="store_true",
        help=(
            "Xu ly them VLSP 2018 (hotel + restaurant). Can tai thu cong "
            "thu muc 'datasets/vlsp2018_hotel' va 'datasets/vlsp2018_restaurant' "
            "tu https://github.com/ds4v/absa-vlsp-2018 vao data/raw/vlsp2018/."
        ),
    )
    args = parser.parse_args()

    try:
        pipeline = VnCorePipeline()
    except RuntimeError as exc:
        print(str(exc))
        raise SystemExit(1)

    process_all("visfd", load_visfd, pipeline=pipeline)
    print_stats("visfd")

    if args.with_vlsp:
        for domain in ("vlsp-hotel", "vlsp-restaurant"):
            def loader_fn(split: str, _domain: str = domain) -> list:
                return load_vlsp(_domain, split)

            try:
                process_all(domain, loader_fn, pipeline=pipeline)
                print_stats(domain)
            except FileNotFoundError as exc:
                logger.warning(f"Bo qua {domain}: {exc}")


if __name__ == "__main__":
    main()
