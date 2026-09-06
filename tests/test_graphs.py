"""[S3.1 / CD1.3] Test do thi cu phap tren cau mau co cay phu thuoc biet truoc.

Dac ta: pLan/PLAN_NSMGAT.md muc S3.1.
Cai dat:  src/nsmgat/graphs/syntactic.py
"""

from __future__ import annotations

import pytest

from nsmgat.graphs.syntactic import ETYPE_SELF, VIEW, SyntacticGraphBuilder
from nsmgat.schema import Example, GraphSample

# Cau mau, cay phu thuoc dung bang tay (chi so 0-based, -1 = root):
#
#   0 pin    <- 2 (nsubj)
#   1 rat    <- 2 (adv)
#   2 trau   root
#
#         trau(2)
#         /     \
#     pin(0)   rat(1)
CAU_MAU = Example(
    uid="test-0001-BATTERY",
    text="pin rất trâu",
    tokens=["pin", "rất", "trâu"],
    pos=["N", "R", "A"],
    heads=[2, 2, -1],
    deprels=["nsubj", "adv", "root"],
    aspect="BATTERY",
    label=2,
    domain="visfd",
    split="train",
)


@pytest.fixture
def builder() -> SyntacticGraphBuilder:
    return SyntacticGraphBuilder()


def make_example(tokens, heads, deprels, **kwargs) -> Example:
    n = len(tokens)
    return Example(
        uid=kwargs.get("uid", "test-x"),
        text=" ".join(tokens),
        tokens=list(tokens),
        pos=kwargs.get("pos", ["X"] * n),
        heads=list(heads),
        deprels=list(deprels),
        aspect=kwargs.get("aspect", "BATTERY"),
        label=kwargs.get("label", 1),
        domain="visfd",
        split="train",
    )


# --- Hop dong co ban ----------------------------------------------------------


def test_view_name_dung_hop_dong(builder):
    assert builder.view_name == VIEW == "syn"


def test_so_canh_dung_cong_thuc(builder):
    """n token, r root hop le => 2*(n-r) canh huong + n self-loop.

    Cau mau: n=3, 1 root => 2*2 + 3 = 7 canh.
    """
    edges = builder.build(CAU_MAU)
    assert len(edges) == 7


def test_moi_token_co_dung_mot_self_loop(builder):
    edges = builder.build(CAU_MAU)
    self_loops = [e for e in edges if e.etype == ETYPE_SELF]

    assert len(self_loops) == len(CAU_MAU.tokens)
    assert sorted(e.src for e in self_loops) == [0, 1, 2]
    assert all(e.src == e.dst for e in self_loops)


def test_tinh_doi_xung_moi_canh_deu_co_chieu_nguoc(builder):
    """Voi moi canh (h -> i) DEP:x phai co dung mot canh (i -> h) DEP:x_rev."""
    edges = builder.build(CAU_MAU)
    xuoi = {(e.src, e.dst, e.etype) for e in edges if not e.etype.endswith("_rev") and e.etype != ETYPE_SELF}
    nguoc = {(e.src, e.dst, e.etype) for e in edges if e.etype.endswith("_rev")}

    assert len(xuoi) == len(nguoc) == 2
    for src, dst, etype in xuoi:
        assert (dst, src, f"{etype}_rev") in nguoc


def test_canh_dung_deprel_va_dung_huong(builder):
    edges = builder.build(CAU_MAU)
    huong = {(e.src, e.dst): e.etype for e in edges}

    # head 2 -> dependent 0, quan he nsubj
    assert huong[(2, 0)] == "DEP:nsubj"
    assert huong[(0, 2)] == "DEP:nsubj_rev"
    assert huong[(2, 1)] == "DEP:adv"
    assert huong[(1, 2)] == "DEP:adv_rev"


def test_root_khong_sinh_canh_di_len(builder):
    """Token root (head = -1) chi co self-loop, khong co canh toi head."""
    edges = builder.build(CAU_MAU)
    canh_tu_root = [e for e in edges if e.src == 2 and e.dst != 2 and not e.etype.endswith("_rev")]

    # root chi la NGUON cua canh xuong con, khong bao gio la DICH cua canh di len
    assert all(e.etype != "DEP:root" for e in edges)
    assert len(canh_tu_root) == 2  # xuong 2 con


