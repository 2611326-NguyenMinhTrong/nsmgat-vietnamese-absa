"""[S3.1 / CD1.3] SyntacticGraphBuilder (view="syn").

Dung do thi cu phap tu cay phu thuoc VnCoreNLP da co san trong Example
(cac truong heads/deprels, sinh o S0.3).

Quy tac sinh canh — theo dung dac ta S3.1 trong pLan/PLAN_NSMGAT.md:
  - Voi moi token i co head h hop le: sinh CA HAI chieu
        (h -> i) etype "DEP:{deprel}"
        (i -> h) etype "DEP:{deprel}_rev"
  - Them self-loop cho MOI token: etype "DEP:self"
  - conf = 1.0 cho moi canh (cu phap khong co bat dinh — khac view "logic")
  - rule_id = None

Vi sao can ca chieu nguoc: GCN lan truyen theo chieu canh. Neu chi giu
chieu head -> dependent thi thong tin chi chay tu goc xuong la, tu cam xuc
o la khong bao gio toi duoc token khia canh nam cao hon trong cay.

Vi sao can self-loop: de moi token giu lai mot phan bieu dien cua chinh no
sau moi lop GCN, thay vi bi thay hoan toan bang trung binh cac lang gieng.

QUY UOC CHI SO (chot o S0.3): heads dung chi so 0-based, -1 = root.

LUU Y QUAN TRONG — do thi la RUNG, khong phai cay:
  UIT-ViSFD "cau" thuc ra la binh luan nhieu cau. VnCoreNLP tach cau nen
  moi cau con co root rieng => 52,2% Example co do thi bi chia cat thanh
  nhieu thanh phan lien thong. Do la hanh vi DUNG cua parser, khong phai loi.
  Module nay KHONG tu y noi cac thanh phan lai — xem GAP-007 va
  scripts/diagnose_syntactic_graph.py.
"""

from __future__ import annotations

from typing import List

from nsmgat.graphs.base import GraphBuilder
from nsmgat.schema import Example, TypedEdge

VIEW = "syn"
ETYPE_SELF = "DEP:self"
REV_SUFFIX = "_rev"
ROOT_HEAD = -1


class SyntacticGraphBuilder(GraphBuilder):
    """Sinh canh cu phap hai chieu + self-loop tu cay phu thuoc."""

    @property
    def view_name(self) -> str:
        return VIEW

    def build(self, example: Example) -> List[TypedEdge]:
        n = len(example.tokens)
        edges: List[TypedEdge] = []

        for dep, (head, deprel) in enumerate(zip(example.heads, example.deprels)):
            if not self._is_valid_link(head, dep, n):
                continue
            edges.append(
                TypedEdge(src=head, dst=dep, view=VIEW, etype=f"DEP:{deprel}", conf=1.0, rule_id=None)
            )
            edges.append(
                TypedEdge(
                    src=dep, dst=head, view=VIEW, etype=f"DEP:{deprel}{REV_SUFFIX}", conf=1.0, rule_id=None
                )
            )

        # Self-loop cho moi token, ke ca token bi co lap (root cua cau con)
        edges.extend(
            TypedEdge(src=i, dst=i, view=VIEW, etype=ETYPE_SELF, conf=1.0, rule_id=None) for i in range(n)
        )
        return edges

    @staticmethod
    def _is_valid_link(head: int, dep: int, n: int) -> bool:
        """Canh head->dep co dung de sinh khong.

        Bo qua ba truong hop, deu KHONG phai loi can bao:
          - head == -1  : token la root, khong co canh di len
          - head ngoai [0, n) : du lieu hong, bo qua thay vi lam sap
          - head == dep : token tu tro vao minh, da co self-loop rieng
        """
        if head == ROOT_HEAD:
            return False
        if not (0 <= head < n):
            return False
        return head != dep
