"""Veri seti secimi ve path cozumleme.

Iki bagimsiz veri seti var (config.yaml -> datasets):

    pilot1  12 katilimci, noise sigma 0 / .02 / .05 / .08 / .25
    pilot2   9 katilimci, noise sigma 0 / .005 / .010 / .015 / .020

Katilimci id'leri iki sette de P001... diye gidiyor ama AYNI KISILER
DEGIL, koşul etiketleri de (N1..N4) ayni ama AYNI SIGMA DEGIL. Setler
hicbir asamada birlestirilmez; ayrim klasor duzeyinde:

    data/<dataset>/raw|interim|processed

load_config, aktif setin yollarini config["paths"] icine yazar; boylece
notebook'larin geri kalani (config["paths"]["interim_dir"] vs.) tek satir
degismeden calisir.
"""

from pathlib import Path

import yaml

MARKER = ".dataset"


def find_root(start=None):
    """config.yaml'i barindiran 'Data Analysis' kokunu yukari dogru arar."""
    p = Path(start or Path.cwd()).resolve()
    for cand in [p, *p.parents]:
        if (cand / "config.yaml").exists():
            return cand
    raise FileNotFoundError(f"config.yaml bulunamadi (baslangic: {p})")


def load_config(dataset=None, root=None):
    """Config'i yukle, aktif veri setinin yollarini yerlestir.

    Doner: (config, root). config["paths"] icinde raw_dir / interim_dir /
    processed_dir aktif sete gore doludur, config["drive"]["folder_id"] de
    oyle. config["dataset"] aktif setin adini tasir.
    """
    root = Path(root).resolve() if root else find_root()
    with open(root / "config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    name = dataset or config.get("dataset")
    if name not in config.get("datasets", {}):
        raise KeyError(
            f"bilinmeyen veri seti {name!r}; "
            f"tanimlilar: {sorted(config.get('datasets', {}))}"
        )
    ds = config["datasets"][name]

    config["dataset"] = name
    config["dataset_label"] = ds.get("label", name)
    config["paths"] = {
        "raw_dir": ds["raw_dir"],
        "interim_dir": ds["interim_dir"],
        "processed_dir": ds["processed_dir"],
    }
    config["drive"] = {"folder_id": ds["drive_folder_id"]}
    if "presentation" in config:
        config["presentation"]["raw_dir_for_check"] = ds["raw_dir"]
        config["presentation"]["figure_dir"] = ds["processed_dir"] + "/sunum"
    return config, root


def dirs(config, root, create=True):
    """(RAW_DIR, INTERIM_DIR, PROCESSED_DIR) mutlak Path.

    Ayrica interim klasorune bir .dataset damgasi yazar. Damga baska bir
    setin adini tasiyorsa hata verir -- yanlis notebook'u yanlis klasore
    yazmaya calismanin tek gercek riski bu.
    """
    root = Path(root)
    raw = root / config["paths"]["raw_dir"]
    interim = root / config["paths"]["interim_dir"]
    processed = root / config["paths"]["processed_dir"]
    if create:
        for d in (raw, interim, processed):
            d.mkdir(parents=True, exist_ok=True)
        stamp(interim, config["dataset"])
    return raw, interim, processed


def stamp(interim_dir, name):
    """Klasorun hangi veri setine ait oldugunu damgala / dogrula."""
    f = Path(interim_dir) / MARKER
    if f.exists():
        found = f.read_text(encoding="utf-8").strip()
        if found != name:
            raise RuntimeError(
                f"veri seti karismasi: {interim_dir} klasoru {found!r} setine ait, "
                f"aktif set {name!r}. Notebook'un DATASET degiskenini kontrol et."
            )
    else:
        f.write_text(name + "\n", encoding="utf-8")
    return f