def test_moi_canh_co_conf_1_va_khong_co_rule_id(builder):
    """Cu phap khong co bat dinh — khac hoan toan view 'logic' o CD2."""
    edges = builder.build(CAU_MAU)

    assert all(e.conf == 1.0 for e in edges)
    assert all(e.rule_id is None for e in edges)
    assert all(e.view == "syn" for e in edges)


# --- Cac ca bien ma dac ta S3.1 yeu cau xu ly duoc ----------------------------


def test_cau_mot_token(builder):
    ex = make_example(["ok"], [-1], ["root"])
    edges = builder.build(ex)

    assert len(edges) == 1
    assert edges[0].etype == ETYPE_SELF
    assert edges[0].src == edges[0].dst == 0


def test_head_tro_ngoai_pham_vi_thi_bo_qua_khong_sap(builder):
    """Du lieu hong khong duoc lam sap pipeline — bo qua canh do."""
    ex = make_example(["a", "b"], [99, -1], ["dep", "root"])
    edges = builder.build(ex)

    assert len(edges) == 2  # chi con 2 self-loop
    assert all(e.etype == ETYPE_SELF for e in edges)


def test_head_am_khac_minus_1_cung_bi_bo_qua(builder):
    ex = make_example(["a", "b"], [-5, -1], ["dep", "root"])
    edges = builder.build(ex)
    assert all(e.etype == ETYPE_SELF for e in edges)


def test_token_tu_tro_vao_minh_khong_tao_self_loop_trung(builder):
    """head == dep se tao self-loop trung voi self-loop rieng => phai bo qua."""
    ex = make_example(["a", "b"], [0, -1], ["dep", "root"])
    edges = builder.build(ex)

    self_loops = [e for e in edges if e.src == e.dst]
    assert len(self_loops) == 2, "moi token dung mot self-loop, khong duoc nhan doi"


def test_cau_khong_co_token(builder):
    ex = make_example([], [], [])
    assert builder.build(ex) == []


def test_rung_nhieu_root_van_dung(builder):
    """52,2% du lieu that co dang rung (binh luan nhieu cau). Phai xu ly duoc.

    n=4, 2 root => 2*(4-2) + 4 = 8 canh.
    """
    ex = make_example(["a", "b", "c", "d"], [1, -1, 3, -1], ["dep", "root", "dep", "root"])
    edges = builder.build(ex)

    assert len(edges) == 8
    # hai thanh phan roi nhau, khong co canh noi giua chung
    assert not any({e.src, e.dst} & {0, 1} and {e.src, e.dst} & {2, 3} for e in edges)


# --- Tich hop voi hop dong GraphSample ----------------------------------------


def test_canh_sinh_ra_hop_le_voi_graphsample(builder):
    """GraphSample.__post_init__ tu kiem canh nam trong [0, n_tokens)."""
    edges = builder.build(CAU_MAU)

    sample = GraphSample(
        uid=CAU_MAU.uid,
        tokens=CAU_MAU.tokens,
        aspect=CAU_MAU.aspect,
        label=CAU_MAU.label,
        n_tokens=len(CAU_MAU.tokens),
        edges=edges,
    )
    assert len(sample.edges) == 7


def test_build_batch_giu_dung_thu_tu(builder):
    ex2 = make_example(["x"], [-1], ["root"])
    ket_qua = builder.build_batch([CAU_MAU, ex2])

    assert len(ket_qua) == 2
    assert len(ket_qua[0]) == 7
    assert len(ket_qua[1]) == 1


# --- Chay tren du lieu that ---------------------------------------------------


def test_chay_duoc_tren_du_lieu_that(builder):
    """Kiem tren vai Example that tu data/processed — bat loi quy uoc chi so."""
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "processed" / "visfd_train.jsonl"
    if not path.exists():
        pytest.skip("chua co data/processed — chay scripts/prepare_data.py truoc")

    with path.open(encoding="utf-8") as fh:
        examples = [Example.from_dict(json.loads(next(fh))) for _ in range(50)]

    for ex in examples:
        edges = builder.build(ex)
        n = len(ex.tokens)
        assert all(0 <= e.src < n and 0 <= e.dst < n for e in edges), f"{ex.uid}: canh ngoai pham vi"
        assert sum(1 for e in edges if e.etype == ETYPE_SELF) == n


