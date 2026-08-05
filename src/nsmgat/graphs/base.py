"""Interface GraphBuilder - hop dong bat bien cho moi bo dung do thi.

CHOT O S0.2 - KHONG SUA SAU BUOC NAY. Ba builder cu the (syntactic o S3.1,
affective o S3.2, logic o S2.2) se ke thua class nay - nho vay model
khong can biet do thi den tu dau, va them view moi khong phai sua model.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from nsmgat.schema import Example, TypedEdge


class GraphBuilder(ABC):
    """Interface chung cho moi bo dung do thi (syn/aff/logic)."""

    @property
    @abstractmethod
    def view_name(self) -> str:
        """Ten view do bo nay sinh ra: 'syn' | 'aff' | 'logic'."""

    @abstractmethod
    def build(self, example: Example) -> List[TypedEdge]:
        """Dung danh sach TypedEdge cho mot Example."""

    def build_batch(self, examples: List[Example]) -> List[List[TypedEdge]]:
        """Dung do thi cho nhieu Example. Mac dinh loop qua build()."""
        return [self.build(example) for example in examples]
