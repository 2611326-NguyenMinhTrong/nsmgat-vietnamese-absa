"""[CD1.7] Kiểm scripts/eval_llm.py mà không gọi API: rút tập con, dựng câu lệnh, đọc câu trả lời, bộ nhớ đệm, bảng."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import eval_llm as m  # noqa: E402

NHAN = ["tiêu cực", "trung tính", "tích cực"]


def _ban_ghi(phan: str, i: int, nhan: int, so_tu: int = 6, khia_canh: str = "BATTERY") -> dict:
    tu = [f"tu{j}" for j in range(so_tu)]
    return {"uid": f"visfd-{phan}-{i:05d}-{khia_canh}", "text": f"câu thô số {i} của {phan}", "tokens": tu,
            "pos": ["N"] * so_tu, "heads": [-1] * so_tu, "deprels": ["root"] * so_tu, "aspect": khia_canh,
            "label": nhan, "domain": "visfd", "split": phan}


def _repo(tmp_path: Path, so_test: int = 30, so_mau: int = 12) -> dict:
    """Dựng một repo tí hon: dữ liệu, cấu hình. Trả về cấu hình đã đọc."""
    d = tmp_path / "data" / "processed"
    d.mkdir(parents=True)
    # test: nhãn lệch 3 : 1 : 6 như dữ liệu thật
    khuon = [0, 0, 0, 1, 2, 2, 2, 2, 2, 2]
    for phan, n in (("train", 60), ("test", so_test)):
        with (d / f"visfd_{phan}.jsonl").open("w", encoding="utf-8") as fh:
            for i in range(n):
                fh.write(json.dumps(_ban_ghi(phan, i, khuon[i % 10]), ensure_ascii=False) + "\n")
    cfg = m.doc_cau_hinh(Path(__file__).resolve().parents[1] / "configs" / "llm.yaml")
    cfg["tap_con"]["so_mau"] = so_mau
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "llm.yaml").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")  # JSON là YAML hợp lệ
    return cfg


def test_cau_hinh_that_co_du_muoi_khia_canh_va_ba_nhan():
    cfg = m.doc_cau_hinh(Path(__file__).resolve().parents[1] / "configs" / "llm.yaml")
    from nsmgat.data.aspects import ASPECT_VI

    assert set(cfg["khia_canh"]) == set(ASPECT_VI)
    # cùng cách gọi tên với Bảng 4.3, chỉ bỏ dấu gạch dưới
    assert {k: v.replace("_", " ") for k, v in ASPECT_VI.items()} == cfg["khia_canh"]
    assert cfg["nhan"] == NHAN
    assert "{binh_luan}" in cfg["nguoi_dung"] and "{khia_canh}" in cfg["nguoi_dung"]
    assert cfg["tham_so"]["temperature"] == 0


def test_chon_tap_con_giu_ti_le_va_lap_lai_duoc():
    ban_ghi = [_ban_ghi("test", i, [0, 0, 0, 1, 2, 2, 2, 2, 2, 2][i % 10]) for i in range(200)]
    uid = m.chon_tap_con(ban_ghi, 50, 42)
    assert len(uid) == len(set(uid)) == 50 and uid == sorted(uid)
    nhan = {r["uid"]: r["label"] for r in ban_ghi}
    assert [sum(1 for u in uid if nhan[u] == k) for k in range(3)] == [15, 5, 30]
    assert m.chon_tap_con(ban_ghi, 50, 42) == uid
    assert m.chon_tap_con(ban_ghi, 50, 7) != uid
    with pytest.raises(ValueError):
        m.chon_tap_con(ban_ghi, 201, 42)


def test_chon_tap_con_lam_tron_theo_phan_du_lon_nhat():
    # 7 mẫu: 3 / 1 / 3. Rút 5 thì phần chia là 2,14 / 0,71 / 2,14; mẫu còn lại phải vào lớp có phần dư lớn nhất.
    ban_ghi = [_ban_ghi("test", i, k) for i, k in enumerate([0, 0, 0, 1, 2, 2, 2])]
    uid = m.chon_tap_con(ban_ghi, 5, 1)
    nhan = {r["uid"]: r["label"] for r in ban_ghi}
    assert [sum(1 for u in uid if nhan[u] == k) for k in range(3)] == [2, 1, 2]


def test_chon_vi_du_can_bang_lop_va_ton_trong_gioi_han_do_dai():
    train = [_ban_ghi("train", i, i % 3, so_tu=3 + i % 50) for i in range(300)]
    a = m.chon_vi_du(train, 2, 42, 5, 40)
    assert sorted(r["label"] for r in a) == [0, 0, 1, 1, 2, 2]
    assert all(5 <= len(r["tokens"]) <= 40 for r in a)
    assert [r["uid"] for r in m.chon_vi_du(train, 2, 42, 5, 40)] == [r["uid"] for r in a]
    assert {r["uid"] for r in m.chon_vi_du(train, 2, 1337, 5, 40)} != {r["uid"] for r in a}
    with pytest.raises(ValueError):
        m.chon_vi_du(train[:3], 2, 42, 5, 40)


def test_tin_nhan_dung_van_ban_tho_va_ten_khia_canh(tmp_path):
    cfg = _repo(tmp_path)
    r = _ban_ghi("test", 1, 2, khia_canh="SER&ACC")
    zs = m.tin_nhan(cfg, r)
    assert [t["role"] for t in zs] == ["system", "user"]
    assert "câu thô số 1 của test" in zs[1]["content"] and "tu0" not in zs[1]["content"]
    assert "dịch vụ và phụ kiện" in zs[1]["content"] and "SER&ACC" not in zs[1]["content"]
    vi_du = [_ban_ghi("train", 5, 0), _ban_ghi("train", 6, 1)]
    fs = m.tin_nhan(cfg, r, vi_du)
    assert [t["role"] for t in fs] == ["system", "user", "assistant", "user", "assistant", "user"]
    assert [fs[2]["content"], fs[4]["content"]] == ["tiêu cực", "trung tính"]
    assert fs[-1] == zs[-1]


@pytest.mark.parametrize("tho, mong", [
    ("tích cực", (2, True)), ("Tiêu cực.", (0, True)), ("  TRUNG TÍNH\n", (1, True)), ("tiêu_cực", (0, True)),
    ("Cảm xúc: tích cực", (2, False)), ("negative", (0, False)), ("trung lập", (1, False)),
    ("tích cực và tiêu cực", (m.KHONG_DOC_DUOC, False)), ("không rõ", (m.KHONG_DOC_DUOC, False)), ("", (m.KHONG_DOC_DUOC, False)),
])
def test_doc_nhan(tho, mong):
    assert m.doc_nhan(tho, NHAN) == mong


def test_do_do_tinh_cau_khong_doc_duoc_la_sai():
    f, acc, f1 = m.do_do(m.dem_o([0, 0, 1, 2], [0, m.KHONG_DOC_DUOC, 1, 2]))
    assert acc == pytest.approx(0.75)
    assert list(f1) == pytest.approx([2 / 3, 1.0, 1.0])
    assert f == pytest.approx(8 / 9)


def test_do_do_khop_sklearn_khi_khong_co_cau_khong_doc_duoc():
    from sklearn.metrics import accuracy_score, f1_score

    rng = np.random.default_rng(0)
    vang, doan = rng.integers(0, 3, 200), rng.integers(0, 3, 200)
    f, acc, _ = m.do_do(m.dem_o(vang, doan))
    assert f == pytest.approx(f1_score(vang, doan, average="macro"))
    assert acc == pytest.approx(accuracy_score(vang, doan))


def _goi_gia(dem: list, tra_loi=lambda tin: "tích cực"):
    def goi(cfg, tin):
        dem.append(tin)
        return {"tho": tra_loi(tin), "mo_hinh": "gia-2026-01-01", "system_fingerprint": "fp_1", "usage": {"prompt_tokens": 100, "completion_tokens": 2}}
    return goi


def test_chay_ghi_du_file_va_lan_sau_khong_goi_lai(tmp_path):
    cfg = _repo(tmp_path)
    assert m.cmd_chon(cfg, tmp_path, False) == 0
    dem: list = []
    meta = m.chay(cfg, "zs", 42, tmp_path, _goi_gia(dem))
    thu_muc = tmp_path / "results" / "gpt4o_zeroshot" / "seed42"
    assert len(dem) == 12 and meta["so_lan_goi_moi"] == 12 and meta["token_vao"] == 1200
    assert meta["mo_hinh_tra_ve"] == ["gia-2026-01-01"] and meta["khong_doc_duoc"] == 0
    du_doan = [json.loads(d) for d in (thu_muc / "predictions.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(du_doan) == 12 and {r["y_pred"] for r in du_doan} == {2}
    khuon = json.loads((thu_muc / "metrics.json").read_text(encoding="utf-8"))
    cu = json.loads((Path(__file__).resolve().parents[1] / "results" / "phobert" / "seed42" / "metrics.json").read_text(encoding="utf-8"))
    assert set(khuon) == set(cu) and set(khuon["test"]) == set(cu["test"])
    # tập con 12 mẫu có 7 mẫu tích cực (4 : 1 : 7 sau khi làm tròn)
    assert khuon["test"]["accuracy"] == pytest.approx(sum(1 for r in du_doan if r["y_true"] == 2) / 12)

    meta2 = m.chay(cfg, "zs", 42, tmp_path, _goi_gia(dem))
    assert len(dem) == 12 and meta2["so_lan_goi_moi"] == 0
    assert meta2["accuracy"] == meta["accuracy"]


def test_chay_thu_khong_ghi_metrics(tmp_path):
    cfg = _repo(tmp_path)
    m.cmd_chon(cfg, tmp_path, False)
    dem: list = []
    meta = m.chay(cfg, "fs", 1337, tmp_path, _goi_gia(dem), gioi_han=3)
    thu_muc = tmp_path / "results" / "gpt4o_fewshot" / "seed1337"
    assert len(dem) == 3 and meta["chay_thu"] and len(meta["uid_vi_du"]) == 6
    assert not (thu_muc / "metrics.json").exists() and not (thu_muc / "predictions.jsonl").exists()
    assert len(dem[0]) == 1 + 2 * 6 + 1  # hệ thống, sáu ví dụ, mẫu cần hỏi
    # chạy đủ sau đó dùng lại ba câu trả lời đã trả tiền
    meta = m.chay(cfg, "fs", 1337, tmp_path, _goi_gia(dem))
    assert len(dem) == 12 and meta["so_lan_goi_moi"] == 9


def test_doi_cau_lenh_thi_bo_nho_dem_khong_con_trung(tmp_path):
    cfg = _repo(tmp_path)
    m.cmd_chon(cfg, tmp_path, False)
    dem: list = []
    m.chay(cfg, "zs", 42, tmp_path, _goi_gia(dem))
    cfg["he_thong"] += " Trả lời ngắn."
    m.chay(cfg, "zs", 42, tmp_path, _goi_gia(dem))
    assert len(dem) == 24


def test_chon_khong_ghi_de_danh_sach_da_co(tmp_path):
    cfg = _repo(tmp_path)
    assert m.cmd_chon(cfg, tmp_path, False) == 0
    tep = tmp_path / cfg["tap_con"]["tep_uid"]
    truoc = tep.read_text(encoding="utf-8")
    assert m.cmd_chon(cfg, tmp_path, False) == 1 and tep.read_text(encoding="utf-8") == truoc
    thong_tin = json.loads(truoc)
    assert thong_tin["so_mau"] == 12 and sum(thong_tin["phan_bo"].values()) == 12
    assert "text" not in truoc and "câu thô" not in truoc  # danh sách không mang câu của bộ dữ liệu


def test_thieu_khoa_thi_dung_va_khong_goi_gi(tmp_path, monkeypatch):
    cfg = _repo(tmp_path)
    monkeypatch.delenv(cfg["nha_cung_cap"]["bien_khoa"], raising=False)
    with pytest.raises(SystemExit):
        m.lay_khoa(cfg)


def test_bang_so_tren_cung_tap_con(tmp_path):
    cfg = _repo(tmp_path, so_test=60, so_mau=30)
    m.cmd_chon(cfg, tmp_path, False)
    test = m.doc_jsonl(tmp_path / cfg["du_lieu"]["test"])
    # phobert đoán đúng mọi mẫu của cả tập kiểm tra; mô hình ngôn ngữ luôn trả "tích cực"
    for s in m.SEED_VI_DU:
        d = tmp_path / "results" / "phobert" / f"seed{s}"
        d.mkdir(parents=True)
        with (d / "predictions.jsonl").open("w", encoding="utf-8") as fh:
            for r in test:
                fh.write(json.dumps({"uid": r["uid"], "aspect": r["aspect"], "y_true": r["label"], "y_pred": r["label"]}) + "\n")
    m.chay(cfg, "zs", 42, tmp_path, _goi_gia([]))
    assert m.cmd_bang(cfg, tmp_path, 200, 1, Path("results/llm_eval.json"), Path("bang.md")) == 0
    kq = {h["exp"]: h for h in json.loads((tmp_path / "results" / "llm_eval.json").read_text(encoding="utf-8"))["ket_qua"]}
    assert set(kq) == {"gpt4o_zeroshot", "phobert"}  # bốn mô hình còn lại chưa có file thì bị bỏ qua
    assert kq["phobert"]["accuracy"] == pytest.approx(1.0) and kq["phobert"]["so_voi_phobert"] is None
    ti_le_tich_cuc = 18 / 30
    assert kq["gpt4o_zeroshot"]["accuracy"] == pytest.approx(ti_le_tich_cuc)
    assert kq["gpt4o_zeroshot"]["accuracy_std"] is None  # một lần chạy thì không có độ lệch chuẩn
    hs = kq["gpt4o_zeroshot"]["so_voi_phobert"]["accuracy"]
    assert hs["gia_tri"] == pytest.approx(ti_le_tich_cuc - 1.0) and hs["ci95_tren"] < 0 and hs["p"] < 0.05
    assert "PhoBERT tinh chỉnh" in (tmp_path / "bang.md").read_text(encoding="utf-8")
