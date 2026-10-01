"""[CD1.6a] Test ASGCNModel + hai file config.

Nhom quan trong nhat la nhom 1: `asgcn_linked.yaml` phai khac `asgcn.yaml`
DUNG MOT khoa `link_roots`. Lech thêm bất kỳ siêu tham số nào thì hiệu số của
GAP-007 mất ý nghĩa, mà lệch kiểu đó không làm gì sập cả — nên phải có chuông.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nsmgat.data.dataset import ACSADataset, collate_fn  # noqa: E402
from nsmgat.models.asgcn import ASGCNModel  # noqa: E402
from nsmgat.utils.io import load_config  # noqa: E402

DEV_JSONL = REPO_ROOT / "data" / "processed" / "visfd_dev.jsonl"
CONFIGS = REPO_ROOT / "configs"


# --- 1. Hai file config -------------------------------------------------------


def test_asgcn_linked_khac_asgcn_DUNG_MOT_khoa():
    """Chuong bao cho GAP-007: hieu so chi co nghia khi moi thu khac giong het."""
    a = load_config(CONFIGS / "asgcn.yaml")
    b = load_config(CONFIGS / "asgcn_linked.yaml")

    khac = _so_sanh_sau(a, b)
    assert khac == {"model.link_roots": (False, True)}, f"hai config lech o: {khac}"


def test_asgcn_dung_chuan_hoa_cua_bai_goc():
    """row_plus1 = chia cho (d_i + 1), cong thuc (3) cua ASGCN. Hoc vien chot 02/10/2026."""
    cfg = load_config(CONFIGS / "asgcn.yaml")
    assert cfg["model"]["normalize"] == "row_plus1"
    assert cfg["model"]["gcn_layers"] == 2, "bai goc do duoc 2 lop la tot nhat (muc 5.1)"


def test_asgcn_BAT_pair_mode_giong_phobert():
    """Khia canh phai di vao bang VAN BAN, giong `phobert`. Neu chi vao bang
    mot embedding hoc tu dau thi bo ma hoa mu khia canh, va hieu so
    phobert <-> asgcn lan hai bien thay vi do dung phan cu phap.

    Mo hinh cung doi ve khia canh de lam truy van attention — tat la nem loi."""
    assert load_config(CONFIGS / "asgcn.yaml")["data"]["pair_mode"] is True


def _so_sanh_sau(a: dict, b: dict, tien_to: str = "") -> dict:
    khac = {}
    for key in set(a) | set(b):
        duong = f"{tien_to}{key}"
        va, vb = a.get(key), b.get(key)
        if isinstance(va, dict) and isinstance(vb, dict):
            khac.update(_so_sanh_sau(va, vb, f"{duong}."))
        elif va != vb:
            khac[duong] = (va, vb)
    return khac


# --- 2. Mo hinh ---------------------------------------------------------------


def _encoder_ti_hon():
    """Encoder cung KIEU nhung ti hon — khong tai 540 MB trong so that ve."""
    from transformers import RobertaConfig, RobertaModel

    return RobertaModel(RobertaConfig(
        vocab_size=64001, hidden_size=32, num_hidden_layers=1,
        num_attention_heads=2, intermediate_size=64, max_position_embeddings=258,
    ))


@pytest.fixture(scope="module")
def du_lieu_dev():
    if not DEV_JSONL.exists():
        pytest.skip("chua co data/processed (chay scripts/prepare_data.py)")
    return DEV_JSONL


@pytest.fixture(scope="module")
def batch_4(du_lieu_dev):
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    ds = ACSADataset(du_lieu_dev, tokenizer, 128, pair_mode=True)
    return collate_fn([ds[i] for i in range(4)])


def _cfg(du_lieu_dev, **ghi_de) -> dict:
    cfg = {
        "data": {"dev_path": str(du_lieu_dev)},
        "model": {"dropout": 0.1, "gcn_layers": 2, "normalize": "row_plus1"},
    }
    cfg["model"].update(ghi_de)
    return cfg


@pytest.fixture(scope="module")
def model(du_lieu_dev):
    return ASGCNModel(_cfg(du_lieu_dev), encoder=_encoder_ti_hon())


def test_forward_ra_dung_shape(model, batch_4):
    logits = model(batch_4)
    assert logits.shape == (4, 3)
    assert torch.isfinite(logits).all()


def test_encoder_dung_ten_thuoc_tinh_ma_trainer_tim(model):
    """Doi ten thuoc tinh la mat co che hai learning rate, trong im lang."""
    from nsmgat.trainer import _build_optimizer

    assert hasattr(model, "encoder")
    opt = _build_optimizer(model, {"train": {"lr": 1e-3, "encoder_lr": 2e-5, "weight_decay": 0.01}})
    assert len(opt.param_groups) == 2


def test_gradient_chay_qua_ca_gcn_va_encoder(model, batch_4):
    model.zero_grad()
    model(batch_4).sum().backward()

    assert model.gcn[0].linear.weight.grad is not None, "GCN khong nhan gradient"
    assert any(p.grad is not None for p in model.encoder.parameters()), "encoder bi cat khoi do thi"


def test_KHONG_co_embedding_khia_canh_rieng(model):
    """Truy van lay tu bieu dien that cua ve khia canh. Them lai mot
    nn.Embedding rieng la quay ve thiet ke da bo (xem docstring muc 3)."""
    assert not hasattr(model, "aspect_emb")


def test_doi_khia_canh_thi_doi_du_doan(model, du_lieu_dev):
    """Test hanh vi: CUNG mot cau, hoi hai khia canh khac nhau phai cho logits
    khac nhau. Day la cach bat loi "mo hinh mu khia canh" ma khong phai doc code.
    """
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    ds = ACSADataset(du_lieu_dev, tokenizer, 128, pair_mode=True)

    # Tim hai Example cung mot cau nhung khac khia canh
    theo_cau = {}
    for i in range(len(ds)):
        r = ds.records[i]
        theo_cau.setdefault(r["text"], []).append(i)
        if len(theo_cau[r["text"]]) == 2:
            i1, i2 = theo_cau[r["text"]]
            break
    else:
        pytest.skip("khong tim duoc cau nao co 2 khia canh")

    a = model(collate_fn([ds[i1]]))
    b = model(collate_fn([ds[i2]]))
    assert not torch.allclose(a, b), "doi khia canh ma du doan khong doi — mo hinh mu khia canh"


def test_cau_bi_cat_van_tim_thay_ve_khia_canh(model, du_lieu_dev):
    """Lỗi làm sập seed 42 trên Colab 01/10/2026.

    Bản đầu nhận diện vế khía cạnh bằng `word_id >= n_tokens`. Khi câu dài hơn
    `max_seq_len`, tokenizer cắt bớt VẾ CÂU (truncation="only_first") nên vế
    khía cạnh mang chỉ số nhỏ hơn `n_tokens` thật → model tưởng không có vế
    khía cạnh và ném lỗi giữa lúc huấn luyện.

    max_seq_len=16 ép mọi câu đều bị cắt.
    """
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    ds = ACSADataset(du_lieu_dev, tokenizer, 16, pair_mode=True)
    batch = collate_fn([ds[i] for i in range(8)])

    # Có câu thật sự bị cắt thì test mới có ý nghĩa
    assert any(n > 8 for n in batch["n_tokens"].tolist()), "chon mau khac, chua cat duoc"

    logits = model(batch)  # khong duoc nem ValueError
    assert logits.shape == (8, 3)
    assert torch.isfinite(logits).all()


def test_ve_khia_canh_khong_lan_vao_token_khi_cau_bi_cat(model, du_lieu_dev):
    """Mặt còn lại của cùng lỗi: cắt câu rồi thì `word_id >= n_tokens` cũng
    không chặn được vế khía cạnh khỏi ô token của câu."""
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    ds = ACSADataset(du_lieu_dev, tokenizer, 16, pair_mode=True)
    batch = collate_fn([ds[i] for i in range(8)])

    h = model.encoder(input_ids=batch["input_ids"],
                      attention_mask=batch["attention_mask"]).last_hidden_state
    so_token = int(batch["n_tokens"].max())
    _, mask = model._gop_subword(h, batch, so_token)

    for b, ws in enumerate(batch["word_ids"]):
        doan = model._cac_ve(ws, h.shape[1])
        so_tu_ve_cau = len({ws[l] for l in range(*(doan[0][0], doan[0][1] + 1))})
        assert mask[b].sum().item() == so_tu_ve_cau, (
            f"mau {b}: so token co mask phai bang so tu CUA VE CAU con lai sau khi cat"
        )


def test_tat_pair_mode_thi_nem_loi_RO_RANG(model, du_lieu_dev):
    """Khong co ve khia canh thi khong co truy van. Phai bao ro, khong duoc
    chay tiep bang mot vector rac."""
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    ds = ACSADataset(du_lieu_dev, tokenizer, 128, pair_mode=False)
    with pytest.raises(ValueError, match="pair_mode"):
        model(collate_fn([ds[0], ds[1]]))


def test_uid_la_thi_nem_loi_ro_rang(model, batch_4):
    batch = dict(batch_4)
    batch["uid"] = ["uid-khong-he-ton-tai"] + list(batch_4["uid"][1:])
    with pytest.raises(KeyError, match="chi muc do thi"):
        model(batch)


# --- 3. Ba buoc ben trong -----------------------------------------------------


def test_gop_subword_lay_trung_binh(model, batch_4):
    """Mot token tieng Viet co the bi tach thanh nhieu subword; gop phai la
    trung binh cua dung nhung subword cua no."""
    h = torch.arange(2 * 6 * 4, dtype=torch.float).reshape(2, 6, 4)
    batch = {
        # token 0 co 2 subword (vi tri 1, 2), token 1 co 1 subword (vi tri 3)
        "word_ids": [[None, 0, 0, 1, None, None], [None, 0, 1, 1, 1, None]],
        "n_tokens": torch.tensor([2, 2]),
    }
    token, mask = model._gop_subword(h, batch, 2)

    assert torch.allclose(token[0, 0], (h[0, 1] + h[0, 2]) / 2)
    assert torch.allclose(token[0, 1], h[0, 3])
    assert torch.allclose(token[1, 1], (h[1, 2] + h[1, 3] + h[1, 4]) / 3)
    assert torch.equal(mask, torch.ones(2, 2))


def test_token_bi_cat_mat_thi_mask_bang_0(model):
    """Cau dai hon max_seq_len: token khong con subword nao -> mask 0, khong
    phai vector rac."""
    h = torch.randn(1, 4, 4)
    batch = {"word_ids": [[None, 0, 1, None]], "n_tokens": torch.tensor([3])}
    token, mask = model._gop_subword(h, batch, 3)

    assert torch.equal(mask, torch.tensor([[1.0, 1.0, 0.0]]))
    assert torch.equal(token[0, 2], torch.zeros(4))


def test_ve_khia_canh_KHONG_lot_vao_o_token_cua_cau(model):
    """Lỗi đo được 02/10/2026: chặn theo độ dài lớn nhất trong batch thì khi
    `pair_mode` bật, subword của vế khía cạnh (word_id = n, n+1, ...) lọt vào ô
    token của câu ngắn — câu 22 token thành 25 token có mask.

    Mô phỏng đúng tình huống đó: mẫu 0 có 2 token thật và 2 subword khía cạnh
    mang word_id 2, 3; mẫu 1 dài 4 token nên `so_token` = 4.
    """
    h = torch.randn(2, 7, 4)
    batch = {
        "word_ids": [
            [None, 0, 1, None, None, 2, 3],  # 2 token that + ve khia canh (2, 3)
            [None, 0, 1, 2, 3, None, None],  # 4 token that
        ],
        "n_tokens": torch.tensor([2, 4]),
    }
    _, mask = model._gop_subword(h, batch, 4)

    assert mask.sum(dim=-1).tolist() == [2.0, 4.0], (
        "so token co mask phai bang dung n_tokens, khong duoc tinh ca ve khia canh"
    )


def test_trong_so_chu_y_tong_bang_1_va_bang_0_o_token_dem(model, batch_4):
    g = torch.randn(4, int(batch_4["n_tokens"].max()), 32)
    q = torch.randn(4, 32)
    mask = torch.zeros_like(g[:, :, 0])
    for i, n in enumerate(batch_4["n_tokens"].tolist()):
        mask[i, :n] = 1.0

    trong_so = model._chu_y(g, q, mask)

    assert torch.allclose(trong_so.sum(dim=-1), torch.ones(4), atol=1e-5)
    assert torch.allclose(trong_so[mask <= 0], torch.zeros(1), atol=1e-6)


def test_link_roots_doi_do_thi_cua_cau_bi_chia_cat(du_lieu_dev):
    """Hai mo hinh chi khac `link_roots` phai cho ma tran ke khac nhau o it
    nhat mot cau — neu giong het thi hoac du lieu khong co cau bi chia cat,
    hoac co che noi goc khong hoat dong."""
    roi = ASGCNModel(_cfg(du_lieu_dev, link_roots=False), encoder=_encoder_ti_hon())
    noi = ASGCNModel(_cfg(du_lieu_dev, link_roots=True), encoder=_encoder_ti_hon())

    them = 0
    for khoa, cap in roi.khoa_to_canh.items():
        them += noi.khoa_to_canh[khoa].shape[0] - cap.shape[0]
    assert them > 0, "noi goc khong them canh nao — kiem tra lai SyntacticGraphBuilder"


def test_chi_muc_do_thi_gop_theo_CAU_chu_khong_theo_Example(model):
    """23.872 Example chi ung voi 7.671 cau; gop theo Example la ton bo nho vo ich."""
    assert len(model.khoa_to_canh) < len(model.uid_to_khoa)
