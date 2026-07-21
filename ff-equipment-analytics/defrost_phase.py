"""Defrost detection — Method 1: Phase Coherence (Mean Resultant Length)

WHAT THIS METHOD DOES
---------------------
Imagine a clock face. For a given candidate period (say 6 hours), we map
every defrost peak time onto this clock:

    angle = 2π × (minutes_since_reference mod period) / period

If defrost runs every 6 hours, all peaks land at the same position on a
6-hour clock — they "point" in the same direction. The Mean Resultant
Length (R) measures how tightly the arrows cluster:

    R = |mean( e^{i·θ} )|   where θ is each event's angle

    R = 1.0  → all events at exactly the same clock position (perfect cycle)
    R = 0.0  → events scattered uniformly around the clock (no periodicity)

We test candidate periods of 4h, 5h, 6h, 7h, 8h — the realistic range for
commercial refrigeration defrost timers.

WHY THIS IS BETTER THAN GAP CV
-------------------------------
CV of gaps breaks when:
  - A defrost cycle is missed (no OOR event recorded)
  - Events from door openings mix in

Phase coherence handles these because it only cares about *when* peaks
happen, not the spacing between consecutive pairs. A missed cycle shifts
nothing on the clock face — the other peaks still cluster tightly.

HOW PEAKS ARE FOUND
-------------------
scipy.signal.find_peaks on the raw temperature series:
  height = operating range high  → only spikes that clear the upper limit
  prominence ≥ 2°F               → genuine spike, not boundary noise
  distance ≥ 30 readings (60 min)→ at most one peak counted per defrost event

EXCLUSIONS
----------
Noisy locations removed from analysis (still shown in output for reference):
  - The King - Store 06          (escalation outlier)
  - The King - Store 10 fridge (threshold miscalibration, ~103 crossings/day)
  - Shwarma Store 01 freezer       (chronically broken, running 21°F above setpoint)

Usage:
    cd ~/Desktop/cogsworth
    source experiments/natalie/.venv/bin/activate
    python3 experiments/natalie/defrost_phase.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
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

# Candidate defrost periods to test (in minutes)
CANDIDATE_PERIODS_MIN = [240, 300, 360, 420, 480]   # 4h, 5h, 6h, 7h, 8h
PERIOD_LABELS         = ["4h", "5h", "6h", "7h", "8h"]

# Threshold: R ≥ this → strong periodicity signal
R_THRESHOLD = 0.45

# find_peaks parameters for defrost peak detection
# height=crh   → only peaks above operating range high
# prominence=2 → peak must rise ≥2°F above its surrounding base (filters boundary noise)
# distance=30  → peaks at least 60 min apart (30 readings × 2 min) — one peak per event
PEAK_PROMINENCE = 2.0
PEAK_DISTANCE   = 30

# ---------------------------------------------------------------------------
# Load data and build OOR event table
# ---------------------------------------------------------------------------

print("Loading data...")
df = load()
df = df[~df["building"].isin(EXCLUDE_BUILDINGS)]
df["datetime"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_convert("America/New_York")
df["label"]    = df["building"].str.replace(r"^\d+ - ", "", regex=True)

print("Finding temperature peaks above operating range...")
rows = []
for (zone, atype), grp in df.groupby(["zone_name", "appliance_type"]):
    bld  = grp["building"].iloc[0]
    lbl  = grp["label"].iloc[0]
    if (bld, atype) in EXCLUDE_BLDG_ATYPE:
        continue
    crh  = grp["op_range_high"].iloc[0]
    grp  = grp.sort_values("datetime").reset_index(drop=True)

    peak_idxs, _ = find_peaks(
        grp["T"].values,
        height=crh,
        prominence=PEAK_PROMINENCE,
        distance=PEAK_DISTANCE,
    )
    for idx in peak_idxs:
        rows.append({
            "label": lbl, "building": bld, "appliance_type": atype,
            "start": grp.loc[idx, "datetime"],
        })

candidates = pd.DataFrame(rows)

print(f"Temperature peak events: {len(candidates):,} across "
      f"{candidates.groupby(['label','appliance_type']).ngroups} zones")

# ---------------------------------------------------------------------------
# Compute Mean Resultant Length for each zone × candidate period
# ---------------------------------------------------------------------------

def mean_resultant_length(timestamps_minutes: np.ndarray, period_minutes: float) -> float:
    """
    Project each timestamp onto a unit circle for the given period,
    then return the length of the mean vector.

    timestamps_minutes : minutes since some reference (e.g. midnight Jan 1)
    period_minutes     : the cycle period to test

    Returns R ∈ [0, 1].  Higher = more periodic at this period.
    """
    angles = 2 * np.pi * (timestamps_minutes % period_minutes) / period_minutes
    # Complex unit vectors, one per event
    vectors = np.exp(1j * angles)
    R = float(np.abs(vectors.mean()))
    return R


print("\nPhase coherence R scores (higher = more periodic):")
print(f"{'Zone':<50} {'type':<8}", end="")
for pl in PERIOD_LABELS:
    print(f"  {pl:>5}", end="")
print(f"  {'best':>5}  {'R':>5}  {'n':>5}")
print("-" * 100)

results = []
ref_time = pd.Timestamp("2025-11-01", tz="America/New_York")

for (lbl, atype), grp in candidates.groupby(["label", "appliance_type"]):
    if len(grp) < 15:
        continue

    t_mins = ((grp["start"] - ref_time).dt.total_seconds() / 60).values

    r_scores = [mean_resultant_length(t_mins, p) for p in CANDIDATE_PERIODS_MIN]
    best_idx = int(np.argmax(r_scores))
    best_R   = r_scores[best_idx]
    best_P   = PERIOD_LABELS[best_idx]

    marker = " ✓ DEFROST" if best_R >= R_THRESHOLD else ""
    score_str = "  ".join(f"{r:.2f}" for r in r_scores)
    print(f"  {lbl:<48} {atype:<8}  {score_str}  {best_P:>5}  {best_R:.2f}  {len(grp):>5}{marker}")

    results.append({
        "label": lbl, "appliance_type": atype, "n": len(grp),
        "best_period": best_P, "best_period_mins": CANDIDATE_PERIODS_MIN[best_idx],
        "best_R": best_R,
        **{f"R_{pl}": r for pl, r in zip(PERIOD_LABELS, r_scores)},
    })

res = pd.DataFrame(results)

# ---------------------------------------------------------------------------
# Chart 1: Heatmap of R scores — zones × periods
# ---------------------------------------------------------------------------

print("\nPlotting heatmap...")

for atype, fname in [("fridge",  "defrost_phase_heatmap_fridges.png"),
                     ("freezer", "defrost_phase_heatmap_freezers.png")]:
    sub = res[res["appliance_type"] == atype].copy()
    if sub.empty:
        continue

    sub = sub.sort_values("best_R", ascending=False)
    labels  = sub["label"].tolist()
    r_matrix = sub[[f"R_{pl}" for pl in PERIOD_LABELS]].values   # shape (n_zones, n_periods)

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.6 + 2)), dpi=DPI)
    fig.suptitle(
        f"Phase Coherence (R) — {'Fridges' if atype=='fridge' else 'Freezers'}\n"
        "Each cell = how tightly events cluster at that period  |  "
        f"R ≥ {R_THRESHOLD} (green outline) = likely defrost cycle detected",
        fontsize=11, fontweight="bold"
    )

    im = ax.imshow(r_matrix, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1)

    # Annotate cells
    for row_i, lbl in enumerate(labels):
        for col_j, pl in enumerate(PERIOD_LABELS):
            r_val = r_matrix[row_i, col_j]
            ax.text(col_j, row_i, f"{r_val:.2f}",
                    ha="center", va="center", fontsize=8,
                    color="white" if r_val > 0.6 else "black",
                    fontweight="bold" if r_val >= R_THRESHOLD else "normal")
            if r_val >= R_THRESHOLD:
                ax.add_patch(mpatches.FancyBboxPatch(
                    (col_j - 0.48, row_i - 0.48), 0.96, 0.96,
                    boxstyle="round,pad=0.02",
                    linewidth=2, edgecolor="#2ca25f", fill=False, zorder=3
                ))

    ax.set_xticks(range(len(PERIOD_LABELS)))
    ax.set_xticklabels(PERIOD_LABELS, fontsize=9)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Candidate defrost period", fontsize=9)

    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="R (0=random · 1=perfectly periodic)")
    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")

# ---------------------------------------------------------------------------
# Chart 2: Clock-face polar plots for the top confirmed zones
# ---------------------------------------------------------------------------

print("Plotting clock-face polar plots...")

confirmed = res[res["best_R"] >= R_THRESHOLD].sort_values("best_R", ascending=False)

if confirmed.empty:
    print("  No zones above R threshold — lowering to top-3 per appliance type for illustration")
    confirmed = (
        res.sort_values("best_R", ascending=False)
        .groupby("appliance_type").head(3)
    )

for atype, fname in [("fridge",  "defrost_phase_clocks_fridges.png"),
                     ("freezer", "defrost_phase_clocks_freezers.png")]:
    sub_conf = confirmed[confirmed["appliance_type"] == atype]
    sub_cand = candidates[candidates["appliance_type"] == atype]
    if sub_conf.empty:
        continue

    n = len(sub_conf)
    ncols = min(3, n)
    nrows = int(np.ceil(n / ncols))

    fig = plt.figure(figsize=(ncols * 4, nrows * 4 + 1.5), dpi=DPI)
    fig.suptitle(
        f"Clock-Face View: Event Timing on Best-Fit Defrost Period\n"
        f"{'Fridges' if atype=='fridge' else 'Freezers'}  |  "
        "Each spike = one OOR event projected onto the cycle clock\n"
        "Tight cluster at one position = strong periodic signal",
        fontsize=11, fontweight="bold"
    )

    for i, (_, row) in enumerate(sub_conf.iterrows()):
        ax = fig.add_subplot(nrows, ncols, i + 1, projection="polar")

        grp    = sub_cand[sub_cand["label"] == row["label"]]
        t_mins = ((grp["start"] - ref_time).dt.total_seconds() / 60).values
        period = row["best_period_mins"]
        angles = 2 * np.pi * (t_mins % period) / period

        # Histogram on polar axis
        bins   = np.linspace(0, 2 * np.pi, 49)
        counts, _ = np.histogram(angles, bins=bins)
        bin_centres = (bins[:-1] + bins[1:]) / 2
        width  = bins[1] - bins[0]

        bars = ax.bar(bin_centres, counts, width=width * 0.9,
                      color="#d62728", alpha=0.75, edgecolor="white", linewidth=0.3)

        # Mean vector arrow
        vectors    = np.exp(1j * angles)
        mean_vec   = vectors.mean()
        mean_angle = float(np.angle(mean_vec))
        R          = float(np.abs(mean_vec))
        ax.annotate("", xy=(mean_angle, R * counts.max()),
                    xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color="#333333", lw=2))

        # Clock labels: 12, 3, 6, 9 positions
        period_h = period / 60
        for frac, label in [(0, "0h"), (0.25, f"{period_h/4:.0f}h"),
                             (0.5, f"{period_h/2:.0f}h"), (0.75, f"{3*period_h/4:.0f}h")]:
            ax.text(2 * np.pi * frac, counts.max() * 1.25,
                    label, ha="center", va="center", fontsize=7, color="#555555")

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(
            f"{row['label']}\n"
            f"Period={row['best_period']}  R={row['best_R']:.2f}  n={row['n']}",
            fontsize=8, fontweight="bold", pad=12
        )
        ax.set_facecolor("#fafafa")

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")

print(f"\nOutputs saved to {OUTPUTS}")
print("\nKey: R = Mean Resultant Length")
print("  R < 0.30  → no periodicity (random timing)")
print("  R 0.30–0.44 → weak signal")
print(f"  R ≥ {R_THRESHOLD}   → strong signal — likely defrost cycle")
