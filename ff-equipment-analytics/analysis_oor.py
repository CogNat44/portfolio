"""OOR deep-dive: escalation prediction + defrost cycle detection.

Usage:
    cd ff-equipment-analytics
    source .venv/bin/activate
    analysis_oor.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
from data_loader import load

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
DPI = 120

# ---------------------------------------------------------------------------
# Load and prep
# ---------------------------------------------------------------------------

EXCLUDE_BUILDINGS = {"The King - Store 06"}

df = load()
df = df[~df["building"].isin(EXCLUDE_BUILDINGS)]
df["datetime"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_convert("America/New_York")
df["label"] = (
    df["building"]
    .str.replace(r"^\d+ - ", "", regex=True)
)

# ---------------------------------------------------------------------------
# Build enriched OOR event table
# Each event carries features observable at the moment it starts
# ---------------------------------------------------------------------------

print("Building enriched OOR event table...")

PRE_ROWS = 15   # 30 min of pre-event history at 2-min intervals


def _shape_features(T: np.ndarray) -> dict:
    """Compute shape features for an OOR event temperature profile.

    Defrost signature (sawtooth/dome):
    - Smooth rise (low diff_std, high rise_frac in first half)
    - Peak near the END of the OOR window (compressor kicks in at timer end → sharp recovery)
    - Negatively skewed T distribution (long flat rise, abrupt drop pulls the tail left)

    Door-open / rush:
    - Jagged (high diff_std) — compressor still cycling, causing oscillations
    - Multiple local maxima
    - Peak can occur anywhere
    """
    n = len(T)
    if n < 3:
        return {"diff_std": np.nan, "peak_pos_frac": np.nan,
                "rise_frac": np.nan, "skewness": np.nan, "amplitude": np.nan}

    diffs = np.diff(T)
    amplitude = float(T.max() - T.min())

    # Smoothness: std of consecutive differences (low = smooth curve)
    diff_std = float(np.std(diffs))

    # Peak position: 0 = start, 1 = end (defrost peaks late, just before sharp recovery)
    peak_pos_frac = float(np.argmax(T) / max(1, n - 1))

    # Rise fraction: in first 2/3 of event, what fraction of steps are rising?
    first_part = diffs[: max(1, 2 * n // 3)]
    rise_frac = float((first_part > 0).mean()) if len(first_part) > 0 else np.nan

    # Skewness: negative = asymmetric with a sharp drop (defrost recovery)
    mean_T = T.mean()
    std_T  = T.std()
    skewness = float(((T - mean_T) ** 3).mean() / (std_T ** 3)) if std_T > 0 else 0.0

    return {
        "diff_std":      diff_std,
        "peak_pos_frac": peak_pos_frac,
        "rise_frac":     rise_frac,
        "skewness":      skewness,
        "amplitude":     amplitude,
    }


def _enrich_zone_events(grp: pd.DataFrame) -> list[dict]:
    grp = grp.sort_values("t").reset_index(drop=True)
    crl = grp["op_range_low"].iloc[0]
    crh = grp["op_range_high"].iloc[0]
    atype = grp["appliance_type"].iloc[0]
    zone = grp["zone_name"].iloc[0]
    bld = grp["building"].iloc[0]
    label = grp["label"].iloc[0]

    oor = ~grp["in_range"]
    run_id = (oor != oor.shift()).cumsum()

    prev_end_dt = None
    prev_duration = None
    events = []

    for rid in run_id[oor].unique():
        mask = oor & (run_id == rid)
        idx = grp.index[mask].tolist()
        if not idx:
            continue

        start_i = idx[0]
        end_i = idx[-1]
        start_row = grp.loc[start_i]
        start_dt = start_row["datetime"]
        start_T = start_row["T"]
        duration_mins = len(idx) * 2

        T_series = grp.loc[idx, "T"].values
        avg_T = T_series.mean()
        direction = "high" if avg_T > crh else "low"

        # Distance from violated boundary at event start
        boundary_dist = (start_T - crh) if direction == "high" else (crl - start_T)

        # Shape features — describe the profile of this OOR event
        shape = _shape_features(T_series)

        # Pre-event slope (°F per 2-min tick) — how fast was T moving?
        pre_slice = grp.loc[max(0, start_i - PRE_ROWS): start_i - 1, "T"].dropna()
        if len(pre_slice) >= 3:
            x = np.arange(len(pre_slice))
            pre_slope = float(np.polyfit(x, pre_slice.values, 1)[0])
        else:
            pre_slope = np.nan

        # Gap since previous OOR event ended
        if prev_end_dt is not None:
            gap_mins = (start_dt - prev_end_dt).total_seconds() / 60.0
        else:
            gap_mins = np.nan

        events.append({
            "zone_name":        zone,
            "building":         bld,
            "label":            label,
            "appliance_type":   atype,
            "start":            start_dt,
            "end":              grp.loc[end_i, "datetime"],
            "duration_mins":    duration_mins,
            "escalated":        duration_mins >= 90,
            "direction":        direction,
            "start_T":          start_T,
            "boundary_dist":    boundary_dist,
            "pre_slope":        pre_slope,
            "hour":             start_dt.hour,
            "dow":              start_dt.dayofweek,
            "gap_since_prev":   gap_mins,
            "prev_duration":    prev_duration,
            # Shape features
            "diff_std":         shape["diff_std"],
            "peak_pos_frac":    shape["peak_pos_frac"],
            "rise_frac":        shape["rise_frac"],
            "skewness":         shape["skewness"],
            "amplitude":        shape["amplitude"],
        })

        prev_end_dt = grp.loc[end_i, "datetime"]
        prev_duration = duration_mins

    return events


all_rows = []
for (zone, atype), grp in df.groupby(["zone_name", "appliance_type"]):
    all_rows.extend(_enrich_zone_events(grp))

ev = pd.DataFrame(all_rows)
print(f"  Total OOR events: {len(ev):,}  |  escalated: {ev['escalated'].sum():,}  ({100*ev['escalated'].mean():.1f}%)")

# Duration buckets used throughout Part 0 and Part 1
BUCKET_BINS   = [0, 30, 90, float("inf")]
BUCKET_LABELS = ["≤30 min", "31–89 min", "≥90 min"]
BUCKET_COLORS = ["#4dac26", "#f4a582", "#d62728"]

ev["bucket"] = pd.cut(
    ev["duration_mins"],
    bins=BUCKET_BINS,
    labels=BUCKET_LABELS,
    right=True,
)

# ---------------------------------------------------------------------------
# PART 0: OOR DURATION OVERVIEW
# How big are each duration bucket, and when do they happen?
# ---------------------------------------------------------------------------

print("\n--- Part 0: OOR duration overview ---")

# --- 0a: Bucket size breakdown (fridge + freezer side-by-side) ---

fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=DPI)
fig.suptitle("OOR Event Duration Buckets", fontsize=12, fontweight="bold")

for ax, (atype, fname_suffix) in zip(axes, [("fridge", "Fridges"), ("freezer", "Freezers")]):
    sub = ev[ev["appliance_type"] == atype]
    counts = sub["bucket"].value_counts().reindex(BUCKET_LABELS, fill_value=0)
    pcts   = counts / counts.sum() * 100

    bars = ax.bar(BUCKET_LABELS, counts.values, color=BUCKET_COLORS, edgecolor="white", linewidth=0.8)

    for bar, pct, n in zip(bars, pcts.values, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + counts.max() * 0.01,
            f"{n:,}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=9, fontweight="bold"
        )

    ax.set_title(fname_suffix, fontsize=11, fontweight="bold")
    ax.set_ylabel("Event count")
    ax.set_ylim(0, counts.max() * 1.18)
    ax.tick_params(labelsize=9)

plt.tight_layout()
plt.savefig(OUTPUTS / "oor_duration_buckets.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("    saved oor_duration_buckets.png")

# --- 0b: Hour-of-day heatmap: event count by hour × bucket, fridge + freezer ---

for atype, fname_suffix in [("fridge", "fridges"), ("freezer", "freezers")]:
    sub = ev[ev["appliance_type"] == atype].copy()

    pivot = (
        sub.groupby(["hour", "bucket"], observed=True)
        .size()
        .unstack("bucket", fill_value=0)
        .reindex(columns=BUCKET_LABELS, fill_value=0)
        .reindex(range(24), fill_value=0)
    )

    fig, axes = plt.subplots(
        2, 1, figsize=(14, 9), dpi=DPI,
        gridspec_kw={"height_ratios": [1, 1.8]}
    )
    fig.suptitle(
        f"{atype.capitalize()}s — OOR Events by Time of Day\n"
        f"Total events: {len(sub):,}",
        fontsize=12, fontweight="bold"
    )

    # Top panel: stacked bar per hour
    ax_bar = axes[0]
    bottom = np.zeros(24)
    for label, color in zip(BUCKET_LABELS, BUCKET_COLORS):
        vals = pivot[label].values.astype(float)
        ax_bar.bar(range(24), vals, bottom=bottom, color=color, label=label,
                   width=0.8, edgecolor="white", linewidth=0.4)
        bottom += vals

    ax_bar.set_xlim(-0.5, 23.5)
    ax_bar.set_xticks(range(24))
    ax_bar.set_xticklabels([f"{h:02d}" for h in range(24)], fontsize=7)
    ax_bar.set_ylabel("Event count")
    ax_bar.set_title("Event count per hour (stacked by severity)", fontsize=9)
    ax_bar.legend(loc="upper right", fontsize=8, framealpha=0.9)

    # Bottom panel: heatmap — rows = buckets, cols = hours
    ax_hm = axes[1]
    hm_data = pivot.T.values.astype(float)  # shape (3, 24)

    # Normalise each row independently so rare buckets are still visible
    row_max = hm_data.max(axis=1, keepdims=True)
    row_max[row_max == 0] = 1
    hm_norm = hm_data / row_max

    im = ax_hm.imshow(hm_norm, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1)

    ax_hm.set_yticks(range(3))
    ax_hm.set_yticklabels(BUCKET_LABELS, fontsize=9)
    ax_hm.set_xticks(range(24))
    ax_hm.set_xticklabels([f"{h:02d}" for h in range(24)], fontsize=7)
    ax_hm.set_xlabel("Hour of day")
    ax_hm.set_title(
        "Relative intensity by hour (each row normalised to its own peak — shows WHEN each bucket peaks)",
        fontsize=9
    )

    # Annotate cells with raw counts
    for row_i in range(3):
        for col_j in range(24):
            n = int(hm_data[row_i, col_j])
            if n > 0:
                ax_hm.text(
                    col_j, row_i, str(n),
                    ha="center", va="center",
                    fontsize=6,
                    color="black" if hm_norm[row_i, col_j] < 0.7 else "white"
                )

    fig.colorbar(im, ax=ax_hm, fraction=0.02, pad=0.01, label="Relative intensity")
    plt.tight_layout()
    plt.savefig(OUTPUTS / f"oor_duration_by_hour_{fname_suffix}.png", dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"    saved oor_duration_by_hour_{fname_suffix}.png")

# --- 0c: Extended OOR deep-dive (≥90 min) — per-location counts + time-of-day ---

print("  Plotting extended OOR deep-dive...")

for atype, fname_suffix in [("fridge", "fridges"), ("freezer", "freezers")]:
    sub = ev[ev["appliance_type"] == atype].copy()

    # Per-location span (days) for rate calculation
    span_days = (
        sub.groupby("label")["start"]
        .agg(lambda s: max(1, (s.max() - s.min()).total_seconds() / 86400))
        .rename("span_days")
    )

    # Escalated events per location
    esc = sub[sub["escalated"]].copy()
    esc_counts = esc.groupby("label").size().rename("n_esc")

    # Short OOR per location per day
    short_counts = (
        sub[~sub["escalated"]]
        .groupby("label").size()
        .rename("n_short")
    )

    loc_stats = (
        esc_counts
        .to_frame()
        .join(short_counts, how="left")
        .join(span_days, how="left")
    )
    loc_stats["short_per_day"] = loc_stats["n_short"] / loc_stats["span_days"]
    loc_stats = loc_stats.sort_values("n_esc", ascending=True)

    if loc_stats.empty:
        continue

    n_locs = len(loc_stats)
    row_h = max(0.45, min(0.7, 10 / n_locs))
    fig_h = max(6, n_locs * row_h + 2)

    fig = plt.figure(figsize=(16, fig_h), dpi=DPI)
    fig.suptitle(
        f"{atype.capitalize()}s — Extended OOR Events (≥90 min)\n"
        f"{int(esc_counts.sum())} total escalated events across {n_locs} locations",
        fontsize=12, fontweight="bold", y=1.01
    )

    gs = fig.add_gridspec(1, 2, width_ratios=[1, 2], wspace=0.35)
    ax_bar = fig.add_subplot(gs[0])
    ax_dot = fig.add_subplot(gs[1])

    # Left: horizontal bar — escalated count, annotated with short/day rate
    y_pos = range(n_locs)
    bars = ax_bar.barh(
        list(y_pos), loc_stats["n_esc"].values,
        color="#d62728", alpha=0.85, edgecolor="white", linewidth=0.5
    )
    ax_bar.set_yticks(list(y_pos))
    ax_bar.set_yticklabels(loc_stats.index.tolist(), fontsize=8)
    ax_bar.set_xlabel("Extended OOR events (≥90 min)", fontsize=8)
    ax_bar.set_title("Event count per location", fontsize=9, fontweight="bold")
    x_max = loc_stats["n_esc"].max()
    for i, (n_esc, spd) in enumerate(
        zip(loc_stats["n_esc"].values, loc_stats["short_per_day"].values)
    ):
        ax_bar.text(
            n_esc + x_max * 0.02, i,
            f"{n_esc}  (short: {spd:.1f}/day)",
            va="center", fontsize=7, color="#333333"
        )
    ax_bar.set_xlim(0, x_max * 1.6)
    ax_bar.tick_params(left=False)
    ax_bar.spines[["top", "right"]].set_visible(False)

    # Right: dot plot — each escalated event as a dot at its start hour
    # y = location (same order as left panel), x = hour, colour = duration
    label_order = loc_stats.index.tolist()
    label_to_y  = {lbl: i for i, lbl in enumerate(label_order)}
    esc_plot = esc[esc["label"].isin(label_order)].copy()
    esc_plot["y"] = esc_plot["label"].map(label_to_y)

    # Jitter y slightly so overlapping dots are visible
    rng = np.random.default_rng(42)
    esc_plot["y_jit"] = esc_plot["y"] + rng.uniform(-0.3, 0.3, len(esc_plot))

    sc = ax_dot.scatter(
        esc_plot["hour"], esc_plot["y_jit"],
        c=esc_plot["duration_mins"],
        cmap="RdPu", vmin=0, vmax=esc_plot["duration_mins"].quantile(0.95),
        s=35, alpha=0.85, edgecolors="#333333", linewidths=0.3
    )
    fig.colorbar(sc, ax=ax_dot, label="Duration (min)", fraction=0.03, pad=0.02)

    ax_dot.set_xticks(range(0, 24, 2))
    ax_dot.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)], fontsize=7, rotation=45, ha="right")
    ax_dot.set_yticks(list(y_pos))
    ax_dot.set_yticklabels(label_order, fontsize=8)
    ax_dot.set_xlim(-0.5, 23.5)
    ax_dot.set_ylim(-0.6, n_locs - 0.4)
    ax_dot.set_xlabel("Hour of day (event start)", fontsize=8)
    ax_dot.set_title(
        "Each dot = one extended OOR event\ncolour = duration  |  y-jitter for visibility",
        fontsize=9, fontweight="bold"
    )

    # Vertical reference lines at meal rush hours
    for h in [6, 11, 14, 17, 21]:
        ax_dot.axvline(h, color="grey", linewidth=0.5, linestyle="--", alpha=0.5)

    ax_dot.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    out_path = OUTPUTS / f"oor_extended_detail_{fname_suffix}.png"
    plt.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"    saved oor_extended_detail_{fname_suffix}.png")

# ---------------------------------------------------------------------------
# PART 1: ESCALATION ANALYSIS
# What signals at event start predict duration ≥ 90 min?
# ---------------------------------------------------------------------------

print("\n--- Part 1: Escalation analysis ---")

FEATURES = ["boundary_dist", "pre_slope", "hour", "dow", "gap_since_prev", "prev_duration"]
FEATURE_LABELS = {
    "boundary_dist":   "Boundary distance at start (°F)",
    "pre_slope":       "Pre-event slope (°F / 2 min)",
    "hour":            "Hour of day",
    "dow":             "Day of week",
    "gap_since_prev":  "Gap since prev OOR (min)",
    "prev_duration":   "Previous OOR duration (min)",
}

# --- 1a: Feature distributions: escalated vs not ---

print("  Plotting feature distributions...")

for atype, fname_suffix in [("fridge", "fridges"), ("freezer", "freezers")]:
    sub = ev[ev["appliance_type"] == atype].copy()
    if sub.empty or sub["escalated"].sum() < 5:
        continue

    fig, axes = plt.subplots(2, 3, figsize=(15, 9), dpi=DPI)
    fig.suptitle(
        f"{atype.capitalize()}s — Feature Distributions: Short OOR vs Escalated (≥90 min)\n"
        f"Short: {(~sub['escalated']).sum():,}  |  Escalated: {sub['escalated'].sum():,}",
        fontsize=11, fontweight="bold"
    )

    for ax, feat in zip(axes.flatten(), FEATURES):
        data_short = sub.loc[~sub["escalated"], feat].dropna()
        data_long  = sub.loc[ sub["escalated"], feat].dropna()
        bins = np.histogram_bin_edges(
            pd.concat([data_short, data_long]).clip(
                np.percentile(pd.concat([data_short, data_long]), 1),
                np.percentile(pd.concat([data_short, data_long]), 99)
            ), bins=30
        )
        ax.hist(data_short, bins=bins, alpha=0.6, density=True, label="Short (<90 min)", color="#2c7bb6")
        ax.hist(data_long,  bins=bins, alpha=0.6, density=True, label="Escalated (≥90 min)", color="#d62728")
        ax.set_xlabel(FEATURE_LABELS[feat], fontsize=8)
        ax.set_ylabel("Density", fontsize=8)
        ax.set_title(feat, fontsize=9, fontweight="bold")
        ax.legend(fontsize=7)
        ax.tick_params(labelsize=7)

    plt.tight_layout()
    plt.savefig(OUTPUTS / f"oor_escalation_features_{fname_suffix}.png", dpi=DPI, bbox_inches="tight")
    plt.close()

# --- 1b: Logistic regression — feature importance ---

print("  Fitting logistic regression...")

coeff_rows = []

for atype, fname_suffix in [("fridge", "fridges"), ("freezer", "freezers")]:
    sub = ev[ev["appliance_type"] == atype].copy()
    model_data = sub[FEATURES + ["escalated"]].dropna()
    if len(model_data) < 50 or model_data["escalated"].sum() < 10:
        print(f"  {atype}: insufficient data for logistic regression")
        continue

    X = model_data[FEATURES].values
    y = model_data["escalated"].astype(int).values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = LogisticRegression(class_weight="balanced", max_iter=500, random_state=0)
    clf.fit(X_scaled, y)

    auc = roc_auc_score(y, clf.predict_proba(X_scaled)[:, 1])
    print(f"  {atype}: AUC = {auc:.3f}  (n={len(model_data):,}, escalated={y.sum():,})")

    for feat, coef in zip(FEATURES, clf.coef_[0]):
        coeff_rows.append({"appliance_type": atype, "feature": FEATURE_LABELS[feat], "coef": coef})

    # ROC curve
    fpr, tpr, _ = roc_curve(y, clf.predict_proba(X_scaled)[:, 1])
    coeff_rows.append({"appliance_type": atype, "_roc_fpr": fpr, "_roc_tpr": tpr, "_auc": auc,
                        "feature": None, "coef": None})

from sklearn.decomposition import PCA
from scipy.stats import gaussian_kde

# Store fitted models for cluster plots
fitted_models = {}

if coeff_rows:
    coeff_df = pd.DataFrame([r for r in coeff_rows if r["feature"] is not None])

    # --- Coefficient bar chart (kept for reference) ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=DPI)
    fig.suptitle("OOR Escalation — Logistic Regression Feature Importance\n"
                 "(standardized coefficients; positive = more likely to escalate)",
                 fontsize=11, fontweight="bold")

    for ax, atype in zip(axes, ["fridge", "freezer"]):
        sub_c = coeff_df[coeff_df["appliance_type"] == atype].sort_values("coef")
        if sub_c.empty:
            ax.set_title(f"{atype.capitalize()}: no model")
            continue
        colors = ["#d62728" if c > 0 else "#2c7bb6" for c in sub_c["coef"]]
        ax.barh(sub_c["feature"], sub_c["coef"], color=colors, alpha=0.85)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel("Coefficient (standardized)")
        ax.set_title(f"{atype.capitalize()}s", fontsize=10, fontweight="bold")
        ax.tick_params(labelsize=8)

    plt.tight_layout()
    plt.savefig(OUTPUTS / "oor_escalation_logreg.png", dpi=DPI, bbox_inches="tight")
    plt.close()

# --- Cluster visualization: PCA biplot + top-feature scatter ---

print("  Plotting escalation cluster visualizations...")

for atype, fname_suffix in [("fridge", "fridges"), ("freezer", "freezers")]:
    sub = ev[ev["appliance_type"] == atype].copy()
    model_data = sub[FEATURES + ["escalated"]].dropna().reset_index(drop=True)
    if len(model_data) < 50 or model_data["escalated"].sum() < 10:
        continue

    X = model_data[FEATURES].values
    y = model_data["escalated"].astype(int).values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Refit model to get coefficients for this plot
    clf = LogisticRegression(class_weight="balanced", max_iter=500, random_state=0)
    clf.fit(X_scaled, y)
    coefs = dict(zip(FEATURES, clf.coef_[0]))

    # PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    var_explained = pca.explained_variance_ratio_

    short_mask = y == 0
    esc_mask   = y == 1

    fig = plt.figure(figsize=(18, 7), dpi=DPI)
    fig.suptitle(
        f"{atype.capitalize()}s — OOR Escalation: Cluster Structure\n"
        f"Short (<90 min): {short_mask.sum():,}  |  Escalated (≥90 min): {esc_mask.sum():,}  |  AUC: {roc_auc_score(y, clf.predict_proba(X_scaled)[:, 1]):.3f}",
        fontsize=11, fontweight="bold"
    )

    # ---- Panel 1: PCA biplot ----
    ax1 = fig.add_subplot(1, 3, 1)

    # Short events: hexbin density (avoids overplotting thousands of points)
    if short_mask.sum() > 50:
        hb = ax1.hexbin(
            X_pca[short_mask, 0], X_pca[short_mask, 1],
            gridsize=40, cmap="Blues", mincnt=1, alpha=0.6, linewidths=0.2
        )

    # Escalated events: individual scatter (there are far fewer)
    ax1.scatter(
        X_pca[esc_mask, 0], X_pca[esc_mask, 1],
        color="#d62728", s=25, alpha=0.8, zorder=4, label="Escalated"
    )

    # Feature loading arrows scaled to fit the plot
    loadings = pca.components_.T  # shape (n_features, 2)
    arrow_scale = 2.5
    for i, feat in enumerate(FEATURES):
        dx, dy = loadings[i, 0] * arrow_scale, loadings[i, 1] * arrow_scale
        ax1.annotate(
            "", xy=(dx, dy), xytext=(0, 0),
            arrowprops=dict(arrowstyle="->", color="#333333", lw=1.3)
        )
        # Label offset slightly beyond arrow tip
        ax1.text(dx * 1.18, dy * 1.18, FEATURE_LABELS[feat],
                 fontsize=6.5, ha="center", va="center", color="#333333")

    ax1.scatter([], [], color="#4c72b0", s=30, alpha=0.6, label="Short (density)")
    ax1.legend(fontsize=7, loc="upper right")
    ax1.set_xlabel(f"PC1 ({var_explained[0]*100:.1f}% variance)", fontsize=8)
    ax1.set_ylabel(f"PC2 ({var_explained[1]*100:.1f}% variance)", fontsize=8)
    ax1.set_title("PCA biplot — 6-feature space\n(arrows = feature loadings)", fontsize=9, fontweight="bold")
    ax1.tick_params(labelsize=7)
    ax1.axhline(0, color="lightgray", linewidth=0.5)
    ax1.axvline(0, color="lightgray", linewidth=0.5)

    # ---- Panel 2: Top predictor scatter — prev_duration vs boundary_dist ----
    ax2 = fig.add_subplot(1, 3, 2)

    pd_col = model_data["prev_duration"].fillna(0)
    bd_col = model_data["boundary_dist"]

    # Clip to 99th percentile for readability
    pd_clip = pd_col.clip(0, pd_col.quantile(0.99))

    ax2.scatter(
        pd_clip[short_mask], bd_col[short_mask],
        color="#2c7bb6", s=6, alpha=0.18, rasterized=True, label="Short"
    )
    ax2.scatter(
        pd_clip[esc_mask], bd_col[esc_mask],
        color="#d62728", s=25, alpha=0.75, zorder=4, label="Escalated"
    )

    # KDE contour for escalated events (if enough)
    if esc_mask.sum() >= 10:
        try:
            kde_x = pd_clip[esc_mask].values
            kde_y = bd_col[esc_mask].values
            kde = gaussian_kde(np.vstack([kde_x, kde_y]))
            xg = np.linspace(pd_clip.min(), pd_clip.max(), 60)
            yg = np.linspace(bd_col.quantile(0.01), bd_col.quantile(0.99), 60)
            Xg, Yg = np.meshgrid(xg, yg)
            Zg = kde(np.vstack([Xg.ravel(), Yg.ravel()])).reshape(Xg.shape)
            ax2.contour(Xg, Yg, Zg, levels=5, colors="#d62728", alpha=0.5, linewidths=0.8)
        except Exception:
            pass

    ax2.set_xlabel("Previous OOR duration (min)\n[strongest predictor]", fontsize=8)
    ax2.set_ylabel("Boundary distance at event start (°F)", fontsize=8)
    ax2.set_title("Top predictors: prev_duration vs boundary_dist\n(red = escalated; contours = escalated density)", fontsize=8, fontweight="bold")
    ax2.legend(fontsize=7)
    ax2.tick_params(labelsize=7)

    # ---- Panel 3: prev_duration vs hour — time-of-day pattern ----
    ax3 = fig.add_subplot(1, 3, 3)

    hour_col = model_data["hour"]

    # For short events: violin or scatter by hour
    ax3.scatter(
        hour_col[short_mask] + np.random.default_rng(0).uniform(-0.3, 0.3, short_mask.sum()),
        pd_clip[short_mask],
        color="#2c7bb6", s=4, alpha=0.12, rasterized=True, label="Short"
    )
    ax3.scatter(
        hour_col[esc_mask] + np.random.default_rng(1).uniform(-0.3, 0.3, esc_mask.sum()),
        pd_clip[esc_mask],
        color="#d62728", s=30, alpha=0.8, zorder=4, label="Escalated"
    )

    ax3.set_xlabel("Hour of day (local time)", fontsize=8)
    ax3.set_ylabel("Previous OOR duration (min)", fontsize=8)
    ax3.set_title("Hour of day vs prev_duration\n(when do high-prev_duration events escalate?)", fontsize=8, fontweight="bold")
    ax3.set_xticks(range(0, 24, 4))
    ax3.legend(fontsize=7)
    ax3.tick_params(labelsize=7)

    plt.tight_layout()
    plt.savefig(OUTPUTS / f"oor_escalation_clusters_{fname_suffix}.png", dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"    {atype}: saved oor_escalation_clusters_{fname_suffix}.png")

# --- 1c: Escalation timing — heatmap (hour × DOW) + smoothed rate line ---

print("  Plotting escalation timing heatmaps...")

DOW_ORDER   = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DOW_MAP     = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

for atype, fname_suffix in [("fridge", "fridges"), ("freezer", "freezers")]:
    sub = ev[ev["appliance_type"] == atype].copy()
    if sub.empty or sub["escalated"].sum() < 5:
        continue

    sub["dow_label"] = sub["dow"].map(DOW_MAP)

    # --- Heatmap: hour × DOW, value = escalation rate ---
    pivot_total = (
        sub.groupby(["dow_label", "hour"])["escalated"]
        .count()
        .unstack(fill_value=0)
        .reindex(DOW_ORDER)
    )
    pivot_esc = (
        sub.groupby(["dow_label", "hour"])["escalated"]
        .sum()
        .unstack(fill_value=0)
        .reindex(DOW_ORDER)
    )
    # Escalation rate; suppress cells with <5 events (too noisy)
    with np.errstate(divide="ignore", invalid="ignore"):
        rate_matrix = np.where(
            pivot_total.values >= 5,
            pivot_esc.values / pivot_total.values * 100,
            np.nan
        )

    # --- Hourly totals (for the bottom panel) ---
    hourly = sub.groupby("hour").agg(
        total=("escalated", "count"),
        n_esc=("escalated", "sum"),
    )
    hourly["rate"] = hourly["n_esc"] / hourly["total"] * 100
    hourly = hourly.reindex(range(24), fill_value=0)
    # Smooth escalation rate with rolling mean to reduce noise
    hourly["rate_smooth"] = hourly["rate"].rolling(3, center=True, min_periods=1).mean()

    fig = plt.figure(figsize=(14, 9), dpi=DPI)
    fig.suptitle(
        f"{atype.capitalize()}s — OOR Escalation Timing\n"
        f"Escalated: {sub['escalated'].sum():,} / {len(sub):,} events  ({100*sub['escalated'].mean():.1f}%)",
        fontsize=11, fontweight="bold"
    )

    # Top: heatmap
    ax_heat = fig.add_subplot(2, 1, 1)
    im = ax_heat.imshow(
        rate_matrix, aspect="auto", cmap="YlOrRd",
        vmin=0, vmax=np.nanpercentile(rate_matrix, 95) if not np.all(np.isnan(rate_matrix)) else 1,
        interpolation="nearest"
    )
    plt.colorbar(im, ax=ax_heat, label="Escalation rate (%)", shrink=0.8)
    ax_heat.set_yticks(range(len(DOW_ORDER)))
    ax_heat.set_yticklabels(DOW_ORDER, fontsize=8)
    ax_heat.set_xticks(range(0, 24, 2))
    ax_heat.set_xticklabels(range(0, 24, 2), fontsize=8)
    ax_heat.set_xlabel("Hour of day (local time)", fontsize=9)
    ax_heat.set_title("Escalation rate by hour × day  (grey = fewer than 5 events in cell)", fontsize=9)

    # Bottom: line chart — volume of all events + smoothed escalation rate
    ax_line = fig.add_subplot(2, 1, 2)
    color_vol  = "#4c72b0"
    color_rate = "#d62728"

    ax_line.bar(hourly.index, hourly["total"], color=color_vol, alpha=0.45, label="All OOR events (left)")
    ax_line.bar(hourly.index, hourly["n_esc"], color=color_rate, alpha=0.7, label="Escalated (left)")
    ax_line.set_ylabel("Event count", color=color_vol, fontsize=9)
    ax_line.tick_params(axis="y", labelcolor=color_vol)
    ax_line.set_xticks(range(0, 24, 2))
    ax_line.set_xlabel("Hour of day (local time)", fontsize=9)

    ax2b = ax_line.twinx()
    ax2b.plot(hourly.index, hourly["rate_smooth"], color=color_rate, linewidth=2.0,
              linestyle="-", marker="o", markersize=4, label="Escalation rate % (right, smoothed)")
    ax2b.set_ylabel("Escalation rate %", color=color_rate, fontsize=9)
    ax2b.tick_params(axis="y", labelcolor=color_rate)
    ax2b.yaxis.set_major_formatter(mticker.PercentFormatter())

    # Combined legend
    lines1, labels1 = ax_line.get_legend_handles_labels()
    lines2, labels2 = ax2b.get_legend_handles_labels()
    ax_line.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper left")

    plt.tight_layout()
    plt.savefig(OUTPUTS / f"oor_escalation_by_hour_{fname_suffix}.png", dpi=DPI, bbox_inches="tight")
    plt.close()

# ---------------------------------------------------------------------------
# PART 2: DEFROST CYCLE DETECTION
#
# BOTH fridges and freezers defrost by shutting off the compressor. The key
# physical difference:
#   - Fridge: air defrost → temp peaks at 42-46°F (above the 40°F upper setpoint)
#   - Freezer: electric defrost → temp rises well above the 10°F upper setpoint
#
# In both cases defrost shows up as a short "high" OOR event.
#
# SHAPE is the key distinguisher from door-open / rush events:
#   - Defrost = smooth sawtooth dome: clean monotone rise → peak near END of event
#     → sharp recovery drop (compressor kicks on hard at timer end)
#   - Door-open = jagged (compressor still cycling → oscillations in the signal)
#   - Rush = many small high-frequency spikes
#
# Shape features:
#   diff_std       : std of 2-min T differences — low = smooth (defrost), high = jagged
#   rise_frac      : fraction of steps rising in first 2/3 of event — high = clean rise
#   peak_pos_frac  : where max T occurs (0=start, 1=end) — defrost peaks late
#   skewness       : negative = long rise then sharp drop (defrost asymmetry)
#
# After filtering by shape, check inter-event gaps for ~6-8h periodicity.
# ---------------------------------------------------------------------------

print("\n--- Part 2: Defrost cycle detection ---")

# ---- 2A: Shape-based defrost candidate filtering (both fridge and freezer) ----

DEFROST_DUR_MIN = 10   # min duration (min) — 20-30 min is the sweet spot
DEFROST_DUR_MAX = 50   # max — excludes stuck-timer / equipment failures
DEFROST_GAP_LO  = 200  # shortest plausible gap between cycles (min)
DEFROST_GAP_HI  = 540  # longest — 9h would be unusual but possible
DEFROST_CV_MAX  = 0.70 # coefficient of variation on gaps

# Step 1: candidate pool — short high OOR events in either appliance type
high_short = ev[
    (ev["direction"] == "high") &
    (ev["duration_mins"] >= DEFROST_DUR_MIN) &
    (ev["duration_mins"] <= DEFROST_DUR_MAX)
].copy()

print(f"  Short high-OOR events ({DEFROST_DUR_MIN}–{DEFROST_DUR_MAX} min): "
      f"{len(high_short):,} across {high_short['zone_name'].nunique()} zones")
print(f"    Fridges:  {(high_short['appliance_type']=='fridge').sum():,}")
print(f"    Freezers: {(high_short['appliance_type']=='freezer').sum():,}")

# Step 2: shape scoring — define a defrost score combining smoothness + peak position
# Defrost: low diff_std (smooth), high rise_frac, high peak_pos_frac, negative skewness
# Normalize each feature to 0-1 and sum into a "defrost score"

def _percentile_rank(series: pd.Series) -> pd.Series:
    return series.rank(pct=True)

hs = high_short.dropna(subset=["diff_std", "peak_pos_frac", "rise_frac"]).copy()

# Smoothness: low diff_std = smooth → invert rank
hs["score_smooth"]   = 1 - _percentile_rank(hs["diff_std"])
# Rise fraction in first 2/3: high = clean monotone rise
hs["score_rise"]     = _percentile_rank(hs["rise_frac"])
# Peak position: high = peak is near the end of the event (timer end)
hs["score_peak_pos"] = _percentile_rank(hs["peak_pos_frac"])

hs["defrost_score"] = (hs["score_smooth"] + hs["score_rise"] + hs["score_peak_pos"]) / 3.0

# Label events with score > 0.55 as "defrost-shaped"
DEFROST_SCORE_THRESH = 0.55
hs["defrost_shaped"] = hs["defrost_score"] >= DEFROST_SCORE_THRESH

print(f"\n  Shape-filtered defrost candidates: {hs['defrost_shaped'].sum():,} "
      f"({100*hs['defrost_shaped'].mean():.0f}% of short-high events)")

# Print shape stats by type
for atype in ["fridge", "freezer"]:
    sub = hs[hs["appliance_type"] == atype]
    if sub.empty:
        continue
    def_sub = sub[sub["defrost_shaped"]]
    non_sub = sub[~sub["defrost_shaped"]]
    print(f"\n  {atype.capitalize()} shape stats:")
    print(f"    Defrost-shaped ({len(def_sub)}):     "
          f"diff_std={def_sub['diff_std'].median():.3f}  "
          f"rise_frac={def_sub['rise_frac'].median():.2f}  "
          f"peak_pos={def_sub['peak_pos_frac'].median():.2f}  "
          f"skew={def_sub['skewness'].median():.2f}")
    print(f"    Non-defrost   ({len(non_sub)}):     "
          f"diff_std={non_sub['diff_std'].median():.3f}  "
          f"rise_frac={non_sub['rise_frac'].median():.2f}  "
          f"peak_pos={non_sub['peak_pos_frac'].median():.2f}  "
          f"skew={non_sub['skewness'].median():.2f}")

# --- 2A-i: Shape feature distributions plot ---

print("\n  Plotting shape feature distributions...")

fig, axes = plt.subplots(2, 4, figsize=(16, 9), dpi=DPI)
fig.suptitle(
    "OOR Event Shape Analysis — Defrost-Shaped vs Door-Open/Rush\n"
    "(short high-OOR events only: 10–50 min; both fridges and freezers)",
    fontsize=11, fontweight="bold"
)

shape_feats = [
    ("diff_std",      "T diff std (low = smooth)"),
    ("rise_frac",     "Rise fraction first 2/3"),
    ("peak_pos_frac", "Peak position (0=start, 1=end)"),
    ("skewness",      "Skewness (negative = sharp recovery)"),
]

for row_i, atype in enumerate(["fridge", "freezer"]):
    sub = hs[hs["appliance_type"] == atype]
    for col_i, (feat, flabel) in enumerate(shape_feats):
        ax = axes[row_i][col_i]
        d_yes = sub.loc[sub["defrost_shaped"], feat].dropna()
        d_no  = sub.loc[~sub["defrost_shaped"], feat].dropna()
        if d_yes.empty and d_no.empty:
            continue
        all_vals = pd.concat([d_yes, d_no])
        lo, hi = all_vals.quantile(0.02), all_vals.quantile(0.98)
        bins = np.linspace(lo, hi, 25)
        ax.hist(d_no,  bins=bins, alpha=0.6, density=True, color="#d62728", label="Door/rush")
        ax.hist(d_yes, bins=bins, alpha=0.6, density=True, color="#2ca02c", label="Defrost-shaped")
        ax.set_title(f"{atype.capitalize()} — {flabel}", fontsize=7.5, fontweight="bold")
        ax.tick_params(labelsize=7)
        ax.set_ylabel("Density", fontsize=7)
        if row_i == 0 and col_i == 0:
            ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig(OUTPUTS / "defrost_shape_features.png", dpi=DPI, bbox_inches="tight")
plt.close()

# --- 2A-ii: Example event profiles — defrost vs door-open ---

print("  Plotting example event profiles (defrost vs door-open shape)...")

def _get_raw_T(zone_name: str, start_dt, end_dt) -> pd.Series:
    mask = (
        (df["zone_name"] == zone_name) &
        (df["datetime"] >= start_dt) &
        (df["datetime"] <= end_dt)
    )
    return df.loc[mask].sort_values("datetime")["T"]

fig, axes = plt.subplots(2, 6, figsize=(18, 8), dpi=DPI)
fig.suptitle(
    "Event Profile Examples — Defrost (smooth dome) vs Door-Open (jagged)\n"
    "Both fridges and freezers shown; dashed line = upper setpoint",
    fontsize=11, fontweight="bold"
)

for row_i, atype in enumerate(["fridge", "freezer"]):
    sub = hs[hs["appliance_type"] == atype].copy()
    # Get 3 best-score defrost and 3 worst-score (most door-like) examples
    defrost_ex = sub[sub["defrost_shaped"]].nlargest(3, "defrost_score")
    dooropen_ex = sub[~sub["defrost_shaped"]].nsmallest(3, "defrost_score")

    for col_i, (_, row) in enumerate(list(defrost_ex.iterrows()) + list(dooropen_ex.iterrows())):
        ax = axes[row_i][col_i]
        T_raw = _get_raw_T(row["zone_name"], row["start"], row["end"])
        if T_raw.empty:
            ax.set_visible(False)
            continue

        crh = ev.loc[ev["zone_name"] == row["zone_name"], "start_T"].iloc[0]
        setpoint_high = row["start_T"] + abs(row["boundary_dist"])  # approximate

        ax.plot(range(len(T_raw)), T_raw.values,
                color="#2ca02c" if col_i < 3 else "#d62728",
                linewidth=1.5, marker=".", markersize=3)

        # Upper setpoint from data_loader
        zone_crh = df.loc[df["zone_name"] == row["zone_name"], "op_range_high"].iloc[0]
        ax.axhline(zone_crh, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)

        kind = "Defrost" if col_i < 3 else "Door/Rush"
        ax.set_title(
            f"{kind} — {row['label'][:22]}\n"
            f"{row['duration_mins']:.0f}min  sc={row['defrost_score']:.2f}",
            fontsize=7, color="#2ca02c" if col_i < 3 else "#d62728",
            fontweight="bold"
        )
        ax.set_xlabel("2-min ticks", fontsize=6)
        ax.set_ylabel("°F", fontsize=6)
        ax.tick_params(labelsize=6)

plt.tight_layout()
plt.savefig(OUTPUTS / "defrost_event_profiles.png", dpi=DPI, bbox_inches="tight")
plt.close()

# ---- Step 3: Periodicity check — ALL short-high events, shape as per-zone validator ----
#
# Shape filtering globally breaks periodic detection (it's biased by zone temperature
# dynamics and event count). Instead:
#   1. Find periodic zones using all short-high events (duration + gap + CV)
#   2. Per periodic zone, show what fraction of events are defrost-shaped — this is
#      the validation that the periodic signal is real defrost and not door-open noise.
# ----

defrost_summary = []

for (zone, atype), grp in high_short.groupby(["zone_name", "appliance_type"]):
    grp = grp.sort_values("start")
    n_days = max(1, (grp["start"].max() - grp["start"].min()).days)
    if len(grp) < 4:
        continue

    gaps = grp["start"].diff().dt.total_seconds().dropna() / 60.0
    median_gap = gaps.median()
    cv = gaps.std() / gaps.mean() if gaps.mean() > 0 else np.nan

    if not np.isnan(median_gap) and median_gap > 0:
        tight_fraction = ((gaps >= median_gap * 0.5) & (gaps <= median_gap * 1.5)).mean()
    else:
        tight_fraction = 0.0

    is_periodic = (
        DEFROST_GAP_LO <= median_gap <= DEFROST_GAP_HI
        and not np.isnan(cv)
        and cv < DEFROST_CV_MAX
        and tight_fraction >= 0.45
    )

    defrost_summary.append({
        "zone_name":       zone,
        "appliance_type":  atype,
        "label":           grp["label"].iloc[0],
        "n_events":        len(grp),
        "events_per_day":  round(len(grp) / n_days, 2),
        "median_gap_min":  round(median_gap, 0),
        "median_gap_hr":   round(median_gap / 60, 2),
        "gap_cv":          round(cv, 3) if not np.isnan(cv) else None,
        "tight_fraction":  round(tight_fraction, 2),
        "median_dur_min":  round(grp["duration_mins"].median(), 1),
        # Shape validation: what fraction of events in this zone are defrost-shaped?
        "defrost_shape_frac": round(grp["defrost_shaped"].mean(), 3) if "defrost_shaped" in grp.columns else np.nan,
        "periodic":        is_periodic,
    })

defrost_df = pd.DataFrame(defrost_summary).sort_values(["appliance_type", "gap_cv"]) if defrost_summary else pd.DataFrame()
periodic = defrost_df[defrost_df["periodic"]] if not defrost_df.empty else pd.DataFrame()

print(f"\n  All zone periodicity results (shape-filtered events, sorted by CV):")
for atype in ["fridge", "freezer"]:
    sub_d = defrost_df[defrost_df["appliance_type"] == atype] if not defrost_df.empty else pd.DataFrame()
    if sub_d.empty:
        print(f"\n  {atype.capitalize()}: no zones with ≥4 defrost-shaped events")
        continue
    print(f"\n  {atype.capitalize()}:")
    for _, r in sub_d.iterrows():
        flag = " ✓ DEFROST" if r["periodic"] else ""
        shape_str = f"  shape={r['defrost_shape_frac']:.2f}" if not np.isnan(r.get("defrost_shape_frac", np.nan)) else ""
        print(f"    {r['label']:45s}  "
              f"n={r['n_events']:3d}  {r['events_per_day']:.1f}/day  "
              f"gap={r['median_gap_hr']:.1f}h  CV={r['gap_cv']:.3f}  "
              f"tight={r['tight_fraction']:.2f}  dur={r['median_dur_min']:.0f}min{shape_str}{flag}")

# Gap histograms
print("\n  Plotting defrost gap histograms...")

for atype, fname_suffix in [("fridge", "fridges"), ("freezer", "freezers")]:
    sub_d = defrost_df[defrost_df["appliance_type"] == atype] if not defrost_df.empty else pd.DataFrame()
    if sub_d.empty:
        continue
    zone_list = sub_d["zone_name"].tolist()
    cols = min(4, len(zone_list))
    rows = -(-len(zone_list) // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3.5), dpi=DPI)
    axes_flat = axes.flatten() if hasattr(axes, "flatten") else [axes]
    fig.suptitle(
        f"{atype.capitalize()} Defrost — Gap Between Shape-Filtered Events\n"
        "(green = periodic 4–9h cycle detected; dashed = 6h and 8h reference lines)",
        fontsize=11, fontweight="bold"
    )
    for ax, zone in zip(axes_flat, zone_list):
        grp = high_short[
            (high_short["zone_name"] == zone) &
            (high_short["appliance_type"] == atype)
        ].sort_values("start")
        gaps = grp["start"].diff().dt.total_seconds().dropna() / 60.0
        row = sub_d[sub_d["zone_name"] == zone].iloc[0]

        ax.hist(gaps.clip(0, 800), bins=min(25, max(5, len(gaps) // 2)),
                color="#4c72b0", alpha=0.8, edgecolor="white")
        for marker, color, mlabel in [(360, "#2ca02c", "6h"), (480, "#ff7f0e", "8h")]:
            ax.axvline(marker, color=color, linestyle="--", linewidth=1.2, alpha=0.9, label=mlabel)

        title_color = "#2ca02c" if row["periodic"] else "#555555"
        ax.set_title(
            f"{row['label']}\ngap={row['median_gap_hr']:.1f}h  CV={row['gap_cv']:.2f}  "
            f"{row['events_per_day']:.1f}/day  {row['median_dur_min']:.0f}min",
            fontsize=7.5, color=title_color,
            fontweight="bold" if row["periodic"] else "normal"
        )
        ax.set_xlabel("Gap to next event (min)", fontsize=7)
        ax.tick_params(labelsize=7)
        if ax == axes_flat[0]:
            ax.legend(fontsize=6)

    for i in range(len(zone_list), len(axes_flat)):
        axes_flat[i].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUTS / f"defrost_gap_histograms_{fname_suffix}.png", dpi=DPI, bbox_inches="tight")
    plt.close()

# Hour-of-day for periodic zones
if not periodic.empty:
    print("  Plotting defrost hour-of-day patterns...")
    n = len(periodic)
    cols = min(4, n)
    rows = -(-n // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3.0), dpi=DPI)
    axes_flat = axes.flatten() if hasattr(axes, "flatten") else [axes]
    fig.suptitle(
        "Defrost Cycle — Event Start Hour (periodic zones only)\n"
        "Peaks at fixed clock times = timer-controlled schedule",
        fontsize=11, fontweight="bold"
    )
    for ax, (_, row) in zip(axes_flat, periodic.iterrows()):
        grp = high_short[
            (high_short["zone_name"] == row["zone_name"]) &
            (high_short["appliance_type"] == row["appliance_type"])
        ]
        hourly = grp.groupby("hour").size().reindex(range(24), fill_value=0)
        ax.bar(hourly.index, hourly.values, color="#2ca02c", alpha=0.8)
        ax.set_title(
            f"{row['label']} ({row['appliance_type']})\n"
            f"{row['median_gap_hr']:.1f}h cycle  {row['median_dur_min']:.0f}min",
            fontsize=8, fontweight="bold", color="#2ca02c"
        )
        ax.set_xticks(range(0, 24, 4))
        ax.tick_params(labelsize=7)

    for i in range(n, len(axes_flat)):
        axes_flat[i].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUTS / "defrost_hour_of_day.png", dpi=DPI, bbox_inches="tight")
    plt.close()

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\nEscalation:")
for atype in ["fridge", "freezer"]:
    sub = ev[ev["appliance_type"] == atype]
    if sub.empty:
        continue
    n = len(sub)
    e = sub["escalated"].sum()
    print(f"  {atype.capitalize()}s: {e:,}/{n:,} events escalated ({100*e/n:.1f}%)")
    for feat in ["boundary_dist", "pre_slope"]:
        m_short = sub.loc[~sub["escalated"], feat].median()
        m_long  = sub.loc[ sub["escalated"], feat].median()
        print(f"    {feat:20s}: short median={m_short:+.3f}  escalated median={m_long:+.3f}")

print(f"\nDefrost cycles detected: {len(periodic)} zones")
for _, r in periodic.iterrows():
    print(f"  [{r['appliance_type']}] {r['label']:45s}  "
          f"{r['median_gap_hr']:.1f}h cycle  {r['median_dur_min']:.0f}min  {r['events_per_day']:.1f}/day")

print(f"\nOutputs saved to: {OUTPUTS.resolve()}")
for f in sorted(OUTPUTS.glob("oor_escalation_*.png")) + sorted(OUTPUTS.glob("defrost_*.png")):
    print(f"  {f.name}")

