"""Does outdoor temperature affect fridge/freezer equipment temperature?

Loads outdoor temp (already in every cache file as `temp` column) alongside
sensor readings, aggregates to daily means, and correlates outdoor temp with:
  1. Equipment temperature (daily mean)
  2. OOR rate (fraction of readings out of range)

Outputs:
  weather_correlation_summary.png   — Spearman r per location, both metrics
  weather_scatter_<atype>.png       — small-multiples scatter per location

Usage:
    cd ~/Desktop/cogsworth
    source experiments/natalie/.venv/bin/activate
    python3 experiments/natalie/weather.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from data_loader import ZONES, t0, t1, SETPOINTS

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
DPI = 130

EXCLUDE_BUILDINGS = {"The King - Store 06"}

# ---------------------------------------------------------------------------
# Load raw cache files, extracting both sensor T and outdoor temp
# ---------------------------------------------------------------------------

print("Loading cache files with outdoor temperature...")

records = []

for zone in ZONES:
    bld_short = zone["building"].split(" - ", 1)[1] if " - " in zone["building"] else zone["building"]
    bld_key   = " - ".join(zone["building"].split(" - ")[1:])  # strip leading ID
    if any(excl in zone["building"] for excl in EXCLUDE_BUILDINGS):
        continue

    device = zone["device"]
    zid    = zone["zid"]
    fb_zid = zone.get("fallback_zid")

    files = sorted(Path.home().glob(f".cogcache/{device}Z{zid}-{t0}-{t1}.csv"))
    if not files and fb_zid:
        files = sorted(Path.home().glob(f".cogcache/{device}Z{fb_zid}-{t0}-{t1}.csv"))
    if not files:
        print(f"  No file: {device} zid={zid}")
        continue

    df = pd.read_csv(files[0])

    if "temp" not in df.columns:
        print(f"  No outdoor temp: {device} zid={zid}")
        continue

    # Find sensor temperature column (same logic as data_loader)
    atype = zone["type"]
    expected_mid = {"fridge": 36.5, "freezer": 0.0}[atype]
    candidates = [c for c in df.columns if c.endswith(".T") and ":" in c]
    valid = [c for c in candidates if df[c].notna().sum() > 100]
    if not valid:
        continue
    temp_col = min(valid, key=lambda c: abs(df[c].dropna().median() - expected_mid))

    # Convert sensor temp from raw to °F
    df["T_equip"] = (df[temp_col] * 0.005) * 9.0 / 5 + 32

    crl = SETPOINTS[atype]["crl"]
    crh = SETPOINTS[atype]["crh"]
    df["in_range"] = (df["T_equip"] >= crl) & (df["T_equip"] <= crh)
    df["oor"] = ~df["in_range"]

    df["datetime"] = pd.to_datetime(df["t"], unit="s", utc=True).dt.tz_convert("America/New_York")
    df["date"]     = df["datetime"].dt.date

    daily = (
        df.groupby("date")
        .agg(
            outdoor_temp=("temp",    "mean"),
            equip_temp  =("T_equip", "mean"),
            oor_rate    =("oor",     "mean"),
            n_readings  =("T_equip", "count"),
        )
        .reset_index()
    )
    daily = daily[daily["n_readings"] >= 20]  # drop sparse days

    daily["label"]          = bld_short
    daily["building"]       = zone["building"]
    daily["appliance_type"] = atype
    daily["zone_name"]      = zone["name"]

    records.append(daily)
    print(f"  Loaded {bld_short} ({atype}): {len(daily)} days")

all_daily = pd.concat(records, ignore_index=True)
print(f"\nTotal: {len(all_daily)} location-days across {all_daily['label'].nunique()} locations")

# ---------------------------------------------------------------------------
# Compute Spearman correlation per zone
# ---------------------------------------------------------------------------

print("\nCorrelations (outdoor temp vs equipment):")

corr_rows = []
for (label, atype), grp in all_daily.groupby(["label", "appliance_type"]):
    grp = grp.dropna(subset=["outdoor_temp", "equip_temp", "oor_rate"])
    if len(grp) < 10:
        continue

    r_temp, p_temp = spearmanr(grp["outdoor_temp"], grp["equip_temp"])
    r_oor,  p_oor  = spearmanr(grp["outdoor_temp"], grp["oor_rate"])

    sig_temp = "**" if p_temp < 0.05 else ("*" if p_temp < 0.1 else "")
    sig_oor  = "**" if p_oor  < 0.05 else ("*" if p_oor  < 0.1 else "")

    print(f"  {label:<45} [{atype}]  "
          f"vs equip_temp: r={r_temp:+.2f}{sig_temp}  "
          f"vs OOR rate: r={r_oor:+.2f}{sig_oor}  (n={len(grp)} days)")

    corr_rows.append({
        "label": label, "appliance_type": atype,
        "r_temp": r_temp, "p_temp": p_temp,
        "r_oor":  r_oor,  "p_oor":  p_oor,
        "n_days": len(grp),
        "outdoor_range": grp["outdoor_temp"].max() - grp["outdoor_temp"].min(),
    })

corr = pd.DataFrame(corr_rows)

# ---------------------------------------------------------------------------
# Chart A: Correlation summary — lollipop per location, two metrics
# ---------------------------------------------------------------------------

print("\nPlotting correlation summary...")

for atype, fname in [("fridge",  "weather_correlation_fridges.png"),
                     ("freezer", "weather_correlation_freezers.png")]:
    sub = corr[corr["appliance_type"] == atype].sort_values("r_temp")
    if sub.empty:
        continue

    n = len(sub)
    fig, axes = plt.subplots(1, 2, figsize=(14, max(5, n * 0.55 + 2.5)), dpi=DPI,
                              sharey=True)
    fig.suptitle(
        f"Outdoor Temperature Correlation: {'Fridges' if atype=='fridge' else 'Freezers'}\n"
        "Spearman r  |  ** p<0.05  * p<0.10  |  "
        "Positive = equipment warms when it's warmer outside",
        fontsize=11, fontweight="bold"
    )

    labels = sub["label"].tolist()
    y      = np.arange(n)

    for ax, col, p_col, title, color in [
        (axes[0], "r_temp", "p_temp", "vs Equipment Temperature", "#2166ac"),
        (axes[1], "r_oor",  "p_oor",  "vs OOR Rate",              "#d62728"),
    ]:
        vals = sub[col].values
        pvals = sub[p_col].values

        ax.axvline(0, color="#aaaaaa", linewidth=1, linestyle="-", zorder=1)
        ax.axvspan(-0.3, 0.3, color="#f5f5f5", alpha=0.6, zorder=0,
                   label="Weak correlation zone (|r| < 0.3)")

        for i, (val, pval) in enumerate(zip(vals, pvals)):
            dot_color = color if abs(val) >= 0.3 else "#bbbbbb"
            ax.plot([0, val], [i, i], color=dot_color, linewidth=1.2, alpha=0.7, zorder=2)
            mk = "D" if pval < 0.05 else ("s" if pval < 0.1 else "o")
            ax.scatter(val, i, color=dot_color, s=55, zorder=3, marker=mk,
                       edgecolors="white", linewidths=0.5)
            sig = "**" if pval < 0.05 else ("*" if pval < 0.1 else "")
            ax.text(val + (0.03 if val >= 0 else -0.03), i,
                    f"{val:+.2f}{sig}", va="center", fontsize=7.5,
                    ha="left" if val >= 0 else "right",
                    color="#333333" if abs(val) >= 0.3 else "#aaaaaa")

        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel("Spearman r", fontsize=8)
        ax.set_title(title, fontsize=9, fontweight="bold")
        ax.set_xlim(-1.05, 1.05)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(left=False)

    legend_elements = [
        plt.scatter([], [], color="#555555", marker="D", s=40, label="p < 0.05 (significant)"),
        plt.scatter([], [], color="#555555", marker="s", s=40, label="p < 0.10 (marginal)"),
        plt.scatter([], [], color="#555555", marker="o", s=40, label="p ≥ 0.10 (not significant)"),
        mpatches.Patch(color="#f5f5f5", label="|r| < 0.3 — weak / no relationship"),
    ]
    axes[0].legend(handles=legend_elements, fontsize=7, loc="lower left")

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")

# ---------------------------------------------------------------------------
# Chart B: Small-multiples scatter — outdoor temp vs equipment temp per location
# ---------------------------------------------------------------------------

print("Plotting scatter small-multiples...")

for atype, fname in [("fridge",  "weather_scatter_fridges.png"),
                     ("freezer", "weather_scatter_freezers.png")]:
    sub_corr  = corr[corr["appliance_type"] == atype].sort_values("r_temp", ascending=False)
    sub_daily = all_daily[all_daily["appliance_type"] == atype]

    if sub_corr.empty:
        continue

    n_locs = len(sub_corr)
    ncols  = 3
    nrows  = int(np.ceil(n_locs / ncols))

    fig, axes = plt.subplots(nrows, ncols,
                              figsize=(ncols * 4.5, nrows * 3.5 + 1), dpi=DPI)
    axes_flat = np.array(axes).flatten()

    fig.suptitle(
        f"Outdoor Temperature vs Equipment Temperature (daily means): "
        f"{'Fridges' if atype=='fridge' else 'Freezers'}\n"
        "Each dot = one day  |  sorted by strength of correlation (strongest top-left)",
        fontsize=11, fontweight="bold"
    )

    crl = SETPOINTS[atype]["crl"]
    crh = SETPOINTS[atype]["crh"]

    for i, (_, crow) in enumerate(sub_corr.iterrows()):
        ax  = axes_flat[i]
        grp = sub_daily[sub_daily["label"] == crow["label"]].dropna(
            subset=["outdoor_temp", "equip_temp"]
        )

        sig   = "**" if crow["p_temp"] < 0.05 else ("*" if crow["p_temp"] < 0.10 else "")
        color = "#2166ac" if crow["r_temp"] >= 0.3 else (
                "#d62728"  if crow["r_temp"] <= -0.3 else "#aaaaaa"
        )

        ax.scatter(grp["outdoor_temp"], grp["equip_temp"],
                   color=color, s=18, alpha=0.6, edgecolors="none")

        # Regression line
        if len(grp) >= 5:
            m, b = np.polyfit(grp["outdoor_temp"], grp["equip_temp"], 1)
            x_line = np.linspace(grp["outdoor_temp"].min(), grp["outdoor_temp"].max(), 50)
            ax.plot(x_line, m * x_line + b, color=color, linewidth=1.2, alpha=0.8)

        # Equipment operating range boundaries
        ax.axhline(crl, color="#4dac26", linewidth=0.8, linestyle="--", alpha=0.6)
        ax.axhline(crh, color="#d62728", linewidth=0.8, linestyle="--", alpha=0.6)

        ax.set_title(
            f"{crow['label']}\nr={crow['r_temp']:+.2f}{sig}  n={crow['n_days']}d",
            fontsize=7.5, fontweight="bold"
        )
        ax.set_xlabel("Outdoor temp (°F)", fontsize=7)
        ax.set_ylabel("Equipment temp (°F)", fontsize=7)
        ax.tick_params(labelsize=6.5)
        ax.spines[["top", "right"]].set_visible(False)

    # Hide unused subplots
    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")

print(f"\nOutputs saved to {OUTPUTS}")
