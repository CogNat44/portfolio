"""Monthly customer report — F/F equipment health summary

Computes per-unit metrics for three complete months and compares each unit
against fleet benchmarks to produce a RAG-status summary and detail view.

METRICS
-------
  avg_T        — monthly mean temperature (°F)
  temp_iqr     — temperature variability (IQR: p75 – p25)
  escalations  — count of OOR runs ≥ 90 consecutive minutes

RAG THRESHOLDS (all relative to fleet, current month)
------------------------------------------------------
  avg_T:       yellow if > fleet median + 1 IQR
               red    if > fleet median + 2 IQR
  variability: yellow if > fleet p75
               red    if > fleet p75 × 1.5
  escalations: yellow if > fleet median
               red    if > fleet p75
  Final status = worst of any indicator.

OUTPUTS
-------
  customer_report_fridges.png   — fleet scorecard (fridges)
  customer_report_freezers.png  — fleet scorecard (freezers)
  customer_report_detail.png    — monthly sparklines for flagged units

Usage:
    cd ~/Desktop/cogsworth
    source experiments/natalie/.venv/bin/activate
    python3 experiments/natalie/customer_report.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from data_loader import load, SETPOINTS

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
DPI = 130

MONTHS = {
    "Dec 2025": (pd.Timestamp("2025-12-01", tz="America/New_York"),
                 pd.Timestamp("2026-01-01", tz="America/New_York")),
    "Jan 2026": (pd.Timestamp("2026-01-01", tz="America/New_York"),
                 pd.Timestamp("2026-02-01", tz="America/New_York")),
    "Feb 2026": (pd.Timestamp("2026-02-01", tz="America/New_York"),
                 pd.Timestamp("2026-03-01", tz="America/New_York")),
}
CURRENT_MONTH = "Feb 2026"
PREV_MONTH    = "Jan 2026"

STAT_EXCLUDE = {
    ("The King - Store 06",                 None),
    ("The King - Store 10",            "fridge"),
    ("Shwarma - Store 01",  "freezer"),
}

STATUS_COLORS = {"green": "#2ca25f", "yellow": "#f0a500", "red": "#d62728"}
RAG_ORDER     = {"red": 0, "yellow": 1, "green": 2}


def is_excluded(building, atype):
    return (building, None) in STAT_EXCLUDE or (building, atype) in STAT_EXCLUDE


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

print("Loading data...")
df = load()
df["datetime"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_convert("America/New_York")
df["label"]    = df["building"].str.replace(r"^\d+ - ", "", regex=True)


# ---------------------------------------------------------------------------
# Monthly metrics
# ---------------------------------------------------------------------------

def compute_monthly_metrics(df, start, end):
    sub  = df[(df["datetime"] >= start) & (df["datetime"] < end)]
    rows = []
    for (zone, atype), grp in sub.groupby(["zone_name", "appliance_type"]):
        if len(grp) < 100:
            continue
        grp    = grp.sort_values("datetime").reset_index(drop=True)
        avg_T  = float(grp["T"].mean())
        t_iqr  = float(grp["T"].quantile(0.75) - grp["T"].quantile(0.25))

        oor    = ~grp["in_range"]
        run_id = (oor != oor.shift()).cumsum()
        esc    = sum(
            1 for rid in run_id[oor].unique()
            if int((oor & (run_id == rid)).sum()) * 2 >= 90
        )
        rows.append({
            "zone_name": zone, "appliance_type": atype,
            "building":  grp["building"].iloc[0],
            "label":     grp["label"].iloc[0],
            "avg_T": avg_T, "temp_iqr": t_iqr, "escalations": esc,
        })
    return pd.DataFrame(rows)


print("Computing monthly metrics...")
monthly = {}
for mn, (s, e) in MONTHS.items():
    monthly[mn] = compute_monthly_metrics(df, s, e)
    print(f"  {mn}: {len(monthly[mn])} zone-months")

curr = monthly[CURRENT_MONTH]
prev = monthly[PREV_MONTH]


# ---------------------------------------------------------------------------
# Fleet benchmarks (clean fleet only)
# ---------------------------------------------------------------------------

def fleet_benchmarks(month_df, atype):
    clean = month_df[
        (month_df["appliance_type"] == atype) &
        ~month_df.apply(lambda r: is_excluded(r["building"], atype), axis=1)
    ]
    return {
        "avg_T_median":  float(clean["avg_T"].median()),
        "avg_T_iqr":     float(clean["avg_T"].quantile(0.75) - clean["avg_T"].quantile(0.25)),
        "temp_iqr_p75":  float(clean["temp_iqr"].quantile(0.75)),
        "esc_median":    float(clean["escalations"].median()),
        "esc_p75":       float(clean["escalations"].quantile(0.75)),
    }


# ---------------------------------------------------------------------------
# RAG status
# ---------------------------------------------------------------------------

def rag_status(row, bm):
    score = 0
    if row["escalations"] > bm["esc_p75"]:
        score = max(score, 2)
    elif row["escalations"] > bm["esc_median"]:
        score = max(score, 1)
    if row["temp_iqr"] > bm["temp_iqr_p75"] * 1.5:
        score = max(score, 2)
    elif row["temp_iqr"] > bm["temp_iqr_p75"]:
        score = max(score, 1)
    warm_hi = bm["avg_T_median"] + bm["avg_T_iqr"]
    if row["avg_T"] > warm_hi + bm["avg_T_iqr"]:
        score = max(score, 2)
    elif row["avg_T"] > warm_hi:
        score = max(score, 1)
    return {0: "green", 1: "yellow", 2: "red"}[score]


def trend_label(curr_val, prev_val, higher_is_worse=True):
    if pd.isna(prev_val):
        return ("—", "#888888")
    delta = curr_val - prev_val
    if abs(delta) < max(abs(prev_val) * 0.1, 0.2):
        return ("stable", "#888888")
    if higher_is_worse:
        return ("↑ worse", "#d62728") if delta > 0 else ("↓ better", "#2ca25f")
    return ("↓ worse", "#d62728") if delta < 0 else ("↑ better", "#2ca25f")


# ---------------------------------------------------------------------------
# Chart 1: Fleet scorecard (one per appliance type)
# ---------------------------------------------------------------------------

print("\nPlotting fleet scorecards...")

for atype in ["fridge", "freezer"]:
    bm       = fleet_benchmarks(curr, atype)
    rows     = curr[curr["appliance_type"] == atype].copy()
    prev_sub = prev[prev["appliance_type"] == atype][
        ["zone_name", "avg_T", "temp_iqr", "escalations"]
    ].rename(columns={"avg_T": "avg_T_p", "temp_iqr": "iqr_p", "escalations": "esc_p"})

    rows = rows.merge(prev_sub, on="zone_name", how="left")
    rows["rag"]      = rows.apply(lambda r: rag_status(r, bm), axis=1)
    rows["excluded"] = rows.apply(lambda r: is_excluded(r["building"], atype), axis=1)
    rows["rag_ord"]  = rows["rag"].map(RAG_ORDER)
    rows = rows.sort_values(["rag_ord", "label"]).reset_index(drop=True)

    n      = len(rows)
    fig_h  = max(5, n * 0.55 + 3.5)
    fig, axes = plt.subplots(1, 3, figsize=(16, fig_h), dpi=DPI,
                              gridspec_kw={"width_ratios": [3, 2, 2]})

    title_atype = "Fridges" if atype == "fridge" else "Freezers"
    op_range    = "33–40°F" if atype == "fridge" else "−10–10°F"
    fig.suptitle(
        f"Equipment Health Report — {title_atype}  |  {CURRENT_MONTH}  |  "
        f"Operating range: {op_range}\n"
        f"Fleet benchmark  avg temp: {bm['avg_T_median']:.1f}°F  |  "
        f"variability: {bm['temp_iqr_p75']:.1f}°F IQR (p75)  |  "
        f"escalations (>90 min OOR): {bm['esc_median']:.0f}/month (median)",
        fontsize=10, fontweight="bold"
    )

    labels = [
        f"{'* ' if r['excluded'] else ''}{r['label']}\n  {r['zone_name']}"
        for _, r in rows.iterrows()
    ]
    y = np.arange(n)

    # ── Panel A: avg temperature ─────────────────────────────────────────
    ax = axes[0]
    fleet_lo = bm["avg_T_median"] - bm["avg_T_iqr"]
    fleet_hi = bm["avg_T_median"] + bm["avg_T_iqr"]
    ax.axvspan(fleet_lo, fleet_hi, color="#e8f4fd", alpha=0.6, label="Fleet IQR band")
    ax.axvline(bm["avg_T_median"], color="#888888", linewidth=1.2, linestyle="--",
               label=f"Fleet median {bm['avg_T_median']:.1f}°F")

    sp = SETPOINTS[atype]
    ax.axvline(sp["crl"], color="#2166ac", linewidth=0.8, linestyle=":", alpha=0.7)
    ax.axvline(sp["crh"], color="#d62728", linewidth=0.8, linestyle=":", alpha=0.7)

    for i, (_, r) in enumerate(rows.iterrows()):
        col = STATUS_COLORS[r["rag"]]
        ax.plot([bm["avg_T_median"], r["avg_T"]], [i, i], color=col, linewidth=1.2, alpha=0.6)
        ax.scatter(r["avg_T"], i, color=col, s=60, zorder=3, edgecolors="white", linewidths=0.5)
        delta = r["avg_T"] - bm["avg_T_median"]
        ax.text(r["avg_T"] + 0.05, i, f"{r['avg_T']:.1f}°F ({delta:+.1f})",
                va="center", fontsize=7, color=col if abs(delta) > 0.5 else "#555555")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.5)
    ax.set_xlabel("Average temperature (°F)", fontsize=8)
    ax.set_title("Avg Temperature vs Fleet", fontsize=9, fontweight="bold")
    ax.legend(fontsize=6.5, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(left=False)

    # ── Panel B: variability ─────────────────────────────────────────────
    ax = axes[1]
    ax.axvline(bm["temp_iqr_p75"], color="#888888", linewidth=1.2, linestyle="--",
               label=f"Fleet p75 {bm['temp_iqr_p75']:.1f}°F")

    for i, (_, r) in enumerate(rows.iterrows()):
        col = STATUS_COLORS[r["rag"]]
        ax.plot([0, r["temp_iqr"]], [i, i], color=col, linewidth=1.2, alpha=0.6)
        mk = "D" if r["temp_iqr"] > bm["temp_iqr_p75"] else "o"
        ax.scatter(r["temp_iqr"], i, color=col, s=55, zorder=3, marker=mk,
                   edgecolors="white", linewidths=0.5)
        ax.text(r["temp_iqr"] + 0.05, i, f"{r['temp_iqr']:.1f}°F",
                va="center", fontsize=7, color=col if r["temp_iqr"] > bm["temp_iqr_p75"] else "#555555")

    ax.set_yticks(y)
    ax.set_yticklabels([], fontsize=7.5)
    ax.set_xlabel("Temperature variability (IQR °F)", fontsize=8)
    ax.set_title("Temp Variability", fontsize=9, fontweight="bold")
    ax.legend(fontsize=6.5, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(left=False)

    # ── Panel C: escalations + trend ─────────────────────────────────────
    ax = axes[2]
    ax.axvline(bm["esc_median"], color="#888888", linewidth=1.2, linestyle="--",
               label=f"Fleet median {bm['esc_median']:.0f}")
    ax.axvline(bm["esc_p75"], color="#f0a500", linewidth=0.8, linestyle=":",
               label=f"Fleet p75 {bm['esc_p75']:.0f}")

    for i, (_, r) in enumerate(rows.iterrows()):
        col = STATUS_COLORS[r["rag"]]
        ax.plot([0, r["escalations"]], [i, i], color=col, linewidth=1.2, alpha=0.6)
        ax.scatter(r["escalations"], i, color=col, s=55, zorder=3,
                   edgecolors="white", linewidths=0.5)

        t_str, t_col = trend_label(r["escalations"], r.get("esc_p", np.nan))
        ax.text(r["escalations"] + 0.15, i,
                f"{int(r['escalations'])}  {t_str}",
                va="center", fontsize=7, color=t_col)

    ax.set_yticks(y)
    ax.set_yticklabels([], fontsize=7.5)
    ax.set_xlabel("Escalations >90 min OOR", fontsize=8)
    ax.set_title(f"Escalations & Trend vs {PREV_MONTH}", fontsize=9, fontweight="bold")
    ax.legend(fontsize=6.5, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(left=False)

    # RAG legend
    for status, col in STATUS_COLORS.items():
        axes[0].scatter([], [], color=col, s=60, label=status.capitalize())
    axes[0].legend(fontsize=6.5, loc="upper right")

    fig.text(0.01, 0.005, "* Excluded from fleet benchmark  |  Diamond marker = above fleet threshold",
             fontsize=6.5, color="#888888", style="italic")

    plt.tight_layout()
    fname = f"customer_report_{atype}s.png"
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")


# ---------------------------------------------------------------------------
# Chart 2: Detail sparklines — flagged units only
# ---------------------------------------------------------------------------

print("\nPlotting detail cards for flagged units...")

flagged = []
for atype in ["fridge", "freezer"]:
    bm   = fleet_benchmarks(curr, atype)
    rows = curr[curr["appliance_type"] == atype].copy()
    rows["rag"] = rows.apply(lambda r: rag_status(r, bm), axis=1)
    for _, r in rows[rows["rag"].isin(["yellow", "red"])].iterrows():
        flagged.append((r["zone_name"], r["appliance_type"], r["rag"],
                        r["label"], bm))

if not flagged:
    print("  No flagged units — all green")
else:
    ncols = 2
    nrows = int(np.ceil(len(flagged) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 6.5, nrows * 4 + 1.5),
                              dpi=DPI)
    axes_flat = np.array(axes).flatten()

    fig.suptitle(
        f"Detail View — Units Requiring Attention  ({CURRENT_MONTH})\n"
        "3-month trend: avg temperature (line) and escalations (bars)",
        fontsize=11, fontweight="bold"
    )

    month_names = list(MONTHS.keys())

    for i, (zone_name, atype, rag, lbl, bm) in enumerate(flagged):
        ax = axes_flat[i]
        col = STATUS_COLORS[rag]

        mv = []
        for mn in month_names:
            row = monthly[mn]
            row = row[(row["zone_name"] == zone_name) & (row["appliance_type"] == atype)]
            if not row.empty:
                mv.append({
                    "month":        mn,
                    "avg_T":        row.iloc[0]["avg_T"],
                    "escalations":  row.iloc[0]["escalations"],
                })
        if not mv:
            ax.set_visible(False)
            continue

        mv_df = pd.DataFrame(mv)
        x     = np.arange(len(mv_df))

        ax2 = ax.twinx()

        # Bars: escalations
        bar_cols = [
            STATUS_COLORS["green"] if e <= bm["esc_median"] else
            STATUS_COLORS["yellow"] if e <= bm["esc_p75"] else
            STATUS_COLORS["red"]
            for e in mv_df["escalations"]
        ]
        ax2.bar(x, mv_df["escalations"], color=bar_cols, alpha=0.35, width=0.5, zorder=1)
        ax2.axhline(bm["esc_median"], color="#888888", linewidth=0.8, linestyle=":",
                    alpha=0.7)
        ax2.set_ylabel("Escalations >90 min", fontsize=7, color="#888888")
        ax2.tick_params(axis="y", labelsize=6.5, colors="#888888")
        ax2.spines[["top"]].set_visible(False)

        # Line: avg temp
        ax.plot(x, mv_df["avg_T"], "-o", color=col, linewidth=2, markersize=7, zorder=3)
        ax.axhspan(SETPOINTS[atype]["crl"], SETPOINTS[atype]["crh"],
                   color="#e8f4fd", alpha=0.4, label="Operating range")
        ax.axhline(bm["avg_T_median"], color="#888888", linewidth=1, linestyle="--",
                   alpha=0.7, label=f"Fleet median {bm['avg_T_median']:.1f}°F")

        for xi, row_m in mv_df.iterrows():
            ax.text(xi, row_m["avg_T"] + 0.1, f"{row_m['avg_T']:.1f}°F",
                    ha="center", va="bottom", fontsize=7, color=col)

        ax.set_xticks(x)
        ax.set_xticklabels(mv_df["month"], fontsize=8)
        ax.set_ylabel("Avg temperature (°F)", fontsize=7)
        ax.set_title(
            f"{lbl} — {zone_name}  [{rag.upper()}]",
            fontsize=8.5, fontweight="bold", color=col
        )
        ax.legend(fontsize=6.5, loc="upper left")
        ax.tick_params(labelsize=6.5)
        ax.spines[["top", "right"]].set_visible(False)

    for j in range(len(flagged), len(axes_flat)):
        axes_flat[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUTS / "customer_report_detail.png", dpi=DPI, bbox_inches="tight")
    plt.close()
    print("  saved customer_report_detail.png")

print(f"\nOutputs saved to {OUTPUTS}")
