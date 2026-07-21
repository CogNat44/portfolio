"""Fleet health narrative — six charts that build a story.

Charts (one PNG each):
  1. story_1_operating_temp.png       — where each location typically runs
  2. story_2_variability.png          — how stable / variable each location is
  3. story_3_short_oor_rate.png       — how often short OOR events (<30 min) happen
  4. story_4_oor_breakdown.png        — OOR severity breakdown per location
  5. story_5_extended_timing.png      — when longer OOR events occur
  6. story_6_operating_position.png   — where each location sits inside its own range

Fleet benchmarks (median + IQR) are computed excluding the two anomalous locations:
  - The King Store 06   (escalation outlier)
  - The King Store 10 fridge  (threshold miscalibration — runs at boundary)
Both are still shown in every chart so you can see how far from normal they sit.

Usage:
    cd ~/Desktop/cogsworth
    source experiments/natalie/.venv/bin/activate
    python3 experiments/natalie/story.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import gaussian_kde
from data_loader import load

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
DPI = 130

# ---------------------------------------------------------------------------
# Locations excluded from fleet benchmark calculations (still shown in charts)
# Format: (building_column_value, appliance_type or None=all)
# ---------------------------------------------------------------------------
STAT_EXCLUDE = {
    ("The King - Store 06", None),              # all types — escalation outlier
    ("The King - Store 10", "fridge"),            # fridge only — threshold miscalibration
    ("Shwarma - Store 01", "freezer"),  # freezer only — chronically broken, 21°F above setpoint
}

OUTLIER_COLOR  = "#888888"   # grey — shown but flagged as excluded from stats
NORMAL_COLOR   = "#2166ac"   # blue — within fleet normal band
ABOVE_COLOR    = "#d62728"   # red — above normal band
BELOW_COLOR    = "#4dac26"   # green — below normal band (cold, generally good)
MEDIAN_COLOR   = "#333333"
BAND_COLOR     = "#ccddee"
FLAG_MARKER    = "D"         # diamond for stat-excluded locations

FRIDGE_COLOR  = "#4393c3"
FREEZER_COLOR = "#762a83"


def _is_excluded(building: str, atype: str) -> bool:
    return (building, None) in STAT_EXCLUDE or (building, atype) in STAT_EXCLUDE


# ---------------------------------------------------------------------------
# Load data — full fleet (no building-level exclusion; exclusion is stat-only)
# ---------------------------------------------------------------------------

print("Loading data...")
df = load()
df["datetime"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_convert("America/New_York")
df["label"] = df["building"].str.replace(r"^\d+ - ", "", regex=True)

# ---------------------------------------------------------------------------
# Build event table
# ---------------------------------------------------------------------------

print("Building event table...")

rows = []
for (zone, atype), grp in df.groupby(["zone_name", "appliance_type"]):
    grp = grp.sort_values("datetime").reset_index(drop=True)
    bld = grp["building"].iloc[0]
    lbl = grp["label"].iloc[0]
    oor = ~grp["in_range"]
    run_id = (oor != oor.shift()).cumsum()
    for rid in run_id[oor].unique():
        mask = oor & (run_id == rid)
        idx  = grp.index[mask].tolist()
        dur  = len(idx) * 2
        rows.append({
            "building":      bld,
            "label":         lbl,
            "appliance_type": atype,
            "start":         grp.loc[idx[0], "datetime"],
            "duration_mins": dur,
            "hour":          grp.loc[idx[0], "datetime"].hour,
        })

ev = pd.DataFrame(rows)
ev["bucket"] = pd.cut(
    ev["duration_mins"],
    bins=[0, 30, 90, float("inf")],
    labels=["≤30 min", "31–89 min", "≥90 min"],
    right=True,
)
ev["excluded"] = ev.apply(lambda r: _is_excluded(r["building"], r["appliance_type"]), axis=1)

# ---------------------------------------------------------------------------
# Per-location summary table
# ---------------------------------------------------------------------------

print("Computing per-location summaries...")

loc_rows = []
for (bld, atype), grp_df in df.groupby(["building", "appliance_type"]):
    lbl = grp_df["label"].iloc[0]
    excluded = _is_excluded(bld, atype)
    T = grp_df["T"].dropna()
    orl = grp_df["op_range_low"].iloc[0]
    orh = grp_df["op_range_high"].iloc[0]
    span_days = max(1, (grp_df["datetime"].max() - grp_df["datetime"].min()).total_seconds() / 86400)

    ev_loc = ev[(ev["building"] == bld) & (ev["appliance_type"] == atype)]
    short = ev_loc[ev_loc["duration_mins"] <= 30]
    mid   = ev_loc[(ev_loc["duration_mins"] > 30) & (ev_loc["duration_mins"] < 90)]
    long_ = ev_loc[ev_loc["duration_mins"] >= 90]

    loc_rows.append({
        "building":       bld,
        "label":          lbl,
        "appliance_type": atype,
        "excluded":       excluded,
        "span_days":      span_days,
        "median_T":       float(T.median()),
        "T_p25":          float(T.quantile(0.25)),
        "T_p75":          float(T.quantile(0.75)),
        "T_iqr":          float(T.quantile(0.75) - T.quantile(0.25)),
        "op_range_low":   orl,
        "op_range_high":  orh,
        "op_range_mid":   (orl + orh) / 2,
        "op_range_span":  orh - orl,
        # position within range: 0=low boundary, 1=high boundary
        "range_position": (float(T.median()) - orl) / max(0.1, orh - orl),
        "n_short":        len(short),
        "n_mid":          len(mid),
        "n_long":         len(long_),
        "n_total_oor":    len(ev_loc),
        "short_per_day":  len(short) / span_days,
        "mid_per_day":    len(mid)   / span_days,
        "long_per_day":   len(long_) / span_days,
    })

loc = pd.DataFrame(loc_rows)
loc_clean = loc[~loc["excluded"]]   # for fleet stats only


# ---------------------------------------------------------------------------
# Helper: fleet benchmarks (median + IQR) from clean locations
# ---------------------------------------------------------------------------

def fleet_stats(series: pd.Series) -> dict:
    return {
        "median": series.median(),
        "p25":    series.quantile(0.25),
        "p75":    series.quantile(0.75),
        "mean":   series.mean(),
    }


# ---------------------------------------------------------------------------
# Shared lollipop helper
# ---------------------------------------------------------------------------

def lollipop(
    ax, labels, values, colors,
    markers=None, median_val=None, p25=None, p75=None,
    xlabel="", title="", excluded_label_color=OUTLIER_COLOR,
    vline_label="Fleet median (excl. outliers)"
):
    y = np.arange(len(labels))
    if p25 is not None and p75 is not None:
        ax.axvspan(p25, p75, color=BAND_COLOR, alpha=0.6, label="Fleet normal band (IQR)", zorder=0)
    if median_val is not None:
        ax.axvline(median_val, color=MEDIAN_COLOR, linewidth=1.5, linestyle="--",
                   label=vline_label, zorder=2)

    for i, (lbl, val, col) in enumerate(zip(labels, values, colors)):
        mk = markers[i] if markers else "o"
        ax.plot([0, val], [i, i], color=col, linewidth=1.2, alpha=0.7, zorder=1)
        ax.scatter(val, i, color=col, s=55, zorder=3, marker=mk,
                   edgecolors="white", linewidths=0.5)

    ax.set_yticks(y)
    yticklabels = ax.set_yticklabels(labels, fontsize=8)
    # grey out excluded location labels
    if markers:
        for tick, mk in zip(ax.get_yticklabels(), markers):
            if mk == FLAG_MARKER:
                tick.set_color(excluded_label_color)

    ax.set_xlabel(xlabel, fontsize=8)
    ax.set_title(title, fontsize=9, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(left=False, labelsize=8)


# ---------------------------------------------------------------------------
# CHART 1: Operating temperature
# ---------------------------------------------------------------------------

print("Chart 1: Operating temperature...")

fig, axes = plt.subplots(1, 2, figsize=(16, 9), dpi=DPI)
fig.suptitle(
    "Chart 1 — Where Does Each Location Typically Run?\n"
    "Dot = median temperature  |  Bar = middle 50% of readings (IQR)  |  "
    "Dashed lines = operating range boundaries",
    fontsize=11, fontweight="bold"
)

for ax, atype in zip(axes, ["fridge", "freezer"]):
    sub = loc[loc["appliance_type"] == atype].sort_values("median_T")
    clean = loc_clean[loc_clean["appliance_type"] == atype]
    fs = fleet_stats(clean["median_T"])

    # Band for normal range boundary lines (shared across all locations in atype)
    orl_common = sub["op_range_low"].median()
    orh_common = sub["op_range_high"].median()

    labels  = sub["label"].tolist()
    medians = sub["median_T"].tolist()
    p25s    = sub["T_p25"].tolist()
    p75s    = sub["T_p75"].tolist()
    colors  = [OUTLIER_COLOR if e else FRIDGE_COLOR if atype == "fridge" else FREEZER_COLOR
               for e in sub["excluded"]]
    markers = [FLAG_MARKER if e else "o" for e in sub["excluded"]]

    y = np.arange(len(labels))

    # Fleet IQR band
    ax.axvspan(fs["p25"], fs["p75"], color=BAND_COLOR, alpha=0.5,
               label=f"Fleet normal band (median ±IQR): {fs['p25']:.1f}–{fs['p75']:.1f}°F")
    ax.axvline(fs["median"], color=MEDIAN_COLOR, linewidth=1.5, linestyle="--",
               label=f"Fleet median: {fs['median']:.1f}°F")

    # Operating range boundaries (dashed)
    ax.axvline(orl_common, color="#aaaaaa", linewidth=1, linestyle=":",
               label=f"Op range: {orl_common:.0f}–{orh_common:.0f}°F")
    ax.axvline(orh_common, color="#aaaaaa", linewidth=1, linestyle=":")

    for i, (lbl, med, p25v, p75v, col, mk) in enumerate(
        zip(labels, medians, p25s, p75s, colors, markers)
    ):
        ax.barh(i, p75v - p25v, left=p25v, height=0.55, color=col, alpha=0.25)
        ax.scatter(med, i, color=col, s=60, zorder=4, marker=mk,
                   edgecolors="white", linewidths=0.5)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    for tick, mk in zip(ax.get_yticklabels(), markers):
        if mk == FLAG_MARKER:
            tick.set_color(OUTLIER_COLOR)

    ax.set_xlabel("Temperature (°F)", fontsize=8)
    ax.set_title(f"{'Fridges' if atype=='fridge' else 'Freezers'}", fontsize=10, fontweight="bold")
    ax.tick_params(left=False, labelsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=7, loc="lower right")

plt.tight_layout()
plt.savefig(OUTPUTS / "story_1_operating_temp.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("  saved story_1_operating_temp.png")


# ---------------------------------------------------------------------------
# CHART 2: Temperature variability (IQR of T)
# ---------------------------------------------------------------------------

print("Chart 2: Variability...")

fig, axes = plt.subplots(1, 2, figsize=(14, 8), dpi=DPI)
fig.suptitle(
    "Chart 2 — How Stable Is Each Location?\n"
    "IQR = spread between 25th and 75th percentile of temperature readings\n"
    "Wider bar = more variable = less stable equipment",
    fontsize=11, fontweight="bold"
)

for ax, atype in zip(axes, ["fridge", "freezer"]):
    sub = loc[loc["appliance_type"] == atype].sort_values("T_iqr")
    clean = loc_clean[loc_clean["appliance_type"] == atype]
    fs = fleet_stats(clean["T_iqr"])

    labels  = sub["label"].tolist()
    values  = sub["T_iqr"].tolist()
    colors  = [OUTLIER_COLOR if e else (
                   ABOVE_COLOR if v > fs["p75"] else
                   NORMAL_COLOR
               ) for e, v in zip(sub["excluded"], values)]
    markers = [FLAG_MARKER if e else "o" for e in sub["excluded"]]

    lollipop(
        ax, labels, values, colors, markers=markers,
        median_val=fs["median"], p25=fs["p25"], p75=fs["p75"],
        xlabel="Temperature IQR (°F)",
        title=f"{'Fridges' if atype=='fridge' else 'Freezers'}",
    )
    ax.legend(fontsize=7)
    for tick, mk in zip(ax.get_yticklabels(), markers):
        if mk == FLAG_MARKER:
            tick.set_color(OUTLIER_COLOR)

plt.tight_layout()
plt.savefig(OUTPUTS / "story_2_variability.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("  saved story_2_variability.png")


# ---------------------------------------------------------------------------
# CHART 3: Short OOR rate (<= 30 min per day)
# ---------------------------------------------------------------------------

print("Chart 3: Short OOR rate...")

fig, axes = plt.subplots(1, 2, figsize=(14, 8), dpi=DPI)
fig.suptitle(
    "Chart 3 — How Often Do Short OOR Events Happen? (≤30 min)\n"
    "These are typically door openings, rush periods, or defrost cycles — "
    "not equipment failures\n"
    "Fleet benchmark excludes 2571 Lawrence E and The King Store 10 fridge",
    fontsize=11, fontweight="bold"
)

for ax, atype in zip(axes, ["fridge", "freezer"]):
    sub = loc[loc["appliance_type"] == atype].sort_values("short_per_day")
    clean = loc_clean[loc_clean["appliance_type"] == atype]
    fs = fleet_stats(clean["short_per_day"])

    labels  = sub["label"].tolist()
    values  = sub["short_per_day"].tolist()
    colors  = [OUTLIER_COLOR if e else (
                   ABOVE_COLOR   if v > fs["p75"] * 2 else
                   "#f4a582"      if v > fs["p75"] else
                   NORMAL_COLOR
               ) for e, v in zip(sub["excluded"], values)]
    markers = [FLAG_MARKER if e else "o" for e in sub["excluded"]]

    lollipop(
        ax, labels, values, colors, markers=markers,
        median_val=fs["median"], p25=fs["p25"], p75=fs["p75"],
        xlabel="Short OOR events per day",
        title=f"{'Fridges' if atype=='fridge' else 'Freezers'}",
    )

    # Annotate each dot with the count
    for i, (val, n) in enumerate(zip(values, sub["n_short"].values)):
        ax.text(val + fs["p75"] * 0.04, i, f"{n:,}", va="center", fontsize=6.5, color="#444444")

    ax.legend(fontsize=7)
    for tick, mk in zip(ax.get_yticklabels(), markers):
        if mk == FLAG_MARKER:
            tick.set_color(OUTLIER_COLOR)

plt.tight_layout()
plt.savefig(OUTPUTS / "story_3_short_oor_rate.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("  saved story_3_short_oor_rate.png")


# ---------------------------------------------------------------------------
# CHART 4: OOR severity breakdown per location
# ---------------------------------------------------------------------------

print("Chart 4: OOR breakdown...")

BUCKET_COLORS = {"≤30 min": "#4dac26", "31–89 min": "#f4a582", "≥90 min": "#d62728"}

for atype, fname in [("fridge", "story_4_oor_breakdown_fridges.png"),
                     ("freezer", "story_4_oor_breakdown_freezers.png")]:
    sub_ev = ev[ev["appliance_type"] == atype]
    sub_loc = loc[loc["appliance_type"] == atype].copy()

    # Total OOR per location for sort order
    totals = sub_ev.groupby("label").size().rename("total")
    sub_loc = sub_loc.join(totals, on="label").sort_values("total", ascending=True)

    labels = sub_loc["label"].tolist()
    excluded_set = set(sub_loc[sub_loc["excluded"]]["label"])

    n_locs = len(labels)
    fig, ax = plt.subplots(figsize=(13, max(5, n_locs * 0.55 + 2)), dpi=DPI)
    fig.suptitle(
        f"Chart 4 — OOR Event Severity Breakdown: {'Fridges' if atype=='fridge' else 'Freezers'}\n"
        "Each bar = total OOR events; colour shows how many are short, concerning, or extended",
        fontsize=11, fontweight="bold"
    )

    y = np.arange(n_locs)
    lefts = np.zeros(n_locs)

    for bucket, color in BUCKET_COLORS.items():
        vals = []
        for lbl in labels:
            n = len(sub_ev[(sub_ev["label"] == lbl) & (sub_ev["bucket"] == bucket)])
            vals.append(n)
        vals = np.array(vals, dtype=float)
        bars = ax.barh(y, vals, left=lefts, color=color, label=bucket,
                       height=0.65, edgecolor="white", linewidth=0.4)
        # Label non-zero segments
        for i, (v, l) in enumerate(zip(vals, lefts)):
            if v >= 3:
                ax.text(l + v / 2, i, str(int(v)), ha="center", va="center",
                        fontsize=6.5, color="white", fontweight="bold")
        lefts += vals

    # Annotate total
    for i, total in enumerate(lefts):
        ax.text(total + max(lefts) * 0.01, i, str(int(total)),
                va="center", fontsize=7.5, color="#333333")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    for tick, lbl in zip(ax.get_yticklabels(), labels):
        if lbl in excluded_set:
            tick.set_color(OUTLIER_COLOR)

    ax.set_xlabel("Number of OOR events", fontsize=8)
    ax.legend(loc="lower right", fontsize=8, framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(left=False)
    ax.set_xlim(0, max(lefts) * 1.1)

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")


# ---------------------------------------------------------------------------
# CHART 5: When do extended OOR events happen?
# ---------------------------------------------------------------------------

print("Chart 5: Extended OOR timing...")

for atype, fname in [("fridge", "story_5_extended_timing_fridges.png"),
                     ("freezer", "story_5_extended_timing_freezers.png")]:
    ext = ev[(ev["appliance_type"] == atype) & (ev["duration_mins"] > 30)].copy()

    if ext.empty:
        continue

    # Sort locations by number of extended events
    order = (
        ext.groupby("label").size()
        .sort_values(ascending=True)
        .index.tolist()
    )
    label_to_y = {lbl: i for i, lbl in enumerate(order)}
    ext["y"] = ext["label"].map(label_to_y)

    rng = np.random.default_rng(42)
    ext["y_jit"] = ext["y"] + rng.uniform(-0.3, 0.3, len(ext))

    n_locs = len(order)
    fig, ax = plt.subplots(figsize=(14, max(5, n_locs * 0.65 + 2)), dpi=DPI)
    fig.suptitle(
        f"Chart 5 — When Do Extended OOR Events Start? {'Fridges' if atype=='fridge' else 'Freezers'}\n"
        "Each dot = one event lasting >30 min  |  colour = duration  |  "
        "shape = severity (circle = 31–89 min, triangle = ≥90 min)",
        fontsize=11, fontweight="bold"
    )

    for _, row in ext.iterrows():
        mk  = "^" if row["duration_mins"] >= 90 else "o"
        col = "#d62728" if row["duration_mins"] >= 90 else "#f4a582"
        sz  = 55 if row["duration_mins"] >= 90 else 30
        ax.scatter(row["hour"], row["y_jit"], color=col, s=sz,
                   marker=mk, alpha=0.75, edgecolors="white", linewidths=0.3, zorder=3)

    # Meal rush reference lines
    for h, label in [(6, "6am"), (11, "11am"), (14, "2pm"), (17, "5pm"), (21, "9pm")]:
        ax.axvline(h, color="#bbbbbb", linewidth=0.8, linestyle="--", zorder=1)
        ax.text(h, -0.55, label, ha="center", fontsize=6.5, color="#888888")

    ax.set_xticks(range(0, 24, 1))
    ax.set_xticklabels([f"{h:02d}" for h in range(24)], fontsize=7)
    ax.set_yticks(range(n_locs))
    ax.set_yticklabels(order, fontsize=8)
    ax.set_xlim(-0.5, 23.5)
    ax.set_ylim(-0.7, n_locs - 0.3)
    ax.set_xlabel("Hour of day (event start)", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(left=False)

    legend_elements = [
        mpatches.Patch(color="#f4a582", label="31–89 min (concerning)"),
        mpatches.Patch(color="#d62728", label="≥90 min (equipment risk)"),
    ]
    ax.legend(handles=legend_elements, fontsize=8, loc="lower right")

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")


# ---------------------------------------------------------------------------
# CHART 6: Operating position within range (Low / Middle / High)
# ---------------------------------------------------------------------------

print("Chart 6: Operating position...")

ZONE_COLORS = {"Low": "#4393c3", "Middle": "#4dac26", "High": "#d62728"}

for atype, fname in [("fridge", "story_6_operating_position_fridges.png"),
                     ("freezer", "story_6_operating_position_freezers.png")]:
    sub = loc[loc["appliance_type"] == atype].copy()
    sub["zone"] = pd.cut(
        sub["range_position"],
        bins=[float("-inf"), 1/3, 2/3, float("inf")],
        labels=["Low", "Middle", "High"],
    )
    sub = sub.sort_values("range_position")

    labels   = sub["label"].tolist()
    pos      = sub["range_position"].tolist()
    zones    = sub["zone"].tolist()
    excluded = sub["excluded"].tolist()
    markers  = [FLAG_MARKER if e else "o" for e in excluded]
    colors   = [OUTLIER_COLOR if e else ZONE_COLORS.get(str(z), NORMAL_COLOR)
                for e, z in zip(excluded, zones)]

    n_locs = len(labels)
    fig, ax = plt.subplots(figsize=(13, max(5, n_locs * 0.55 + 2)), dpi=DPI)
    fig.suptitle(
        f"Chart 6 — Where Does Each Location Sit Within Its Operating Range? "
        f"{'Fridges' if atype=='fridge' else 'Freezers'}\n"
        "0 = lower boundary, 1 = upper boundary  |  "
        "Middle third (0.33–0.67) = healthy operating zone",
        fontsize=11, fontweight="bold"
    )

    ax.axvspan(1/3, 2/3, color="#d5f5d5", alpha=0.7, label="Healthy middle third", zorder=0)
    ax.axvspan(0,   1/3, color="#d0e8f5", alpha=0.4, label="Low third (cool — generally fine)", zorder=0)
    ax.axvspan(2/3, max(1.05, max(pos) + 0.05), color="#fde8e8", alpha=0.4,
               label="High third / above range (warm — watch carefully)", zorder=0)
    ax.axvline(0,   color="#aaaaaa", linewidth=0.8, linestyle=":")
    ax.axvline(1.0, color="#aaaaaa", linewidth=0.8, linestyle=":", label="Range boundaries")
    ax.axvline(0.5, color="#bbbbbb", linewidth=0.6, linestyle="--", alpha=0.5)

    y = np.arange(n_locs)
    for i, (lbl, p, col, mk, exc) in enumerate(zip(labels, pos, colors, markers, excluded)):
        ax.plot([0, p], [i, i], color=col, linewidth=1, alpha=0.5, zorder=1)
        ax.scatter(p, i, color=col, s=60, zorder=3, marker=mk,
                   edgecolors="white", linewidths=0.5)
        ax.text(p + 0.015, i, f"{p:.2f}", va="center", fontsize=7,
                color=OUTLIER_COLOR if exc else "#333333")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    for tick, mk in zip(ax.get_yticklabels(), markers):
        if mk == FLAG_MARKER:
            tick.set_color(OUTLIER_COLOR)

    ax.set_xlabel("Position within operating range  (0 = cold boundary, 1 = warm boundary)", fontsize=8)
    ax.set_xlim(-0.05, max(1.05, max(pos) + 0.08))
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(left=False)

    legend_elements = [
        mpatches.Patch(color="#d5f5d5", alpha=0.9, label="Healthy middle third (0.33–0.67)"),
        mpatches.Patch(color="#d0e8f5", alpha=0.7, label="Low third — cool"),
        mpatches.Patch(color="#fde8e8", alpha=0.7, label="High third / above range — warm"),
        plt.scatter([], [], color=OUTLIER_COLOR, marker=FLAG_MARKER, s=40,
                    label="Excluded from fleet stats (shown for reference)"),
    ]
    ax.legend(handles=legend_elements, fontsize=7.5, loc="lower right")

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")


# ---------------------------------------------------------------------------
# CHART 7: Operating position vs variability — 2D health map
# ---------------------------------------------------------------------------

print("Chart 7: Position vs variability scatter...")

for atype, fname in [("fridge",  "story_7_position_vs_variability_fridges.png"),
                     ("freezer", "story_7_position_vs_variability_freezers.png")]:
    sub   = loc[loc["appliance_type"] == atype].copy()
    clean = loc_clean[loc_clean["appliance_type"] == atype]

    fs_pos = fleet_stats(clean["range_position"])
    fs_var = fleet_stats(clean["T_iqr"])

    fig, ax = plt.subplots(figsize=(11, 8), dpi=DPI)
    fig.suptitle(
        f"Chart 7 — Operating Position vs Temperature Variability: "
        f"{'Fridges' if atype == 'fridge' else 'Freezers'}\n"
        "Ideal location: centre of the range, low variability (bottom-centre green zone)\n"
        "Shaded band = fleet normal (IQR)  |  dashed lines = fleet medians",
        fontsize=11, fontweight="bold"
    )

    # ── Quadrant shading ──────────────────────────────────────────────────
    # x = variability, y = range position
    y_lo, y_hi = fs_pos["p25"], fs_pos["p75"]
    x_hi        = fs_var["p75"]

    x_max = fs_var["p75"] * 2.0
    y_min = min(sub["range_position"].min() - 0.05, -0.02)
    y_max = max(sub["range_position"].max() + 0.05,  1.05)

    # Green zone: low variability + position within IQR — use data coordinates so it never rescales
    ax.add_patch(mpatches.Rectangle(
        (0, y_lo), x_hi, y_hi - y_lo,
        color="#c8e6c9", alpha=0.55, zorder=0,
        label="Healthy zone (position & variability within fleet IQR)",
        transform=ax.transData,
    ))

    # Warm-side zone: above position IQR, any variability
    ax.axhspan(y_hi, y_max, color="#fde8e8", alpha=0.35, zorder=0, label="Running warm")

    # Cool-side zone: below position IQR
    ax.axhspan(y_min, y_lo, color="#e3f2fd", alpha=0.35, zorder=0, label="Running cool")

    # High-variability band across full height
    ax.axvspan(x_hi, x_max, color="#fff3e0", alpha=0.45, zorder=0, label="High variability")

    # ── Fleet median reference lines ──────────────────────────────────────
    ax.axhline(fs_pos["median"], color=MEDIAN_COLOR, linewidth=1.3, linestyle="--",
               label=f"Fleet median position ({fs_pos['median']:.2f})", zorder=2)
    ax.axvline(fs_var["median"], color=MEDIAN_COLOR, linewidth=1.3, linestyle=":",
               label=f"Fleet median variability ({fs_var['median']:.1f}°F IQR)", zorder=2)

    # Operating range boundary lines at y=0 and y=1
    ax.axhline(0,   color="#aaaaaa", linewidth=0.8, linestyle=":", alpha=0.7)
    ax.axhline(1.0, color="#aaaaaa", linewidth=0.8, linestyle=":", alpha=0.7)
    ax.text(x_max * 0.99, 0,   "Cold boundary", ha="right", va="bottom", fontsize=7, color="#aaaaaa")
    ax.text(x_max * 0.99, 1.0, "Warm boundary", ha="right", va="top",    fontsize=7, color="#aaaaaa")

    # ── Scatter each location ─────────────────────────────────────────────
    for _, row in sub.iterrows():
        excl    = row["excluded"]
        mk      = FLAG_MARKER if excl else "o"
        col     = OUTLIER_COLOR if excl else (
            ABOVE_COLOR if row["range_position"] > y_hi or row["T_iqr"] > x_hi else
            "#4dac26"
        )
        clipped = row["T_iqr"] > x_max
        x_plot  = x_max * 0.985 if clipped else row["T_iqr"]

        ax.scatter(x_plot, row["range_position"],
                   color=col, s=80, marker=mk if not clipped else ">", zorder=4,
                   edgecolors="white", linewidths=0.7, alpha=0.9)

        if clipped:
            ax.annotate(
                f"{row['label']} ({row['T_iqr']:.0f}°F →)",
                xy=(x_max * 0.985, row["range_position"]),
                xytext=(x_max * 0.72, row["range_position"] + (y_max - y_min) * 0.06),
                fontsize=7, color=OUTLIER_COLOR,
                arrowprops=dict(arrowstyle="->", color=OUTLIER_COLOR, lw=0.8),
            )
            continue

        x_nudge = x_max * 0.015
        y_nudge = 0.01
        va = "bottom"
        if row["range_position"] > y_max - 0.1:
            y_nudge = -0.01
            va = "top"

        ax.text(x_plot + x_nudge,
                row["range_position"] + y_nudge,
                row["label"], fontsize=7,
                color=OUTLIER_COLOR if excl else "#222222",
                ha="left", va=va)

    ax.set_xlabel("Temperature variability (IQR, °F)", fontsize=9)
    ax.set_ylabel("Position within operating range  (0 = cold boundary · 1 = warm boundary)", fontsize=9)
    ax.set_xlim(0, x_max)
    ax.set_ylim(y_min, y_max)
    ax.spines[["top", "right"]].set_visible(False)

    legend_elements = [
        mpatches.Patch(color="#c8e6c9", alpha=0.8, label="Healthy zone (fleet IQR on both axes)"),
        mpatches.Patch(color="#fde8e8", alpha=0.6, label="Running warm"),
        mpatches.Patch(color="#e3f2fd", alpha=0.6, label="Running cool"),
        mpatches.Patch(color="#fff3e0", alpha=0.7, label="High variability"),
        plt.Line2D([0], [0], color=MEDIAN_COLOR, linestyle="--", linewidth=1.2,
                   label=f"Fleet median position ({fs_pos['median']:.2f})"),
        plt.Line2D([0], [0], color=MEDIAN_COLOR, linestyle=":", linewidth=1.2,
                   label=f"Fleet median variability ({fs_var['median']:.1f}°F)"),
        plt.scatter([], [], color="#4dac26",    marker="o", s=50, label="Within healthy zone"),
        plt.scatter([], [], color=ABOVE_COLOR,  marker="o", s=50, label="Outside healthy zone"),
        plt.scatter([], [], color=OUTLIER_COLOR, marker=FLAG_MARKER, s=50,
                    label="Excluded from fleet stats"),
    ]
    ax.legend(handles=legend_elements, fontsize=7.5, loc="upper left",
              framealpha=0.9, edgecolor="#cccccc")

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")


# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("FLEET BENCHMARKS (clean fleet, median / IQR)")
print("=" * 60)

for atype in ["fridge", "freezer"]:
    c = loc_clean[loc_clean["appliance_type"] == atype]
    print(f"\n{atype.upper()}S  (n={len(c)} locations)")
    for col, label in [
        ("median_T",      "Median operating temp (°F)"),
        ("T_iqr",         "Temp IQR — variability (°F)"),
        ("short_per_day", "Short OOR/day (≤30 min)"),
        ("range_position","Position in range (0–1)"),
    ]:
        fs = fleet_stats(c[col])
        print(f"  {label:<40}  median={fs['median']:.2f}  IQR {fs['p25']:.2f}–{fs['p75']:.2f}  "
              f"(mean={fs['mean']:.2f})")

print(f"\nOutputs saved to {OUTPUTS}")
for f in sorted(OUTPUTS.glob("story_*.png")):
    print(f"  {f.name}")
