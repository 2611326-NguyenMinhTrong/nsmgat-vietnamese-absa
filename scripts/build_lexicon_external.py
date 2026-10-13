"""[CD1.6c] Dựng bảng điểm cảm xúc cho `senticgcn` từ một từ điển CÓ SẴN, và kiểm trước khi huấn luyện.

Bậc 5 của thang mô hình (`configs/senticgcn.yaml`) lấy điểm cảm xúc từ `data/lexicon_from_train.json`,
bảng điểm suy ra từ NHÃN của tập huấn luyện. Bài gốc của Sentic-GCN lấy điểm từ SenticNet, một tài
nguyên bên ngoài không biết gì về bộ dữ liệu. Lệnh này dựng bảng điểm từ hai tài nguyên như vậy, để
chạy thêm hai biến thể chỉ khác bậc 5 ở đúng một khoá `model.lexicon_path`:

    configs/senticgcn_senticnet.yaml   SenticNet bản tiếng Việt (sentic.net/downloads, senticnet_vi.zip)
    configs/senticgcn_vswn.yaml        VietSentiWordNet 1.3.5 (github.com/sonvx/VietSentiWordNet)

    python scripts/build_lexicon_external.py senticnet --nguon duong/dan/senticnet.py
    python scripts/build_lexicon_external.py vswn --nguon duong/dan/VietSentiWordnet_Ver1.3.5.txt
    python scripts/build_lexicon_external.py kiem --tu-dien data/processed/lexicon_senticnet_vi.json

Đầu ra là JSON phẳng {từ: điểm trong [-1, 1]}, đúng dạng `SenticGCNModel` đọc. File nằm trong
data/processed/ và KHÔNG lên GitHub: SenticNet chỉ cho dùng phi thương mại, kho VietSentiWordNet không
ghi giấy phép. Khi chạy trên Colab, tải file .json lên Drive/nsmgat/data/processed/.

SENTICNET TIẾNG VIỆT VIẾT KHÔNG DẤU
Khái niệm trong bản tiếng Việt là `tot`, `dep`, `a_xit_uric`. Mô hình thì tra đúng mặt chữ của từ
trong dữ liệu (`Tốt` rồi `tốt`). Lệnh `senticnet` vì vậy đi qua mọi từ khác nhau của dữ liệu đã tách
từ, bỏ dấu, tra SenticNet, rồi ghi {từ có dấu viết thường: điểm}. Làm vậy tương đương với bỏ dấu lúc
tra, mà không phải sửa mã của mô hình. Lệnh chỉ đọc trường `tokens` của cả ba phần dữ liệu, không đọc
nhãn, nên không có gì của tập kiểm tra đi vào bảng điểm ngoài mặt chữ của từ.
Hệ quả phải nêu khi báo cáo: bỏ dấu làm từ khác nghĩa trùng nhau. `máy` tra thành `may` và nhận
điểm -0,951. Bảng điểm này vì vậy chứa nhiễu có hệ thống, không chỉ thiếu độ phủ.

VIETSENTIWORDNET
Mỗi dòng là một tập đồng nghĩa có PosScore và NegScore. Điểm của một mục từ là trung bình của
(PosScore - NegScore) trên mọi tập đồng nghĩa chứa nó, không phân biệt từ loại. Mục từ nhiều âm tiết
được nối bằng gạch dưới cho khớp cách tách từ của VnCoreNLP.

VÌ SAO PHẢI CHẠY `kiem` TRƯỚC
Công thức (7) của bài chia mỗi hàng của ma trận kề cho (E_i + 1), với E_i là TỔNG CÓ DẤU của trọng
số. Mẫu số này có thể bằng 0. `GCNLayer` có một dây bẫy: |mẫu số| < 1e-6 thì dừng huấn luyện với
thông báo lỗi, thay vì cho ra NaN. Điểm của SenticNet chỉ có ba chữ số thập phân nên tổng trùng đúng
-1 là chuyện có thể xảy ra. `kiem` dựng ma trận kề bằng CHÍNH lớp mô hình cho mọi câu của ba phần dữ
liệu và đếm; mã thoát 1 nghĩa là bảng điểm này sẽ làm lần huấn luyện dừng giữa chừng.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))

import do_phu_tu_dien as dp  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DU_LIEU_MAC_DINH = Path("data/processed")
RA_MAC_DINH = {"senticnet": Path("data/processed/lexicon_senticnet_vi.json"), "vswn": Path("data/processed/lexicon_vswn.json")}
PHAN = ("train", "dev", "test")
NGUONG_GAN_KHONG = 1e-3  # dưới mức này một hàng bị khuếch đại hơn 1000 lần


def tu_cua_du_lieu(du_lieu: Path) -> List[str]:
    """Mọi từ khác nhau, viết thường, trong các phần dữ liệu đã tách từ. Chỉ đọc trường `tokens`."""
    ra = set()
    for sp in PHAN:
        p = du_lieu / f"visfd_{sp}.jsonl"
        if not p.exists():
            continue
        with p.open(encoding="utf-8") as fh:
            for dong in fh:
                ra.update(t.lower() for t in json.loads(dong)["tokens"])
    return sorted(ra)


def tu_senticnet(sn: Dict[str, float], tu_vung: Iterable[str]) -> Dict[str, float]:
    """{từ của dữ liệu: điểm của khái niệm SenticNet trùng mặt chữ sau khi bỏ dấu}."""
    ra = {}
    for t in sorted(set(tu_vung)):
        k = dp.bo_dau(t)
        if k in sn:
            ra[t] = sn[k]
    return ra


def doc_vswn_diem(duong_dan: Path) -> Dict[str, float]:
    """{mục từ: trung bình (PosScore - NegScore) trên các tập đồng nghĩa chứa nó}."""
    gom: Dict[str, List[float]] = defaultdict(list)
    with duong_dan.open(encoding="utf-8") as fh:
        for dong in fh:
            o = dong.rstrip("\n").split("\t")
            if dong.startswith("#") or len(o) < 5:
                continue
            try:
                diem = float(o[2]) - float(o[3])
            except ValueError:
                continue
            for m in dp.MAU_MUC_TU.finditer(o[4]):
                gom[m.group(1).strip().lower().replace(" ", "_")].append(diem)
    return {k: sum(v) / len(v) for k, v in sorted(gom.items())}


def bam_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ghi(tu_dien: Dict[str, float], ra: Path, nguon: Path, cach_dung: str) -> str:
    """Ghi bảng điểm (tất định: khoá xếp thứ tự, xuống dòng kiểu LF) và một file mô tả đi kèm. Trả về sha256."""
    noi_dung = json.dumps({k: round(v, 6) for k, v in sorted(tu_dien.items())}, ensure_ascii=False, indent=0) + "\n"
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_bytes(noi_dung.encode("utf-8"))  # write_bytes: Windows không đổi LF thành CRLF, sha256 giống trên Colab
    bam = bam_file(ra)
    gia_tri = list(tu_dien.values())
    mo_ta = {
        "tao_ngay": dt.date.today().strftime("%d/%m/%Y"), "nguon": nguon.name, "sha256_nguon": bam_file(nguon),
        "sha256_bang_diem": bam, "so_muc": len(tu_dien), "so_muc_duong": sum(v > 0 for v in gia_tri),
        "so_muc_am": sum(v < 0 for v in gia_tri), "so_muc_bang_0": sum(v == 0 for v in gia_tri),
        "diem_nho_nhat": min(gia_tri), "diem_lon_nhat": max(gia_tri), "cach_dung": cach_dung,
    }
    ra.with_suffix(".meta.json").write_text(json.dumps(mo_ta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return bam


def in_do_phu(tu_dien: Dict[str, float], du_lieu: Path) -> None:
    for sp in PHAN:
        p = du_lieu / f"visfd_{sp}.jsonl"
        if p.exists():
            r = dp.do_phu(p, tu_dien)
            print(f"  {sp}: phủ {r['ti_le_phu'] * 100:.2f} % số lượt từ | {r['so_muc_gap']} mục có mặt | "
                  f"{r['ti_le_mau_co_tu'] * 100:.1f} % số mẫu có ít nhất một từ tra được".replace(".", ","))


def thong_ke_mau_so(tu_dien: Path, du_lieu: Path, phan: Iterable[str] = PHAN) -> Dict[str, dict]:
    """Mẫu số chuẩn hoá (E_i + 1) của công thức (7), tính bằng chính `SenticGCNModel`, đếm theo MẪU.

    Ma trận kề chỉ phụ thuộc câu, nên mỗi câu được tính một lần rồi nhân với số mẫu dùng câu đó.
    Tính ở float32 như lúc huấn luyện, vì dây bẫy của `GCNLayer` so trên chính giá trị float32.
    """
    import torch
    from transformers import RobertaConfig, RobertaModel

    sys.path.insert(0, str(GOC / "src"))
    from nsmgat.models.layers import EPS_MAU_SO
    from nsmgat.models.senticgcn import SenticGCNModel

    ra: Dict[str, dict] = {}
    for sp in phan:
        p = du_lieu / f"visfd_{sp}.jsonl"
        if not p.exists():
            continue
        # Bộ mã hoá tí hon: ở đây chỉ cần phần dựng ma trận kề của mô hình, không cần PhoBERT thật.
        nho = RobertaModel(RobertaConfig(vocab_size=64001, hidden_size=32, num_hidden_layers=1, num_attention_heads=2,
                                         intermediate_size=64, max_position_embeddings=258))
        m = SenticGCNModel({"data": {f"{sp}_path": str(p)},
                            "model": {"dropout": 0.1, "gcn_layers": 2, "normalize": "row_plus1", "lexicon_path": str(tu_dien)}}, encoder=nho)
        so_mau_cua_cau = Counter(m.uid_to_khoa.values())
        dai_dien = {}
        for uid, khoa in m.uid_to_khoa.items():
            dai_dien.setdefault(khoa, uid)
        r = {"so_mau": len(m.uid_to_khoa), "so_tu": 0, "tu_mau_so_khong_duong": 0, "mau_dinh": 0, "tu_gan_khong": 0,
             "tu_kich_bay": 0, "mau_kich_bay": 0, "mau_so_nho_nhat": float("inf"), "canh_am": 0, "so_canh": 0}
        for khoa, uid in dai_dien.items():
            k = so_mau_cua_cau[khoa]
            n = len(m.khoa_to_diem[khoa])
            a = m._ma_tran_ke([uid], n, "cpu", torch.float32)[0]
            mau = a.sum(dim=-1) + 1.0
            tri = mau.abs()
            r["so_tu"] += n * k
            r["tu_mau_so_khong_duong"] += int((mau <= 0).sum()) * k
            r["mau_dinh"] += k * bool((mau <= 0).any())
            r["tu_gan_khong"] += int((tri < NGUONG_GAN_KHONG).sum()) * k
            r["tu_kich_bay"] += int((tri < EPS_MAU_SO).sum()) * k
            r["mau_kich_bay"] += k * bool((tri < EPS_MAU_SO).any())
            r["mau_so_nho_nhat"] = min(r["mau_so_nho_nhat"], float(tri.min()))
            r["canh_am"] += int((a < 0).sum()) * k
            r["so_canh"] += int((a != 0).sum()) * k
        ra[sp] = r
    return ra


def cmd_kiem(tu_dien: Path, du_lieu: Path) -> int:
    td = json.loads(tu_dien.read_text(encoding="utf-8"))
    print(f"{tu_dien}: {len(td)} mục | sha256 {bam_file(tu_dien)}")
    in_do_phu(td, du_lieu)
    tk = thong_ke_mau_so(tu_dien, du_lieu)
    hong = False
    print("Mẫu số chuẩn hoá (E_i + 1), đếm theo mẫu:")
    for sp, r in tk.items():
        hong = hong or r["tu_kich_bay"] > 0
        print((f"  {sp}: {r['tu_mau_so_khong_duong']} từ có mẫu số <= 0 ({r['tu_mau_so_khong_duong'] / r['so_tu'] * 100:.3f} %) | "
               f"{r['mau_dinh']} mẫu dính ({r['mau_dinh'] / r['so_mau'] * 100:.2f} %) | |mẫu số| nhỏ nhất {r['mau_so_nho_nhat']:.1e} | "
               f"{r['tu_gan_khong']} từ có |mẫu số| < {NGUONG_GAN_KHONG:g} | {r['tu_kich_bay']} từ kích dây bẫy, thuộc {r['mau_kich_bay']} mẫu | "
               f"{r['canh_am'] / r['so_canh'] * 100:.2f} % số ô khác 0 mang trọng số âm").replace(".", ","))
    if hong:
        print("KHÔNG HUẤN LUYỆN ĐƯỢC với công thức gốc: có từ mà mẫu số bằng 0, `GCNLayer` sẽ dừng với ValueError.")
    else:
        print("Không từ nào kích dây bẫy: huấn luyện chạy được với công thức gốc.")
    return 1 if hong else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Dựng bảng điểm cảm xúc cho senticgcn từ một từ điển có sẵn, và kiểm trước khi huấn luyện.")
    sub = ap.add_subparsers(dest="lenh", required=True)
    p = sub.add_parser("senticnet", help="từ senticnet.py của bản SenticNet tiếng Việt")
    p.add_argument("--nguon", type=Path, required=True, help="file senticnet.py trong senticnet_vi.zip")
    p.add_argument("--du-lieu", type=Path, default=DU_LIEU_MAC_DINH, help="thư mục chứa visfd_{train,dev,test}.jsonl")
    p.add_argument("--ra", type=Path, default=RA_MAC_DINH["senticnet"])
    p = sub.add_parser("vswn", help="từ file VietSentiWordnet_Ver*.txt")
    p.add_argument("--nguon", type=Path, required=True, help="file VietSentiWordnet_Ver1.3.5.txt của tác giả")
    p.add_argument("--du-lieu", type=Path, default=DU_LIEU_MAC_DINH, help="chỉ dùng để in độ phủ")
    p.add_argument("--ra", type=Path, default=RA_MAC_DINH["vswn"])
    p = sub.add_parser("kiem", help="đo độ phủ và mẫu số chuẩn hoá của một bảng điểm; mã thoát 1 nếu huấn luyện sẽ dừng giữa chừng")
    p.add_argument("--tu-dien", type=Path, required=True, help="file .json do lệnh senticnet hoặc vswn ghi ra")
    p.add_argument("--du-lieu", type=Path, default=DU_LIEU_MAC_DINH)
    a = ap.parse_args(argv)

    if a.lenh == "kiem":
        return cmd_kiem(a.tu_dien, a.du_lieu)
    if a.lenh == "senticnet":
        sn = dp.doc_senticnet(a.nguon)
        tu_vung = tu_cua_du_lieu(a.du_lieu)
        if not tu_vung:
            print(f"DỪNG: không đọc được từ nào trong {a.du_lieu}. Bản SenticNet không dấu cần từ vựng của dữ liệu để dựng bảng điểm.")
            return 1
        td = tu_senticnet(sn, tu_vung)
        cach = "tra khái niệm SenticNet theo mặt chữ đã bỏ dấu của từng từ trong dữ liệu; khoá là từ có dấu viết thường"
        print(f"SenticNet ({a.nguon.name}): {len(sn)} khái niệm; {len(tu_vung)} từ khác nhau trong dữ liệu, tra được {len(td)}.")
    else:
        td = doc_vswn_diem(a.nguon)
        cach = "điểm = trung bình (PosScore - NegScore) trên các tập đồng nghĩa chứa mục từ; âm tiết nối bằng gạch dưới"
        print(f"VietSentiWordNet ({a.nguon.name}): {len(td)} mục từ.")
    if not td:
        print("DỪNG: bảng điểm rỗng, kiểm lại file nguồn.")
        return 1
    bam = ghi(td, a.ra, a.nguon, cach)
    print(f"Đã ghi {a.ra} ({len(td)} mục) và {a.ra.with_suffix('.meta.json').name}")
    print(f"sha256: {bam}")
    in_do_phu(td, a.du_lieu)
    print(f"Bước tiếp: python scripts/build_lexicon_external.py kiem --tu-dien {a.ra.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
