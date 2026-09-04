"""Google Drive'dan veri cekme.

Drive klasoru link ile herkese acik oldugu icin kimlik dogrulama yok:
API anahtari, OAuth, client_secrets.json gerekmiyor. gdown klasoru
listeler, biz sadece bekledigimiz dosyalari indiririz.

Beklenen uzak yapi:
    <folder_id>/<participant_id>/<session_id>/<pid>_<sid>_metadata.json
                                             /<pid>_<sid>_timeseries.csv
                                             /<pid>_<sid>_trial_summary.csv
"""

import re
from pathlib import Path

import gdown

WANTED_SUFFIXES = ("_metadata.json", "_timeseries.csv", "_trial_summary.csv")

# Beklenen yol tam olarak uc parca: <participant>/<session>/<dosya>
PID_RE = re.compile(r"^P\d+$")
SID_RE = re.compile(r"^S\d{8}_\d{6}$")


def _list_remote(folder_id):
    """Klasoru listele. Doner: [(file_id, "P001/S.../dosya.csv"), ...]"""
    entries = gdown.download_folder(
        id=folder_id,
        output=None,
        quiet=True,
        use_cookies=False,
        skip_download=True,
    )
    if not entries:
        return []

    out = []
    skipped = []
    for e in entries:
        rel = Path(str(e.path)).as_posix()
        parts = rel.split("/")
        # gdown yollari istenen klasore GORE veriyor. Daha derin bir yol
        # baska bir veri setinin ic ice konmus klasoru demek -- eskiden
        # sondan uc parca alindigi icin sessizce ayni veri setine
        # karisiyordu. Artik tam uc parca sart.
        ok = (
            len(parts) == 3
            and PID_RE.match(parts[0])
            and SID_RE.match(parts[1])
            and parts[2].startswith(f"{parts[0]}_{parts[1]}")
            and parts[2].endswith(WANTED_SUFFIXES)
        )
        if not ok:
            skipped.append(rel)
            continue
        out.append((e.id, "/".join(parts)))

    if skipped:
        print(f"UYARI: beklenen yapiya uymayan {len(skipped)} girdi atlandi "
              f"(ic ice klasor / baska veri seti olabilir):")
        for rel in skipped[:5]:
            print(f"  {rel}")
        if len(skipped) > 5:
            print(f"  ... ve {len(skipped) - 5} tane daha")

    return sorted(out, key=lambda x: x[1])


def sync_data(folder_id, raw_dir, force=False):
    """Drive klasorunu data/raw/ icine indirir.

    Var olan dosya tekrar indirilmez (force=True ise indirilir).
    Yerelde olup Drive'da olmayan hicbir sey silinmez.

    Doner: (indirilen, atlanan, hatali) sayilari.
    """
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    print("Drive klasoru listeleniyor...")
    try:
        remote = _list_remote(folder_id)
    except Exception as exc:
        print(f"HATA: klasor listelenemedi -> {exc}")
        print("Klasorun 'baglantiya sahip herkes' olarak paylasildigini kontrol et:")
        print(f"  https://drive.google.com/drive/folders/{folder_id}")
        return 0, 0, 0

    if not remote:
        print("Drive klasorunde beklenen dosya bulunamadi.")
        return 0, 0, 0

    print(f"{len(remote)} dosya bulundu.")

    n_new = n_skip = n_err = 0
    for file_id, rel in remote:
        dest = raw_dir / rel
        if dest.exists() and not force:
            n_skip += 1
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"  indiriliyor: {rel}")
        try:
            got = gdown.download(
                id=file_id,
                output=str(dest),
                quiet=True,
                use_cookies=False,
            )
        except Exception as exc:
            got = None
            print(f"    HATA: {exc}")

        if got is None:
            n_err += 1
            if dest.exists() and dest.stat().st_size == 0:
                dest.unlink()
        else:
            n_new += 1

    print(f"Indirilen: {n_new}  |  zaten var: {n_skip}  |  hata: {n_err}")
    return n_new, n_skip, n_err
