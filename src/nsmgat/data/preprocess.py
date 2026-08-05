"""Tien xu ly du lieu tho bang VnCoreNLP: tach tu, POS, cay phu thuoc.

Ghi chu quan trong - kiem chung THUC TE khi viet step nay (khong doan):
- `py_vncorenlp.download_model()` goi noi bo lenh `wget` qua os.system(),
  Windows mac dinh KHONG co wget.exe -> luon that bai. VnCorePipeline tu
  tai model bang urllib (thuan Python, chay duoc tren moi he dieu hanh).
- `DependencyParser` cua VnCoreNLP CAN file models/ner/vi-500brownclusters.xz
  ngay ca khi annotator "ner" khong duoc bat (dung lam dac trung tu vung
  cho parser) -> van phai tai du ca 3 file trong models/ner/.
- pyjnius (jnius) doc bien moi truong JAVA_HOME de tim JVM, KHONG tu suy ra
  tu lenh `java` co san trong PATH. Neu JAVA_HOME chua dat, tu do tim vai
  vi tri cai JDK pho bien truoc khi bao loi.
- `annotate_text()` tra ve dict {sentence_idx(int): [{"index":1-based,
  "wordForm","posTag","nerLabel","head":1-based (0=root CUA CAU do),
  "depLabel"}, ...]}. Ta noi cac cau thanh MOT chuoi phang cho moi Example,
  va doi head ve 0-based toan van ban voi -1=root (co the co nhieu root
  neu text co nhieu cau - do la mot rung phu thuoc, khong phai loi).
"""

from __future__ import annotations

import os
import shutil
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from nsmgat.schema import Example
from nsmgat.utils.io import write_jsonl
from nsmgat.utils.logging import get_logger

logger = get_logger(__name__)

POLARITY_TO_LABEL = {"negative": 0, "neutral": 1, "positive": 2}

_VNCORENLP_BASE_URL = "https://raw.githubusercontent.com/vncorenlp/VnCoreNLP/master"
_VNCORENLP_MODEL_FILES = [
    "models/wordsegmenter/vi-vocab",
    "models/wordsegmenter/wordsegmenter.rdr",
    "models/postagger/vi-tagger",
    "models/dep/vi-dep.xz",
    # DependencyParser doc noi bo 3 file nay du khong bat annotator "ner"
    "models/ner/vi-500brownclusters.xz",
    "models/ner/vi-ner.xz",
    "models/ner/vi-pretrainedembeddings.xz",
]

_COMMON_JDK_DIRS = [
    r"C:\Program Files\Java",
    r"C:\Program Files\Eclipse Adoptium",
    "/usr/lib/jvm",
    "/opt/homebrew/opt/openjdk",
    "/Library/Java/JavaVirtualMachines",
]

JAVA_SETUP_HELP = """
Khong khoi tao duoc VnCoreNLP (can Java/JDK de chay).

Cach cai:
  1. Cai JDK 8 tro len, khuyen nghi Temurin/OpenJDK: https://adoptium.net/
  2. Dat bien moi truong JAVA_HOME tro toi thu muc cai dat JDK, vi du tren
     Windows: JAVA_HOME=C:\\Program Files\\Java\\jdk-17
  3. Chay lai lenh nay.
"""


def _download_vncorenlp_models(save_dir: Path) -> None:
    """Tai VnCoreNLP-1.2.jar + cac model can thiet bang urllib (khong dung wget)."""
    save_dir.mkdir(parents=True, exist_ok=True)

    jar_path = save_dir / "VnCoreNLP-1.2.jar"
    if not jar_path.exists():
        logger.info("Tai VnCoreNLP-1.2.jar ...")
        urllib.request.urlretrieve(f"{_VNCORENLP_BASE_URL}/VnCoreNLP-1.2.jar", jar_path)

    for rel_path in _VNCORENLP_MODEL_FILES:
        dest = save_dir / rel_path
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Tai {rel_path} ...")
        urllib.request.urlretrieve(f"{_VNCORENLP_BASE_URL}/{rel_path}", dest)


def _find_java_home() -> Optional[str]:
    """Do tim JAVA_HOME neu chua duoc dat, thu vai vi tri cai JDK pho bien."""
    if os.environ.get("JAVA_HOME"):
        return os.environ["JAVA_HOME"]
    for base in _COMMON_JDK_DIRS:
        base_path = Path(base)
        if not base_path.is_dir():
            continue
        candidates = sorted(base_path.glob("jdk*"), reverse=True) or sorted(
            (p for p in base_path.iterdir() if p.is_dir()), reverse=True
        )
        if candidates:
            return str(candidates[0])
    return None


