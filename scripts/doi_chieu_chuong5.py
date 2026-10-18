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
import probe_oracle_rules as po  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEP_MAC_DINH = Path("chuyende1/report/nhap_rut_gon/Chuong5_HanCheVaDinhHuong.md")
MO_HINH = dc4.MO_HINH
HOC = tuple(e for e in MO_HINH if e != "lexicon")  # năm mô hình học
MANH = ea.MANH  # bốn mô hình dùng PhoBERT
DO_THI = tuple(e for e in MANH if e != "phobert")
NHAN = ("tiêu cực", "trung tính", "tích cực")
# Bốn ca của mục 5.3, theo thứ tự trong danh sách. Câu lấy từ tập chẩn đoán, gộp khoảng trắng.
CA = ("visfd-test-01659-FEATURES", "visfd-test-01581-CAMERA", "visfd-test-00801-BATTERY", "visfd-test-01975-PRICE")
TU_KHOA_BANG = {"5.1": "lật đúng mọi lỗi ngược cực"}
# Bỏ qua khi quét số: tham chiếu mục, bảng, hình, chương ("mục 5.2 và 5.4" bỏ cả hai số), số thứ tự đầu dòng
# của danh sách, tiêu đề và đường dẫn hình.
MAU_THAM_CHIEU = re.compile(r"(?:mục|Mục|Bảng|Hình|Chương|bảng|hình) \d+(?:\.\d+)?(?: và \d+\.\d+)?|^\d+\. |^#+ .*$|^!\[.*$", re.M)

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
    tt = kc["ti_le_trung_tinh"]
    khac_price = max(v for k, v in tt.items() if k != "PRICE")
    hang_price = sorted(f1_kc, key=f1_kc.get, reverse=True).index("PRICE") + 1
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
        dc4.neu(seeds == 5, "Mọi tỉ lệ là trung bình năm seed", "5.1, năm seed"),
        dc4.neu(all(min(range(3), key=lambda i: tim_lai[e][i]) == 1 for e in MO_HINH) and nham_ca_hai,
                "Ở cả sáu mô hình, lớp trung tính có tỉ lệ tìm lại thấp nhất trong ba lớp, và mẫu trung tính bị đoán thành cả tích cực lẫn tiêu cực",
                "5.1, tìm lại lớp trung tính"),
        dc4.neu(all(co_tt[e] > 0.8 for e in MANH),
                "ở cả bốn mô hình dùng PhoBERT, hơn bốn phần năm số lỗi có lớp trung tính ở nhãn thật hoặc nhãn đoán", "5.1, lỗi có lớp trung tính"),
        ("5.1, ba khía cạnh thấp nhất", f"khía cạnh có macro-F1 thấp nhất ở PhoBERT tinh chỉnh là {dc4.liet_ke(thap)}"),
        dc4.neu(all(sp[e]["rho"] > 0 for e in HOC),
                f"tương quan dương với macro-F1 ở cả năm mô hình học, nhưng tương quan hạng Spearman chỉ có ý nghĩa ở {dc4.so_chu(so_y_nghia)} mô hình",
                "5.1, tương quan theo khía cạnh"),
        ("5.1, PRICE", f"PRICE có {pt(tt['PRICE'])} % mẫu kiểm tra là trung tính, trong khi ở chín khía cạnh còn lại tỉ lệ này "
                       f"không quá {pt(khac_price)} %, vậy mà macro-F1 của PhoBERT ở PRICE cao thứ {dc4.so_chu(hang_price)} trong mười khía cạnh"),
        dc4.neu(giam_dan, "giảm dần khi bình luận dài ra ở cả sáu mô hình", "5.1, giảm theo độ dài"),
        ("5.1, PhoBERT theo độ dài", f"từ {pt(acc_dd['phobert'][0])} % với bình luận đến {ea.DO_DAI[0][3]} từ xuống "
                                    f"{pt(acc_dd['phobert'][-1])} % với bình luận trên {ea.DO_DAI[-1][2] - 1} từ"),
        dc4.neu(chenh_dai < 1, "ba mô hình đồ thị chênh PhoBERT không quá 1 điểm", "5.1, nhóm dài nhất"),
        ("5.1, cắt đầu vào", f"việc cắt đầu vào ở {max_len} subword (mục 4.2)"),
        dc4.neu(trai_kem, "accuracy trên mẫu thuộc bình luận trái nhãn thấp hơn mẫu thuộc bình luận nhiều khía cạnh cùng nhãn, với p nhỏ hơn 0,001",
                "5.1, bình luận trái nhãn"),
        ("5.1, khoảng cách ở PhoBERT", f"ở PhoBERT, khoảng cách là {pt(-lc['phobert']['da_trai']['accuracy']['hieu_voi_moc'])} điểm"),
        ("5.1, lỗi sang nhãn kia", f"từ {pt(min(kia))} đến {pt(max(kia))} % số lỗi của bốn mô hình dùng PhoBERT rơi vào chính nhãn còn lại"),
        ("Hình 5.1, tên", f"(trung bình {seeds} seed, khoảng tin cậy 95 % bằng bootstrap theo bình luận)"),
        ("5.1, luôn sai", f"sai ở cả {dc4.so_chu(seeds)} seed, trên {min(luon)} đến {max(luon)} mẫu, và {c} mẫu trong số đó là chung cho cả bốn mô hình, "
                          f"bằng {pt(c / n)} % tập kiểm tra"),
        ("5.1, lỗi cứng của PhoBERT", f"Trong {gl['luon_sai']['phobert']} mẫu PhoBERT luôn sai, {c} mẫu vẫn luôn sai ở cả ba mô hình đồ thị"),
        dc4.neu(tt_cung / c > 0.5, f"Nhóm {c} mẫu này có hơn một nửa là mẫu trung tính, trong khi lớp trung tính chỉ chiếm "
                                   f"{pt(gl['tat_ca_theo_nhan']['trung tính'] / n)} % tập kiểm tra, và {pt(gl['cung_sai_o_cau_trai_nhan'] / c)} % số mẫu "
                                   "thuộc bình luận trái nhãn", "5.1, đặc điểm nhóm cùng sai"),
        dc4.neu(tt_cung / c > 0.5, "chiếm hơn một nửa số mẫu mà cả bốn mô hình dùng PhoBERT cùng sai", "5.2, hạn chế 1"),
        dc4.neu(c / gl["luon_sai"]["phobert"] > 0.5, "phần lớn lỗi cứng của PhoBERT vẫn là lỗi cứng ở ba mô hình đồ thị", "5.2, lỗi cứng"),
        dc4.neu(all(sn[e]["phan_loi_sang_nhan_kia"] > 0.5 for e in MO_HINH) and trai_kem,
                "Bình luận trái nhãn khó hơn rõ ở mọi mô hình, và phần lớn lỗi ở bình luận hai nhãn là lấy nhãn của khía cạnh kia", "5.2, hạn chế 2"),
        dc4.neu(all(lc[e]["da_trai"]["accuracy"]["gia_tri"] <= lc["phobert"]["da_trai"]["accuracy"]["gia_tri"] for e in DO_THI),
                "các mô hình đồ thị ở Chương 4 chưa cải thiện được nó so với PhoBERT", "5.2, đồ thị ở bình luận trái nhãn"),
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
    kiem: Kiem = [
        ("5.2, mẫu vừa cùng sai vừa thuộc tập chẩn đoán",
         f"trong {len(giao)} mẫu vừa thuộc nhóm cùng sai vừa thuộc tập chẩn đoán, người chú thích không đồng ý với nhãn gốc ở {len(khac)} mẫu, "
         f"và {len(goc_tt)} mẫu trong số đó có nhãn gốc trung tính mà người chú thích cho là có cực"),
        ("5.3, số lần chạy", f"Nhãn đoán là nhãn được đoán nhiều nhất trong {so_lan} lần chạy"),
    ]
    ten_kt = {"dong_y": "đồng ý", "negative": "gán tiêu cực", "neutral": "gán trung tính", "positive": "gán tích cực"}
    for i, u in enumerate(CA, 1):
        if u not in cung or u not in cd:
            kiem.append((f"5.3, mẫu {i}", f"SỐ LIỆU KHÔNG CÒN ĐỠ MẪU: {u} không còn thuộc nhóm cùng sai hoặc không có trong tập chẩn đoán"))
            continue
        r = cd[u]
        nhan, dem = Counter(doan[u]).most_common(1)[0]
        kiem.append((f"5.3, mẫu {i}", f"{i}. Khía cạnh {r['aspect']} của \"{cau_ca(r)}\": nhãn gốc {NHAN[r['label']]}, người chú thích "
                                      f"{ten_kt[r['nhan_kiem_tra']]}, các mô hình đoán {NHAN[nhan]} ở {dem} trên {so_lan} lần chạy"))
    ba = "visfd-test-00801-BATTERY"
    kiem.append(dc4.neu({cd[ba]["label"], Counter(doan[ba]).most_common(1)[0][0]} == {0, 2},
                        "Đây là một lỗi ngược cực: người viết phản bác lời chê về pin", "5.3, mẫu thứ ba"))
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
    kiem: Kiem = [("Bảng 5.1, tên", f"(số lỗi trung bình mỗi seed, {len(cb.SEEDS)} seed)")]
    for g in nhom:
        x = c[g]
        kiem.append((f"Bảng 5.1, {g}", f"| {po.TEN_NHOM[g]} | {x['n']} | {s1(x['loi'])} | {s1(x['loi_nguoc_cuc'])} | {s1(x['loi_goc_trung_tinh'])} | "
                                       f"{s1(x['loi_o_dong_khong_dong_y'])} | {pt(x['tang'], 2)} |"))
    tho = sum(len(po.o_cua(r) is not None and [1] or []) for r in chan_doan)
    kiem += [
        dc4.neu(all(c[g]["loi_nguoc_cuc"] / c[g]["loi"] < 0.2 and c[g]["loi_goc_trung_tinh"] / c[g]["loi"] > 0.5 for g in nhom),
                "Lỗi ngược cực chỉ là phần nhỏ trong mọi nhóm; phần lớn lỗi là mẫu có nhãn gốc trung tính mà mô hình đoán có cực", "5.4, loại lỗi"),
        dc4.neu(c["negation"]["tang"] < 0.01 and abs(c["negation"]["tang"] - c["regular"]["tang"]) < 0.005,
                "nâng macro-F1 của nhóm phủ định chưa tới 1 điểm, và mức tăng ở nhóm phủ định không khác nhiều nhóm thường", "5.4, nhóm phủ định"),
        ("5.4, toàn tập", f"macro-F1 của PhoBERT tăng tối đa {pt(t['nguoc_cuc_o_cau_co_phu_dinh']['tang_macro_f1'], 2)} điểm; lật đúng mọi lỗi ngược cực "
                          f"ở bất cứ đâu cũng chỉ tăng {pt(t['nguoc_cuc_moi_cho']['tang_macro_f1'], 2)} điểm"),
        ("5.4, ba mô hình đồ thị", f"macro-F1 trên toàn tập tăng từ {pt(min(tang_dt), 2)} đến {pt(max(tang_dt), 2)} điểm"),
        ("5.4, luật phủ định", f"luật từ khoá phủ định bắt được {pt(p2['phu_dinh']['do_phu'])} % số mẫu thật sự có phủ định, nhưng chỉ "
                               f"{pt(p2['phu_dinh']['do_chinh_xac'])} % số mẫu nó bắt là có phủ định tác động lên đúng khía cạnh đó"),
        ("5.4, luật chuyển ý", f"Luật từ nối chuyển ý có độ chính xác {pt(p2['chuyen_y']['do_chinh_xac'])} % và độ phủ {pt(p2['chuyen_y']['do_phu'])} %"),
        dc4.neu(p2["chuyen_y"]["bo_sot_tren_tap_chan_doan"]["co_tu_ngo"] > 0
                and p2["chuyen_y"]["bo_sot_tren_tap_chan_doan"]["dong"] > p2["chuyen_y"]["bo_sot_tren_tap_chan_doan"]["co_tu_ngo"],
                "nó bỏ sót những chuyển ý dùng từ đa nghĩa như \"mà\", \"còn\", vốn đã bị loại khỏi danh sách, hay những cách nói không có trong danh sách",
                "5.4, chuyển ý bị bỏ sót"),
        ("5.4, quần thể ước lượng", f"các mẫu thuộc bình luận từ {po.bd.DO_DAI_MAC_DINH[0]} đến {po.bd.DO_DAI_MAC_DINH[1]} từ và không chỉ chứa từ đa nghĩa"),
        dc4.neu(tho / len(chan_doan) > 0.9, "vì tập chẩn đoán được rút chủ yếu từ phần này", "5.4, tập chẩn đoán rút từ đâu"),
        ("5.4, dạng chuẩn", f"được gán là phó từ ở {pt(p3['chuan']['ti_le_pho_tu'])} % số lượt và kề từ đứng sau trên cây ở "
                            f"{pt(p3['chuan']['ti_le_ke_nhau'])} % số lượt"),
        dc4.neu(abs(p3["viet_tat"]["luot"] / (p3["viet_tat"]["luot"] + p3["chuan"]["luot"]) - 0.5) < 0.02,
                "Một nửa số lượt từ phủ định trong tập kiểm tra lại là dạng viết tắt", "5.4, một nửa là viết tắt"),
        dc4.neu(p3["viet_tat"]["ti_le_pho_tu"] == 0, "VnCoreNLP không gán phó từ cho lượt nào trong số đó", "5.4, viết tắt không là phó từ"),
        ("5.4, viết tắt kề nhau", f"chỉ {pt(p3['viet_tat']['ti_le_ke_nhau'])} % số lượt được gắn kề từ đứng sau"),
        dc4.neu(all(c[g]["loi_o_dong_khong_dong_y"] / c[g]["loi"] > 0.5 for g in co_ht),
                "hơn một nửa số lỗi của PhoBERT ở ba nhóm có hiện tượng nằm ở những mẫu như vậy", "5.2, hạn chế 4"),
        dc4.neu(all(c[g]["loi_nguoc_cuc"] / c[g]["loi"] < 0.5 for g in co_ht),
                "lỗi ở các nhóm này phần lớn không phải lỗi ngược cực", "5.2, hạn chế 3"),
    ]
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
    kiem = (so_lieu_phan_tich_loi(a.goc) + so_lieu_trung_tinh_trai_nhan(a.goc) + so_lieu_ca(a.goc) + so_lieu_tham_do(a.goc))
    da_kiem, lech = tim(kiem, van, cac_bang)
    for mo_ta, chuoi, ly_do in lech:
        print(f"KHÔNG THẤY  {mo_ta}: {ly_do}\n            cần có: {chuoi}")
    cd = {r["uid"]: r for r in po.doc_jsonl(a.goc / "data/diagnostic/diagnostic_300.jsonl")}
    la = so_chua_kiem(tho, kiem, [cau_ca(cd[u]) for u in CA if u in cd])
    for s in la:
        print(f"SỐ CHƯA CÓ CHỖ KIỂM  {s}")
    print(f"Đã kiểm {da_kiem} chỗ trong {a.nhap.name}: {da_kiem - len(lech)} khớp, {len(lech)} lệch."
          + (f" {len(la)} con số chưa có chỗ kiểm." if la else " Mọi con số trong chương đều có chỗ kiểm."))
    return 1 if lech or la else 0


if __name__ == "__main__":
    raise SystemExit(main())
