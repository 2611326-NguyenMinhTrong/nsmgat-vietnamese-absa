"""[CD1.7] Mốc tham chiếu bằng mô hình ngôn ngữ lớn, gọi qua API, trên một tập con của tập kiểm tra.

    python scripts/eval_llm.py chon                    # rút 500 mẫu phân tầng, ghi results/llm_subset_uids.json
    python scripts/eval_llm.py xem                     # in câu lệnh mẫu và độ dài; KHÔNG gọi API
    python scripts/eval_llm.py kiem                    # kiểm khoá và tên mô hình; một lần gọi không tốn phí
    python scripts/eval_llm.py chay --che-do zs --thu 5        # gọi thử 5 mẫu, in số token thật
    python scripts/eval_llm.py chay --che-do zs                # zero-shot, một lần chạy
    python scripts/eval_llm.py chay --che-do fs --seed 42      # few-shot với bộ ví dụ rút bằng seed 42
    python scripts/eval_llm.py bang                    # bảng so với sáu mô hình trên CÙNG tập con

Khoá API đọc từ biến môi trường ghi trong configs/llm.yaml (mặc định OPENAI_API_KEY).
Khoá không được ghi vào file hay in ra màn hình ở bất kỳ bước nào.

BA ĐIỀU PHẢI NÓI RÕ KHI ĐƯA VÀO BÁO CÁO
----------------------------------------
1. Kết quả tính trên một tập con (mặc định 500 mẫu), không phải cả tập kiểm tra. Sáu mô hình
   đã huấn luyện được chấm lại trên đúng tập con đó ở lệnh `bang` để so cùng mẫu.
2. Zero-shot chạy MỘT lần: ở nhiệt độ 0, chạy lại cho gần như cùng kết quả, nên độ lệch chuẩn
   giữa các lần chạy không có nghĩa (GAP-003). Few-shot chạy ba lần với ba BỘ VÍ DỤ khác nhau
   (seed 42, 1337, 2024 dùng để rút ví dụ); độ lệch chuẩn khi đó đo độ nhạy với việc chọn ví dụ.
3. Mô hình sau API có thể đổi mà không báo. File llm_meta.json ghi tên phiên bản và mã
   system_fingerprint mà API trả về cùng ngày gọi. Kết quả không tái lập tuyệt đối được.

Mọi câu trả lời thô được lưu ở llm_raw.jsonl của từng lần chạy. File đó cũng là bộ nhớ đệm:
chạy lại không gọi lại những mẫu đã có, nên không tốn thêm phí.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import random
import re
import statistics
import sys
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import yaml

for _luong in (sys.stdout, sys.stderr):  # thong bao loi cung phai in duoc tieng Viet tren console Windows
    if hasattr(_luong, "reconfigure"):
        _luong.reconfigure(encoding="utf-8", errors="replace")

CAU_HINH = Path("configs/llm.yaml")
SEED_VI_DU = (42, 1337, 2024)
KHONG_DOC_DUOC = -1
SO_LOP = 3
# Từ khoá nhận nhãn khi mô hình không trả đúng khuôn. Đã bỏ dấu, viết thường.
TU_KHOA = (("tieu cuc", "negative"), ("trung tinh", "trung lap", "neutral"), ("tich cuc", "positive"))
MO_HINH_SO = ("lexicon", "bilstm", "phobert", "asgcn", "asgcn_linked", "senticgcn")
TEN_HIEN_THI = {"lexicon": "Từ điển cảm xúc", "bilstm": "BiLSTM với attention", "phobert": "PhoBERT tinh chỉnh",
                "asgcn": "ASGCN", "asgcn_linked": "ASGCN nối gốc", "senticgcn": "Sentic-GCN"}


# --- Đọc dữ liệu và cấu hình -------------------------------------------------


def doc_cau_hinh(duong_dan: Path) -> dict:
    return yaml.safe_load(duong_dan.read_text(encoding="utf-8"))


def doc_jsonl(duong_dan: Path) -> List[dict]:
    with duong_dan.open(encoding="utf-8") as fh:
        return [json.loads(d) for d in fh if d.strip()]


def van_tay(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]


def ma_cau(uid: str) -> str:
    return uid.rsplit("-", 1)[0]


# --- Rút tập con và ví dụ ----------------------------------------------------


def chon_tap_con(ban_ghi: Sequence[dict], so_mau: int, seed: int) -> List[str]:
    """Rút phân tầng theo nhãn, giữ tỉ lệ ba nhãn (làm tròn theo phần dư lớn nhất). Trả về uid đã sắp xếp."""
    if so_mau > len(ban_ghi):
        raise ValueError(f"Cần {so_mau} mẫu nhưng tập chỉ có {len(ban_ghi)}")
    theo_nhan: Dict[int, List[str]] = {}
    for r in ban_ghi:
        theo_nhan.setdefault(int(r["label"]), []).append(r["uid"])
    phan = {k: so_mau * len(v) / len(ban_ghi) for k, v in theo_nhan.items()}
    so = {k: int(p) for k, p in phan.items()}
    for k in sorted(phan, key=lambda k: (-(phan[k] - so[k]), k))[: so_mau - sum(so.values())]:
        so[k] += 1
    rng = random.Random(seed)
    chon: List[str] = []
    for k in sorted(theo_nhan):
        chon.extend(rng.sample(sorted(theo_nhan[k]), so[k]))
    return sorted(chon)


def chon_vi_du(train: Sequence[dict], moi_lop: int, seed: int, tu_toi_thieu: int, tu_toi_da: int) -> List[dict]:
    """Rút `moi_lop` ví dụ cho mỗi nhãn từ tập huấn luyện rồi xáo thứ tự. Cùng seed cho cùng bộ ví dụ."""
    rng = random.Random(seed)
    chon: List[dict] = []
    for k in range(SO_LOP):
        ung_vien = sorted((r for r in train if int(r["label"]) == k and tu_toi_thieu <= len(r["tokens"]) <= tu_toi_da),
                          key=lambda r: r["uid"])
        if len(ung_vien) < moi_lop:
            raise ValueError(f"Nhãn {k} chỉ có {len(ung_vien)} ứng viên, cần {moi_lop}")
        chon.extend(rng.sample(ung_vien, moi_lop))
    rng.shuffle(chon)
    return chon


# --- Câu lệnh và đọc câu trả lời ---------------------------------------------


def noi_dung_hoi(cfg: dict, r: dict) -> str:
    return cfg["nguoi_dung"].format(binh_luan=r["text"].strip(), khia_canh=cfg["khia_canh"][r["aspect"]])


def tin_nhan(cfg: dict, r: dict, vi_du: Sequence[dict] = ()) -> List[dict]:
    """Câu lệnh hệ thống, rồi từng ví dụ dưới dạng một lượt hỏi và một lượt đáp, rồi mẫu cần hỏi."""
    tin = [{"role": "system", "content": cfg["he_thong"]}]
    for v in vi_du:
        tin.append({"role": "user", "content": noi_dung_hoi(cfg, v)})
        tin.append({"role": "assistant", "content": cfg["nhan"][int(v["label"])]})
    tin.append({"role": "user", "content": noi_dung_hoi(cfg, r)})
    return tin


def chuan_hoa(chu: str) -> str:
    chu = unicodedata.normalize("NFD", chu.lower().replace("đ", "d").replace("_", " "))
    chu = "".join(c for c in chu if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", chu)).strip()


def doc_nhan(tho: str, nhan: Sequence[str]) -> Tuple[int, bool]:
    """(nhãn 0/1/2 hoặc -1, đúng khuôn hay không). Đúng khuôn: câu trả lời chỉ gồm đúng một nhãn."""
    sach = chuan_hoa(tho)
    for k, n in enumerate(nhan):
        if sach == chuan_hoa(n):
            return k, True
    co = [k for k in range(SO_LOP) if any(t in sach for t in TU_KHOA[k] + (chuan_hoa(nhan[k]),))]
    return (co[0] if len(co) == 1 else KHONG_DOC_DUOC), False


# --- Gọi API -----------------------------------------------------------------


def lay_khoa(cfg: dict) -> str:
    bien = cfg["nha_cung_cap"]["bien_khoa"]
    khoa = os.environ.get(bien, "").strip()
    if not khoa:
        raise SystemExit(f"Chưa có khoá API. Đặt biến môi trường {bien} trong cửa sổ lệnh rồi chạy lại, ví dụ ở PowerShell:\n"
                         f"    $env:{bien} = \"...\"\nKhông dán khoá vào file nào của repo.")
    return khoa


def goi_api(cfg: dict, tin: List[dict], khoa: str, so_lan_thu: int = 6) -> dict:
    """Một lần gọi Chat Completions. Thử lại khi bị giới hạn tốc độ hoặc máy chủ lỗi."""
    import requests

    than = {"model": cfg["mo_hinh"], "messages": tin, **cfg.get("tham_so", {})}
    loi = ""
    for lan in range(so_lan_thu):
        try:
            tl = requests.post(cfg["nha_cung_cap"]["dia_chi"].rstrip("/") + "/chat/completions", json=than, timeout=60,
                               headers={"Authorization": f"Bearer {khoa}", "Content-Type": "application/json"})
        except requests.RequestException as e:
            loi = type(e).__name__
            time.sleep(min(60, 2 ** lan))
            continue
        if tl.status_code == 200:
            d = tl.json()
            return {"tho": d["choices"][0]["message"]["content"] or "", "mo_hinh": d.get("model"),
                    "system_fingerprint": d.get("system_fingerprint"), "usage": d.get("usage") or {}}
        loi = f"HTTP {tl.status_code}: {tl.text[:300]}"
        if tl.status_code not in (408, 409, 429, 500, 502, 503, 504):
            break
        time.sleep(min(60, float(tl.headers.get("Retry-After", 2 ** lan))))
    raise RuntimeError(f"Gọi API không thành công: {loi}")


def khoa_dem(cfg: dict, tin: List[dict]) -> str:
    goi = {"mo_hinh": cfg["mo_hinh"], "tham_so": cfg.get("tham_so", {}), "tin": tin}
    return hashlib.sha256(json.dumps(goi, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


# --- Độ đo, có tính câu trả lời không đọc được -------------------------------


def dem_o(vang: Sequence[int], doan: Sequence[int]) -> np.ndarray:
    """Ma trận (3, 4): hàng là nhãn thật, cột 0 đến 2 là nhãn đoán, cột 3 là không đọc được."""
    o = np.zeros((SO_LOP, SO_LOP + 1), dtype=np.float64)
    for g, d in zip(vang, doan):
        o[int(g), SO_LOP if int(d) == KHONG_DOC_DUOC else int(d)] += 1
    return o


def do_do(o: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Từ ô đếm (..., 3, 4) ra (macro-F1, accuracy, F1 từng lớp). Câu không đọc được luôn tính là sai."""
    tp = np.einsum("...ii->...i", o[..., :SO_LOP])
    that = o.sum(axis=-1)
    doan = o[..., :SO_LOP].sum(axis=-2)
    mau = that + doan
    f1 = np.divide(2 * tp, mau, out=np.zeros_like(tp), where=mau > 0)
    return f1.mean(axis=-1), tp.sum(axis=-1) / o.sum(axis=(-1, -2)), f1


