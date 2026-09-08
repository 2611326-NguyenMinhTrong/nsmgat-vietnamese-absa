"""[CD1.4b] Theo doi LIEN TUC mot lan huan luyen — dung cho MOI mo hinh sau nay.

VI SAO CAN
----------
Huan luyen tren CPU mat hang gio. Ba van de thuc te da gap:

  1. Khong biet con bao lau. Nhin mot man hinh dung im khong biet no dang chay
     hay da treo. Script nay in thoi gian TUNG epoch va uoc luong luc xong.
  2. Dong terminal la mat log. Nay log ghi ra `logs/<exp>/seed<N>.log`, script
     doc file do nen mo bao nhieu cua so cung duoc, dong luc nao cung duoc.
  3. Epoch 1 luon nhin nhu cham bat thuong vi con gom ca thoi gian dung
     dataset va dung mo hinh. Script tach rieng dong "chuan bi" nen doc so
     epoch khong bi hieu nham.

CACH DUNG (chay o mot cua so terminal KHAC voi cua so dang huan luyen)
---------------------------------------------------------------------
    .venv\\Scripts\\python.exe scripts/watch_train.py                    # tu tim lan chay moi nhat
    .venv\\Scripts\\python.exe scripts/watch_train.py --exp bilstm --seed 42
    .venv\\Scripts\\python.exe scripts/watch_train.py --mot-lan          # in roi thoat, khong theo doi
    .venv\\Scripts\\python.exe scripts/watch_train.py --file duong/dan/bat_ky.log

Mo TRUOC KHI huan luyen bat dau cung duoc: script se doi file log xuat hien.
Nhan Ctrl+C de thoat — KHONG anh huong gi toi tien trinh huan luyen, vi day
chi la doc file.

GIOI HAN — doc ky truoc khi trich so vao bao cao
------------------------------------------------
Cot "kien nhan" la ƯỚC LƯỢNG: script mo phong lai luat dung som cua
`trainer.py` de bao truoc, chu KHONG phai doc trang thai that cua tien trinh.
Nguon su that ve ket qua van la `results/<exp>/seed<N>/metrics.json`.
Thoi gian epoch o day do bang HIEU DAU THOI GIAN hai dong log — chenh vai
giay so voi dong ho trong tien trinh. Dung de theo doi thi du, dung de bao
cao chi phi thi lay `train_time_sec` trong metrics.json.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Console Windows mac dinh la cp1252, khong in duoc chu tieng Viet co dau.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nsmgat.utils.io import load_config  # noqa: E402

DINH_DANG_GIO = "%Y-%m-%d %H:%M:%S"

RE_GIO = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \|")
RE_MOC = re.compile(
    r"=== BAT DAU (?P<exp>\S+?)/seed(?P<seed>\d+) \| config=(?P<config>\S+) \| device=(?P<device>\S+) ==="
)
RE_CHUAN_BI = re.compile(r"Chuan bi xong")
RE_EPOCH = re.compile(
    r"epoch (?P<k>\d+)/(?P<tong>\d+) \| train_loss=(?P<loss>[\d.]+) "
    r"\| dev_acc=(?P<acc>[\d.]+) \| dev_macro_f1=(?P<f1>[\d.]+)"
)
RE_DUNG_SOM = re.compile(r"Dung som o epoch (\d+)")
RE_CHAY_TIEP = re.compile(r"Chay tiep tu epoch (?P<k>\d+)/(?P<tong>\d+)")
RE_KET_THUC = re.compile(r"=== KET THUC")
RE_GHI_METRICS = re.compile(r"Da ghi (\S+metrics\.json)")


def gio_cua(dong: str) -> datetime | None:
    m = RE_GIO.match(dong)
    return datetime.strptime(m.group(1), DINH_DANG_GIO) if m else None


def khoang(giay: float) -> str:
    """3725 -> '1g02p'. Do dai co dinh de cot thang hang."""
    giay = int(round(giay))
    if giay >= 3600:
        return f"{giay // 3600}g{(giay % 3600) // 60:02d}p"
    if giay >= 60:
        return f"{giay // 60}p{giay % 60:02d}s"
    return f"{giay}s"


class TrangThai:
    """Gom moi thu doc duoc tu log cua MOT lan chay."""

    def __init__(self) -> None:
        self.exp = self.seed = self.device = self.config = None
        self.tong_epoch: int | None = None
        self.kien_nhan_toi_da: int | None = None
        self.bat_dau: datetime | None = None
        self.chuan_bi_xong: datetime | None = None
        self.epochs: list[dict] = []
        self.f1_tot_nhat = -1.0
        self.kien_nhan_con: int | None = None
        self.xong = False
        # Epoch da xong o CAC PHIEN TRUOC (khac 0 khi chay tiep bang --resume).
        # Khong co bien nay thi bang chi co cac epoch cua phien nay, va uoc
        # luong gio xong se sai hoan toan.
        self.epoch_da_co = 0
        self.ly_do_xong = ""
        self.metrics_path: str | None = None

    # --- doc config de biet ke hoach ---------------------------------------

    def _nap_config(self) -> None:
        if not self.config:
            return
        duong = REPO_ROOT / self.config
        if not duong.exists():
            return
        try:
            cfg = load_config(duong)
        except Exception:
            return
        tcfg = cfg.get("train", {})
        self.tong_epoch = tcfg.get("epochs")
        self.kien_nhan_toi_da = tcfg.get("early_stop_patience")
        self.kien_nhan_con = self.kien_nhan_toi_da
        self.batch_size = tcfg.get("batch_size")
        self.lr = tcfg.get("lr")

    # --- an tung dong log ---------------------------------------------------

    def an(self, dong: str) -> str | None:
        """Doc mot dong log. Tra ve dong can IN RA man hinh (None = bo qua)."""
        g = gio_cua(dong)

        if m := RE_MOC.search(dong):
            self.__init__()  # gap moc moi = lan chay moi, xoa sach trang thai cu
            self.exp, self.seed = m.group("exp"), int(m.group("seed"))
            self.config, self.device = m.group("config"), m.group("device")
            self.bat_dau = g
            self._nap_config()
            return None

        if m := RE_CHAY_TIEP.search(dong):
            self.epoch_da_co = int(m.group("k")) - 1
            self.tong_epoch = self.tong_epoch or int(m.group("tong"))
            return (f"  {'chạy tiếp':>7}  {'':>9}   {'':>10}   {'':>7}   {'':>12}   "
                    f"{self.epoch_da_co} epoch đã xong ở lần chạy trước")

        if RE_CHUAN_BI.search(dong) and g:
            self.chuan_bi_xong = g
            if self.bat_dau:
                return (f"  {'chuẩn bị':>7}  {khoang((g - self.bat_dau).total_seconds()):>9}"
                        f"   {'':>10}   {'':>7}   {'':>12}   dựng dataset + mô hình")
            return None

        if m := RE_EPOCH.search(dong):
            return self._an_epoch(m, g)

        if m := RE_DUNG_SOM.search(dong):
            self.xong = True
            self.ly_do_xong = (f"DỪNG SỚM ở epoch {m.group(1)} — "
                               f"{self.kien_nhan_toi_da} epoch liền không cải thiện")
            return f"\n  {self.ly_do_xong}"

        if m := RE_GHI_METRICS.search(dong):
            self.metrics_path = m.group(1)
            return f"  Đã ghi kết quả: {m.group(1)}"

        if RE_KET_THUC.search(dong):
            self.xong = True
            if not self.ly_do_xong:
                self.ly_do_xong = "Chạy hết số epoch đã đặt"
            return None

        return None

    def _an_epoch(self, m: re.Match, g: datetime | None) -> str:
        k = int(m.group("k"))
        f1 = float(m.group("f1"))
        self.tong_epoch = self.tong_epoch or int(m.group("tong"))

        truoc = (self.epochs[-1]["gio"] if self.epochs else
                 self.chuan_bi_xong or self.bat_dau)
        keo_dai = (g - truoc).total_seconds() if (g and truoc) else None

        tot_hon = f1 > self.f1_tot_nhat
        if tot_hon:
            self.f1_tot_nhat = f1
            self.kien_nhan_con = self.kien_nhan_toi_da
            ghi_chu = "★ tốt nhất"
        elif self.kien_nhan_con is not None:
            self.kien_nhan_con -= 1
            ghi_chu = f"kiên nhẫn còn {max(self.kien_nhan_con, 0)}/{self.kien_nhan_toi_da}"
        else:
            ghi_chu = ""

        self.epochs.append({"k": k, "gio": g, "keo_dai": keo_dai, "f1": f1})

        return (f"  {k:>7}  {khoang(keo_dai) if keo_dai else '—':>9}"
                f"   {float(m.group('loss')):>10.4f}"
                f"   {float(m.group('acc')):>7.4f}   {f1:>12.4f}   {ghi_chu}")

    # --- suy ra thong tin tong hop ------------------------------------------

    def trung_binh(self) -> float | None:
        dai = [e["keo_dai"] for e in self.epochs if e["keo_dai"]]
        return sum(dai) / len(dai) if dai else None

    def dong_trang_thai(self) -> str:
        """Dong duy nhat cap nhat lien tuc o day man hinh."""
        if self.xong:
            return ""
        tb = self.trung_binh()
        # Lay so epoch tu chinh dong log, khong dem so dong — dem so dong se sai
        # khi lan chay nay la chay tiep tu giua chung.
        da_xong = self.epochs[-1]["k"] if self.epochs else self.epoch_da_co
        moc_cuoi = (self.epochs[-1]["gio"] if self.epochs
                    else self.chuan_bi_xong or self.bat_dau)
        if not moc_cuoi:
            return "  … đang chờ dòng log đầu tiên"

        troi = (datetime.now() - moc_cuoi).total_seconds()
        phan = [f"đang chạy epoch {da_xong + 1} — {khoang(troi)}"]
        if tb:
            phan.append(f"tb {khoang(tb)}/epoch")
            if self.tong_epoch:
                con = (self.tong_epoch - da_xong) * tb - troi
                if con > 0:
                    xong_luc = datetime.now() + timedelta(seconds=con)
                    phan.append(f"nếu chạy đủ {self.tong_epoch} epoch: còn ~{khoang(con)} "
                                f"(≈{xong_luc:%H:%M})")
            if self.kien_nhan_con is not None and self.kien_nhan_con < (self.kien_nhan_toi_da or 0):
                som = max(self.kien_nhan_con, 0) * tb - troi
                if som > 0:
                    phan.append(f"có thể dừng sớm sau ~{khoang(som)}")
        return "  [" + " | ".join(phan) + "]"

    def tom_tat(self) -> str:
        tb = self.trung_binh()
        d = ["", "=" * 78, "  KẾT THÚC", "=" * 78]
        d.append(f"  Lý do        : {self.ly_do_xong or '—'}")
        d.append(f"  Số epoch chạy: {self.epochs[-1]['k'] if self.epochs else 0}"
                 + (f"/{self.tong_epoch}" if self.tong_epoch else ""))
        if tb:
            d.append(f"  Thời gian    : trung bình {khoang(tb)}/epoch"
                     f" · tổng huấn luyện {khoang(tb * len(self.epochs))}")
        if self.chuan_bi_xong and self.bat_dau:
            d.append(f"  Chuẩn bị     : {khoang((self.chuan_bi_xong - self.bat_dau).total_seconds())}"
                     f"  (dựng dataset + mô hình, chưa tính vào train_time_sec)")
        d.append(f"  dev_macro_f1 tốt nhất: {self.f1_tot_nhat:.4f}"
                 if self.f1_tot_nhat >= 0 else "  Chưa có epoch nào")
        if self.metrics_path:
            d.append(f"  Kết quả      : {self.metrics_path}")
            d += self._nhac_don_dep()
        else:
            d.append("  ! Chưa thấy dòng 'Da ghi ...metrics.json' — lần chạy này CHƯA "
                     "có kết quả hoàn chỉnh.")
        return "\n".join(d)

    def _nhac_don_dep(self) -> list[str]:
        """Nhac xoa last.pt khi no khong con tac dung — KHONG tu xoa.

        Chay xong roi thi last.pt chi con dung neu muon chay THEM epoch nua.
        Danh gia va bao cao deu doc best.pt, nen no thuong la file thua. Nhung
        quyet dinh xoa la cua hoc vien: xoa nham mot checkpoint dat vai gio
        huan luyen thi khong lay lai duoc.
        """
        if not (self.exp and self.seed is not None):
            return []
        last = REPO_ROOT / "checkpoints" / self.exp / f"seed{self.seed}" / "last.pt"
        if not last.exists():
            return []
        mb = last.stat().st_size / 1024 / 1024
        return [
            "",
            f"  Có thể dọn : {last.relative_to(REPO_ROOT)}  ({mb:,.0f} MB)",
            "               Chạy xong rồi thì file này chỉ còn cần nếu bạn muốn chạy",
            "               THÊM epoch — đánh giá và báo cáo đều đọc best.pt.",
            f"               Xoá bằng:  Remove-Item {last.relative_to(REPO_ROOT)}",
        ]


# --- Tim file log --------------------------------------------------------------


def tim_log(exp: str | None, seed: int | None, file: str | None) -> Path:
    if file:
        return Path(file)
    thu_muc = REPO_ROOT / "logs"
    if exp:
        return thu_muc / exp / f"seed{seed if seed is not None else 42}.log"

    cac_log = sorted(thu_muc.glob("*/seed*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not cac_log:
        raise SystemExit(
            f"  Chưa có file log nào trong {thu_muc}.\n"
            "  Hãy chạy huấn luyện trước, hoặc chỉ rõ: --exp <tên> --seed <N>\n"
            "  (log chỉ sinh ra từ lần huấn luyện bắt đầu SAU khi có tính năng này)"
        )
    return cac_log[0]


def doi_file(path: Path, im_lang: bool = False) -> None:
    if path.exists():
        return
    if not im_lang:
        print(f"  Chưa có {path} — đang đợi huấn luyện bắt đầu … (Ctrl+C để thoát)")
    while not path.exists():
        time.sleep(1.0)


# --- Vong theo doi -------------------------------------------------------------

TIEU_DE = (f"  {'Epoch':>7}  {'Thời gian':>9}   {'train_loss':>10}   "
           f"{'dev_acc':>7}   {'dev_macro_f1':>12}   Ghi chú")


def in_dau(tt: TrangThai, log: Path) -> None:
    print("=" * 78)
    ten = f"{tt.exp} / seed {tt.seed}" if tt.exp else log.stem
    print(f"  THEO DÕI HUẤN LUYỆN — {ten}")
    print("=" * 78)
    print(f"  Log      : {log}")
    if tt.config:
        print(f"  Config   : {tt.config}")
    if tt.device:
        print(f"  Thiết bị : {tt.device}")
    ke_hoach = []
    if tt.tong_epoch:
        ke_hoach.append(f"{tt.tong_epoch} epoch")
    if getattr(tt, "batch_size", None):
        ke_hoach.append(f"batch {tt.batch_size}")
    if getattr(tt, "lr", None):
        ke_hoach.append(f"lr {tt.lr}")
    if tt.kien_nhan_toi_da:
        ke_hoach.append(f"dừng sớm sau {tt.kien_nhan_toi_da} epoch không cải thiện")
    if ke_hoach:
        print(f"  Kế hoạch : {' · '.join(ke_hoach)}")
    if tt.bat_dau:
        print(f"  Bắt đầu  : {tt.bat_dau:%Y-%m-%d %H:%M:%S}")
    print()
    print(TIEU_DE)
    print(f"  {'-' * 7}  {'-' * 9}   {'-' * 10}   {'-' * 7}   {'-' * 12}   {'-' * 20}")


def phan_tich(noi_dung: str, tt: TrangThai) -> list[str]:
    """An het noi dung, tra ve cac dong can in. Neu co moc BAT DAU thi chi
    lay tu moc CUOI CUNG tro di — mot file co the chua nhieu lan chay."""
    dong = noi_dung.splitlines()
    vi_tri_moc = [i for i, d in enumerate(dong) if RE_MOC.search(d)]
    if vi_tri_moc:
        dong = dong[vi_tri_moc[-1]:]
    return [ra for d in dong if (ra := tt.an(d)) is not None]


def xoa_dong_trang_thai() -> None:
    sys.stdout.write("\r" + " " * 118 + "\r")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--exp", help="Tên thí nghiệm, ví dụ bilstm")
    parser.add_argument("--seed", type=int, help="Seed (mặc định 42)")
    parser.add_argument("--file", help="Theo dõi một file log bất kỳ")
    parser.add_argument("--mot-lan", dest="mot_lan", action="store_true",
                        help="In trạng thái hiện tại rồi thoát, không theo dõi tiếp")
    parser.add_argument("--nhip", type=float, default=2.0,
                        help="Số giây giữa hai lần đọc lại file (mặc định 2)")
    args = parser.parse_args(argv)

    log = tim_log(args.exp, args.seed, args.file)
    if not args.mot_lan:
        doi_file(log)
    elif not log.exists():
        raise SystemExit(f"  Không có {log}")

    tt = TrangThai()
    noi_dung = log.read_text(encoding="utf-8", errors="replace")
    cac_dong = phan_tich(noi_dung, tt)

    in_dau(tt, log)
    for d in cac_dong:
        print(d)

    if args.mot_lan or tt.xong:
        if tt.xong:
            print(tt.tom_tat())
        else:
            print(tt.dong_trang_thai())
        return 0

    vi_tri = len(noi_dung.encode("utf-8"))
    try:
        while True:
            kich_thuoc = log.stat().st_size
            if kich_thuoc < vi_tri:  # file bi ghi de -> doc lai tu dau
                vi_tri = 0
            if kich_thuoc > vi_tri:
                with open(log, "rb") as f:
                    f.seek(vi_tri)
                    them = f.read().decode("utf-8", errors="replace")
                vi_tri = kich_thuoc
                if moi := [ra for d in them.splitlines() if (ra := tt.an(d)) is not None]:
                    xoa_dong_trang_thai()
                    for d in moi:
                        print(d)
            if tt.xong:
                xoa_dong_trang_thai()
                print(tt.tom_tat())
                return 0
            sys.stdout.write("\r" + tt.dong_trang_thai().ljust(118)[:118])
            sys.stdout.flush()
            time.sleep(args.nhip)
    except KeyboardInterrupt:
        xoa_dong_trang_thai()
        print("\n  Đã thoát theo dõi. Tiến trình huấn luyện VẪN ĐANG CHẠY "
              "(script này chỉ đọc file log).")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
