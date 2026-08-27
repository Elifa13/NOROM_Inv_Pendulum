"""Oturum kesfi ve veri yukleme."""

from collections import defaultdict
from pathlib import Path
import json

import pandas as pd


def discover_sessions(raw_dir: Path) -> list[dict]:
    """raw_dir/<participant>/<session>/ yapisini tarar.

    Doner: participant_id, session_id, session_dir,
           has_metadata, has_timeseries, has_trial_summary,
           measurement_trial_count
    """
    raw_dir = Path(raw_dir)
    sessions = []

    for pid_dir in sorted(raw_dir.iterdir()):
        if not pid_dir.is_dir() or pid_dir.name.startswith("."):
            continue
        pid = pid_dir.name

        for sid_dir in sorted(pid_dir.iterdir()):
            if not sid_dir.is_dir() or sid_dir.name.startswith("."):
                continue
            sid = sid_dir.name
            prefix = f"{pid}_{sid}"

            has_meta = (sid_dir / f"{prefix}_metadata.json").exists()
            has_ts = (sid_dir / f"{prefix}_timeseries.csv").exists()
            has_sum = (sid_dir / f"{prefix}_trial_summary.csv").exists()

            n_measurement = 0
            if has_sum:
                try:
                    df = pd.read_csv(sid_dir / f"{prefix}_trial_summary.csv")
                    n_measurement = int((df["practice"] == 0).sum())
                except Exception:
                    pass

            sessions.append(
                {
                    "participant_id": pid,
                    "session_id": sid,
                    "session_dir": sid_dir,
                    "has_metadata": has_meta,
                    "has_timeseries": has_ts,
                    "has_trial_summary": has_sum,
                    "measurement_trial_count": n_measurement,
                }
            )

    return sessions


def select_sessions(
    sessions: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Her katilimci icin en cok measurement trial iceren oturumu sec.

    Doner: (selected, incomplete)
    """
    by_pid: dict[str, list[dict]] = defaultdict(list)
    for s in sessions:
        by_pid[s["participant_id"]].append(s)

    selected, incomplete = [], []
    for pid in sorted(by_pid):
        lst = sorted(
            by_pid[pid],
            key=lambda x: x["measurement_trial_count"],
            reverse=True,
        )
        selected.append(lst[0])
        incomplete.extend(lst[1:])

    return selected, incomplete


def load_metadata(
    session_dir: Path, pid: str, sid: str
) -> dict | None:
    path = session_dir / f"{pid}_{sid}_metadata.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_timeseries(
    session_dir: Path, pid: str, sid: str
) -> pd.DataFrame:
    path = session_dir / f"{pid}_{sid}_timeseries.csv"
    return pd.read_csv(path)


def load_trial_summary(
    session_dir: Path, pid: str, sid: str
) -> pd.DataFrame:
    path = session_dir / f"{pid}_{sid}_trial_summary.csv"
    return pd.read_csv(path)


def load_all(
    raw_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict], list[dict]]:
    """Tum oturumlari yukle.

    Doner:
        df_samples   -- birlesmis timeseries
        df_trials    -- birlesmis trial summary
        metadata     -- dict, anahtar "pid/sid"
        session_report -- oturum secim bilgisi
    """
    sessions = discover_sessions(raw_dir)
    selected, incomplete = select_sessions(sessions)

    sample_frames: list[pd.DataFrame] = []
    trial_frames: list[pd.DataFrame] = []
    metadata: dict[str, dict] = {}
    session_report: list[dict] = []

    for s in selected:
        pid, sid, sdir = s["participant_id"], s["session_id"], s["session_dir"]
        report: dict = {**s, "status": "selected", "warnings": []}

        meta = load_metadata(sdir, pid, sid)
        if meta is not None:
            metadata[f"{pid}/{sid}"] = meta
        else:
            report["warnings"].append("metadata.json eksik")

        if s["has_timeseries"]:
            sample_frames.append(load_timeseries(sdir, pid, sid))

        if s["has_trial_summary"]:
            df_tr = load_trial_summary(sdir, pid, sid)
            if len(df_tr) > 0:
                trial_frames.append(df_tr)
            else:
                report["warnings"].append("trial_summary bos (sadece header)")

        session_report.append(report)

    for s in incomplete:
        session_report.append({**s, "status": "incomplete", "warnings": []})

    df_samples = (
        pd.concat(sample_frames, ignore_index=True)
        if sample_frames
        else pd.DataFrame()
    )
    df_trials = (
        pd.concat(trial_frames, ignore_index=True)
        if trial_frames
        else pd.DataFrame()
    )

    return df_samples, df_trials, metadata, session_report