def dem_theo_cau(uid: Sequence[str], vang: Sequence[int], doan: Sequence[int], cau: Sequence[str]) -> np.ndarray:
    vi_tri = {c: i for i, c in enumerate(cau)}
    o = np.zeros((len(cau), SO_LOP, SO_LOP + 1), dtype=np.float64)
    for u, g, d in zip(uid, vang, doan):
        o[vi_tri[ma_cau(u)], int(g), SO_LOP if int(d) == KHONG_DOC_DUOC else int(d)] += 1
    return o


def bootstrap(a: np.ndarray, b: Optional[np.ndarray], so_lan: int, rng: np.random.Generator, khoi: int = 500) -> Dict[str, Dict[str, float]]:
    """a, b: (lần chạy, câu, 3, 4). Không có b: khoảng tin cậy của a. Có b: hiệu số a trừ b và giá trị p hai phía.

    Lấy mẫu theo câu, thống kê là trung bình các lần chạy, như scripts/compare_baselines.py.
    """
    so_cau = a.shape[1]

    def gia_tri(x):
        f, acc, _ = do_do(x)
        return {"macro_f1": f.mean(axis=-1), "accuracy": acc.mean(axis=-1)}

    qs_a = gia_tri(a.sum(axis=1))
    qs_b = gia_tri(b.sum(axis=1)) if b is not None else None
    mau: Dict[str, list] = {"macro_f1": [], "accuracy": []}
    con = so_lan
    while con > 0:
        n = min(khoi, con)
        w = rng.multinomial(so_cau, np.full(so_cau, 1.0 / so_cau), size=n).astype(np.float64)
        ga = gia_tri(np.einsum("nc,scij->nsij", w, a))
        gb = gia_tri(np.einsum("nc,scij->nsij", w, b)) if b is not None else None
        for k in mau:
            mau[k].append(ga[k] - gb[k] if gb is not None else ga[k])
        con -= n
    ra = {}
    for k, v in mau.items():
        d = np.concatenate(v)
        muc = {"gia_tri": float(qs_a[k] - qs_b[k]) if qs_b is not None else float(qs_a[k]),
               "ci95_duoi": float(np.percentile(d, 2.5)), "ci95_tren": float(np.percentile(d, 97.5))}
        if b is not None:
            muc["p"] = float(min(1.0, 2 * min((np.sum(d <= 0) + 1) / (len(d) + 1), (np.sum(d >= 0) + 1) / (len(d) + 1))))
        ra[k] = muc
    return ra


