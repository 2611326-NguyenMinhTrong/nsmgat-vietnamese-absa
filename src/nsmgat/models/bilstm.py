"""[CD1.4b] BiLSTMModel — baseline mang no-ron tuan tu + attention theo khia canh.

Ban GVHD duyet (docs/Tom_Tat_Dinh_Huong_Final.docx muc 1) liet ke "BiLSTM/Bi-GRU"
trong nhom can thuc nghiem lai. Vai tro trong thang bac 6 mo hinh:

    lexicon -> BILSTM -> phobert -> asgcn -> senticgcn -> [NS-MGAT o CD2]
               ^^^^^^
    Moc TRUOC ky nguyen tien huan luyen. Hieu so bilstm <-> phobert tra loi:
    "mo hinh ngon ngu tien huan luyen dang gia bao nhieu diem?"

KIEN TRUC — theo tinh than ATAE-LSTM (Wang et al. 2016)
--------------------------------------------------------
    input_ids (subword PhoBERT)
        -> Embedding (KHOI TAO NGAU NHIEN, hoc tu dau — khong tien huan luyen)
        -> noi them vector khia canh vao TUNG token   <- diem mau chot
        -> BiLSTM
        -> attention voi TRUY VAN la vector khia canh <- diem mau chot
        -> Linear -> 3 lop

Hai "diem mau chot" la thu phan biet mo hinh nay voi `lexicon`. LexiconModel
MU KHIA CANH: moi Example cua cung mot cau nhan cung mot du doan, nen bi chan
o tran 80,2% accuracy (do duoc o CD1.4a). BiLSTM nhin thay khia canh o CA HAI
cho — luc ma hoa va luc gop — nen KHONG bi tran do chan.

VI SAO NHUNG SUBWORD PHOBERT CHU KHONG PHAI TU MUC WORD
--------------------------------------------------------
ATAE-LSTM goc dung tu muc word + GloVe. Nhung o day chon subword PhoBERT vi:

  1. So sanh SACH HON voi `phobert`. Dung chung bo tach tu => hieu so
     bilstm <-> phobert chi con la (trong so tien huan luyen + kien truc),
     bot duoc mot bien gay nhieu la cach tach tu.
  2. Chiu duoc tu la. UIT-ViSFD la binh luan mang xa hoi, day loi chinh ta va
     teencode. Tu la o muc word -> UNK hoan toan; o muc subword -> van tach
     duoc thanh cac manh da tung thay.
  3. Dung lai duoc input_ids san co trong batch, khong phai doc lai jsonl nhu
     LexiconModel (xem GAP-008 — chi phi tokenize khong con lang phi).

DANH DOI: kem "trung thanh lich su" hon so voi ATAE-LSTM goc. Da ghi ro de
tra loi neu hoi dong hoi.

BANG NHUNG GON — do duoc, khong doan
-------------------------------------
Tu vung PhoBERT day du: 64.000 o. Nhung chi 9.134 (14,3%) thuc su xuat hien
trong tap train. Neu cap phat ca 64.000 thi 85,7% bang nhung KHONG BAO GIO
duoc huan luyen — vua phi tham so, vua nguy hiem: luc suy luan mot subword la
se lay ra mot vector NGAU NHIEN chua he duoc hoc.

Nen: dung bang nhung GON chi gom subword thay trong TRAIN, cong 2 o dac biet
(0 = PAD, 1 = UNK). Subword la luc suy luan -> UNK. Xay chi so tu TRAIN,
khong dung dev/test => khong ro ri.
"""

from __future__ import annotations

from typing import Any, Dict, List

import torch
import torch.nn as nn

from nsmgat.models.base import BaseModel
from nsmgat.utils.io import read_jsonl

PAD_ID = 0
UNK_ID = 1
SO_O_DAC_BIET = 2


