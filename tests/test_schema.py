"""Test schema.py: khoi tao dataclass hop le va bat loi field sai."""

import pytest

from nsmgat.schema import LABEL_NAMES, VIEWS, Example, GraphSample, TypedEdge


def make_example(**overrides):
    base = dict(
        uid="visfd-train-00001-BATTERY",
        text="Pin rat tot",
        tokens=["Pin", "rat", "tot"],
        pos=["N", "R", "A"],
        heads=[2, 2, -1],
        deprels=["nsubj", "advmod", "root"],
        aspect="BATTERY",
        label=2,
        domain="visfd",
        split="train",
    )
    base.update(overrides)
    return Example(**base)


def make_edge(**overrides):
    base = dict(src=0, dst=1, view="syn", etype="DEP:nsubj", conf=1.0, rule_id=None)
    base.update(overrides)
    return TypedEdge(**base)


def test_example_valid():
    ex = make_example()
    assert ex.label == 2
    assert len(ex.tokens) == 3


def test_example_len_mismatch_raises():
    with pytest.raises(ValueError):
        make_example(pos=["N", "R"])


def test_example_bad_label_raises():
    with pytest.raises(ValueError):
        make_example(label=5)


def test_example_roundtrip_dict():
    ex = make_example()
    assert Example.from_dict(ex.to_dict()) == ex


def test_typed_edge_valid():
    edge = make_edge()
    assert edge.view == "syn"


def test_typed_edge_bad_conf_raises():
    with pytest.raises(ValueError):
        make_edge(conf=1.5)


def test_graph_sample_valid():
    sample = GraphSample(
        uid="visfd-train-00001-BATTERY",
        tokens=["Pin", "rat", "tot"],
        aspect="BATTERY",
        label=2,
        n_tokens=3,
        edges=[make_edge(src=0, dst=1)],
    )
    assert sample.n_tokens == 3


def test_graph_sample_bad_label_raises():
    with pytest.raises(ValueError):
        GraphSample(
            uid="x", tokens=["a"], aspect="X", label=5, n_tokens=1, edges=[]
        )


def test_graph_sample_edge_out_of_range_raises():
    with pytest.raises(ValueError):
        GraphSample(
            uid="x",
            tokens=["a"],
            aspect="X",
            label=0,
            n_tokens=1,
            edges=[make_edge(src=0, dst=5)],
        )


def test_graph_sample_roundtrip_dict():
    sample = GraphSample(
        uid="u", tokens=["a", "b"], aspect="X", label=1, n_tokens=2,
        edges=[make_edge(src=0, dst=1)],
    )
    assert GraphSample.from_dict(sample.to_dict()) == sample


def test_constants():
    assert LABEL_NAMES == ["negative", "neutral", "positive"]
    assert VIEWS == ["syn", "aff", "logic"]
