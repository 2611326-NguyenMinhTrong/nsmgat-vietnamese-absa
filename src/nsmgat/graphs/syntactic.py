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

  Da thu va LOAI phuong an ep parser doc ca binh luan mot lan (bo dau cham
  cau): lam duoc, nhung doi head cua 24,8% token va sinh ra canh SAI nguy
  trang thanh cu phap that. Xem scripts/probe_force_single_parse.py.

  Cach xu ly da chot (GAP-007 phuong an C): tham so `link_roots` cho phep
  chay CA HAI bien the va do hieu so:
      link_roots=False -> baseline `asgcn`         (giu nguyen)
      link_roots=True  -> bien the `asgcn_linked`  (noi root cac cau con)
"""

from __future__ import annotations

from typing import List

from nsmgat.graphs.base import GraphBuilder
from nsmgat.schema import Example, TypedEdge

VIEW = "syn"
ETYPE_SELF = "DEP:self"
ETYPE_ROOT_LINK = "DEP:root_link"
REV_SUFFIX = "_rev"
ROOT_HEAD = -1


class SyntacticGraphBuilder(GraphBuilder):
    """Sinh canh cu phap hai chieu + self-loop tu cay phu thuoc.

    link_roots (GAP-007, phuong an C — hoc vien chot 06/09/2026):
      False (mac dinh) : do thi dung y nhu parser tra ve. La hanh vi cua
                         baseline `asgcn` — trung thuc voi phuong phap goc.
      True             : them canh hai chieu noi root cua cac cau con LIEN KE,
                         etype "DEP:root_link". La hanh vi cua bien the
                         `asgcn_linked`.

      Hai bien the chi khac DUNG MOT BIEN nay, moi thu khac giu nguyen, nen
      hieu so ket qua giua chung do truc tiep tac dong cua viec do thi bi
      chia cat. Xem chuyende1/gaps/GAP-007.

      Mac dinh la False co chu y: `asgcn` phai giu nguyen hanh vi da co, khong
      duoc doi ngam vi mot tham so moi.
    """

    def __init__(self, link_roots: bool = False) -> None:
        self.link_roots = link_roots

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

        if self.link_roots:
            edges.extend(self._build_root_links(example.heads))

        # Self-loop cho moi token, ke ca token bi co lap (root cua cau con)
        edges.extend(
            TypedEdge(src=i, dst=i, view=VIEW, etype=ETYPE_SELF, conf=1.0, rule_id=None) for i in range(n)
        )
        return edges

    @staticmethod
    def _build_root_links(heads: List[int]) -> List[TypedEdge]:
        """Noi root cua cac cau con lien ke thanh mot chuoi.

        Noi theo CHUOI (root1 <-> root2 <-> root3) chu khong theo hinh sao
        (root1 <-> tat ca): chuoi giu duoc trat tu tuyen tinh cua dien ngon —
        hai cau lien ke lien quan nhau hon hai cau cach xa.

        conf = 1.0 giong moi canh view "syn" khac. KHONG dat mot con so < 1
        vi khong co co so nao de bien minh cho gia tri cu the (dung cai bay
        "confidence = 0,92 o dau ra?" ma PLAN_NSMGAT.md canh bao). Thay vao
        do canh nay duoc phan biet bang ETYPE rieng, nen:
          - CD1: ASGCN doi xu moi canh nhu nhau, ta chi do co/khong
          - CD2: NS-MGAT co the hoc trong so rieng cho "DEP:root_link"
        """
        roots = [i for i, head in enumerate(heads) if head == ROOT_HEAD]
        edges: List[TypedEdge] = []
        for truoc, sau in zip(roots, roots[1:]):
            edges.append(
                TypedEdge(src=truoc, dst=sau, view=VIEW, etype=ETYPE_ROOT_LINK, conf=1.0, rule_id=None)
            )
            edges.append(
                TypedEdge(
                    src=sau,
                    dst=truoc,
                    view=VIEW,
                    etype=f"{ETYPE_ROOT_LINK}{REV_SUFFIX}",
                    conf=1.0,
                    rule_id=None,
                )
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
