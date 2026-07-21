# F/F Equipment Analytics

Exploratory data analysis on commercial refrigeration equipment (fridges and freezers) from different locations where hardware hub + sensors were installed. 3.5 months of temperature data from 28 fridges or freezers; data provided every 2 minutes. 

The goal was to develop a richer picture of how the equipment operated: how stable is each unit, how does it compare to the fleet, and what does its temperature behaviour look like over time? And to build this contextual information into the dashboard experience.

All location names are anonymized.

---

## Analyses and outputs

### Fleet narrative (`story.py`)

A sequence of charts that builds a complete picture of fleet health, designed to be read in order:

| Chart | File | What it shows |
|---|---|---|
| 1 | `story_1_operating_temp` | Where each location typically runs within its operating range, with fleet median and IQR as reference |
| 2 | `story_2_variability` | Temperature stability (IQR) per location — how much does the temperature move around? |
| 3 | `story_3_short_oor_rate` | Frequency of short Out of Range (OOR) events (≤30 min/day), the normal background noise of door openings and restocking |
| 6 | `story_6_position` | Where each location sits within its operating band — running cold, middle, or warm |
| 7 | `story_7_health_map` | 2D health map: temperature variability (x) vs operating position (y), with fleet healthy zone shaded; immediately shows which units are outliers and in which direction |

Each chart is produced separately for fridges and freezers.

---

### OOR escalation detail (`analysis_oor.py`)

`oor_extended_detail_fridges/freezers.png`

OOR events ≥90 consecutive minutes. For each location, shows count and a dot plot of when they started (hour of day), coloured by duration. Helps to identify locations with chronic problems.

---

### Temperature activity patterns (`temperature_raster.py`)

Two heatmap views of raw equipment temperature — no OOR filtering, every reading used. Visualized to see if there were consistent patterns in temperature variability that could be deemed "normal operations", and if these were distinct from "non-normal operations" (those that require a customer alert).

**Calendar heatmap** (`raster_calendar_fridges/freezers.png`)
Each row is one calendar day; each column is an hour of the day; colour is mean temperature. Mechanical cycles (defrost, compressor) appear as evenly-spaced vertical stripes that repeat every row. Human operational patterns (service hours, restocking) appear at consistent columns but may vary in intensity by day.

**Weekly rhythm** (`raster_weekly_fridges/freezers.png`)
Collapses the full window into 7 rows (Mon–Sun). Patterns that look identical on all 7 rows are mechanical. Patterns that vary by day reflect human activity in the restaurant.

In general, much easier to detect patters in freezers.
---

### Monthly customer health report (`customer_report.py`)

`customer_report_fridges/freezers.png`

A summary of health relative to fleet. Three panels per fridge/freezer type:
- **Avg temperature vs fleet** — each unit's monthly mean plotted against the fleet median and IQR band
- **Temperature variability** — IQR per unit vs fleet p75 threshold
- **Escalations + trend** — count of OOR events ≥90 min this month, vs fleet median/p75, with a month-over-month trend label

Units are sorted red → yellow → green. The intent is that a customer with 20 units can scan this in under a minute and know where to focus (the red units).

---

## Setup

```bash
cd ff-equipment-analytics
python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib scipy astropy pyarrow
```

Anonymized sensor data is included in `data/ff_sensors.parquet` — no additional setup needed. Run any analysis script directly; outputs are saved to `outputs/`.

```bash
python3 story.py
```
