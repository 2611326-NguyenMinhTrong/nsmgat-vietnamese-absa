"""[CD1.5] Ten tieng Viet cua 10 khia canh UIT-ViSFD.

VI SAO O FILE RIENG, KHONG O schema.py
--------------------------------------
`schema.py` la hop dong du lieu dong bang tu S0.2; `chuyende1/MODULE.md` muc
2.3 ghi ro module KHONG duoc dong vao file do. Bang nay la tai nguyen rieng
cua CD1.5, khong phai hop dong du lieu — nen o day.

VI SAO CAN DICH
---------------
UIT-ViSFD dat ten khia canh bang MA TIENG ANH VIET HOA ("BATTERY"), trong khi
van ban la tieng Viet va PhoBERT la mo hinh tieng Viet. Dua thang "BATTERY"
vao PhoBERT thi BPE bam no thanh may manh vo nghia: mo hinh phai hoc lai tu
dau moi ma nghia la gi, chi qua 23.872 mau. Dua "pin" vao thi tu khoa trung
ngay voi tu trong cau, dung duoc tri thuc tien huan luyen.

Gach duoi la quy uoc tach tu cua VnCoreNLP/PhoBERT ("man_hinh" = MOT tu).

DAY LA TAI NGUYEN NHAN TAO do nhom nghien cuu dat ra, KHONG lay tu bai bao.
Hai rang buoc di kem:
  1. Phai ghi ro trong bao cao, khong giau.
  2. Moi mo hinh (phobert, senticgcn, NS-MGAT) phai dung DUNG bang nay, neu
     khong thi so sanh giua chung khong con cong bang.
Hoc vien duyet 21/09/2026 — xem so quyet dinh trong pLan/chuyende1/progress_cd1.md.
"""

from __future__ import annotations

from typing import Dict, List

ASPECT_VI: Dict[str, str] = {
    "BATTERY": "pin",
    "SCREEN": "màn_hình",
    "CAMERA": "camera",
    "FEATURES": "tính_năng",
    "PERFORMANCE": "hiệu_năng",
    "STORAGE": "bộ_nhớ",
    "DESIGN": "thiết_kế",
    "PRICE": "giá",
    "GENERAL": "tổng_thể",
    "SER&ACC": "dịch_vụ và phụ_kiện",
}


def aspect_tokens(aspect: str) -> List[str]:
    """Ma khia canh -> danh sach token tieng Viet da tach tu.

    Ma la thi NEM LOI chu khong doan: mot ma moi xuat hien nghia la du lieu
    doi, phai xem lai — khong duoc im lang dua mot chuoi vo nghia vao mo hinh.
    """
    if aspect not in ASPECT_VI:
        raise KeyError(
            f"Khia canh '{aspect}' khong co trong ASPECT_VI. "
            f"Cac ma da biet: {sorted(ASPECT_VI)}"
        )
    return ASPECT_VI[aspect].split()