# --- Chan doan chat luong do thi (scripts/diagnose_syntactic_graph.py) --------
#
# count_components la chi so quan trong nhat cua CD1.3: no do ti le Example co
# do thi bi chia cat. Neu ham nay sai thi ca ket luan ve chat luong cay phu
# thuoc deu sai theo, nen phai kiem ky.

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "scripts"))

from diagnose_syntactic_graph import count_components  # noqa: E402


@pytest.mark.parametrize(
    "heads, mong_doi, mo_ta",
    [
        ([-1], 1, "mot token la root"),
        ([2, 2, -1], 1, "cay lien thong day du"),
        ([1, -1, 3, -1], 2, "rung hai cay roi nhau"),
        ([-1, -1, -1], 3, "ba token roi rac, khong canh nao"),
        ([], 0, "cau rong"),
        ([99, -1], 2, "head ngoai pham vi khong duoc noi hai token"),
        ([0, -1], 2, "token tu tro vao minh khong tao lien ket"),
    ],
)
def test_dem_thanh_phan_lien_thong(heads, mong_doi, mo_ta):
    assert count_components(heads) == mong_doi, mo_ta


def test_thanh_phan_lien_thong_khop_so_root_khi_cay_hop_le():
    """Voi cay phu thuoc hop le, so thanh phan = so root. Day la ly do bang
    'root trung binh' va 'thanh phan trung binh' trong ket qua chan doan bang
    nhau (2,37) — khong phai trung hop."""
    heads = [1, -1, 3, -1, 5, -1]
    assert count_components(heads) == sum(1 for h in heads if h == -1) == 3


# --- GAP-007 phuong an C: bien the link_roots --------------------------------
#
# `asgcn` (link_roots=False) va `asgcn_linked` (link_roots=True) khac nhau DUNG
# MOT BIEN. Hieu so ket qua giua chung do truc tiep tac dong cua viec do thi bi
# chia cat. Cac test duoi day canh dung mot bien do that su la mot bien duy nhat.

from nsmgat.graphs.syntactic import ETYPE_ROOT_LINK  # noqa: E402


@pytest.fixture
def builder_linked() -> SyntacticGraphBuilder:
    return SyntacticGraphBuilder(link_roots=True)


def test_mac_dinh_la_khong_noi_root(builder):
    """Mac dinh PHAI la False — `asgcn` khong duoc doi hanh vi vi tham so moi."""
    assert builder.link_roots is False
    edges = builder.build(CAU_MAU)
    assert not any(e.etype.startswith(ETYPE_ROOT_LINK) for e in edges)


def test_cay_mot_root_thi_hai_bien_the_giong_het_nhau(builder, builder_linked):
    """Cau chi co 1 root thi khong co gi de noi -> hai bien the phai trung khop.

    Quan trong: no cho biet hieu so ket qua giua asgcn va asgcn_linked CHI den
    tu nhung cau nhieu root, dung nhu thiet ke thi nghiem.
    """
    a = [(e.src, e.dst, e.etype) for e in builder.build(CAU_MAU)]
    b = [(e.src, e.dst, e.etype) for e in builder_linked.build(CAU_MAU)]
    assert a == b


def test_rung_hai_root_duoc_noi_lai(builder_linked):
    """n=4, 2 root => 2*(4-2) canh cu phap + 4 self-loop + 2 canh noi root = 10."""
    ex = make_example(["a", "b", "c", "d"], [1, -1, 3, -1], ["dep", "root", "dep", "root"])
    edges = builder_linked.build(ex)

    assert len(edges) == 10
    noi = [e for e in edges if e.etype.startswith(ETYPE_ROOT_LINK)]
    assert len(noi) == 2
    assert {(e.src, e.dst) for e in noi} == {(1, 3), (3, 1)}, "phai noi hai chieu giua 2 root"


