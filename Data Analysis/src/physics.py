"""Cart-pole dinamigi ve T0 hesabi.

Model veriden dogrulandi, varsayilmadi: kayitli applied_force_n ile
simule edilen acisal ivme, gozlenen ivmeyle 0.989-0.997 arasi korele
(bkz. verify_model). Onemli detay, denkleme tam pole uzunlugu degil
YARIM uzunluk giriyor (duzgun cubuk, 4/3 atalet terimi).

    temp = (F + m_p * l * w**2 * sin(th)) / (m_c + m_p)
    th'' = (g * sin(th) - cos(th) * temp) / (l * (k - m_p * cos(th)**2 / (m_c + m_p)))
    x''  = temp - m_p * l * th'' * cos(th) / (m_c + m_p)

T0 = kuvvet uygulanmasaydi bu acidan fall limitine kac saniyede varilirdi.
F = 0 iken dinamik sadece (th, w) uzerinde kapali -- cart konumu ve hizi
geri beslemiyor -- yani T0 tek basina baslangic acisinin fonksiyonu.
"""

import numpy as np
import pandas as pd

try:
    from .qc import _active_segments
except ImportError:  # dogrudan calistirma
    from qc import _active_segments

DEG = np.pi / 180.0


def params_from_config(config):
    """config.yaml'dan dinamik parametrelerini cikarir."""
    ph = config["physics"]
    t0 = config.get("t0", {})
    return {
        "m_c": float(ph["cart_mass_kg"]),
        "m_p": float(ph["pole_mass_kg"]),
        "l": float(ph.get("pole_half_length_m", ph["pole_length_m"] / 2.0)),
        "g": float(ph["gravity"]),
        "k": float(ph.get("inertia_coeff", 4.0 / 3.0)),
        "angle_limit_deg": float(ph["angle_limit_deg"]),
        "track_limit_m": float(ph["track_limit_m"]),
        "dt": float(t0.get("integration_dt_s", 1.0 / 60.0)),
        "max_time_s": float(t0.get("max_time_s", 60.0)),
        "round_decimals": int(t0.get("angle_round_decimals", 4)),
    }


def cartpole_deriv(state, force, p):
    """Durum turevi. state = [theta_rad, omega_rad_s, x_m, v_m_s]."""
    th, om = state[0], state[1]
    tot = p["m_c"] + p["m_p"]
    sin_th, cos_th = np.sin(th), np.cos(th)

    temp = (force + p["m_p"] * p["l"] * om ** 2 * sin_th) / tot
    alpha = (p["g"] * sin_th - cos_th * temp) / (
        p["l"] * (p["k"] - p["m_p"] * cos_th ** 2 / tot)
    )
    accel = temp - p["m_p"] * p["l"] * alpha * cos_th / tot
    return np.array([om, alpha, state[3], accel])


def rk4_step(state, force, p, dt):
    """Tek RK4 adimi. Kuvvet adim boyunca sabit varsayilir."""
    k1 = cartpole_deriv(state, force, p)
    k2 = cartpole_deriv(state + dt / 2.0 * k1, force, p)
    k3 = cartpole_deriv(state + dt / 2.0 * k2, force, p)
    k4 = cartpole_deriv(state + dt * k3, force, p)
    return state + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def compute_T0(theta0_deg, p, omega0_deg_s=0.0):
    """Kuvvetsiz serbest dususte fall limitine varma suresi (saniye).

    Baslangic acisi zaten limitin disindaysa 0.0 doner; max_time_s icinde
    limite varilmazsa NaN doner (pratikte sadece theta0 ~ 0 icin).
    """
    if not np.isfinite(theta0_deg):
        return np.nan

    limit = p["angle_limit_deg"] * DEG
    dt = p["dt"]
    state = np.array([theta0_deg * DEG, omega0_deg_s * DEG, 0.0, 0.0])
    t = 0.0

    while t < p["max_time_s"]:
        if abs(state[0]) >= limit:
            return t
        state = rk4_step(state, 0.0, p, dt)
        t += dt

    return np.nan


def T0_for_angles(angles_deg, p):
    """Aci dizisi icin T0. Tekrar eden acilar bir kez hesaplanir.

    Kayitta ayni baslangic acisi cok kere goruldugu icin (RNG dizisi
    ortak) cache buyuk fark yaratir.
    """
    ser = pd.Series(angles_deg, dtype=float)
    key = ser.round(p["round_decimals"])
    lut = {v: compute_T0(v, p) for v in key.dropna().unique()}
    return key.map(lut)


def verify_model(df_samples, p, min_len=300, max_segments=8):
    """Modeli kayitli veriye karsi dogrular.

    Kesintisiz active parcalarda, kayitli applied_force_n ile hesaplanan
    acisal ivmeyi kayitli acisal hizin sayisal turevi ile karsilastirir.

    Doner: DataFrame (participant_id, trial_id, n, corr_alpha, rms_alpha)
    """
    if df_samples.empty:
        return pd.DataFrame()

    rows = []
    for (pid, tid), g in df_samples.groupby(["participant_id", "trial_id"]):
        if len(rows) >= max_segments:
            break
        g = g.sort_values("sample_index")
        for seg in _active_segments(g):
            if len(seg) < min_len:
                continue
            dt = float(seg["fixed_delta_time_s"].iloc[0])
            th = seg["pole_angle_deg"].values * DEG
            om = seg["pole_angular_velocity_deg_s"].values * DEG
            force = seg["applied_force_n"].values

            tot = p["m_c"] + p["m_p"]
            temp = (force + p["m_p"] * p["l"] * om ** 2 * np.sin(th)) / tot
            alpha = (p["g"] * np.sin(th) - np.cos(th) * temp) / (
                p["l"] * (p["k"] - p["m_p"] * np.cos(th) ** 2 / tot)
            )
            observed = np.gradient(om, dt)

            # kenarlarda tek yonlu fark var, atilir
            a, b = observed[3:-3], alpha[3:-3]
            if len(a) < 10:
                continue
            rows.append({
                "participant_id": pid,
                "trial_id": tid,
                "n": len(a),
                "corr_alpha": round(float(np.corrcoef(a, b)[0, 1]), 4),
                "rms_alpha": round(float(np.sqrt(np.mean((a - b) ** 2))), 4),
            })
            break

    return pd.DataFrame(rows)
