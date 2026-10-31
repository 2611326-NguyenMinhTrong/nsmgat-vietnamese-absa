"""[CD1.11d] Tin hieu luat cua `phobert_luat`: danh dau phu dinh va chuyen y theo tu khoa.

DAY KHONG PHAI BO LUAT S2.2
---------------------------
Thi nghiem can thiep cua Chuyen de 1 chi hoi mot cau: dua cau truc phu dinh, chuyen y vao PhoBERT
thi ket qua co tot hon khong. Bo luat that (co do tin cay, theo tung khia canh) la viec cua Chuyen
de 2, nam o `src/nsmgat/rules/`, xem chuyende1/MODULE.md muc 2.3.

Danh sach tu khoa la BAN CHEP cua scripts/build_diagnostic_candidates.py, dung cach da dung voi
TEN_LOP cua file do: script khong import goi, goi khong import script, va co test canh hai noi
khong lech nhau (tests/test_tin_hieu_luat.py). Khong them, khong bot tu: them tu sau khi da xem ket
qua la chinh luat theo tap kiem tra.

HAI KENH, DOC LAP VOI NHAU
--------------------------
Mot tu co the vua trong pham vi phu dinh vua o ve sau tu noi, nen moi tu co hai nhan:

    "pin khong trau nhung man_hinh dep"
    phu_dinh   0   TU  PHAM_VI   0    0         0
    chuyen_y   NHUONG NHUONG NHUONG TU NHAN    NHAN

Tach kenh con la de thi nghiem loai bo tat duoc tung luat ma khong doi luat kia.

Pham vi phu dinh: tu sau tu phu dinh den dau cau hoac tu noi chuyen y gan nhat. Ve chuyen y: tinh
trong mot cau (het cau la . ! ? ; hoac gach dau dong), KHONG dung o dau phay vi "tuy A, nhung B" va
"A, B, nhung C" deu co dau phay giua ve. Tu noi nhuong bo (tuy, mac du...) dat ve nhuong SAU tu noi,
den dau cau gan nhat; cac tu noi con lai dat ve nhuong TRUOC tu noi.

Nhan chi noi "tu nay nam o dau", KHONG noi "doi cuc di". Muc 5.3 cua bao cao cho thay lat cuc gan
nhu khong khai thac duoc gi tren du lieu nay; mo hinh tu hoc nhan do dang gia bao nhieu.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

PHU_DINH = frozenset({
    "không", "chẳng", "chả", "chưa",
    "không_thể", "không_thể_nào", "không_nổi",
    "ko", "k", "kh", "kg", "khong", "hok", "kô", "éo",
})
CHUYEN_Y = frozenset({
    "nhưng", "nhưng_mà", "nhưg", "cơ_mà", "song", "ngược_lại", "vậy_mà",
    "tuy", "tuy_nhiên", "tuy_rằng", "mặc_dù", "dù",
    "trừ", "ngoại_trừ", "có_điều", "mỗi_tội", "chỉ_tội", "được_cái", "được_mỗi_cái",
})
NHUONG_BO = frozenset({"tuy", "tuy_rằng", "mặc_dù", "dù"})

# Nhan 0 luon la "khong co gi": embedding cua no dung yen o 0 (xem models/phobert_luat.py).
PD_KHONG, PD_TU, PD_PHAM_VI = 0, 1, 2
CY_KHONG, CY_TU, CY_VE_NHUONG, CY_VE_NHAN = 0, 1, 2, 3
SO_NHAN = {"phu_dinh": 3, "chuyen_y": 4}

_KY_TU_HET_CAU = frozenset(".!?;…+-*")


def la_dau_cau(tok: str) -> bool:
    """Token khong co chu cai hay chu so. Bieu tuong cam xuc cung tinh, vi no cung ngat y."""
    return not any(c.isalnum() for c in tok)


def la_het_cau(tok: str) -> bool:
    return bool(tok) and all(c in _KY_TU_HET_CAU for c in tok)


def danh_dau_phu_dinh(tokens: Sequence[str]) -> List[int]:
    nhan = [PD_KHONG] * len(tokens)
    trong_pham_vi = False
    for i, tok in enumerate(tokens):
        t = tok.lower()
        if t in PHU_DINH:
            nhan[i] = PD_TU
            trong_pham_vi = True
        elif la_dau_cau(t) or t in CHUYEN_Y:
            trong_pham_vi = False
        elif trong_pham_vi:
            nhan[i] = PD_PHAM_VI
    return nhan


def _cac_cau(tokens: Sequence[str]) -> List[Tuple[int, int]]:
    """Cac doan [dau, cuoi) ngan boi dau het cau."""
    doan: List[Tuple[int, int]] = []
    dau = 0
    for i, tok in enumerate(tokens):
        if la_het_cau(tok):
            if i > dau:
                doan.append((dau, i))
            dau = i + 1
    if dau < len(tokens):
        doan.append((dau, len(tokens)))
    return doan


def danh_dau_chuyen_y(tokens: Sequence[str]) -> List[int]:
    tu = [t.lower() for t in tokens]
    nhan = [CY_KHONG] * len(tu)
    for dau, cuoi in _cac_cau(tu):
        noi = [i for i in range(dau, cuoi) if tu[i] in CHUYEN_Y]
        if not noi:
            continue
        # Mac dinh: truoc tu noi dau tien la ve nhuong, sau no la ve nhan.
        # "may dep du pin yeu": tu noi dau la nhuong bo thi phan truoc no moi la ve nhan.
        truoc = CY_VE_NHAN if tu[noi[0]] in NHUONG_BO else CY_VE_NHUONG
        for i in range(dau, cuoi):
            if tu[i] in CHUYEN_Y:
                nhan[i] = CY_TU
            elif not la_dau_cau(tu[i]):
                nhan[i] = truoc if i < noi[0] else CY_VE_NHAN
        for i in noi:
            if tu[i] not in NHUONG_BO:
                continue
            j = i + 1
            while j < cuoi and not la_dau_cau(tu[j]) and tu[j] not in CHUYEN_Y:
                nhan[j] = CY_VE_NHUONG
                j += 1
    return nhan


def tin_hieu_cua(tokens: Sequence[str]) -> Dict[str, List[int]]:
    """{kenh: nhan cua tung tu}. Chi doc mat chu cua tu: khong nhan, khong khia canh, khong cay cu phap."""
    return {"phu_dinh": danh_dau_phu_dinh(tokens), "chuyen_y": danh_dau_chuyen_y(tokens)}