def test_noi_root_lam_do_thi_lien_thong(builder, builder_linked):
    """Cot loi cua phuong an C: bien the linked phai xoa duoc su chia cat."""
    ex = make_example(["a", "b", "c", "d"], [1, -1, 3, -1], ["dep", "root", "dep", "root"])

    def lien_thong(edges, n):
        par = list(range(n))
        def f(x):
            while par[x] != x:
                par[x] = par[par[x]]; x = par[x]
            return x
        for e in edges:
            a, b = f(e.src), f(e.dst)
            if a != b:
                par[a] = b
        return len({f(i) for i in range(n)})

    assert lien_thong(builder.build(ex), 4) == 2, "giu nguyen: 2 manh roi nhau"
    assert lien_thong(builder_linked.build(ex), 4) == 1, "noi root: lien thong"


def test_noi_theo_CHUOI_khong_phai_hinh_sao(builder_linked):
    """3 root -> noi 1-2 va 2-3, KHONG noi 1-3.

    Chuoi giu duoc trat tu tuyen tinh cua dien ngon: hai cau lien ke lien quan
    nhau hon hai cau cach xa. Hinh sao se lam moi cau cach root dau dung 1 buoc.
    """
    ex = make_example(list("abcdef"), [-1, 0, -1, 2, -1, 4], ["root", "d", "root", "d", "root", "d"])
    noi = {(e.src, e.dst) for e in builder_linked.build(ex) if e.etype.startswith(ETYPE_ROOT_LINK)}

    assert noi == {(0, 2), (2, 0), (2, 4), (4, 2)}
    assert (0, 4) not in noi and (4, 0) not in noi, "khong duoc noi truc tiep root dau va root cuoi"


def test_canh_noi_root_phan_biet_duoc_bang_etype(builder_linked):
    """Canh nhan tao PHAI phan biet duoc voi canh cu phap that.

    Day la khac biet cot loi so voi phuong an D (ep parse): o do canh sai
    nguy trang thanh cu phap that, khong tach ra duoc.
    """
    ex = make_example(["a", "b"], [-1, -1], ["root", "root"])
    edges = builder_linked.build(ex)

    nhan_tao = [e for e in edges if e.etype.startswith(ETYPE_ROOT_LINK)]
    that = [e for e in edges if e.etype.startswith("DEP:") and not e.etype.startswith(ETYPE_ROOT_LINK)]

    assert nhan_tao and all(e.etype in (ETYPE_ROOT_LINK, f"{ETYPE_ROOT_LINK}_rev") for e in nhan_tao)
    assert all(not e.etype.startswith(ETYPE_ROOT_LINK) for e in that)


def test_cong_thuc_so_canh_khi_noi_root(builder_linked):
    """Khi noi root, so canh luon = 3n - 2 BAT KE co bao nhieu root.

    Chung minh: 2*(n-r) canh cu phap + n self-loop + 2*(r-1) canh noi
              = 2n - 2r + n + 2r - 2 = 3n - 2
    """
    for heads, deprels in [
        ([2, 2, -1], ["nsubj", "adv", "root"]),
        ([1, -1, 3, -1], ["dep", "root", "dep", "root"]),
        ([-1, -1, -1], ["root", "root", "root"]),
    ]:
        n = len(heads)
        ex = make_example([f"t{i}" for i in range(n)], heads, deprels)
        assert len(builder_linked.build(ex)) == 3 * n - 2, f"heads={heads}"


def test_khong_noi_gi_khi_cau_rong_hoac_mot_token(builder_linked):
    assert builder_linked.build(make_example([], [], [])) == []
    edges = builder_linked.build(make_example(["x"], [-1], ["root"]))
    assert len(edges) == 1 and edges[0].etype == ETYPE_SELF


def test_bien_the_linked_chay_duoc_tren_du_lieu_that(builder, builder_linked):
    """Tren du lieu that: linked phai luon co >= so canh cua ban giu nguyen,
    va phan chenh lech dung bang 2*(so root - 1)."""
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "processed" / "visfd_train.jsonl"
    if not path.exists():
        pytest.skip("chua co data/processed")

    with path.open(encoding="utf-8") as fh:
        examples = [Example.from_dict(json.loads(next(fh))) for _ in range(50)]

    for ex in examples:
        n_root = sum(1 for h in ex.heads if h == -1)
        chenh = len(builder_linked.build(ex)) - len(builder.build(ex))
        assert chenh == max(0, 2 * (n_root - 1)), ex.uid
