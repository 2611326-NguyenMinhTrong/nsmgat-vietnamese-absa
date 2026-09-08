"""[CD1.4b] Test BiLSTMModel.

Trong tam: hai thu phan biet mo hinh nay voi `lexicon`.
  1. NHIN THAY khia canh (lexicon mu khia canh, bi chan o tran 80,2%)
  2. KHONG ro ri — tu vung xay CHI tu tap train
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nsmgat.models.bilstm import PAD_ID, UNK_ID, BiLSTMModel  # noqa: E402


def viet_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8"
    )


def lam_record(uid: str, tokens: list[str], aspect: str, label: int, split: str = "train") -> dict:
    n = len(tokens)
    return {
        "uid": uid,
        "text": " ".join(tokens),
        "tokens": tokens,
        "pos": ["X"] * n,
        "heads": [-1] * n,
        "deprels": ["root"] * n,
        "aspect": aspect,
        "label": label,
        "domain": "visfd",
        "split": split,
    }


@pytest.fixture(scope="module")
def cfg(tmp_path_factory) -> dict:
    d = tmp_path_factory.mktemp("bilstm")
    train = [
        lam_record("t1", ["pin", "rất", "trâu"], "BATTERY", 2),
        lam_record("t2", ["màn_hình", "tối"], "SCREEN", 0),
        lam_record("t3", ["máy", "đẹp"], "DESIGN", 2),
    ]
    viet_jsonl(d / "train.jsonl", train)
    viet_jsonl(d / "dev.jsonl", [lam_record("d1", ["pin", "tệ"], "BATTERY", 0, "dev")])
    return {
        "data": {"train_path": str(d / "train.jsonl"), "dev_path": str(d / "dev.jsonl")},
        "model": {
            "emb_dim": 16,
            "aspect_dim": 8,
            "lstm_hidden": 12,
            "dropout": 0.0,
            "encoder_name": "vinai/phobert-base-v2",
        },
    }


@pytest.fixture(scope="module")
def model(cfg) -> BiLSTMModel:
    return BiLSTMModel(cfg)


def lam_batch(aspect_texts: list[str], seq_len: int = 6) -> dict:
    b = len(aspect_texts)
    return {
        "input_ids": torch.randint(0, 60000, (b, seq_len)),
        "attention_mask": torch.ones((b, seq_len), dtype=torch.long),
        "aspect_text": aspect_texts,
        "labels": torch.zeros(b, dtype=torch.long),
        "uid": [f"u{i}" for i in range(b)],
    }


# --- Hop dong BaseModel -------------------------------------------------------


def test_forward_tra_ve_dung_shape(model):
    logits = model(lam_batch(["BATTERY", "SCREEN"]))
    assert logits.shape == (2, 3)


def test_explain_tra_ve_rong_theo_mac_dinh_BaseModel(model):
    """Hop dong noi baseline duoc phep tra []. KHONG duoc nem loi."""
    assert model.explain(lam_batch(["BATTERY"])) == []


def test_co_tham_so_hoc_duoc(model):
    assert model.count_params() > 0


def test_id_map_la_buffer_khong_phai_tham_so(model):
    """id_map la bang tra tinh — phai di theo GPU va nam trong state_dict,
    nhung KHONG duoc dem vao so tham so hoc duoc."""
    assert "id_map" in dict(model.named_buffers())
    assert "id_map" not in dict(model.named_parameters())


# --- Diem mau chot 1: NHIN THAY khia canh ------------------------------------


def test_doi_khia_canh_thi_dau_ra_DOI(model):
    """Day la khac biet cot loi so voi LexiconModel.

    LexiconModel mu khia canh: cung mot cau, moi khia canh cho cung mot du
    doan => bi chan o tran 80,2% accuracy (do o CD1.4a). BiLSTM phai vuot qua
    duoc tran do, nen dau ra BAT BUOC phai phu thuoc khia canh.
    """
    model.eval()
    batch = lam_batch(["BATTERY"])
    with torch.no_grad():
        a = model(batch)
        batch["aspect_text"] = ["SCREEN"]
        b = model(batch)

    assert not torch.allclose(a, b), "doi khia canh ma dau ra khong doi => mu khia canh"


def test_khia_canh_la_khong_lam_sap(model):
    """Khia canh chua tung thay luc huan luyen -> lui ve chi so 0, khong crash."""
    with torch.no_grad():
        logits = model(lam_batch(["KHIA_CANH_LA"]))
    assert logits.shape == (1, 3)
    assert torch.isfinite(logits).all()


# --- Diem mau chot 2: KHONG ro ri --------------------------------------------


def test_tu_vung_chi_xay_tu_TRAIN(cfg, tmp_path):
    """Doc dev/test de xay tu vung se la ro ri: mo hinh 'biet truoc' nhung tu
    chi xuat hien o tap kiem tra. Kiem bang cach them mot tu la vao dev roi
    xac nhan no KHONG duoc cap o rieng."""
    d = tmp_path
    viet_jsonl(d / "train.jsonl", [lam_record("t1", ["pin", "trâu"], "BATTERY", 2)])
    viet_jsonl(d / "dev.jsonl", [lam_record("d1", ["xyzqwerty"], "BATTERY", 0, "dev")])

    cfg_2 = {
        "data": {"train_path": str(d / "train.jsonl"), "dev_path": str(d / "dev.jsonl")},
        "model": {"emb_dim": 8, "aspect_dim": 4, "lstm_hidden": 8, "dropout": 0.0},
    }
    m = BiLSTMModel(cfg_2)

    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    ids_la = tok(["xyzqwerty"], is_split_into_words=True)["input_ids"]
    ids_train = set(tok(["pin", "trâu"], is_split_into_words=True)["input_ids"])

    for i in ids_la:
        if i not in ids_train:
            assert m.id_map[i].item() == UNK_ID, f"subword chi co o dev ma duoc cap o rieng: {i}"


def test_pad_anh_xa_ve_o_pad(model):
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    assert model.id_map[tok.pad_token_id].item() == PAD_ID


def test_bang_nhung_gon_hon_han_tu_vung_day_du(model):
    """64.000 o cua PhoBERT nhung chi ~14% xuat hien trong train. Bang nhung
    phai gon lai, neu khong thi 85,7% tham so khong bao gio duoc huan luyen."""
    assert model.emb.num_embeddings < 64000
    assert model.id_map.shape[0] == 64000, "bang tra van phai phu het khong gian id goc"


# --- Attention ----------------------------------------------------------------


def test_token_bi_pad_khong_duoc_chu_y(model):
    """Vi tri pad phai bi loai khoi attention, neu khong mo hinh se hoc tu rac."""
    model.eval()
    batch = lam_batch(["BATTERY"], seq_len=8)
    batch["attention_mask"][0, 5:] = 0  # 3 vi tri cuoi la pad

    with torch.no_grad():
        a = model(batch)
        batch["input_ids"][0, 5:] = torch.randint(0, 60000, (3,))  # doi noi dung pad
        b = model(batch)

    assert torch.allclose(a, b, atol=1e-5), "doi noi dung o vi tri pad ma ket qua doi"


def test_gradient_chay_duoc(model):
    """Kiem mo hinh hoc duoc that — gradient toi duoc bang nhung."""
    batch = lam_batch(["BATTERY", "SCREEN"])
    loss = torch.nn.functional.cross_entropy(model(batch), batch["labels"])
    loss.backward()

    assert model.emb.weight.grad is not None
    assert model.aspect_emb.weight.grad is not None
    assert model.emb.weight.grad.abs().sum() > 0


# --- Dang ky ------------------------------------------------------------------


def test_dang_ky_trong_model_registry():
    from nsmgat.train import MODEL_REGISTRY

    assert MODEL_REGISTRY["bilstm"] is BiLSTMModel


# --- Canh cong cu thu tay khong lech khoi mo hinh -----------------------------


def test_duong_code_cua_cong_cu_cho_KET_QUA_Y_HET_forward(model):
    """scripts/try_bilstm.py di duong ma_hoa() -> _chu_y() -> classifier de lay
    duoc trong so attention (forward() vut no di). Test nay canh hai duong do
    khong bao gio lech nhau: neu ai sua forward() ma quen, cong cu se im lang
    bao so sai vao bao cao — dung mau hong lap lai da ghi trong INDEX.md.
    """
    model.eval()
    batch = lam_batch(["BATTERY", "SCREEN"], seq_len=7)

    with torch.no_grad():
        qua_forward = model(batch)

        h, a_lap, mask = model.ma_hoa(batch)
        trong_so = model._chu_y(h, a_lap, mask)
        gop = torch.bmm(trong_so.unsqueeze(1), h).squeeze(1)
        qua_cong_cu = model.classifier(gop)

    assert torch.allclose(qua_forward, qua_cong_cu, atol=1e-6)


def test_trong_so_chu_y_cong_lai_bang_1(model):
    """Bang attention in ra chi doc duoc neu tong bang 1 — nguoi doc hieu
    'token nay chiem 91,5% su chu y'."""
    model.eval()
    batch = lam_batch(["BATTERY"], seq_len=9)
    batch["attention_mask"][0, 6:] = 0

    with torch.no_grad():
        h, a_lap, mask = model.ma_hoa(batch)
        trong_so = model._chu_y(h, a_lap, mask)

    assert torch.allclose(trong_so.sum(dim=-1), torch.ones(1), atol=1e-5)
    assert trong_so[0, 6:].sum() < 1e-6, "vi tri pad van an trong so"
