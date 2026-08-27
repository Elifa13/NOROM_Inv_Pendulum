"""Google Drive'dan veri cekme.

Drive klasoru link ile herkese acik oldugu icin kimlik dogrulama yok:
API anahtari, OAuth, client_secrets.json gerekmiyor. gdown klasoru
listeler, biz sadece bekledigimiz dosyalari indiririz.

Beklenen uzak yapi:
    <folder_id>/<participant_id>/<session_id>/<pid>_<sid>_metadata.json
                                             /<pid>_<sid>_timeseries.csv
                                             /<pid>_<sid>_trial_summary.csv
"""

from pathlib import Path

import gdown

WANTED_SUFFIXES = ("_metadata.json", "_timeseries.csv", "_trial_summary.csv")


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
    for e in entries:
        rel = Path(str(e.path)).as_posix()
        # gdown yolun basina kok klasor adini koyabilir; parcalara ayirip
        # sondan uc seviyeyi (participant/session/dosya) aliriz.
        parts = rel.split("/")
        if len(parts) < 3:
            continue
        parts = parts[-3:]
        if not parts[2].endswith(WANTED_SUFFIXES):
            continue
        out.append((e.id, "/".join(parts)))

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
