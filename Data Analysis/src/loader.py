"""Oturum kesfi ve veri yukleme."""

from collections import defaultdict
from pathlib import Path
import json

import pandas as pd


def discover_sessions(raw_dir):
    """raw_dir/<participant>/<session>/ yapisini tarar."""
    raw_dir = Path(raw_dir)
    sessions = []

    if not raw_dir.exists():
        return sessions

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

            sessions.append({
                "participant_id": pid,
                "session_id": sid,
                "session_dir": sid_dir,
                "has_metadata": has_meta,
                "has_timeseries": has_ts,
                "has_trial_summary": has_sum,
                "measurement_trial_count": n_measurement,
            })

    return sessions


def select_sessions(sessions):
    """Her katilimci icin en cok measurement trial iceren oturumu sec."""
    by_pid = defaultdict(list)
    for s in sessions:
        by_pid[s["participant_id"]].append(s)

    selected = []
    incomplete = []

    for pid in sorted(by_pid):
        lst = sorted(
            by_pid[pid],
            key=lambda x: x["measurement_trial_count"],
            reverse=True,
        )
        selected.append(lst[0])
        incomplete.extend(lst[1:])

    return selected, incomplete


def load_all(raw_dir):
    """Tum oturumlari yukle.

    Doner:
        df_samples   -- birlesmis timeseries
        df_trials    -- birlesmis trial summary
        metadata     -- dict, anahtar "pid/sid"
        session_report -- oturum secim bilgisi
    """
    sessions = discover_sessions(raw_dir)
    selected, incomplete = select_sessions(sessions)

    sample_frames = []
    trial_frames = []
    metadata = {}
    session_report = []

    for s in selected:
        pid = s["participant_id"]
        sid = s["session_id"]
        sdir = s["session_dir"]
        prefix = f"{pid}_{sid}"
        report = {**s, "status": "selected", "warnings": []}

        # metadata
        meta_path = sdir / f"{prefix}_metadata.json"
        if meta_path.exists():
            with open(meta_path, encoding="utf-8") as f:
                metadata[f"{pid}/{sid}"] = json.load(f)
        else:
            report["warnings"].append("metadata.json eksik")

        # timeseries
        ts_path = sdir / f"{prefix}_timeseries.csv"
        if ts_path.exists():
            sample_frames.append(pd.read_csv(ts_path))

        # trial summary
        sum_path = sdir / f"{prefix}_trial_summary.csv"
        if sum_path.exists():
            df_tr = pd.read_csv(sum_path)
            if len(df_tr) > 0:
                trial_frames.append(df_tr)
            else:
                report["warnings"].append("trial_summary bos")

        session_report.append(report)

    for s in incomplete:
        session_report.append({**s, "status": "incomplete", "warnings": []})

    if sample_frames:
        df_samples = pd.concat(sample_frames, ignore_index=True)
    else:
        df_samples = pd.DataFrame()

    if trial_frames:
        df_trials = pd.concat(trial_frames, ignore_index=True)
    else:
        df_trials = pd.DataFrame()

    return df_samples, df_trials, metadata, session_report
