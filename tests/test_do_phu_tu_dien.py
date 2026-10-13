"""[CD1.12b] Kiểm scripts/do_phu_tu_dien.py trên một từ điển và một tập dữ liệu tí hon."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import do_phu_tu_dien as m  # noqa: E402


def test_doc_vswn_tach_muc_tu_va_do_phu_dem_tren_mau(tmp_path):
    v = tmp_path / "v.txt"
    v.write_text("# POS\tID\tPosScore\tNegScore\tSynsetTerms\tGloss\n"
                 "a\t1\t0.5\t0\thấp_dẫn#1\tgiải thích\n"
                 "a\t2\t0.7\t0\ttốt_hơn#3 tốt nhất#2\tgiải thích\n"
                 "dòng hỏng\n", encoding="utf-8")
    so_dong, muc = m.doc_vswn(v)
    assert so_dong == 2 and muc == {"hấp_dẫn", "tốt_hơn", "tốt_nhất"}
    d = tmp_path / "x.jsonl"
    d.write_text("".join(json.dumps({"tokens": t}, ensure_ascii=False) + "\n"
                         for t in (["Hấp_dẫn", "lắm"], ["pin", "tệ"], ["tốt_nhất", "tốt_nhất", "luôn", "nhé"])), encoding="utf-8")
    r = m.do_phu(d, muc)
    assert r["luot_tu"] == 8 and r["ti_le_phu"] == pytest.approx(3 / 8)
    assert r["ti_le_mau_co_tu"] == pytest.approx(2 / 3) and r["so_muc_gap"] == 2


def test_senticnet_khong_dau_duoc_tra_sau_khi_bo_dau(tmp_path):
    assert m.bo_dau("Tốt") == "tot" and m.bo_dau("ĐẸP") == "dep" and m.bo_dau("thất_vọng") == "that_vong"
    s = tmp_path / "senticnet.py"
    s.write_text("# -*- coding: utf-8 -*-\nsenticnet={}\n"
                 "senticnet['tot'] = [0, 0, 0.9, 0, '#joy', None, 'positive', 0.659, 'a', 'b', 'c', 'd', 'e']\n"
                 "senticnet['may'] = [-0.9, 0, 0, 0, '#grief', None, 'negative', -0.951, 'a', 'b', 'c', 'd', 'e']\n"
                 "senticnet['hong'] = [0, 0, 0, 0]\n", encoding="utf-8")
    sn = m.doc_senticnet(s)
    assert sn == {"tot": 0.659, "may": -0.951}  # dòng thiếu điểm cực tính bị bỏ qua
    d = tmp_path / "x.jsonl"
    d.write_text(json.dumps({"tokens": ["Máy", "tốt", "lắm"]}, ensure_ascii=False) + "\n", encoding="utf-8")
    assert m.do_phu(d, sn)["ti_le_phu"] == 0.0  # không bỏ dấu thì không tra được gì
    r = m.do_phu(d, sn, m.bo_dau)
    assert r["ti_le_phu"] == pytest.approx(2 / 3) and r["so_muc_gap"] == 2
