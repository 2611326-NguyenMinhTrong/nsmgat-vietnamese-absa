"""[CD1.11] Đối chiếu số liệu Chương 5 (bản chính) với file kết quả.

Cùng cách làm với doi_chieu_chuong4.py: tính lại từng con số và từng câu định tính của chương từ
results/error_analysis.json, results/probe_results.json, dự đoán đã công bố và tập chẩn đoán, dựng lại
đúng cụm chữ hay hàng bảng mà chương phải có, rồi tìm trong bản nháp. Câu định tính (neu) chỉ được có
trong chương khi số liệu còn đỡ được câu đó; từ chỉ mức độ như "phần lớn", "hơn một nửa" là khẳng định
định lượng và được kiểm như số (GAP-042).

Thêm một lượt quét ngược: mọi con số trong lời văn và bảng của chương (trừ số mục, số bảng, số hình và
lời trích nguyên văn của bộ dữ liệu) phải nằm trong ít nhất một chỗ kiểm. Con số mới viết thêm mà chưa có
chỗ kiểm thì bị báo, để không con số nào vào chương mà không truy được nguồn.

    python scripts/doi_chieu_chuong5.py

Mã thoát 0 khi mọi chỗ đều khớp, 1 khi có chỗ lệch hoặc con số chưa có chỗ kiểm.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).parent))

import compare_baselines as cb  # noqa: E402
import doi_chieu_chuong4 as dc4  # noqa: E402
import error_analysis as ea  # noqa: E402
import phan_tich_bo_sung as pb  # noqa: E402
import probe_oracle_rules as po  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEP_MAC_DINH = Path("chuyende1/report/nhap_rut_gon/Chuong5_HanCheVaDinhHuong.md")
MO_HINH = dc4.MO_HINH
HOC = tuple(e for e in MO_HINH if e != "lexicon")  # năm mô hình học
MANH = ea.MANH  # bốn mô hình dùng PhoBERT
DO_THI = tuple(e for e in MANH if e != "phobert")
NHAN = ("tiêu cực", "trung tính", "tích cực")
# Các ca của mục 5.2, theo thứ tự trong hai danh sách. Câu lấy từ tập chẩn đoán, gộp khoảng trắng.
VI_DU_LOI = ("visfd-test-01090-GENERAL", "visfd-test-01388-PERFORMANCE", "visfd-test-00144-CAMERA")  # loại lỗi phổ biến nhất, mỗi nhóm một mẫu
CA = ("visfd-test-01659-FEATURES", "visfd-test-00801-BATTERY", "visfd-test-01975-PRICE")  # lỗi cứng chung của bốn mô hình
TU_KHOA_BANG = {"5.1": "theo nhãn gốc và nhãn đoán", "5.2": "lật đúng mọi lỗi ngược cực"}
# Bỏ qua khi quét số: tham chiếu mục, bảng, hình, chương ("mục 5.3 và 5.4" bỏ cả hai số, "mục 4.1.2" bỏ cả ba cấp),
# số thứ tự đầu dòng của danh sách, tiêu đề và đường dẫn hình.
MAU_THAM_CHIEU = re.compile(r"(?:mục|Mục|Bảng|Hình|Chương|bảng|hình) \d+(?:\.\d+)*(?: và \d+(?:\.\d+)*)?|^\d+\. |^#+ .*$|^!\[.*$|\[@[^\]]+\]",
                            re.M)
# Mục 5.4 và 5.6 dẫn các công trình tìm thêm ngày 23/10 và 31/10/2026. Mỗi nhận định về một công trình phải có câu nguyên văn làm
# chứng trong bản gốc đã tải về data/cache/nguon_goc/ (python scripts/doi_chieu_ban_goc.py tai). So khớp sau khi bỏ mọi ký tự không
# phải chữ hay số, vì bản gốc ngắt dòng giữa từ bằng dấu gạch nối.
NGUON_GOC = Path("data/cache/nguon_goc")
CHUNG_CU = {
    "DaiDoesSyntaxMatter2021": ("can outperform or approximate to the previous SOTA performances on six datasets across four languages",
                                "incorporating trees over the RoBERTa brings no significant improvement",
                                "MLP - 87.37 80.96 83.78 80.73 77.17 76.20", "ASGCN Dep. 86.90 80.75 81.66 78.31 75.28 74.38",
                                "The inappropriate hyperparameters may be the cause"),
    "DualGCN": ("the improvement is limited due to the inaccuracy of the dependency parsing results and the informal expressions",),
    "MooreNegationTSA": ("incorporating negation auxiliary tasks gives an average improvement of 3.8 pp", "when using GloVe embeddings",
                         "TL reduces the improvements of MTL"),
    "BarnesNotSolved2019": ("that all of the sentiment systems predicted incorrectly", "come from the no-sentiment (214), mixed category",
                            "(185), non-standard spelling and hashtags", "Negation, which accounts for 97 errors"),
    "MAMS": ("most sentences in these datasets consist of only one aspect or multiple aspects with the same sentiment polarity",
             "degenerate to sentence-level sentiment analysis",
             "each sentence contains at least two different aspects with different sentiment polarities", "perform poorly on MAMS datasets"),
    "KrishnaLogicRules2018": ("averaged over far more random seeds",
                              "which incorporates explicit logic rules for sentiment classification, is ineffective",
                              "implicitly learn logic rules"),
    "WangClauseAttention2018": ("segment a sentence into several clauses", "clause-level attention"),
    "AC-MIMLLN": ("aggregation of the sentiments of the words indicating the aspect category", "implicitly indicating the aspect category",
                  "should be neutral"),
    "CAN": ("the opinion words from other aspects", "orthogonal regularization"),
    "DataProgramming": ("noisy and may conflict", "learning the accuracies of the labeling functions", "depends on the amount of unlabeled data"),
}


def gon(s: str) -> str:
    """Chỉ giữ chữ và số, chữ thường; thay chữ ghép fi, fl của PDF."""
    return re.sub(r"[^0-9a-z]", "", s.replace("ﬁ", "fi").replace("ﬂ", "fl").lower())

Kiem = List[Tuple[str, Optional[str]]]


def pt(x: float, chu_so: int = 1) -> str:
    return f"{x * 100:.{chu_so}f}".replace(".", ",")


def s1(x: float, chu_so: int = 1) -> str:
    return f"{x:.{chu_so}f}".replace(".", ",")


def tim_khoa(d, khoa: str):
    """Giá trị đầu tiên của khoá trong một cây dict lồng nhau."""
    if isinstance(d, dict):
        if khoa in d:
            return d[khoa]
        for v in d.values():
            x = tim_khoa(v, khoa)
            if x is not None:
                return x
    return None


def so_lieu_phan_tich_loi(goc: Path) -> Kiem:
    a = json.loads((goc / "results/error_analysis.json").read_text(encoding="utf-8"))
    mt, kc, dd, lc, sn, gl = a["ma_tran"], a["khia_canh"], a["do_dai"], a["loai_cau"], a["sup_nhan"]["mo_hinh"], a["giao_loi"]
    tim_lai = {e: mt[e]["ti_le_tim_lai"] for e in MO_HINH}
    co_tt = {e: 1 - mt[e]["phan_loi_theo_cap"]["0->2"] - mt[e]["phan_loi_theo_cap"]["2->0"] for e in MO_HINH}
    nham_ca_hai = all(mt[e]["ma_tran"][1][0] > 0 and mt[e]["ma_tran"][1][2] > 0 for e in MO_HINH)
    f1_kc = {k: kc["ket_qua"]["phobert"][k]["macro_f1"]["gia_tri"] for k in kc["thu_tu"]}
    thap = sorted(f1_kc, key=f1_kc.get)[:3]
    sp = kc["spearman"]
    so_y_nghia = sum(sp[e]["p"] < 0.05 for e in HOC)
    acc_dd = {e: [dd[e][k]["accuracy"]["gia_tri"] for k, *_ in ea.DO_DAI] for e in MO_HINH}
    giam_dan = all(all(x > y for x, y in zip(v, v[1:])) for v in acc_dd.values())
    chenh_dai = max(abs(acc_dd[e][-1] - acc_dd["phobert"][-1]) for e in DO_THI) * 100
    trai_kem = all(lc[e]["da_trai"]["accuracy"]["hieu_voi_moc"] < 0 and lc[e]["da_trai"]["accuracy"]["p"] < 0.001 for e in MO_HINH)
    kia = [sn[e]["phan_loi_sang_nhan_kia"] for e in MANH]
    luon = [gl["luon_sai"][e] for e in MANH]
    c, n = gl["cung_sai"], gl["so_mau"]
    tt_cung = gl["cung_sai_theo_nhan"]["trung tính"]
    max_len = tim_khoa(yaml.safe_load((goc / "configs/base.yaml").read_text(encoding="utf-8")), "max_seq_len")
    seeds = len(cb.SEEDS)
    return [
        ("5.1, số lần chạy", f"dự đoán đã có của {len(MO_HINH) * seeds} lần chạy ở mục 4.4"),
        dc4.neu(seeds == 5, "Mọi tỉ lệ về kết quả của mô hình là trung bình năm seed", "5.1, năm seed"),
        dc4.neu(all(min(range(3), key=lambda i: tim_lai[e][i]) == 1 for e in MO_HINH) and nham_ca_hai,
                "Ở cả sáu mô hình, lớp trung tính có tỉ lệ tìm lại thấp nhất trong ba lớp, và mẫu trung tính bị đoán thành cả tích cực lẫn tiêu cực",
                "5.1, tìm lại lớp trung tính"),
        dc4.neu(all(co_tt[e] > 0.8 for e in MANH),
                "ở cả bốn mô hình dùng PhoBERT, hơn bốn phần năm số lỗi có lớp trung tính ở nhãn thật hoặc nhãn đoán", "5.1, lỗi có lớp trung tính"),
        ("5.1, ba khía cạnh thấp nhất", f"khía cạnh có macro-F1 thấp nhất ở PhoBERT tinh chỉnh là {dc4.liet_ke(thap)}"),
        dc4.neu(all(sp[e]["rho"] > 0 for e in HOC),
                f"tương quan dương với macro-F1 ở cả năm mô hình học, nhưng tương quan hạng Spearman chỉ có ý nghĩa ở {dc4.so_chu(so_y_nghia)} mô hình",
                "5.1, tương quan theo khía cạnh"),
        dc4.neu(giam_dan, "giảm dần khi bình luận dài ra ở cả sáu mô hình", "5.1, giảm theo độ dài"),
        ("5.1, PhoBERT theo độ dài", f"từ {pt(acc_dd['phobert'][0])} % với bình luận đến {ea.DO_DAI[0][3]} từ xuống "
                                    f"{pt(acc_dd['phobert'][-1])} % với bình luận trên {ea.DO_DAI[-1][2] - 1} từ"),
        dc4.neu(chenh_dai < 1, "ba mô hình đồ thị chênh PhoBERT không quá 1 điểm", "5.1, nhóm dài nhất"),
        ("5.1, cắt đầu vào", f"việc cắt đầu vào ở {max_len} subword (mục 4.2)"),
        dc4.neu(trai_kem, "accuracy trên mẫu thuộc bình luận trái nhãn thấp hơn mẫu thuộc bình luận nhiều khía cạnh cùng nhãn, với p nhỏ hơn 0,001",
                "5.1, bình luận trái nhãn"),
        ("5.1, khoảng cách ở PhoBERT", f"ở PhoBERT, khoảng cách là {pt(-lc['phobert']['da_trai']['accuracy']['hieu_voi_moc'])} điểm"),
        ("5.1, lỗi sang nhãn kia", f"Ở bốn mô hình dùng PhoBERT, từ {pt(min(kia))} đến {pt(max(kia))} % số lỗi rơi vào nhãn còn lại"),
        ("Hình 5.1, tên", f"(trung bình {seeds} seed, khoảng tin cậy 95 % bằng bootstrap theo bình luận)"),
        ("5.1, định nghĩa lỗi cứng", f"Gọi một mẫu là lỗi cứng của một mô hình khi mô hình đó sai ở cả {dc4.so_chu(seeds)} seed"),
        dc4.neu(min(c / x for x in luon) > 0.5, "Lỗi cứng của bốn mô hình dùng PhoBERT phần lớn trùng nhau", "5.1, lỗi cứng trùng nhau"),
        ("5.1, lỗi cứng", f"mỗi mô hình có từ {min(luon)} đến {max(luon)} lỗi cứng, trong đó {c} mẫu là chung cho cả bốn, bằng {pt(c / n)} % tập kiểm tra "
                          f"và bằng từ {c / max(luon) * 100:.0f} đến {c / min(luon) * 100:.0f} % số lỗi cứng của từng mô hình"),
        ("5.1, lỗi cứng của PhoBERT", f"cả ba cách thêm đồ thị đều không gỡ được {c} trong {gl['luon_sai']['phobert']} lỗi cứng của PhoBERT"),
        dc4.neu(tt_cung / c > 0.5, f"Nhóm {c} mẫu này có hơn một nửa là mẫu trung tính, trong khi lớp trung tính chỉ chiếm "
                                   f"{pt(gl['tat_ca_theo_nhan']['trung tính'] / n)} % tập kiểm tra, và {pt(gl['cung_sai_o_cau_trai_nhan'] / c)} % số mẫu "
                                   "thuộc bình luận trái nhãn", "5.1, đặc điểm nhóm cùng sai"),
        dc4.neu(gl["tat_ca_o_cau_trai_nhan"] / n > 0.5, "mẫu thuộc bình luận trái nhãn đã chiếm hơn một nửa tập kiểm tra (mục 4.4)",
                "5.6.1, trái nhãn chiếm hơn một nửa"),
        dc4.neu(tt_cung / c > 0.5, "Lớp này chiếm hơn một nửa số mẫu mà cả bốn mô hình dùng PhoBERT cùng sai", "5.5, hạn chế 1"),
        dc4.neu(c / gl["luon_sai"]["phobert"] > 0.5, "phần lớn lỗi cứng của PhoBERT vẫn là lỗi cứng ở ba mô hình đồ thị", "5.5, lỗi cứng"),
        dc4.neu(c / gl["luon_sai"]["phobert"] > 0.5, "Phần lớn lỗi cứng của PhoBERT vẫn là lỗi cứng ở ba mô hình đồ thị (mục 5.1)", "5.6.1, lỗi cứng"),
        dc4.neu(trai_kem, "Bình luận trái nhãn khó hơn rõ ở mọi mô hình", "5.5, hạn chế 2"),
        dc4.neu(all(lc[e]["da_trai"]["accuracy"]["gia_tri"] <= lc["phobert"]["da_trai"]["accuracy"]["gia_tri"] for e in DO_THI),
                "Các mô hình đồ thị ở Chương 4 chưa cải thiện được việc gắn ý kiến so với PhoBERT (mục 5.4)", "5.5, đồ thị ở bình luận trái nhãn"),
    ]


def so_lieu_tu_du_doan(goc: Path) -> Kiem:
    """Các số tính thẳng từ dự đoán của 30 lần chạy: tìm lại lớp trung tính theo khía cạnh, mức nền của lỗi rơi vào nhãn
    còn lại ở bình luận hai nhãn, và hai yếu tố đi cùng độ dài bình luận."""
    a = json.loads((goc / "results/error_analysis.json").read_text(encoding="utf-8"))
    test, vang, doan = ea.nap(goc / "results", goc / "data/processed/visfd_test.jsonl", MO_HINH)
    _, cau_idx = ea.chi_so_cau(test)
    loai = ea.loai_cau(cau_idx, vang)

    # Tìm lại lớp trung tính của PhoBERT: PRICE so với chín khía cạnh còn lại.
    kc = np.asarray([r["aspect"] for r in test])
    tt_kc = a["khia_canh"]["ti_le_trung_tinh"]
    khac_price = max(v for k, v in tt_kc.items() if k != "PRICE")
    f1_kc = {k: a["khia_canh"]["ket_qua"]["phobert"][k]["macro_f1"]["gia_tri"] for k in a["khia_canh"]["thu_tu"]}
    hang_price = sorted(f1_kc, key=f1_kc.get, reverse=True).index("PRICE") + 1

    def tim_lai_tt(chon: np.ndarray) -> float:
        m = chon & (vang == 1)
        return float(np.mean([(d[m] == 1).mean() for d in doan["phobert"]]))

    tl_price, tl_khac = tim_lai_tt(kc == "PRICE"), tim_lai_tt(kc != "PRICE")

    # Bình luận có đúng hai nhãn: lỗi rơi vào nhãn còn lại, so với mức nền. Mức nền giả định lỗi của mỗi lớp chia cho hai lớp
    # kia theo đúng tỉ lệ của ma trận nhầm lẫn trên các mẫu KHÔNG thuộc bình luận hai nhãn (cùng mô hình, cùng seed).
    co_nhan = np.zeros((cau_idx.max() + 1, cb.SO_LOP), dtype=bool)
    co_nhan[cau_idx, vang] = True
    hai = (co_nhan.sum(axis=1) == 2)[cau_idx]
    thuc, nen = {}, {}
    for e in MO_HINH:
        trung, tong, p_nen = 0, 0, 0.0
        for d in doan[e]:
            m = np.zeros((cb.SO_LOP, cb.SO_LOP))
            np.add.at(m, (vang[~hai], d[~hai]), 1)
            for i in np.flatnonzero((d != vang) & hai):
                t = vang[i]
                kia = next(x for x in range(cb.SO_LOP) if x != t and co_nhan[cau_idx[i], x])
                ba = cb.SO_LOP - t - kia
                p_nen += m[t, kia] / (m[t, kia] + m[t, ba]) if m[t, kia] + m[t, ba] else 0.5
                trung += int(d[i] == kia)
                tong += 1
        thuc[e], nen[e] = trung / tong, p_nen / tong
    chenh = [(thuc[e] - nen[e]) * 100 for e in MANH]

    # Độ dài (số từ sau tách từ, như ea.DO_DAI): tỉ lệ mẫu thuộc bình luận trái nhãn và tỉ lệ mẫu trung tính theo nhóm.
    so_tu = np.asarray([len(r["tokens"]) for r in test])
    nhom = [(so_tu >= lo) & (so_tu <= hi) for _, _, lo, hi in ea.DO_DAI]
    trai = [float((loai[c] == 2).mean()) for c in nhom]
    tt_dd = [float((vang[c] == 1).mean()) for c in nhom]
    tang = lambda v: all(x < y for x, y in zip(v, v[1:]))  # noqa: E731

    return [
        dc4.neu(tl_price - tl_khac > 0.1, "Độ khó của lớp này khác nhau rõ giữa các khía cạnh", "5.1, trung tính theo khía cạnh"),
        ("5.1, PRICE", f"Ở PRICE, nơi trung tính chiếm {pt(tt_kc['PRICE'])} % mẫu kiểm tra, PhoBERT tìm lại được {pt(tl_price)} % số mẫu trung tính, "
                       f"và macro-F1 của khía cạnh này cao thứ {dc4.so_chu(hang_price)} trong mười khía cạnh"),
        ("5.1, chín khía cạnh còn lại", f"Ở chín khía cạnh còn lại, nơi trung tính chiếm không quá {pt(khac_price)} %, PhoBERT chỉ tìm lại được "
                                        f"{pt(tl_khac)} % số mẫu trung tính"),
        dc4.neu(tl_khac < tl_price and khac_price < tt_kc["PRICE"], "Như vậy lớp trung tính khó nhất ở chính những khía cạnh mà nó hiếm",
                "5.1, trung tính khó ở nơi nó hiếm"),
        ("5.1, mức nền", f"tỉ lệ này chỉ từ {pt(min(nen[e] for e in MANH))} đến {pt(max(nen[e] for e in MANH))} %"),
        ("5.1, phần chênh", f"Phần chênh từ {min(chenh):.0f} đến {max(chenh):.0f} điểm"),
        dc4.neu(all(thuc[e] - nen[e] > 0.1 for e in MO_HINH),
                "ở bình luận hai nhãn, lỗi rơi vào nhãn của khía cạnh kia nhiều hơn rõ so với mức nền (mục 5.1)", "5.5, hạn chế 2, mức nền"),
        dc4.neu(tang(trai) and tang(tt_dd), "Chênh lệch theo độ dài chưa được tách khỏi ba yếu tố đi cùng với nó", "5.1, yếu tố đi cùng độ dài"),
        ("5.1, độ dài và trái nhãn", f"tỉ lệ mẫu thuộc bình luận trái nhãn, tăng từ {pt(trai[0])} % ở nhóm ngắn nhất lên {pt(trai[-1])} % ở nhóm dài nhất"),
        ("5.1, độ dài và trung tính", f"tỉ lệ mẫu trung tính, tăng từ {pt(tt_dd[0])} % lên {pt(tt_dd[-1])} %"),
    ]


def so_lieu_trung_tinh_trai_nhan(goc: Path) -> Kiem:
    test = po.doc_jsonl(goc / "data/processed/visfd_test.jsonl")
    nhan_cua_cau: Dict[str, set] = {}
    for r in test:
        nhan_cua_cau.setdefault(ea.cb.ma_cau(r["uid"]), set()).add(r["label"])
    tt = [r for r in test if r["label"] == 1]
    trong = sum(len(nhan_cua_cau[ea.cb.ma_cau(r["uid"])]) >= 2 for r in tt)
    return [("5.1, mẫu trung tính ở bình luận trái nhãn", f"{trong} trên {len(tt)} mẫu trung tính của tập kiểm tra thuộc bình luận trái nhãn")]


def du_doan_bon_mo_hinh(goc: Path) -> Dict[str, List[int]]:
    ra: Dict[str, List[int]] = {}
    for e in MANH:
        for s in cb.SEEDS:
            uid, _, doan = cb.doc_du_doan(goc / "results" / e / f"seed{s}" / "predictions.jsonl")
            for u, d in zip(uid, doan):
                ra.setdefault(u, []).append(int(d))
    return ra


def so_lieu_ca(goc: Path) -> Kiem:
    a = json.loads((goc / "results/error_analysis.json").read_text(encoding="utf-8"))
    cung = set(a["giao_loi"]["uid_cung_sai"])
    cd = {r["uid"]: r for r in po.doc_jsonl(goc / "data/diagnostic/diagnostic_300.jsonl")}
    doan = du_doan_bon_mo_hinh(goc)
    giao = [u for u in cung if u in cd]
    khac = [u for u in giao if cd[u]["nhan_kiem_tra"] != "dong_y"]
    goc_tt = [u for u in khac if cd[u]["label"] == 1 and cd[u]["nhan_kiem_tra"] in ("negative", "positive")]
    so_lan = len(MANH) * len(cb.SEEDS)
    theo_nhom = Counter(cd[u]["phenomenon"] for u in giao).most_common()
    thanh_phan = ", ".join(f"{n} mẫu nhóm {po.TEN_NHOM[g].lower()}" for g, n in theo_nhom[:-1])
    thanh_phan += f" và {theo_nhom[-1][1]} mẫu nhóm {po.TEN_NHOM[theo_nhom[-1][0]].lower()}"
    kiem: Kiem = [
        ("5.2, nhóm của ba ca", f"thuộc nhóm {len(cung)} mẫu là lỗi cứng chung của cả bốn mô hình dùng PhoBERT"),
        ("5.2, ba mươi mẫu", f"Có {len(giao)} mẫu như vậy: {thanh_phan}, và người chú thích không đồng ý với nhãn gốc ở {len(khac)} mẫu"),
        dc4.neu(all(u in cd and cd[u]["phenomenon"] != "regular" for u in CA) and sum(cd[u]["nhan_kiem_tra"] != "dong_y" for u in CA if u in cd) == 1,
                "chúng đều thuộc nhóm có hiện tượng và chỉ một mẫu bị người chú thích không đồng ý", "5.2, bốn ca không đại diện"),
        ("5.5, hạn chế 1, ba mươi mẫu",
         f"trong {len(giao)} mẫu ở mục 5.2, người chú thích không đồng ý với nhãn gốc ở {len(khac)} mẫu, "
         f"và {len(goc_tt)} mẫu trong số đó có nhãn gốc trung tính mà người chú thích cho là có cực"),
        ("5.2, số lần chạy", f"Nhãn đoán là nhãn được đoán nhiều nhất trong {so_lan} lần chạy"),
    ]
    ten_kt = {"dong_y": "đồng ý", "negative": "gán tiêu cực", "neutral": "gán trung tính", "positive": "gán tích cực"}
    for i, u in enumerate(CA, 1):
        if u not in cung or u not in cd:
            kiem.append((f"5.2, mẫu {i}", f"SỐ LIỆU KHÔNG CÒN ĐỠ MẪU: {u} không còn thuộc nhóm cùng sai hoặc không có trong tập chẩn đoán"))
            continue
        r = cd[u]
        nhan, dem = Counter(doan[u]).most_common(1)[0]
        kiem.append((f"5.2, mẫu {i}", f"{i}. Khía cạnh {r['aspect']} của \"{cau_ca(r)}\": nhóm {po.TEN_NHOM[r['phenomenon']].lower()}, "
                                      f"nhãn gốc {NHAN[r['label']]}, người chú thích {ten_kt[r['nhan_kiem_tra']]}, "
                                      f"các mô hình đoán {NHAN[nhan]} ở {dem} trên {so_lan} lần chạy"))
    ba = "visfd-test-00801-BATTERY"
    kiem.append(dc4.neu({cd[ba]["label"], Counter(doan[ba]).most_common(1)[0][0]} == {0, 2},
                        "Đây là một lỗi ngược cực: người viết phản bác lời chê về pin", "5.2, mẫu thứ ba"))
    return kiem


def cau_ca(r: dict) -> str:
    """Câu của một ca như in trong chương: nguyên văn, chỉ gộp khoảng trắng."""
    return " ".join(r["text"].split())


def so_lieu_tham_do(goc: Path) -> Kiem:
    kq = json.loads((goc / "results/probe_results.json").read_text(encoding="utf-8"))
    if kq["mo_hinh"] != "phobert" or kq["seeds"] != list(cb.SEEDS):
        raise ValueError("results/probe_results.json không phải của phobert với đúng các seed hiện tại: chạy lại probe_oracle_rules.py")
    c, t, p2, p3 = kq["p1"]["tap_chan_doan"], kq["p1"]["toan_tap_kiem_tra"], kq["p2"], kq["p3"]
    test = po.doc_jsonl(goc / "data/processed/visfd_test.jsonl")
    chan_doan = po.doc_jsonl(goc / "data/diagnostic/diagnostic_300.jsonl")
    tang_dt = [po.p1_toan_tap(test, po.nap_du_doan(goc / "results", e, test))["nguoc_cuc_o_cau_co_phu_dinh"]["tang_macro_f1"] for e in DO_THI]
    nhom = ("regular", "negation", "contrast", "both")
    co_ht = ("negation", "contrast", "both")
    ea_kq = json.loads((goc / "results/error_analysis.json").read_text(encoding="utf-8"))
    cap = ea_kq["ma_tran"]["phobert"]["phan_loi_theo_cap"]
    loi_tt_toan_tap, loi_nc_toan_tap = cap["1->0"] + cap["1->2"], cap["0->2"] + cap["2->0"]
    tt_toan_tap = float(np.mean([int(r["label"]) == 1 for r in test]))
    tt_nhom = {g: float(np.mean([int(r["label"]) == 1 for r in chan_doan if r["phenomenon"] == g])) for g in nhom}
    kdy_nhom = {g: float(np.mean([r["nhan_kiem_tra"] != "dong_y" for r in chan_doan if r["phenomenon"] == g])) for g in nhom}
    co_tt_manh = all(1 - ea_kq["ma_tran"][e]["phan_loi_theo_cap"]["0->2"] - ea_kq["ma_tran"][e]["phan_loi_theo_cap"]["2->0"] > 0.8 for e in MANH)
    kiem: Kiem = [("Bảng 5.2, tên", f"và mức tăng macro-F1 của nhóm khi một luật lý tưởng lật đúng mọi lỗi ngược cực (số lỗi trung bình mỗi seed, {len(cb.SEEDS)} seed)")]
    for g in nhom:
        x = c[g]
        kiem.append((f"Bảng 5.2, {g}", f"| {po.TEN_NHOM[g]} | {x['n']} | {s1(x['loi'])} | {s1(x['loi_nguoc_cuc'])} | {s1(x['loi_goc_trung_tinh'])} | "
                                       f"{s1(x['loi_o_dong_khong_dong_y'])} | {pt(x['tang'], 2)} |"))
    tho = sum(len(po.o_cua(r) is not None and [1] or []) for r in chan_doan)
    kiem += [
        dc4.neu(all(c[g]["loi_nguoc_cuc"] / c[g]["loi"] < 0.2 and c[g]["loi_goc_trung_tinh"] / c[g]["loi"] > 0.5 for g in nhom),
                "Lỗi ngược cực chỉ là phần nhỏ trong mọi nhóm; phần lớn lỗi là mẫu có nhãn gốc trung tính mà mô hình đoán có cực", "5.3, loại lỗi"),
        # Tập chẩn đoán rút cân bằng nhãn nên có nhiều mẫu trung tính hơn tập kiểm tra; trên toàn tập, phần lỗi trung tính nhỏ hơn.
        dc4.neu(min(tt_nhom.values()) > tt_toan_tap and min(c[g]["loi_goc_trung_tinh"] / c[g]["loi"] for g in nhom) > loi_tt_toan_tap,
                "Tỉ lệ lỗi có nhãn gốc trung tính bị đẩy lên một phần vì tập chẩn đoán được rút cho ba nhãn gần cân bằng nên có nhiều mẫu "
                "trung tính hơn tập kiểm tra", "5.3, tập chẩn đoán cân bằng nhãn"),
        ("5.3, toàn tập: lỗi trung tính", f"trên toàn tập kiểm tra, lỗi có nhãn gốc trung tính chiếm {pt(loi_tt_toan_tap)} % số lỗi của PhoBERT"),
        dc4.neu(loi_nc_toan_tap < 0.2, f"Lỗi ngược cực thì vẫn ít, chỉ chiếm {pt(loi_nc_toan_tap)} % số lỗi", "5.3, toàn tập: lỗi ngược cực"),
        dc4.neu(c["negation"]["tang"] < 0.01 and abs(c["negation"]["tang"] - c["regular"]["tang"]) < 0.005,
                "nâng macro-F1 của nhóm phủ định chưa tới 1 điểm, và mức tăng ở nhóm phủ định không khác nhiều nhóm thường", "5.3, nhóm phủ định"),
        ("5.3, toàn tập", f"macro-F1 của PhoBERT tăng tối đa {pt(t['nguoc_cuc_o_cau_co_phu_dinh']['tang_macro_f1'], 2)} điểm; lật đúng mọi lỗi ngược cực "
                          f"ở bất cứ đâu cũng chỉ tăng {pt(t['nguoc_cuc_moi_cho']['tang_macro_f1'], 2)} điểm"),
        ("5.3, ba mô hình đồ thị", f"macro-F1 trên toàn tập tăng từ {pt(min(tang_dt), 2)} đến {pt(max(tang_dt), 2)} điểm"),
        ("5.3, luật phủ định", f"luật từ khoá phủ định bắt được {pt(p2['phu_dinh']['do_phu'])} % số mẫu thật sự có phủ định, nhưng chỉ "
                               f"{pt(p2['phu_dinh']['do_chinh_xac'])} % số mẫu nó bắt là có phủ định tác động lên đúng khía cạnh đó"),
        ("5.3, luật chuyển ý", f"Luật từ nối chuyển ý có độ chính xác {pt(p2['chuyen_y']['do_chinh_xac'])} % và độ phủ {pt(p2['chuyen_y']['do_phu'])} %"),
        dc4.neu(p2["chuyen_y"]["bo_sot_tren_tap_chan_doan"]["co_tu_ngo"] > 0
                and p2["chuyen_y"]["bo_sot_tren_tap_chan_doan"]["dong"] > p2["chuyen_y"]["bo_sot_tren_tap_chan_doan"]["co_tu_ngo"],
                "nó bỏ sót những chuyển ý dùng từ đa nghĩa như \"mà\", \"còn\", vốn đã bị loại khỏi danh sách, hay những cách nói không có trong danh sách",
                "5.3, chuyển ý bị bỏ sót"),
        ("5.3, quần thể ước lượng", f"các mẫu thuộc bình luận từ {po.bd.DO_DAI_MAC_DINH[0]} đến {po.bd.DO_DAI_MAC_DINH[1]} từ và không chỉ chứa từ đa nghĩa"),
        dc4.neu(tho / len(chan_doan) > 0.9, "vì tập chẩn đoán được rút chủ yếu từ phần này", "5.3, tập chẩn đoán rút từ đâu"),
        ("5.3, dạng chuẩn", f"được gán là phó từ ở {pt(p3['chuan']['ti_le_pho_tu'])} % số lượt và kề từ đứng sau trên cây ở "
                            f"{pt(p3['chuan']['ti_le_ke_nhau'])} % số lượt"),
        dc4.neu(abs(p3["viet_tat"]["luot"] / (p3["viet_tat"]["luot"] + p3["chuan"]["luot"]) - 0.5) < 0.02,
                "Một nửa số lượt từ phủ định trong tập kiểm tra lại là dạng viết tắt", "5.3, một nửa là viết tắt"),
        dc4.neu(p3["viet_tat"]["ti_le_pho_tu"] == 0, "VnCoreNLP không gán phó từ cho lượt nào trong số đó", "5.3, viết tắt không là phó từ"),
        ("5.3, viết tắt kề nhau", f"chỉ {pt(p3['viet_tat']['ti_le_ke_nhau'])} % số lượt được gắn kề từ đứng sau"),
        dc4.neu(co_tt_manh, "vì phần lớn lỗi có lớp trung tính ở một đầu (mục 5.1)", "5.3, kết luận, việc thứ nhất"),
        dc4.neu(max(p2["phu_dinh"]["do_chinh_xac"], p2["chuyen_y"]["do_chinh_xac"]) < 0.6,
                "thường không tác động lên mọi khía cạnh của bình luận đó. Luật từ khoá chưa làm được việc thứ hai", "5.3, kết luận, việc thứ hai"),
        dc4.neu(p3["viet_tat"]["ti_le_pho_tu"] == 0 and p3["chuan"]["ti_le_ke_nhau"] > 0.9,
                "với từ phủ định dạng chuẩn, nó không cho thêm thông tin so với vị trí của từ trong câu, còn dạng viết tắt thì nó không nhận ra là phó từ",
                "5.3, kết luận, cây phụ thuộc"),
        dc4.neu(all(c[g]["loi_o_dong_khong_dong_y"] / c[g]["loi"] > 0.5 for g in nhom),
                "ở cả bốn nhóm, kể cả nhóm thường, hơn một nửa số lỗi của PhoBERT nằm ở các mẫu này", "5.5, hạn chế 4, lỗi dồn vào"),
        dc4.neu(max(kdy_nhom.values()) < 0.5, "dù chúng chỉ là thiểu số trong mỗi nhóm", "5.5, hạn chế 4, thiểu số"),
        dc4.neu(min(kdy_nhom["contrast"], kdy_nhom["both"]) / max(kdy_nhom["regular"], kdy_nhom["negation"]) > 2,
                "Người chú thích không đồng ý với nhãn gốc ở hai nhóm có chuyển ý nhiều gấp hơn hai lần ở nhóm thường và nhóm phủ định",
                "5.5, hạn chế 4, gấp hơn hai lần"),
        dc4.neu(all(c[g]["loi_nguoc_cuc"] / c[g]["loi"] < 0.5 for g in co_ht),
                "lỗi của PhoBERT ở các nhóm này phần lớn không phải lỗi ngược cực (mục 5.3)", "5.5, hạn chế 3"),
        dc4.neu(max(p2["phu_dinh"]["do_chinh_xac"], p2["chuyen_y"]["do_chinh_xac"]) < 0.6,
                "luật từ khoá đúng dưới ba phần năm số mẫu nó bắt", "5.6.3, độ chính xác của luật từ khoá"),
        dc4.neu(t["nguoc_cuc_o_cau_co_phu_dinh"]["tang_macro_f1"] < 0.01,
                "trên PhoBERT, ngay cả luật lật cực lý tưởng cũng chỉ đem lại mức tăng nhỏ", "5.6.2, trần của luật lật cực"),
    ]
    return kiem


def so_lieu_bo_sung(goc: Path) -> Kiem:
    """Mục 5.2 (loại lỗi), 5.4 (vì sao đồ thị không giúp), 5.6.2 (phần lỗi và mức tăng tối đa), từ results/phan_tich_bo_sung.json."""
    kq = json.loads((goc / pb.TEP_KET_QUA).read_text(encoding="utf-8"))
    if kq["mo_hinh"] != "phobert" or kq["seeds"] != list(cb.SEEDS):
        raise ValueError("results/phan_tich_bo_sung.json không phải của phobert với đúng các seed hiện tại: chạy lại phan_tich_bo_sung.py")
    tc, dy = kq["loai_loi"]["tat_ca"], kq["loai_loi"]["dong_y"]
    co_ht = ("negation", "contrast", "both")

    def cap(x: dict, k: str) -> float:
        return x["cap"].get(k, 0.0)

    def nhieu_nhat(x: dict) -> str:
        return max(x["cap"], key=x["cap"].get)

    tt = {g: (cap(tc[g], "1->0") + cap(tc[g], "1->2")) / tc[g]["loi"] for g in pb.NHOM}
    nc = {g: (cap(tc[g], "0->2") + cap(tc[g], "2->0")) / tc[g]["loi"] for g in pb.NHOM}
    sai_tt = {g: tc[g]["ti_le_sai_theo_nhan"][1] for g in pb.NHOM}
    sai_co_cuc = max(tc[g]["ti_le_sai_theo_nhan"][y] for g in pb.NHOM for y in (0, 2))
    so_seed = len(cb.SEEDS)
    kiem: Kiem = [("Bảng 5.1, tên", f"(số lỗi trung bình mỗi seed, {so_seed} seed)")]
    for g in pb.NHOM:
        x = tc[g]
        kiem.append((f"Bảng 5.1, {g}", f"| {po.TEN_NHOM[g]} | {x['n']} | {s1(x['loi'])} | {s1(cap(x, '1->2'))} | {s1(cap(x, '1->0'))} | "
                                       f"{s1(cap(x, '0->1') + cap(x, '2->1'))} | {s1(cap(x, '0->2') + cap(x, '2->0'))} | {pt(sai_tt[g])} |"))
    kiem += [
        dc4.neu(all(tt[g] > max(nc[g], 0.5) for g in co_ht),
                "Trên các câu có phủ định và chuyển ý, lỗi phổ biến nhất của PhoBERT tinh chỉnh là đoán có cực cho một mẫu có nhãn gốc trung tính", "5.2, lỗi phổ biến nhất"),
        ("5.2, tỉ trọng", f"Loại lỗi này chiếm từ {pt(min(tt[g] for g in co_ht))} đến {pt(max(tt[g] for g in co_ht))} % số lỗi của ba nhóm có hiện tượng, "
                          f"trong khi lỗi ngược cực chỉ chiếm từ {pt(min(nc[g] for g in co_ht))} đến {pt(max(nc[g] for g in co_ht))} %"),
        dc4.neu(nhieu_nhat(tc["contrast"]) == "1->2" and nhieu_nhat(tc["both"]) == "1->2" and nhieu_nhat(tc["negation"]) == "1->0",
                "Ở nhóm chuyển ý và nhóm cả hai, hướng sai thường gặp nhất là trung tính thành tích cực; ở nhóm phủ định là trung tính thành tiêu cực", "5.2, hướng sai"),
        dc4.neu(tt["regular"] > 0.5, "ở nhóm thường nó cũng chiếm phần lớn số lỗi", "5.2, không đặc thù"),
        dc4.neu(all(sai_tt[g] > sai_tt["regular"] for g in co_ht) and max(sai_tt, key=sai_tt.get) == "both",
                "tỉ lệ sai của mẫu trung tính tăng rõ khi có hiện tượng và cao nhất ở nhóm cả hai", "5.2, tỉ lệ sai của mẫu trung tính"),
        ("5.2, mẫu có cực", f"ở mẫu tiêu cực và tích cực tỉ lệ sai không vượt quá {pt(sai_co_cuc)} %"),
        dc4.neu(all(nhieu_nhat(dy[g]) == "1->2" for g in co_ht), "trung tính thành tích cực là lỗi nhiều nhất ở cả ba nhóm", "5.2, trên mẫu đồng ý"),
        dc4.neu(cap(dy["negation"], "1->0") < 1 <= cap(tc["negation"], "1->0") / 5,
                "trung tính thành tiêu cực ở nhóm phủ định gần như biến mất", "5.2, lỗi ở nhãn bị nghi ngờ"),
    ]
    cd = {r["uid"]: r for r in po.doc_jsonl(goc / "data/diagnostic/diagnostic_300.jsonl")}
    doan: Dict[str, List[int]] = {}
    for s in cb.SEEDS:
        uid, _, d = cb.doc_du_doan(goc / "results/phobert" / f"seed{s}" / "predictions.jsonl")
        for u, x in zip(uid, d):
            doan.setdefault(u, []).append(int(x))
    nhom_vd = []
    for i, u in enumerate(VI_DU_LOI, 1):
        r = cd[u]
        nhom_vd.append(r["phenomenon"])
        nhan, dem = Counter(doan[u]).most_common(1)[0]
        kiem.append((f"5.2, ví dụ {i}", f"{i}. Khía cạnh {r['aspect']} của \"{cau_ca(r)}\": nhóm {po.TEN_NHOM[r['phenomenon']].lower()}, "
                                        f"nhãn gốc {NHAN[r['label']]}, PhoBERT đoán {NHAN[nhan]} ở {dem} trên {so_seed} seed"))
    kiem += [
        dc4.neu(sorted(nhom_vd) == sorted(co_ht) and all(cd[u]["label"] == 1 and all(x != 1 for x in doan[u]) and cd[u]["nhan_kiem_tra"] == "dong_y" for u in VI_DU_LOI),
                "Cả ba đều được người chú thích đồng ý với nhãn gốc và bị PhoBERT đoán sai ở cả năm seed", "5.2, ba ví dụ"),
    ]
    p = kq["phan_loi"]
    co, th, tr, trd = p["nhom"]["co_hien_tuong"], p["nhom"]["thuong"], p["tran"]["co_hien_tuong"], p["tran"]["co_hien_tuong_dong_y"]
    kiem += [
        ("5.6.2, quần thể", f"gồm {dc4.nghin(p['quan_the'])} mẫu (mục 5.3)"),
        ("5.6.2, phần lỗi", f"chiếm khoảng {pt(co['ti_le_mau'])} % số mẫu và {pt(co['ti_le_loi'])} % số lỗi của PhoBERT (khoảng tin cậy 95 % từ {pt(co['ci95_ti_le_loi'][0])} đến "
                            f"{pt(co['ci95_ti_le_loi'][1])} %), với tỉ lệ sai {pt(co['ti_le_sai'])} % so với {pt(th['ti_le_sai'])} % ở mẫu thường"),
        dc4.neu(0.4 < th["ti_le_loi"] < 0.6 and co["ti_le_sai"] > th["ti_le_sai"], "Hai hiện tượng làm tăng nguy cơ sai, nhưng khoảng một nửa số lỗi vẫn nằm ở mẫu thường", "5.6.2, tiền đề"),
        ("5.6.2, mức tăng tối đa", f"macro-F1 trên toàn tập kiểm tra tăng khoảng {pt(tr['tang'], 2)} điểm (khoảng tin cậy 95 % từ {pt(tr['ci95'][0], 2)} đến {pt(tr['ci95'][1], 2)})"),
        ("5.6.2, mức tăng trên mẫu đồng ý", f"mức này còn {pt(trd['tang'], 2)} điểm (từ {pt(trd['ci95'][0], 2)} đến {pt(trd['ci95'][1], 2)})"),
        ("5.6.2, phần cần sửa", f"phải sửa đúng khoảng {tr['phan_can_de_tang_1_diem'] * 100:.0f} % số lỗi này, hoặc {trd['phan_can_de_tang_1_diem'] * 100:.0f} % nếu không tính"),
        ("5.6.2, ngoài quần thể", f"Các con số không gồm {dc4.nghin(p['ngoai_quan_the'])} mẫu không ước lượng được"),
    ]
    d = kq["do_thi"]
    khac = d["khac_du_doan"]
    dh = d["dung_het_sai_het"]
    dung = {x["do_thi_dung_phobert_sai"] for x in dh.values()}
    nguoc = [dh[e]["phobert_dung_do_thi_sai"] for e in pb.DO_THI]
    a_trai = pb.tim_cap(d, "trai_nhan", "asgcn", "asgcn_khong_gcn")["accuracy"]
    a_khong = pb.tim_cap(d, "khong_trai_nhan", "asgcn", "asgcn_khong_gcn")["accuracy"]
    s_trai = pb.tim_cap(d, "trai_nhan", "senticgcn", "asgcn_khong_gcn")["accuracy"]
    s_pb = pb.tim_cap(d, "trai_nhan", "senticgcn", "phobert")["macro_f1"]
    a_vt = pb.tim_cap(d, "khong_viet_tat", "asgcn", "asgcn_khong_gcn")["macro_f1"]
    s_vt = pb.tim_cap(d, "khong_viet_tat", "senticgcn", "asgcn_khong_gcn")["macro_f1"]
    a_chuan = pb.tim_cap(d, "chi_phu_dinh_chuan", "asgcn", "asgcn_khong_gcn")["macro_f1"]
    a_pb, s_pb_tb = pb.tim_cap(d, "toan_bo", "asgcn", "phobert")["macro_f1"], pb.tim_cap(d, "toan_bo", "senticgcn", "phobert")["macro_f1"]

    def so(x: float) -> str:
        return pt(abs(x), 2)

    def gia_tri_p(x: float) -> str:
        return f"{x:.3f}".replace(".", ",")

    kiem += [
        ("5.4, dự đoán khác nhau", f"Hai seed của PhoBERT cho dự đoán khác nhau ở {pt(khac['phobert_voi_chinh_no'], 2)} % số mẫu, còn PhoBERT với ba mô hình đồ thị khác nhau ở từ "
                                   f"{pt(min(khac['phobert_voi_do_thi'].values()), 2)} đến {pt(max(khac['phobert_voi_do_thi'].values()), 2)} %"),
        (("5.4, đúng hết sai hết", f"đúng ở cả năm seed mà PhoBERT sai ở cả năm seed là {dung.copy().pop()} ở mỗi mô hình, chiều ngược lại là {nguoc[0]}, {nguoc[1]} và {nguoc[2]}")
         if len(dung) == 1 else ("5.4, đúng hết sai hết", "SỐ LIỆU KHÔNG CÒN ĐỠ CÂU: số mẫu không còn bằng nhau ở cả ba mô hình")),
        dc4.neu(a_trai["hieu_so"] < 0 < a_khong["hieu_so"],
                f"accuracy giảm {so(a_trai['hieu_so'])} điểm ở mẫu thuộc bình luận trái nhãn (p bằng {gia_tri_p(a_trai['p'])}) nhưng tăng {so(a_khong['hieu_so'])} điểm ở các mẫu còn lại "
                f"(p bằng {gia_tri_p(a_khong['p'])})", "5.4, ASGCN theo loại bình luận"),
        dc4.neu(s_trai["hieu_so"] > 0, f"Sentic-GCN thì tăng {so(s_trai['hieu_so'])} điểm ở bình luận trái nhãn (p bằng {gia_tri_p(s_trai['p'])})", "5.4, Sentic-GCN ở bình luận trái nhãn"),
        dc4.neu(s_pb["p"] >= 0.05, "vẫn không hơn PhoBERT có ý nghĩa ở nhóm này", "5.4, Sentic-GCN so với PhoBERT"),
        dc4.neu(min(a_trai["p_hoan_vi_seed"], a_khong["p_hoan_vi_seed"], s_trai["p_hoan_vi_seed"]) >= 0.05,
                "Các hiệu số trên chưa qua được phép hoán vị seed", "5.4, phép hoán vị seed"),
        dc4.neu(a_vt["hieu_so"] < 0 < s_vt["hieu_so"] and min(a_vt["p"], s_vt["p"]) >= 0.05,
                f"ASGCN giảm {so(a_vt['hieu_so'])} điểm macro-F1 và Sentic-GCN chỉ tăng {so(s_vt['hieu_so'])} điểm, đều không có ý nghĩa (p bằng {gia_tri_p(a_vt['p'])} và {gia_tri_p(s_vt['p'])})",
                "5.4, bình luận không có dạng viết tắt"),
        dc4.neu(a_chuan["hieu_so"] < 0, f"ASGCN giảm {so(a_chuan['hieu_so'])} điểm (p bằng {gia_tri_p(a_chuan['p'])})", "5.4, bình luận chỉ có từ phủ định dạng chuẩn"),
        dc4.neu(a_pb["hieu_so"] < 0 and a_pb["p"] < 0.05 and s_pb_tb["p"] >= 0.05, "PhoBERT tinh chỉnh ngang hoặc hơn các mô hình đồ thị đã thử", "5.6.1, PhoBERT so với đồ thị"),
    ]
    return kiem


def so_lieu_dinh_huong(goc: Path) -> Kiem:
    """Mục 5.4 và 5.6: ràng buộc rút từ Chương 4, và chứng cứ trong bản gốc cho các nhận định về các công trình tìm thêm."""
    mf = {e: [json.loads((goc / "results" / e / f"seed{s}" / "metrics.json").read_text(encoding="utf-8"))["test"]["macro_f1"]
              for s in cb.SEEDS] for e in MANH}
    cap = [(a, b) for i, a in enumerate(MANH) for b in MANH[i + 1:]]
    hieu = {ab: [x - y for x, y in zip(mf[ab[0]], mf[ab[1]])] for ab in cap}
    nho_va_doi_dau = all(abs(np.mean(d)) < 0.01 and min(d) < 0 < max(d) for d in hieu.values())
    kiem: Kiem = [dc4.neu(nho_va_doi_dau, "mọi chênh lệch giữa các mô hình dùng PhoBERT đều dưới 1 điểm macro-F1 và thay đổi theo seed",
                          "5.6.2, mốc so sánh"),
                  dc4.neu(nho_va_doi_dau, "Muốn tăng 1 điểm, lớn hơn mọi chênh lệch giữa các mô hình dùng PhoBERT ở Chương 4", "5.6.2, mức 1 điểm")]
    for k, cau in CHUNG_CU.items():
        p = goc / NGUON_GOC / f"{k}.txt"
        if not p.exists():
            kiem.append((f"5.6, bản gốc {k}", f"THIẾU BẢN GỐC {k}: chạy python scripts/doi_chieu_ban_goc.py tai"))
            continue
        van = gon(p.read_text(encoding="utf-8"))
        thieu = [x for x in cau if gon(x) not in van]
        kiem.append((f"5.6, chứng cứ của {k}", f"[@{k}]" if not thieu else f"BẢN GỐC {k} KHÔNG CÓ CÂU: {thieu[0]}"))
    kiem.append(("5.6.2, Moore và Barnes", "thêm tác vụ phụ về phủ định làm F1 tăng trung bình 3,8 điểm trên các tập thử thách phủ định khi dùng GloVe"))
    bn = goc / NGUON_GOC / "BarnesNotSolved2019.txt"
    if bn.exists():
        t = re.sub(r"\s+", " ", bn.read_text(encoding="utf-8"))
        so = [re.search(m, t) for m in (r"no-sentiment \((\d+)\)", r"\((\d+)\), non-standard spelling", r"Negation, which accounts for (\d+) errors")]
        if all(so):
            khong_cx, lan_lon, phu_dinh = (int(m.group(1)) for m in so)
            kiem.append(dc4.neu(1.5 < min(khong_cx, lan_lon) / phu_dinh and max(khong_cx, lan_lon) / phu_dinh < 2.5,
                                "mỗi nguồn khoảng gấp đôi số câu sai có phủ định", "5.6.1, Barnes và cộng sự"))
        else:
            kiem.append(("5.6.1, Barnes và cộng sự", "KHÔNG ĐỌC ĐƯỢC SỐ ĐẾM TRONG BẢN GỐC BarnesNotSolved2019"))
    return kiem


def tim(kiem: Kiem, van: str, cac_bang: Dict[str, dict]) -> Tuple[int, List[Tuple[str, str, str]]]:
    """Hàng bảng (mô tả "Bảng 5.x, ...") tìm trong đúng bảng đó; tên bảng phải chứa từ khoá; còn lại tìm trong toàn chương."""
    lech = []
    for mo_ta, chuoi in kiem:
        m = re.match(r"^(Bảng|Hình) (\d+\.\d+), (.*)$", mo_ta)
        if m and m.group(1) == "Bảng" and m.group(3) != "tên":
            bang = cac_bang.get(m.group(2))
            if bang is None:
                lech.append((mo_ta, chuoi, f"bản nháp không có Bảng {m.group(2)}"))
            elif dc4.chuan(chuoi) not in bang["van"]:
                lech.append((mo_ta, chuoi, f"Bảng {m.group(2)} không có hàng này"))
            elif TU_KHOA_BANG[m.group(2)] not in bang["ten"]:
                lech.append((mo_ta, chuoi, f"tên Bảng {m.group(2)} không chứa \"{TU_KHOA_BANG[m.group(2)]}\""))
        elif dc4.chuan(chuoi) not in van:
            lech.append((mo_ta, chuoi, "không thấy cụm chữ này trong chương"))
    return len(kiem), lech


def so_chua_kiem(tho: str, kiem: Kiem, cac_cau: Sequence[str] = ()) -> List[str]:
    """Các con số trong chương (trừ tham chiếu mục, bảng, hình và lời trích nguyên văn ở mục 5.3) không nằm trong chỗ kiểm nào."""
    bo = MAU_THAM_CHIEU.sub(" ", tho)
    for cau in cac_cau:
        bo = bo.replace(cau, " ")
    gom = " ".join(dc4.chuan(c) for _, c in kiem if c)
    ra = []
    for s in dict.fromkeys(dc4.MAU_SO.findall(bo)):
        if not re.search(rf"(?<![\d,.]){re.escape(s)}(?![\d,]|\.\d)", gom):
            ra.append(s)
    return ra


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Đối chiếu số liệu Chương 5 với file kết quả.")
    ap.add_argument("--goc", type=Path, default=Path("."), help="thư mục gốc của repo")
    ap.add_argument("--nhap", type=Path, default=TEP_MAC_DINH, help=f"bản nháp Chương 5 (mặc định {TEP_MAC_DINH})")
    a = ap.parse_args(argv)

    tho = (a.goc / a.nhap).read_text(encoding="utf-8")
    van = dc4.chuan(tho)
    cac_bang = dc4.tach_bang(tho)
    kiem = (so_lieu_phan_tich_loi(a.goc) + so_lieu_tu_du_doan(a.goc) + so_lieu_trung_tinh_trai_nhan(a.goc) + so_lieu_ca(a.goc)
            + so_lieu_tham_do(a.goc) + so_lieu_bo_sung(a.goc) + so_lieu_dinh_huong(a.goc))
    da_kiem, lech = tim(kiem, van, cac_bang)
    for mo_ta, chuoi, ly_do in lech:
        print(f"KHÔNG THẤY  {mo_ta}: {ly_do}\n            cần có: {chuoi}")
    cd = {r["uid"]: r for r in po.doc_jsonl(a.goc / "data/diagnostic/diagnostic_300.jsonl")}
    la = so_chua_kiem(tho, kiem, [cau_ca(cd[u]) for u in CA + VI_DU_LOI if u in cd])
    for s in la:
        print(f"SỐ CHƯA CÓ CHỖ KIỂM  {s}")
    print(f"Đã kiểm {da_kiem} chỗ trong {a.nhap.name}: {da_kiem - len(lech)} khớp, {len(lech)} lệch."
          + (f" {len(la)} con số chưa có chỗ kiểm." if la else " Mọi con số trong chương đều có chỗ kiểm."))
    return 1 if lech or la else 0


if __name__ == "__main__":
    raise SystemExit(main())
