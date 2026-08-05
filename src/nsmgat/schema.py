"""Hop dong du lieu bat bien cua du an nsmgat.

CHOT O S0.2 - KHONG SUA SAU BUOC NAY. Moi module ve sau (data/, graphs/,
rules/, models/) phu thuoc truc tiep vao 3 dataclass duoi day. Neu thay
can doi ten field, kieu du lieu, hay chu ky ham: DUNG LAI, day gan nhu
luon la dau hieu dang lam sai step chu khong phai hop dong thiet ke toi.
Xem README.md muc "QUY TAC BAT BUOC" va pLan/PLAN_NSMGAT.md muc 1.2.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

LABEL_NAMES = ["negative", "neutral", "positive"]
VIEWS = ["syn", "aff", "logic"]


@dataclass
class Example:
    """Mot cap (cau, khia canh) - don vi phan loai cua ACSA."""

    uid: str  # "visfd-train-00042-BATTERY"
    text: str  # cau goc
    tokens: List[str]  # da tach tu VnCoreNLP, dung "_" noi am tiet
    pos: List[str]  # nhan tu loai, cung do dai tokens
    heads: List[int]  # chi so head trong cay phu thuoc, -1 = root
    deprels: List[str]  # nhan quan he phu thuoc
    aspect: str  # "BATTERY" | "CAMERA" | ...
    label: int  # 0=negative, 1=neutral, 2=positive
    domain: str  # "visfd" | "vlsp-hotel" | "vlsp-restaurant"
    split: str  # "train" | "dev" | "test"

    def __post_init__(self) -> None:
        if not (len(self.tokens) == len(self.pos) == len(self.heads) == len(self.deprels)):
            raise ValueError(
                "tokens/pos/heads/deprels phai cung do dai, nhan duoc "
                f"{len(self.tokens)}/{len(self.pos)}/{len(self.heads)}/{len(self.deprels)}"
            )
        if self.label not in (0, 1, 2):
            raise ValueError(f"label phai thuoc {{0,1,2}}, nhan duoc {self.label!r}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "text": self.text,
            "tokens": self.tokens,
            "pos": self.pos,
            "heads": self.heads,
            "deprels": self.deprels,
            "aspect": self.aspect,
            "label": self.label,
            "domain": self.domain,
            "split": self.split,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Example":
        return cls(
            uid=d["uid"],
            text=d["text"],
            tokens=list(d["tokens"]),
            pos=list(d["pos"]),
            heads=list(d["heads"]),
            deprels=list(d["deprels"]),
            aspect=d["aspect"],
            label=d["label"],
            domain=d["domain"],
            split=d["split"],
        )


@dataclass
class TypedEdge:
    """Canh co thuoc tinh - trai tim cua co che neuro-symbolic."""

    src: int  # chi so token nguon
    dst: int  # chi so token dich
    view: str  # "syn" | "aff" | "logic"
    etype: str  # "DEP:nsubj" | "AFF:sim" | "LOGIC:NEGATION" | ...
    conf: float  # [0,1]; syn/aff mac dinh 1.0; logic lay tu calibration
    rule_id: Optional[str]  # "NEG-005" - de truy vet khi giai thich

    def __post_init__(self) -> None:
        if not (0.0 <= self.conf <= 1.0):
            raise ValueError(f"conf phai thuoc [0,1], nhan duoc {self.conf!r}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "src": self.src,
            "dst": self.dst,
            "view": self.view,
            "etype": self.etype,
            "conf": self.conf,
            "rule_id": self.rule_id,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TypedEdge":
        return cls(
            src=d["src"],
            dst=d["dst"],
            view=d["view"],
            etype=d["etype"],
            conf=d["conf"],
            rule_id=d.get("rule_id"),
        )


@dataclass
class GraphSample:
    """Mot Example da dung du 3 do thi. Day la thu Dataset tra ve."""

    uid: str
    tokens: List[str]
    aspect: str
    label: int
    n_tokens: int
    edges: List[TypedEdge]  # gop ca 3 view, phan biet bang field `view`

    def __post_init__(self) -> None:
        if self.label not in (0, 1, 2):
            raise ValueError(f"label phai thuoc {{0,1,2}}, nhan duoc {self.label!r}")
        for edge in self.edges:
            if not (0 <= edge.src < self.n_tokens) or not (0 <= edge.dst < self.n_tokens):
                raise ValueError(
                    f"edge ({edge.src}->{edge.dst}) vuot qua n_tokens={self.n_tokens}"
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "tokens": self.tokens,
            "aspect": self.aspect,
            "label": self.label,
            "n_tokens": self.n_tokens,
            "edges": [edge.to_dict() for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GraphSample":
        return cls(
            uid=d["uid"],
            tokens=list(d["tokens"]),
            aspect=d["aspect"],
            label=d["label"],
            n_tokens=d["n_tokens"],
            edges=[TypedEdge.from_dict(e) for e in d["edges"]],
        )