# --- Các lệnh ----------------------------------------------------------------


def nap_tap_con(cfg: dict, goc: Path) -> Tuple[List[dict], dict]:
    tep = goc / cfg["tap_con"]["tep_uid"]
    if not tep.exists():
        raise SystemExit(f"Chưa có {tep}. Chạy trước: python scripts/eval_llm.py chon")
    thong_tin = json.loads(tep.read_text(encoding="utf-8"))
    theo_uid = {r["uid"]: r for r in doc_jsonl(goc / cfg["du_lieu"]["test"])}
    thieu = [u for u in thong_tin["uid"] if u not in theo_uid]
    if thieu:
        raise SystemExit(f"{len(thieu)} uid của tập con không có trong tập kiểm tra, ví dụ {thieu[0]}")
    return [theo_uid[u] for u in thong_tin["uid"]], thong_tin


def cmd_chon(cfg: dict, goc: Path, ghi_de: bool) -> int:
    tep = goc / cfg["tap_con"]["tep_uid"]
    if tep.exists() and not ghi_de:
        print(f"Đã có {tep}; không rút lại. Mọi kết quả đã chạy gắn với danh sách này. Muốn rút lại thì thêm --ghi-de.")
        return 1
    test = doc_jsonl(goc / cfg["du_lieu"]["test"])
    uid = chon_tap_con(test, cfg["tap_con"]["so_mau"], cfg["tap_con"]["seed"])
    nhan = {r["uid"]: int(r["label"]) for r in test}
    phan_bo = {cfg["nhan"][k]: sum(1 for u in uid if nhan[u] == k) for k in range(SO_LOP)}
    tep.parent.mkdir(parents=True, exist_ok=True)
    tep.write_text(json.dumps({"nguon": cfg["du_lieu"]["test"], "so_mau": len(uid), "seed": cfg["tap_con"]["seed"],
                               "so_binh_luan": len({ma_cau(u) for u in uid}), "phan_bo": phan_bo, "uid": uid},
                              ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"Đã ghi {tep}: {len(uid)} mẫu thuộc {len({ma_cau(u) for u in uid})} bình luận; phân bố {phan_bo}")
    return 0


def cmd_xem(cfg: dict, goc: Path) -> int:
    mau, _ = nap_tap_con(cfg, goc)
    train = doc_jsonl(goc / cfg["du_lieu"]["train"])
    v = cfg["vi_du"]
    for che_do, seeds in (("zs", (None,)), ("fs", SEED_VI_DU)):
        for s in seeds:
            vi_du = chon_vi_du(train, v["moi_lop"], s, v["tu_toi_thieu"], v["tu_toi_da"]) if s is not None else []
            ky_tu = [sum(len(t["content"]) for t in tin_nhan(cfg, r, vi_du)) for r in mau]
            ten = "zero-shot" if s is None else f"few-shot, seed {s}"
            print(f"{ten}: {len(mau)} lần gọi; tổng {sum(ky_tu):,} ký tự đầu vào, trung bình {statistics.mean(ky_tu):.0f}, dài nhất {max(ky_tu)}")
    print("\nSố token phụ thuộc bộ tách từ của từng mô hình nên không ước lượng ở đây.")
    print("Chạy `chay --che-do zs --thu 5` để lấy số token thật của 5 lần gọi rồi nhân lên.")
    print("\n--- Câu lệnh few-shot (seed 42) của mẫu đầu tiên trong tập con ---")
    vi_du = chon_vi_du(train, v["moi_lop"], 42, v["tu_toi_thieu"], v["tu_toi_da"])
    for t in tin_nhan(cfg, mau[0], vi_du):
        print(f"[{t['role']}]\n{t['content']}\n")
    return 0


def cmd_kiem(cfg: dict) -> int:
    import requests

    khoa = lay_khoa(cfg)
    tl = requests.get(cfg["nha_cung_cap"]["dia_chi"].rstrip("/") + f"/models/{cfg['mo_hinh']}", timeout=30,
                      headers={"Authorization": f"Bearer {khoa}"})
    if tl.status_code == 200:
        print(f"Khoá dùng được và mô hình {cfg['mo_hinh']!r} có trên API.")
        return 0
    print(f"KHÔNG ĐƯỢC: HTTP {tl.status_code}: {tl.text[:300]}")
    return 1


def chay(cfg: dict, che_do: str, seed: int, goc: Path, goi: Callable[[dict, List[dict]], dict],
         gioi_han: Optional[int] = None) -> dict:
    """Gọi mô hình cho từng mẫu của tập con (trừ mẫu đã có trong bộ nhớ đệm) rồi ghi kết quả.

    `goi(cfg, tin_nhan)` trả về {"tho", "mo_hinh", "system_fingerprint", "usage"}. Tách ra để test không cần mạng.
    `gioi_han`: chỉ chạy N mẫu đầu và KHÔNG ghi metrics.json, dùng để thử.
    """
    mau, thong_tin = nap_tap_con(cfg, goc)
    vi_du: List[dict] = []
    if che_do == "fs":
        v = cfg["vi_du"]
        vi_du = chon_vi_du(doc_jsonl(goc / cfg["du_lieu"]["train"]), v["moi_lop"], seed, v["tu_toi_thieu"], v["tu_toi_da"])
    exp = cfg["ten_thi_nghiem"][che_do]
    thu_muc = goc / "results" / exp / f"seed{seed}"
    thu_muc.mkdir(parents=True, exist_ok=True)
    tep_tho = thu_muc / "llm_raw.jsonl"
    dem: Dict[str, dict] = {r["khoa"]: r for r in doc_jsonl(tep_tho)} if tep_tho.exists() else {}

    dung = mau if gioi_han is None else mau[:gioi_han]
    hang, goi_moi = [], 0
    with tep_tho.open("a", encoding="utf-8", newline="\n") as fh:
        for i, r in enumerate(dung, 1):
            tin = tin_nhan(cfg, r, vi_du)
            k = khoa_dem(cfg, tin)
            if k not in dem:
                tl = goi(cfg, tin)
                dem[k] = {"khoa": k, "uid": r["uid"], "tho": tl["tho"], "mo_hinh": tl.get("mo_hinh"),
                          "system_fingerprint": tl.get("system_fingerprint"), "usage": tl.get("usage") or {},
                          "luc": datetime.datetime.now().isoformat(timespec="seconds")}
                fh.write(json.dumps(dem[k], ensure_ascii=False) + "\n")
                fh.flush()
                goi_moi += 1
                if goi_moi % 50 == 0:
                    print(f"  {i}/{len(dung)} mẫu, {goi_moi} lần gọi mới")
            nhan, dung_khuon = doc_nhan(dem[k]["tho"], cfg["nhan"])
            hang.append({"uid": r["uid"], "aspect": r["aspect"], "y_true": int(r["label"]), "y_pred": nhan,
                         "tho": dem[k]["tho"], "dung_khuon": dung_khuon, "ban_ghi": dem[k]})

    f, acc, f1 = do_do(dem_o([h["y_true"] for h in hang], [h["y_pred"] for h in hang]))
    vao = sum(int(h["ban_ghi"]["usage"].get("prompt_tokens", 0)) for h in hang)
    ra_tk = sum(int(h["ban_ghi"]["usage"].get("completion_tokens", 0)) for h in hang)
    meta = {
        "exp": exp, "che_do": che_do, "seed": seed, "so_mau": len(hang), "tap_con": cfg["tap_con"]["tep_uid"],
        "mo_hinh_yeu_cau": cfg["mo_hinh"], "mo_hinh_tra_ve": sorted({str(h["ban_ghi"].get("mo_hinh")) for h in hang}),
        "system_fingerprint": sorted({str(h["ban_ghi"].get("system_fingerprint")) for h in hang}),
        "tham_so": cfg.get("tham_so", {}), "van_tay_cau_hinh": van_tay(cfg),
        "luc_goi_dau": min(h["ban_ghi"]["luc"] for h in hang), "luc_goi_cuoi": max(h["ban_ghi"]["luc"] for h in hang),
        "so_lan_goi_moi": goi_moi, "khong_doc_duoc": sum(1 for h in hang if h["y_pred"] == KHONG_DOC_DUOC),
        "khong_dung_khuon": sum(1 for h in hang if not h["dung_khuon"]),
        "token_vao": vao, "token_ra": ra_tk, "uid_vi_du": [v["uid"] for v in vi_du],
        "accuracy": float(acc), "macro_f1": float(f), "f1_tung_lop": [float(x) for x in f1],
    }
    if gioi_han is not None:
        meta["chay_thu"] = True
        return meta

    with (thu_muc / "predictions.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for h in hang:
            fh.write(json.dumps({k: h[k] for k in ("uid", "aspect", "y_true", "y_pred", "tho")}, ensure_ascii=False) + "\n")
    (thu_muc / "llm_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    # Cùng khuôn với metrics.json của các mô hình khác. LƯU Ý: khối "test" ở đây tính trên TẬP CON.
    khuon = {"exp_name": exp, "seed": seed, "dataset": "visfd",
             "test": {"accuracy": float(acc), "macro_f1": float(f), "f1_per_class": [float(x) for x in f1]},
             "diagnostic": {n: {"macro_f1": 0.0, "n": 0} for n in ("negation", "contrast", "regular")},
             "train_time_sec": 0, "n_params": 0, "config_hash": van_tay(cfg)}
    (thu_muc / "metrics.json").write_text(json.dumps(khuon, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return meta


def cmd_chay(cfg: dict, goc: Path, che_do: str, seed: int, thu: Optional[int]) -> int:
    khoa = lay_khoa(cfg)
    meta = chay(cfg, che_do, seed, goc, lambda c, tin: goi_api(c, tin, khoa), thu)
    print(f"{meta['exp']}/seed{seed}: {meta['so_mau']} mẫu, {meta['so_lan_goi_moi']} lần gọi mới; mô hình trả về {meta['mo_hinh_tra_ve']}")
    print(f"  accuracy {meta['accuracy'] * 100:.2f} % | macro-F1 {meta['macro_f1'] * 100:.2f} % | "
          f"không đọc được {meta['khong_doc_duoc']} | không đúng khuôn {meta['khong_dung_khuon']}")
    print(f"  token đầu vào {meta['token_vao']:,} | token đầu ra {meta['token_ra']:,}")
    if thu is not None:
        tong = len(nap_tap_con(cfg, goc)[0])
        print(f"  ĐÂY LÀ LẦN THỬ {thu} mẫu, chưa ghi metrics.json. Cả {tong} mẫu sẽ tốn khoảng "
              f"{meta['token_vao'] * tong // max(1, meta['so_mau']):,} token đầu vào cho một lần chạy.")
    return 0


def _so(x: float) -> str:
    return f"{x * 100:.2f}".replace(".", ",")


def cmd_bang(cfg: dict, goc: Path, so_lan: int, seed: int, out_json: Optional[Path], out_md: Optional[Path]) -> int:
    mau, _ = nap_tap_con(cfg, goc)
    uid = [r["uid"] for r in mau]
    vang = [int(r["label"]) for r in mau]
    cau = sorted({ma_cau(u) for u in uid})

    def nap(exp: str, seeds: Sequence[int]) -> Optional[np.ndarray]:
        lop = []
        for s in seeds:
            p = goc / "results" / exp / f"seed{s}" / "predictions.jsonl"
            if not p.exists():
                return None
            theo_uid = {r["uid"]: r for r in doc_jsonl(p)}
            thieu = [u for u in uid if u not in theo_uid]
            if thieu:
                raise SystemExit(f"{p} thiếu {len(thieu)} uid của tập con, ví dụ {thieu[0]}")
            lech = [u for u, g in zip(uid, vang) if int(theo_uid[u]["y_true"]) != g]
            if lech:
                raise SystemExit(f"{p}: nhãn thật của {lech[0]} khác tập kiểm tra")
            lop.append(dem_theo_cau(uid, vang, [int(theo_uid[u]["y_pred"]) for u in uid], cau))
        return np.stack(lop)

    ten = dict(TEN_HIEN_THI)
    ten[cfg["ten_thi_nghiem"]["zs"]] = f"{cfg['mo_hinh']}, zero-shot"
    ten[cfg["ten_thi_nghiem"]["fs"]] = f"{cfg['mo_hinh']}, few-shot"
    du_lieu: Dict[str, np.ndarray] = {}
    for exp, seeds in ((cfg["ten_thi_nghiem"]["zs"], (42,)), (cfg["ten_thi_nghiem"]["fs"], SEED_VI_DU),
                       *((m, SEED_VI_DU) for m in MO_HINH_SO)):
        a = nap(exp, seeds)
        if a is None:
            print(f"(bỏ qua {exp}: chưa đủ {len(seeds)} file predictions.jsonl)")
            continue
        du_lieu[exp] = a

    rng = np.random.default_rng(seed)
    hang = []
    for exp, a in du_lieu.items():
        f, acc, f1 = do_do(a.sum(axis=1))  # theo từng lần chạy
        kq = bootstrap(a, None, so_lan, rng)
        muc = {"exp": exp, "so_lan_chay": int(a.shape[0]), "accuracy": float(acc.mean()), "macro_f1": float(f.mean()),
               "accuracy_std": float(np.std(acc, ddof=1)) if len(acc) > 1 else None,
               "macro_f1_std": float(np.std(f, ddof=1)) if len(f) > 1 else None,
               "f1_tung_lop": [float(x) for x in f1.mean(axis=0)], "khong_doc_duoc": float(a[..., SO_LOP].sum() / a.shape[0]),
               "ci95": kq, "so_voi_phobert": None}
        if exp != "phobert" and "phobert" in du_lieu:
            muc["so_voi_phobert"] = bootstrap(a, du_lieu["phobert"], so_lan, rng)
        hang.append(muc)

    dong = [f"Kết quả trên {len(uid)} mẫu của tập con ({len(cau)} bình luận). Bootstrap {so_lan:,} lần theo bình luận.".replace(",", "."),
            "", "| Mô hình | Số lần chạy | Accuracy (%) | Macro-F1 (%) | F1 tiêu cực | F1 trung tính | F1 tích cực | Không đọc được | Hiệu số accuracy so với PhoBERT |",
            "|---|---|---|---|---|---|---|---|---|"]
    for m in hang:
        def co_std(k):
            s = m[f"{k}_std"]
            return _so(m[k]) + (f" ± {_so(s)}" if s is not None else "")
        hs = "" if m["so_voi_phobert"] is None else (
            f"{m['so_voi_phobert']['accuracy']['gia_tri'] * 100:+.2f}".replace(".", ",")
            + f" (p {m['so_voi_phobert']['accuracy']['p']:.3f})".replace(".", ","))
        dong.append(f"| {ten.get(m['exp'], m['exp'])} | {m['so_lan_chay']} | {co_std('accuracy')} | {co_std('macro_f1')} | "
                    + " | ".join(_so(x) for x in m["f1_tung_lop"]) + f" | {m['khong_doc_duoc']:g} | {hs} |")
    van_ban = "\n".join(dong) + "\n"
    print(van_ban)
    if out_json is not None:
        (goc / out_json).write_text(json.dumps({"so_mau": len(uid), "so_binh_luan": len(cau), "so_lan": so_lan, "seed": seed,
                                                "ket_qua": hang}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"Đã ghi {goc / out_json}")
    if out_md is not None:
        (goc / out_md).parent.mkdir(parents=True, exist_ok=True)
        (goc / out_md).write_text(van_ban, encoding="utf-8", newline="\n")
        print(f"Đã ghi {goc / out_md}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Mốc tham chiếu bằng mô hình ngôn ngữ lớn trên một tập con của tập kiểm tra.")
    ap.add_argument("--cau-hinh", type=Path, default=CAU_HINH, help=f"file cấu hình (mặc định {CAU_HINH})")
    ap.add_argument("--goc", type=Path, default=Path("."), help="thư mục gốc của repo")
    sub = ap.add_subparsers(dest="lenh", required=True)
    p = sub.add_parser("chon", help="rút tập con phân tầng và ghi danh sách uid")
    p.add_argument("--ghi-de", action="store_true", help="rút lại dù đã có danh sách (kết quả cũ không còn dùng được)")
    sub.add_parser("xem", help="in câu lệnh mẫu và độ dài, không gọi API")
    sub.add_parser("kiem", help="kiểm khoá API và tên mô hình")
    p = sub.add_parser("chay", help="gọi mô hình trên tập con")
    p.add_argument("--che-do", choices=("zs", "fs"), required=True, help="zs: zero-shot; fs: few-shot")
    p.add_argument("--seed", type=int, default=42, help="seed rút ví dụ few-shot; với zero-shot chỉ là tên thư mục (mặc định 42)")
    p.add_argument("--thu", type=int, default=None, help="chỉ gọi N mẫu đầu để xem số token, không ghi metrics.json")
    p = sub.add_parser("bang", help="bảng so với sáu mô hình trên cùng tập con")
    p.add_argument("--so-lan", type=int, default=10000, help="số lần lấy mẫu bootstrap (mặc định 10000)")
    p.add_argument("--seed", type=int, default=20261013, help="seed của bootstrap")
    p.add_argument("--out-json", type=Path, default=Path("results/llm_eval.json"))
    p.add_argument("--out-md", type=Path, default=Path("chuyende1/tables/bang_4_llm.md"))
    p.add_argument("--chi-in", action="store_true", help="chỉ in bảng, không ghi file")
    a = ap.parse_args(argv)

    cfg = doc_cau_hinh(a.goc / a.cau_hinh)
    if a.lenh == "chon":
        return cmd_chon(cfg, a.goc, a.ghi_de)
    if a.lenh == "xem":
        return cmd_xem(cfg, a.goc)
    if a.lenh == "kiem":
        return cmd_kiem(cfg)
    if a.lenh == "chay":
        return cmd_chay(cfg, a.goc, a.che_do, a.seed, a.thu)
    return cmd_bang(cfg, a.goc, a.so_lan, a.seed, None if a.chi_in else a.out_json, None if a.chi_in else a.out_md)


if __name__ == "__main__":
    raise SystemExit(main())
