"""[CD1.5] Test baseline PhoBERT (models/phobert.py + pair_mode trong dataset).

Ba nhom, nhom dau quan trong nhat:

1. **pair_mode KHONG duoc bat mac dinh.** `bilstm` doc chinh `input_ids` de
   tra bang embedding cua no. Neu mot ngay nao do ai do doi mac dinh thanh
   True, dau vao cua `bilstm` doi theo va ba seed da chay (acc 0,8642) khong
   con tai lap duoc — ma khong co gi sap ca. Test nay la cai chuong bao.

2. Cap cau dung dang `<s> cau </s></s> khia_canh </s>`, ve khia canh viet
   bang tieng Viet da tach tu, va KHONG BAO GIO bi cat khi cau qua dai.

3. Mo hinh chay duoc, ra dung shape (B, 3). Dung encoder ti hon khoi tao ngau
   nhien — test khong tai 540 MB trong so that ve.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nsmgat.data.dataset import ACSADataset, collate_fn  # noqa: E402
from nsmgat.models.phobert import PhoBERTClassifier  # noqa: E402
from nsmgat.data.aspects import ASPECT_VI, aspect_tokens  # noqa: E402

DEV_JSONL = REPO_ROOT / "data" / "processed" / "visfd_dev.jsonl"


# --- 1. Bang anh xa khia canh -------------------------------------------------


def test_moi_khia_canh_trong_du_lieu_deu_co_ten_tieng_viet():
    """Thieu mot ma la `aspect_tokens` nem loi giua lucchay — bat o day."""
    if not DEV_JSONL.exists():
        pytest.skip("chua co data/processed (chay scripts/prepare_data.py)")
    import json

    trong_du_lieu = {json.loads(d)["aspect"] for d in DEV_JSONL.open(encoding="utf-8") if d.strip()}
    thieu = trong_du_lieu - set(ASPECT_VI)
    assert not thieu, f"khia canh chua co ten tieng Viet: {sorted(thieu)}"


def test_ten_tieng_viet_dung_quy_uoc_tach_tu():
    """PhoBERT doi van ban da tach tu: tu nhieu am tiet phai noi bang '_'.
    Quen gach duoi thi mo hinh VAN CHAY, chi kem di ma khong bao loi."""
    for ma, ten in ASPECT_VI.items():
        for tu in ten.split():
            assert " " not in tu
            if tu not in ("camera", "pin", "giá", "và"):
                assert "_" in tu, f"{ma} -> '{tu}' co ve la tu ghep ma thieu gach duoi"


def test_ma_la_thi_nem_loi_chu_khong_doan():
    with pytest.raises(KeyError, match="KHONG_TON_TAI"):
        aspect_tokens("KHONG_TON_TAI")


# --- 2. pair_mode -------------------------------------------------------------


@pytest.fixture(scope="module")
def tokenizer():
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained("vinai/phobert-base-v2")


@pytest.fixture(scope="module")
def du_lieu_dev():
    if not DEV_JSONL.exists():
        pytest.skip("chua co data/processed (chay scripts/prepare_data.py)")
    return DEV_JSONL


def test_pair_mode_MAC_DINH_TAT(tokenizer, du_lieu_dev):
    """Bat mac dinh la doi dau vao cua bilstm — mo hinh da chay xong 3 seed."""
    ds = ACSADataset(du_lieu_dev, tokenizer, 128)
    assert ds.pair_mode is False

    khong_cap = ds[0]["input_ids"]
    co_cap = ACSADataset(du_lieu_dev, tokenizer, 128, pair_mode=True)[0]["input_ids"]
    assert khong_cap != co_cap, "bat pair_mode phai doi input_ids"
    assert len(co_cap) > len(khong_cap), "them ve khia canh thi phai dai ra"


def test_pair_mode_noi_dung_dang_cap_cau(tokenizer, du_lieu_dev):
    """Dang chuan: <s> cau </s></s> khia_canh </s>"""
    ds = ACSADataset(du_lieu_dev, tokenizer, 128, pair_mode=True)
    item = ds[0]
    pieces = tokenizer.convert_ids_to_tokens(item["input_ids"])
    ten_vi = ASPECT_VI[item["aspect_text"]].split()

    assert pieces[0] == "<s>"
    assert pieces[-len(ten_vi) - 1:] == ten_vi + ["</s>"], f"duoi sai: {pieces[-5:]}"
    assert pieces[-len(ten_vi) - 3:-len(ten_vi) - 1] == ["</s>", "</s>"], (
        f"phai co '</s></s>' ngan giua hai ve, dang la {pieces[-6:]}"
    )


def test_aspect_text_van_la_ma_goc_du_da_dich(tokenizer, du_lieu_dev):
    """Cac mo hinh khac (bilstm) tra `aspect_text` de tra bang rieng cua no —
    dich sang tieng Viet chi de dua vao PhoBERT, khong duoc doi truong nay."""
    ds = ACSADataset(du_lieu_dev, tokenizer, 128, pair_mode=True)
    assert ds[0]["aspect_text"] in ASPECT_VI


def test_cau_dai_thi_cat_ve_cau_chu_khong_cat_ve_khia_canh(tokenizer, du_lieu_dev):
    """max_seq_len nho de ep truncation. Mat ve khia canh la mat cau hoi."""
    ds = ACSADataset(du_lieu_dev, tokenizer, 16, pair_mode=True)
    for i in range(min(len(ds), 50)):
        item = ds[i]
        pieces = tokenizer.convert_ids_to_tokens(item["input_ids"])
        ten_vi = ASPECT_VI[item["aspect_text"]].split()
        assert len(item["input_ids"]) <= 16
        assert pieces[-len(ten_vi) - 1:] == ten_vi + ["</s>"], (
            f"mau {i} bi cat mat ve khia canh: {pieces[-4:]}"
        )


# --- 3. Mo hinh ---------------------------------------------------------------


def _encoder_ti_hon():
    """Encoder cung KIEU nhung ti hon — khong tai 540 MB trong so that."""
    from transformers import RobertaConfig, RobertaModel

    return RobertaModel(RobertaConfig(
        vocab_size=64001, hidden_size=32, num_hidden_layers=1,
        num_attention_heads=2, intermediate_size=64, max_position_embeddings=258,
    ))


def test_forward_ra_dung_shape(tokenizer, du_lieu_dev):
    ds = ACSADataset(du_lieu_dev, tokenizer, 128, pair_mode=True)
    batch = collate_fn([ds[i] for i in range(4)])
    model = PhoBERTClassifier({"model": {"dropout": 0.1}}, encoder=_encoder_ti_hon())

    logits = model(batch)
    assert logits.shape == (4, 3)
    assert torch.isfinite(logits).all()


def test_encoder_dung_ten_thuoc_tinh_ma_trainer_tim():
    """trainer._build_optimizer tach learning rate bang cach tim thuoc tinh
    ten `encoder`. Doi ten la mat luon co che hai learning rate — im lang."""
    from nsmgat.trainer import _build_optimizer

    model = PhoBERTClassifier({"model": {}}, encoder=_encoder_ti_hon())
    assert hasattr(model, "encoder")

    cfg = {"train": {"lr": 1e-3, "encoder_lr": 2e-5, "weight_decay": 0.01}}
    opt = _build_optimizer(model, cfg)
    assert len(opt.param_groups) == 2, "phai co 2 nhom: encoder va dau phan loai"
    assert {g["lr"] for g in opt.param_groups} == {1e-3, 2e-5}


def test_explain_tra_rong():
    model = PhoBERTClassifier({"model": {}}, encoder=_encoder_ti_hon())
    assert model.explain({}) == []


# --- 4. Config ----------------------------------------------------------------


def test_config_phobert_bat_dung_ba_thu_da_chot():
    cfg = yaml.safe_load((REPO_ROOT / "configs" / "phobert.yaml").read_text(encoding="utf-8"))
    assert cfg["data"]["pair_mode"] is True, "phobert phai bat pair_mode"
    assert cfg["train"]["use_amp"] is True, "fp16 la dieu kien de 30-45 phut/seed"
    assert cfg["train"]["encoder_lr"] < cfg["train"]["lr"], (
        "encoder da biet tieng Viet -> lr nho; dau phan loai khoi tao ngau nhien -> lr lon"
    )


def test_cai_dat_rieng_cua_phobert_KHONG_tran_sang_base_yaml():
    """Doi base.yaml la doi config_hash cua MOI ket qua cu — dung loi GAP-014.
    `lexicon` va `bilstm` da chay xong 3 seed moi ben."""
    base = yaml.safe_load((REPO_ROOT / "configs" / "base.yaml").read_text(encoding="utf-8"))
    assert base["train"]["use_amp"] is False
    assert "pair_mode" not in base["data"]
