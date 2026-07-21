"""Temperature activity patterns — calendar heatmap and weekly rhythm

Views raw equipment temperature through a time-of-day lens to reveal
recurring patterns across the full observation window without any OOR
filtering. Every reading is used.

TWO CHARTS PER APPLIANCE TYPE
------------------------------
Calendar heatmap  — rows = calendar days, columns = hour of day
                    colour = hourly mean temperature
                    Repeating vertical stripes = same-time-of-day pattern
                    every day (mechanical or daily human routine)
                    Evenly-spaced stripes within a row = sub-daily cycle
                    (defrost every 6h → 4 warm bands per row, every day)

Weekly rhythm     — rows = Mon–Sun, columns = hour of day
                    colour = mean temperature averaged across all weeks
                    Mechanical cycles look identical on all 7 rows
                    Human activity varies by day (busier service windows,
                    different restocking days, etc.)

All zones included — no locations excluded. This is exploratory: we want
to see the full signal.

Usage:
    cd ~/Desktop/cogsworth
    source experiments/natalie/.venv/bin/activate
    python3 experiments/natalie/temperature_raster.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from data_loader import load

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
DPI = 130

# Fridge scale: 34–40°F, dark blue→white. Anything ≥40°F clips to white.
FRIDGE_VMIN = 34.0
FRIDGE_VMAX = 40.0

DOW_ORDER  = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DOW_SHORT  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ---------------------------------------------------------------------------
# Load and prepare
# ---------------------------------------------------------------------------

print("Loading data...")
df = load()
df["datetime"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_convert("America/New_York")
df["label"]    = df["building"].str.replace(r"^\d+ - ", "", regex=True)
df["date"]     = df["datetime"].dt.date
df["hour"]     = df["datetime"].dt.hour
df["dow"]      = df["datetime"].dt.dayofweek        # 0=Mon, 6=Sun
df["dow_name"] = df["datetime"].dt.day_name()

# ---------------------------------------------------------------------------
# Chart 1: Calendar heatmap — rows=days, cols=hours
# ---------------------------------------------------------------------------

print("\nPlotting calendar heatmaps...")

for atype, fname in [("fridge",  "raster_calendar_fridges.png"),
                     ("freezer", "raster_calendar_freezers.png")]:
    sub = df[df["appliance_type"] == atype]
    zone_list = (
        sub.groupby(["label", "zone_name"])
        .size()
        .reset_index()[["label", "zone_name"]]
        .values.tolist()
    )
    if not zone_list:
        continue

    # Fridges: fixed 31–41°F scale, blue gradient (dark=cold, white=warm)
    # Freezers: per-zone scale, diverging colour
    if atype == "fridge":
        cmap_str   = "Blues_r"
        fixed_vmin = FRIDGE_VMIN
        fixed_vmax = FRIDGE_VMAX
    else:
        cmap_str   = "RdBu_r"
        fixed_vmin = None
        fixed_vmax = None

    n     = len(zone_list)
    ncols = 3
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(ncols * 5.5, nrows * 5 + 2), dpi=DPI
    )
    axes_flat = np.array(axes).flatten()

    fig.suptitle(
        f"Temperature Calendar Heatmap — {'Fridges' if atype=='fridge' else 'Freezers'}\n"
        "Rows = calendar days  |  Columns = hour of day  |  Colour = mean temperature °F\n"
        "Vertical stripe every row = daily pattern  |  "
        "Evenly-spaced stripes = mechanical cycle (e.g. defrost every 6h → 4 bands/day)",
        fontsize=10, fontweight="bold"
    )

    for i, (lbl, zone_name) in enumerate(zone_list):
        ax  = axes_flat[i]
        grp = sub[(sub["label"] == lbl) & (sub["zone_name"] == zone_name)]

        hourly = grp.groupby(["date", "hour"])["T"].mean().reset_index()
        pivot  = hourly.pivot(index="date", columns="hour", values="T")
        pivot  = pivot.reindex(columns=range(24))

        vmin = fixed_vmin if fixed_vmin is not None else float(grp["T"].quantile(0.02))
        vmax = fixed_vmax if fixed_vmax is not None else float(grp["T"].quantile(0.98))

        im = ax.imshow(
            pivot.values, aspect="auto",
            cmap=cmap_str, vmin=vmin, vmax=vmax,
            interpolation="nearest"
        )

        # Y-axis: label at month boundaries
        dates = list(pivot.index)
        month_ticks, month_labels, prev_month = [], [], None
        for row_i, d in enumerate(dates):
            if d.month != prev_month:
                month_ticks.append(row_i)
                month_labels.append(pd.Timestamp(d).strftime("%b %d"))
                prev_month = d.month
        ax.set_yticks(month_ticks)
        ax.set_yticklabels(month_labels, fontsize=6.5)

        ax.set_xticks(range(0, 24, 4))
        ax.set_xticklabels([f"{h:02d}h" for h in range(0, 24, 4)], fontsize=6.5)

        cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        cb.set_label("°F", fontsize=7)
        cb.ax.tick_params(labelsize=6)

        ax.set_title(f"{lbl}\n{zone_name}", fontsize=7.5, fontweight="bold")
        ax.set_xlabel("Hour of day", fontsize=7)
        ax.spines[["top", "right"]].set_visible(False)

    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")

# ---------------------------------------------------------------------------
# Chart 2: Weekly rhythm — 7 rows × 24 cols
# ---------------------------------------------------------------------------

print("\nPlotting weekly rhythm heatmaps...")

for atype, fname in [("fridge",  "raster_weekly_fridges.png"),
                     ("freezer", "raster_weekly_freezers.png")]:
    sub = df[df["appliance_type"] == atype]
    zone_list = (
        sub.groupby(["label", "zone_name"])
        .size()
        .reset_index()[["label", "zone_name"]]
        .values.tolist()
    )
    if not zone_list:
        continue

    if atype == "fridge":
        cmap_str   = "Blues_r"
        fixed_vmin = FRIDGE_VMIN
        fixed_vmax = FRIDGE_VMAX
    else:
        cmap_str   = "RdBu_r"
        fixed_vmin = None
        fixed_vmax = None

    n     = len(zone_list)
    ncols = 3
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(ncols * 5, nrows * 3 + 2), dpi=DPI
    )
    axes_flat = np.array(axes).flatten()

    fig.suptitle(
        f"Weekly Temperature Rhythm — {'Fridges' if atype=='fridge' else 'Freezers'}\n"
        "Rows = day of week  |  Columns = hour of day  |  "
        "Colour = mean temperature °F averaged across all weeks\n"
        "Warm bands identical on all 7 rows → mechanical cycle  |  "
        "Warm bands varying by day → human operational pattern",
        fontsize=10, fontweight="bold"
    )

    for i, (lbl, zone_name) in enumerate(zone_list):
        ax  = axes_flat[i]
        grp = sub[(sub["label"] == lbl) & (sub["zone_name"] == zone_name)]

        weekly = grp.groupby(["dow", "hour"])["T"].mean().reset_index()
        pivot  = weekly.pivot(index="dow", columns="hour", values="T")
        pivot  = pivot.reindex(index=range(7), columns=range(24))

        vmin = fixed_vmin if fixed_vmin is not None else float(grp["T"].quantile(0.02))
        vmax = fixed_vmax if fixed_vmax is not None else float(grp["T"].quantile(0.98))

        im = ax.imshow(
            pivot.values, aspect="auto",
            cmap=cmap_str, vmin=vmin, vmax=vmax,
            interpolation="nearest"
        )

        ax.set_yticks(range(7))
        ax.set_yticklabels(DOW_SHORT, fontsize=7)
        ax.set_xticks(range(0, 24, 4))
        ax.set_xticklabels([f"{h:02d}h" for h in range(0, 24, 4)], fontsize=6.5)

        cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        cb.set_label("°F", fontsize=7)
        cb.ax.tick_params(labelsize=6)

        ax.set_title(f"{lbl}\n{zone_name}", fontsize=7.5, fontweight="bold")
        ax.set_xlabel("Hour of day", fontsize=7)
        ax.spines[["top", "right"]].set_visible(False)

    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUTS / fname, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  saved {fname}")

print(f"\nOutputs saved to {OUTPUTS}")
print("\nWhat to look for:")
print("  Calendar heatmap — vertical stripes every row = same-time daily pattern")
print("                      evenly-spaced bands = mechanical cycle (count bands/day → period)")
print("  Weekly rhythm    — flat across all 7 rows = mechanical (defrost, compressor)")
print("                      varies by day = human activity (service hours, restocking)")