class BiLSTMModel(BaseModel):
    """BiLSTM + attention theo khia canh, hoc tu dau (khong tien huan luyen)."""

    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()
        mcfg = cfg.get("model", {})
        emb_dim = mcfg.get("emb_dim", 300)
        aspect_dim = mcfg.get("aspect_dim", 64)
        hidden_dim = mcfg.get("lstm_hidden", 256)
        num_layers = mcfg.get("lstm_layers", 1)
        dropout = mcfg.get("dropout", 0.1)
        self.rnn_type = mcfg.get("rnn_type", "lstm").lower()

        id_map, self.aspect_to_idx = self._xay_chi_so(cfg)
        # register_buffer: di theo model sang GPU va nam trong state_dict, nhung
        # KHONG phai tham so hoc duoc (khong vao count_params, khong bi optimizer
        # cap nhat). Dung cho bang tra cuu tinh nhu the nay.
        self.register_buffer("id_map", id_map)

        self.emb = nn.Embedding(int(id_map.max().item()) + 1, emb_dim, padding_idx=PAD_ID)
        self.aspect_emb = nn.Embedding(len(self.aspect_to_idx), aspect_dim)
        self.dropout = nn.Dropout(dropout)

        rnn_cls = nn.GRU if self.rnn_type == "gru" else nn.LSTM
        self.rnn = rnn_cls(
            input_size=emb_dim + aspect_dim,  # ATAE: noi vector khia canh vao tung token
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        # Attention: truy van la vector khia canh, khoa la trang thai an BiLSTM
        self.attn = nn.Linear(2 * hidden_dim + aspect_dim, 1)
        self.classifier = nn.Linear(2 * hidden_dim, 3)

    def _xay_chi_so(self, cfg: Dict[str, Any]) -> tuple[torch.Tensor, Dict[str, int]]:
        """Xay bang tra subword PhoBERT -> chi so gon, va bang khia canh -> chi so.

        CHI doc tap TRAIN. Doc dev/test de xay tu vung se la ro ri du lieu:
        mo hinh se "biet truoc" nhung tu chi xuat hien o tap kiem tra.
        """
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(
            cfg.get("model", {}).get("encoder_name", "vinai/phobert-base-v2")
        )
        records = read_jsonl(cfg["data"]["train_path"])

        # Nhieu Example dung chung mot cau (23.872 Example / 7.671 cau) — chi
        # tokenize cau KHAC NHAU, nhanh hon ~3 lan.
        cau_khac_nhau = {r["text"]: r["tokens"] for r in records}
        thay: set[int] = set()
        for tokens in cau_khac_nhau.values():
            thay.update(tokenizer(tokens, is_split_into_words=True)["input_ids"])

        id_map = torch.full((tokenizer.vocab_size,), UNK_ID, dtype=torch.long)
        for gon, goc in enumerate(sorted(thay), start=SO_O_DAC_BIET):
            id_map[goc] = gon
        if tokenizer.pad_token_id is not None:
            id_map[tokenizer.pad_token_id] = PAD_ID

        aspects = sorted({r["aspect"] for r in records})
        return id_map, {a: i for i, a in enumerate(aspects)}

    def forward(self, batch: Dict[str, Any]) -> torch.Tensor:
        h, a_lap, mask = self.ma_hoa(batch)  # (B, L, 2H), (B, L, A), (B, L)
        trong_so = self._chu_y(h, a_lap, mask)  # (B, L)
        gop = torch.bmm(trong_so.unsqueeze(1), h).squeeze(1)  # (B, 2H)
        return self.classifier(self.dropout(gop))

    def _chu_y(
        self, h: torch.Tensor, a_lap: torch.Tensor, mask: torch.Tensor
    ) -> torch.Tensor:
        """Attention voi TRUY VAN la vector khia canh. Tra ve trong so (B, L).

        Tach rieng khoi forward() de scripts/try_bilstm.py xem duoc mo hinh
        nhin vao token nao MA KHONG phai chep lai cong thuc. Chep lai la cach
        cong cu va mo hinh lech nhau — dung loai loi ca repo nay dang chong
        (xem docstring scripts/try_lexicon.py).
        """
        diem = self.attn(torch.cat([h, a_lap], dim=-1)).squeeze(-1)  # (B, L)
        diem = diem.masked_fill(~mask, torch.finfo(diem.dtype).min)
        return torch.softmax(diem, dim=-1)

    def ma_hoa(self, batch: Dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Chay den truoc buoc gop: tra ve (h, a_lap, mask).

        Cung ly do voi _chu_y(): de cong cu thu tay dung DUNG duong code that.
        """
        device = batch["labels"].device
        mask = batch["attention_mask"].bool()

        # Subword PhoBERT -> chi so gon. Tra cuu tensor, khong vong lap Python.
        ids = self.id_map[batch["input_ids"].clamp(min=0, max=self.id_map.shape[0] - 1)]
        x = self.dropout(self.emb(ids))  # (B, L, E)

        aspect_idx = torch.tensor(
            [self.aspect_to_idx.get(a, 0) for a in batch["aspect_text"]],
            dtype=torch.long,
            device=device,
        )
        a = self.aspect_emb(aspect_idx)
        a_lap = a.unsqueeze(1).expand(-1, x.size(1), -1)

        # ATAE: noi vector khia canh vao TUNG token truoc khi vao BiLSTM
        h, _ = self.rnn(torch.cat([x, a_lap], dim=-1))  # (B, L, 2H)
        return h, a_lap, mask

    # explain(): KHONG ghi de — ke thua mac dinh cua BaseModel (tra ve []).
    #
    # Mo hinh nay VE NGUYEN TAC giai thich duoc: trong so attention cho biet no
    # nhin vao token nao khi quyet dinh. Nhung chua ghi de vi:
    #   - Hop dong BaseModel noi ro baseline duoc phep tra ve []
    #   - Chua co doan code nao tieu thu ket qua explain() => cai bay gio la
    #     doan xem CD1.9 can dinh dang gi (quy tac 6: khong viet logic step chua toi)
    # Khi CD1.9 (phan tich loi) can den, ghi de o day: tra ve trong_so attention
    # kem token da giai ma, tuong tu LexiconModel.explain().
