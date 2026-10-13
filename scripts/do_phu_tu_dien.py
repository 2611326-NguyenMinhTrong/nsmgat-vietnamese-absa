"""[CD1.12b] Đo độ phủ của một từ điển cảm xúc có sẵn trên văn bản UIT-ViSFD đã tách từ.

Dùng để có con số thật cho câu "tài nguyên cảm xúc tiếng Việt công khai phủ được bao nhiêu" ở mục
2.4 và 4.3 của báo cáo, thay cho một nhận định không đo.

    python scripts/do_phu_tu_dien.py --vswn duong/dan/VietSentiWordnet_Ver1.3.5.txt
    python scripts/do_phu_tu_dien.py --senticnet duong/dan/senticnet.py
    python scripts/do_phu_tu_dien.py --vswn ... --senticnet ...

Hai file từ điển KHÔNG nằm trong repo này:
- VietSentiWordNet: kho của tác giả, github.com/sonvx/VietSentiWordNet, thư mục VietSentiWordNet/dicts/.
- SenticNet tiếng Việt: sentic.net/downloads, mục VIETNAMESE RESOURCES, file senticnet_vi.zip. Giấy phép
  chỉ cho dùng phi thương mại.

Độ phủ = số lượt từ tra được / tổng số lượt từ, đếm trên các MẪU (một bình luận có ba khía cạnh được
đếm ba lần, đúng như cách mô hình từ điển nhìn dữ liệu). So khớp theo từ đã tách, viết thường.

Bản SenticNet tiếng Việt ghi khái niệm KHÔNG DẤU (`tot`, `a_xit_uric`), nên từ của dữ liệu phải bỏ dấu
trước khi tra. Bỏ dấu làm nhiều từ khác nghĩa trùng nhau (`tệ`, `tê`, `tế` cùng thành `te`), vì vậy độ
phủ đo theo cách này là cận trên của số lượt tra đúng nghĩa.

Con số của từ điển tự suy ra từ tập huấn luyện được in cạnh để đối chiếu; các con số không so được
trực tiếp về chất lượng, vì từ điển tự suy ra chứa cả từ không mang cảm xúc.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MAU_MUC_TU = re.compile(r"([^#\t]+)#\d+")
MAU_SENTICNET = re.compile(r"^senticnet\['(.+?)'\] = \[(.*)\]\s*$")
VI_TRI_DIEM_SENTICNET = 7  # senticnet['khái niệm'] = [4 trục cảm xúc, 2 cảm xúc, nhãn cực tính, ĐIỂM cực tính, 5 khái niệm gần]


def bo_dau(chu: str) -> str:
    """Viết thường và bỏ dấu tiếng Việt: `Tốt` -> `tot`, `đẹp` -> `dep`."""
    chu = chu.lower().replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", chu) if not unicodedata.combining(c))


def doc_vswn(duong_dan: Path) -> Tuple[int, Set[str]]:
    """Trả về (số tập đồng nghĩa, tập mục từ viết thường, âm tiết nối bằng gạch dưới)."""
    so_dong, muc = 0, set()
    with duong_dan.open(encoding="utf-8") as fh:
        for dong in fh:
            o = dong.rstrip("\n").split("\t")
            if dong.startswith("#") or len(o) < 5:
                continue
            so_dong += 1
            for m in MAU_MUC_TU.finditer(o[4]):
                muc.add(m.group(1).strip().lower().replace(" ", "_"))
    return so_dong, muc


def doc_senticnet(duong_dan: Path) -> Dict[str, float]:
    """{khái niệm: điểm cực tính trong [-1, 1]} từ file senticnet.py của SenticNet."""
    ra: Dict[str, float] = {}
    with duong_dan.open(encoding="utf-8") as fh:
        for dong in fh:
            m = MAU_SENTICNET.match(dong)
            if not m:
                continue
            o = m.group(2).split(", ")
            try:
                ra[m.group(1)] = float(o[VI_TRI_DIEM_SENTICNET])
            except (IndexError, ValueError):
                continue
    return ra


def do_phu(jsonl: Path, muc: Iterable[str], chuan_hoa: Optional[Callable[[str], str]] = None) -> Dict[str, float]:
    muc = set(muc)
    chuan_hoa = chuan_hoa or str.lower
    tong = co = so_mau = mau_co = 0
    gap: Set[str] = set()
    with jsonl.open(encoding="utf-8") as fh:
        for dong in fh:
            tu = [chuan_hoa(t) for t in json.loads(dong)["tokens"]]
            trung = [t for t in tu if t in muc]
            tong += len(tu)
            co += len(trung)
            so_mau += 1
            mau_co += bool(trung)
            gap.update(trung)
    return {"luot_tu": tong, "ti_le_phu": co / tong if tong else 0.0, "ti_le_mau_co_tu": mau_co / so_mau if so_mau else 0.0, "so_muc_gap": len(gap)}


def in_do_phu(du_lieu: Path, muc: Iterable[str], chuan_hoa=None, tu_suy: Optional[Set[str]] = None) -> None:
    for sp in ("train", "dev", "test"):
        p = du_lieu / f"visfd_{sp}.jsonl"
        if not p.exists():
            continue
        r = do_phu(p, muc, chuan_hoa)
        dong = (f"  {sp}: phủ {r['ti_le_phu'] * 100:.2f} % số lượt từ | {r['so_muc_gap']} mục có mặt | "
                f"{r['ti_le_mau_co_tu'] * 100:.1f} % số mẫu có ít nhất một từ tra được")
        if tu_suy is not None:
            dong += f" | từ điển tự suy ra phủ {do_phu(p, tu_suy)['ti_le_phu'] * 100:.2f} %"
        print(dong.replace(".", ","))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đo độ phủ của một từ điển cảm xúc có sẵn trên UIT-ViSFD.")
    ap.add_argument("--vswn", type=Path, help="file VietSentiWordnet_Ver*.txt của tác giả")
    ap.add_argument("--senticnet", type=Path, help="file senticnet.py trong senticnet_vi.zip")
    ap.add_argument("--du-lieu", type=Path, default=Path("data/processed"), help="thư mục chứa visfd_{train,dev,test}.jsonl")
    ap.add_argument("--tu-suy", type=Path, default=Path("data/lexicon_from_train.json"), help="từ điển tự suy ra từ tập huấn luyện, để đối chiếu")
    a = ap.parse_args(argv)
    if not a.vswn and not a.senticnet:
        ap.error("cần ít nhất một trong hai: --vswn, --senticnet")

    tu_suy = set(json.loads(a.tu_suy.read_text(encoding="utf-8"))) if a.tu_suy.exists() else None
    if a.vswn:
        so_dong, muc = doc_vswn(a.vswn)
        print(f"VietSentiWordNet ({a.vswn.name}): {so_dong} tập đồng nghĩa, {len(muc)} mục từ khác nhau")
        in_do_phu(a.du_lieu, muc, None, tu_suy)
    if a.senticnet:
        sn = doc_senticnet(a.senticnet)
        co_dau = sum(any(ord(c) > 127 for c in k) for k in sn)
        print(f"SenticNet ({a.senticnet.name}): {len(sn)} khái niệm, trong đó {sum('_' not in k for k in sn)} khái niệm một từ, "
              f"{co_dau} khái niệm có ký tự có dấu. Tra sau khi BỎ DẤU từ của dữ liệu:")
        in_do_phu(a.du_lieu, sn, bo_dau, tu_suy)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
