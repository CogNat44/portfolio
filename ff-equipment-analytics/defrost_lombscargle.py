"""Defrost detection — Method 2: Lomb-Scargle Periodogram

WHAT THIS METHOD DOES
---------------------
A periodogram answers the question: "Is there a frequency hidden in this
data that explains more variance than chance?"

The classic approach is a Fourier transform (FFT), but FFT requires evenly
spaced data. Our OOR events are unevenly spaced in time — so we use the
Lomb-Scargle periodogram, which was designed for exactly this.

HOW IT WORKS
------------
We feed the raw equipment temperature time series directly into Lomb-Scargle.
The algorithm fits sine waves of varying frequency to the temperature values
and returns a power score at each frequency. High power at 1/6h means the
temperature signal repeats (rises and falls) every 6 hours.

LombScargle removes the mean automatically so the DC offset (the baseline
temperature) doesn't dominate. What remains is the periodic structure —
the rhythmic rise-and-fall signature of a defrost cycle.

The false alarm probability (FAP) tells us how likely that power level is
to appear by chance in random data. FAP < 0.01 → significant. In practice
with months of dense data the FAP is always near zero — the periodogram
shape (where the peak falls) matters more than the FAP value.

THE DIFFERENCE FROM PHASE COHERENCE (Method 1)
-----------------------------------------------
Phase coherence looks at discrete event times (temperature peaks above the
operating range). Lomb-Scargle uses the entire continuous temperature record —
it sees the full rhythm of warming and cooling across the whole time window.

In practice:
- Phase coherence is better when events are sparse or short
- Lomb-Scargle is better when events are regular and the signal is dense
- Together they give two independent lines of evidence

EXCLUSIONS
----------
Same as Method 1 — noisy locations removed from analysis:
  - The King - Store 06
  - The King - Store 10 fridge
  - Shwarma Store 01 freezer

Usage:
    cd ff-equipment-analytics
    source .venv/bin/activate
    defrost_lombscargle.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from astropy.timeseries import LombScargle
from data_loader import load

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
DPI = 130

EXCLUDE_BUILDINGS = {"The King - Store 06"}
EXCLUDE_BLDG_ATYPE = {
    ("The King - Store 10", "fridge"),
    ("Shwarma - Store 01", "freezer"),
}

# Frequency grid: periods 2h–12h, in cycles-per-hour
FREQ_MIN = 1 / 12   # one cycle per 12 hours
FREQ_MAX = 1 / 2    # one cycle per 2 hours
N_FREQS  = 2000

FAP_THRESHOLD = 0.01   # false alarm probability — below this = significant
PERIOD_LABELS = {"4h": 240, "5h": 300, "6h": 360, "7h": 420, "8h": 480}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

print("Loading data...")
df = load()
df = df[~df["building"].isin(EXCLUDE_BUILDINGS)]
df["datetime"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_convert("America/New_York")
df["label"]    = df["building"].str.replace(r"^\d+ - ", "", regex=True)

# ---------------------------------------------------------------------------
# Run Lomb-Scargle per zone
# ---------------------------------------------------------------------------

freqs     = np.linspace(FREQ_MIN, FREQ_MAX, N_FREQS)
periods_h = 1 / freqs

print("\nLomb-Scargle results:")
print(f"  (FAP < {FAP_THRESHOLD} = statistically significant periodic signal)\n")
print(f"{'Zone':<50} {'type':<8}  {'best period':>12}  {'FAP':>10}  {'sig?':>6}")
print("-" * 95)

ls_results = []

for (zone, atype), grp in df.groupby(["zone_name", "appliance_type"]):
    bld = grp["building"].iloc[0]
    lbl = grp["label"].iloc[0]
    if (bld, atype) in EXCLUDE_BLDG_ATYPE:
        continue

    grp = grp.sort_values("datetime").reset_index(drop=True)

    if len(grp) < 100:
        continue

    # Time axis in hours from start of record
    t_hours = (grp["datetime"] - grp["datetime"].iloc[0]).dt.total_seconds().values / 3600

    # Lomb-Scargle on raw temperature (fit_mean=True by default removes DC offset)
    ls = LombScargle(t_hours, grp["T"].values, normalization="standard")
    power = ls.power(freqs)

    best_idx    = int(np.argmax(power))
    best_period = periods_h[best_idx]
    best_power  = float(power[best_idx])
    fap         = float(ls.false_alarm_probability(best_power))
    significant = fap < FAP_THRESHOLD

    marker = " ✓ DEFROST" if significant else ""
    print(f"  {lbl:<48} {atype:<8}  {best_period:>10.1f}h  {fap:>10.4f}  {'YES' if significant else 'no':>6}{marker}")

    ls_results.append({
        "label": lbl, "building": bld, "appliance_type": atype,
        "zone_name": zone,
        "best_period_h": best_period,
        "best_power": best_power,
        "fap": fap,
        "significant": significant,
        "freqs": freqs,
        "power": power,
        "t_hours": t_hours,
        "signal": grp["T"].values,
        "n_readings": len(grp),
    })

res_df = pd.DataFrame([{k: v for k, v in r.items()
                        if k not in ("freqs", "power", "t_hours", "signal")}
                       for r in ls_results])

# ---------------------------------------------------------------------------
# Chart 1: Periodogram plots — one per zone, small multiples
# ---------------------------------------------------------------------------

print("\nPlotting periodograms...")

for atype, fname in [("fridge",  "defrost_ls_periodogram_fridges.png"),
                     ("freezer", "defrost_ls_periodogram_freezers.png")]:
    sub_res = [r for r in ls_results if r["appliance_type"] == atype]
    if not sub_res:
        continue

    # Sort: significant first, then by FAP
    sub_res = sorted(sub_res, key=lambda r: (not r["significant"], r["fap"]))

    n     = len(sub_res)
    ncols = 3
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(nrows, ncols,
                              figsize=(ncols * 5, nrows * 3 + 1.5), dpi=DPI)
    axes_flat = np.array(axes).flatten()

    fig.suptitle(
        f"Lomb-Scargle Periodograms — {'Fridges' if atype=='fridge' else 'Freezers'}\n"
        "X-axis = period in hours  |  Y-axis = spectral power  |  "
        "Peak at a given period = signal repeats at that interval\n"
        f"Green shading = defrost-plausible range (4–8h)  |  "
        f"Dashed line = FAP={FAP_THRESHOLD} significance threshold",
        fontsize=10, fontweight="bold"
    )

    for i, r in enumerate(sub_res):
        ax = axes_flat[i]

        # Convert frequency to period for plotting
        plot_periods = 1 / r["freqs"]
        plot_power   = r["power"]

        # Shade the defrost-plausible period band
        ax.axvspan(4, 8, color="#d5f5d5", alpha=0.45, zorder=0, label="Defrost range (4–8h)")

        ax.plot(plot_periods, plot_power,
                color="#2166ac" if r["significant"] else "#aaaaaa",
                linewidth=0.9, zorder=2)

        # FAP threshold line
        fap_level = float(LombScargle(r["t_hours"], r["signal"],
                                       normalization="standard")
                           .false_alarm_level(FAP_THRESHOLD))
        ax.axhline(fap_level, color="#d62728", linewidth=0.8, linestyle="--",
                   alpha=0.8, label=f"FAP={FAP_THRESHOLD} threshold")

        # Mark the peak
        best_idx = int(np.argmax(plot_power))
        ax.scatter(plot_periods[best_idx], plot_power[best_idx],
                   color="#d62728" if r["significant"] else "#888888",
                   s=50, zorder=4, marker="v")
        ax.text(plot_periods[best_idx], plot_power[best_idx],
                f" {plot_periods[best_idx]:.1f}h",
                fontsize=7, va="bottom", color="#333333")

        # Reference lines at common defrost periods
        for ph in [4, 6, 8]:
            ax.axvline(ph, color="#bbbbbb", linewidth=0.6, linestyle=":", alpha=0.7)

        sig_label = f"FAP={r['fap']:.4f} ✓" if r["significant"] else f"FAP={r['fap']:.3f}"
        ax.set_title(
            f"{r['label']}\n{sig_label}  peak={r['best_period_h']:.1f}h",
            fontsize=7.5, fontweight="bold" if r["significant"] else "normal"
        )
        ax.set_xlabel("Period (hours)", fontsize=7)
        ax.set_ylabel("Power", fontsize=7)
        ax.set_xlim(2, 12)
        ax.tick_params(labelsize=6.5)
        ax.spines[["top", "right"]].set_visible(False)

        if i == 0:
            ax.legend(fontsize=6, loc="upper right")

    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")

# ---------------------------------------------------------------------------
# Chart 2: Summary — FAP and best period per zone
# ---------------------------------------------------------------------------

print("Plotting summary chart...")

for atype, fname in [("fridge",  "defrost_ls_summary_fridges.png"),
                     ("freezer", "defrost_ls_summary_freezers.png")]:
    sub = res_df[res_df["appliance_type"] == atype].sort_values("fap")
    if sub.empty:
        continue

    n = len(sub)
    fig, axes = plt.subplots(1, 2, figsize=(13, max(4, n * 0.55 + 2.5)),
                              dpi=DPI, sharey=True)
    fig.suptitle(
        f"Lomb-Scargle Summary — {'Fridges' if atype=='fridge' else 'Freezers'}\n"
        f"Left: false alarm probability (lower = more significant)  |  "
        f"Right: period of strongest signal",
        fontsize=11, fontweight="bold"
    )

    labels = sub["label"].tolist()
    y      = np.arange(n)

    # Left: FAP (log scale)
    ax = axes[0]
    faps   = sub["fap"].values
    colors = ["#2166ac" if s else "#aaaaaa" for s in sub["significant"]]
    ax.axvline(FAP_THRESHOLD, color="#d62728", linewidth=1.2, linestyle="--",
               label=f"Significance threshold (FAP={FAP_THRESHOLD})")
    for i, (fap, col) in enumerate(zip(faps, colors)):
        ax.plot([0, fap], [i, i], color=col, linewidth=1.2, alpha=0.7)
        ax.scatter(fap, i, color=col, s=55, zorder=3, edgecolors="white", linewidths=0.5)
    ax.set_xscale("log")
    ax.set_xlabel("False alarm probability (log scale)", fontsize=8)
    ax.set_title("Significance", fontsize=9, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.legend(fontsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(left=False)

    # Right: best period
    ax = axes[1]
    periods = sub["best_period_h"].values
    ax.axvspan(4, 8, color="#d5f5d5", alpha=0.5, label="Defrost range (4–8h)")
    for ph in [4, 6, 8]:
        ax.axvline(ph, color="#bbbbbb", linewidth=0.7, linestyle=":", alpha=0.8)
    for i, (period, col, sig) in enumerate(zip(periods, colors, sub["significant"])):
        ax.plot([0, period], [i, i], color=col, linewidth=1.2, alpha=0.7)
        mk = "D" if sig else "o"
        ax.scatter(period, i, color=col, s=55, zorder=3, marker=mk,
                   edgecolors="white", linewidths=0.5)
        ax.text(period + 0.1, i, f"{period:.1f}h", va="center", fontsize=7.5,
                color="#333333" if sig else "#aaaaaa")
    ax.set_xlabel("Best period (hours)", fontsize=8)
    ax.set_title("Period of strongest signal", fontsize=9, fontweight="bold")
    ax.set_xlim(0, 13)
    ax.legend(fontsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(left=False)

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")

print(f"\nOutputs saved to {OUTPUTS}")
print("\nKey:")
print(f"  FAP < {FAP_THRESHOLD}  → statistically significant periodic signal")
print(f"  Best period in 4–8h range + significant FAP → defrost cycle candidate")