class VnCorePipeline:
    """Boc py_vncorenlp, tai model 1 lan vao bo nho.

    save_dir: noi luu VnCoreNLP-1.2.jar + models/ (mac dinh <cwd>/vncorenlp -
    da them vao .gitignore vi la tai nguyen ben thu ba ~100MB, khong commit).
    """

    def __init__(self, save_dir: str | Path = "vncorenlp"):
        self.save_dir = Path(save_dir).resolve()

        if shutil.which("java") is None:
            raise RuntimeError(JAVA_SETUP_HELP)

        java_home = _find_java_home()
        if java_home is None:
            raise RuntimeError(JAVA_SETUP_HELP)
        os.environ.setdefault("JAVA_HOME", java_home)

        _download_vncorenlp_models(self.save_dir)

        # QUAN TRONG: tren Windows, JVM mac dinh dung code page he thong
        # (khong phai UTF-8) cho file.encoding/sun.jnu.encoding - lam hong
        # dau tieng Viet khi marshal chuoi qua JNI (vi du "này" bi bien
        # thanh "n�\xa0y"). Phat hien thuc te khi kiem tra ket qua
        # scripts/prepare_data.py o S0.3. Phai ep UTF-8 TRUOC KHI JVM khoi
        # dong (truoc import py_vncorenlp/jnius).
        import jnius_config

        if not jnius_config.vm_running:
            jnius_config.add_options("-Dfile.encoding=UTF-8", "-Dsun.jnu.encoding=UTF-8")

        import py_vncorenlp  # import cham: khong bat buoc voi module khong dung VnCoreNLP

        # QUAN TRONG: py_vncorenlp.VnCoreNLP.__init__ tu goi os.chdir(save_dir)
        # va KHONG BAO GIO tra lai - neu khong tu khoi phuc, moi duong dan
        # tuong doi sau do trong toan bo chuong trinh (data/processed/,
        # results/, ...) se bi ghi nham vao trong save_dir. Da phat hien
        # thuc te khi chay scripts/prepare_data.py o S0.3.
        cwd_before = os.getcwd()
        try:
            self._model = py_vncorenlp.VnCoreNLP(
                save_dir=str(self.save_dir), annotators=["wseg", "pos", "parse"]
            )
        except Exception as exc:  # jnius.JavaException khong luon la subclass on dinh
            raise RuntimeError(f"Khong khoi tao duoc VnCoreNLP: {exc}\n{JAVA_SETUP_HELP}") from exc
        finally:
            os.chdir(cwd_before)

    def annotate(self, text: str) -> Tuple[List[str], List[str], List[int], List[str]]:
        """Tra ve (tokens, pos, heads, deprels) noi phang qua moi cau trong text.

        heads: 0-based, -1 = root. VnCoreNLP tra head 1-based voi 0=root
        THEO TUNG CAU; ta cong don offset so token qua cac cau truoc do va
        doi 0 -> -1, nen mot text nhieu cau co the co nhieu root (dung).
        Xu ly duoc text rong ("" -> tra 4 list rong) va text 1 tu.
        """
        text = text.strip()
        if not text:
            return [], [], [], []

        sentences = self._model.annotate_text(text)

        tokens: List[str] = []
        pos: List[str] = []
        heads: List[int] = []
        deprels: List[str] = []
        offset = 0
        for sent_idx in sorted(sentences.keys()):
            words = sentences[sent_idx]
            for w in words:
                tokens.append(w["wordForm"])
                pos.append(w["posTag"])
                deprels.append(w["depLabel"])
                raw_head = int(w["head"])
                heads.append(-1 if raw_head == 0 else offset + raw_head - 1)
            offset += len(words)
        return tokens, pos, heads, deprels


def build_examples(raw_records: List[Dict], domain: str, split: str, pipeline) -> List[Example]:
    """Bung moi ban ghi tho ({"text","labels"}) thanh nhieu Example.

    MOI ASPECT LA MOT Example RIENG (bai toan aspect-CATEGORY: phan loai
    theo tung cap cau-khia canh). `pipeline` chi can co method
    `.annotate(text) -> (tokens, pos, heads, deprels)` (VnCorePipeline that
    hoac gia lap trong test).
    """
    examples: List[Example] = []
    for idx, record in enumerate(raw_records):
        labels = record["labels"]
        if not labels:
            continue

        text = record["text"]
        tokens, pos, heads, deprels = pipeline.annotate(text)
        if not tokens:
            continue

        for aspect, polarity in labels.items():
            label = POLARITY_TO_LABEL.get(polarity.lower())
            if label is None:
                continue
            examples.append(
                Example(
                    uid=f"{domain}-{split}-{idx:05d}-{aspect}",
                    text=text,
                    tokens=tokens,
                    pos=pos,
                    heads=heads,
                    deprels=deprels,
                    aspect=aspect,
                    label=label,
                    domain=domain,
                    split=split,
                )
            )
    return examples


def process_all(
    domain: str,
    loader_fn,
    splits: Tuple[str, ...] = ("train", "dev", "test"),
    pipeline: Optional[VnCorePipeline] = None,
    output_dir: str | Path = "data/processed",
) -> Dict[str, int]:
    """Chay full pipeline cho mot domain: tai -> VnCoreNLP -> bung Example ->
    ghi data/processed/{domain}_{split}.jsonl.

    loader_fn(split) -> List[{"text":..., "labels": {aspect: polarity}}],
    chinh la load_visfd hoac load_vlsp da bind san domain.
    Tra ve dict {split: so_luong_Example} de scripts/prepare_data.py in thong ke.
    """
    if pipeline is None:
        pipeline = VnCorePipeline()

    output_dir = Path(output_dir)
    counts: Dict[str, int] = {}
    for split in splits:
        raw_records = loader_fn(split)
        examples = build_examples(raw_records, domain=domain, split=split, pipeline=pipeline)
        out_path = output_dir / f"{domain}_{split}.jsonl"
        write_jsonl(out_path, [ex.to_dict() for ex in examples])
        counts[split] = len(examples)
        logger.info(
            f"{domain}/{split}: {len(raw_records)} cau -> {len(examples)} Example -> {out_path}"
        )
    return counts
