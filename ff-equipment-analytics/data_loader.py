"""Fridge/freezer data loader.

Anonymized sensor data is included in data/ff_sensors.parquet — no setup needed.
The build() function is provided for reference if you want to rebuild from your own
source CSVs using the same zone/device mapping.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
SENSOR_PARQUET = DATA_DIR / "ff_sensors.parquet"

t0 = 1764547200  # Dec 1, 2025 00:00 UTC
t1 = 1773619200  # Mar 16, 2026 00:00 UTC (= Mar 15 Eastern)

SETPOINTS = {
    "fridge":  {"crl": 33.0, "crh": 40.0},
    "freezer": {"crl": -10.0, "crh": 10.0},
}
EXPECTED_MID = {"fridge": 36.5, "freezer": 0.0}

ZONES = [
    # The King locations
    {"building": "The King - Store 01",          "device": "CCTHR30000300", "zid": 331,  "name": "331 - Freezer Hub",                      "type": "freezer"},
    {"building": "The King - Store 01",          "device": "CCTHR30000300", "zid": 365,  "name": "365 - Fridge Hub",                       "type": "fridge"},
    {"building": "The King - Store 02",           "device": "CCTHR30000302", "zid": 338,  "name": "338 - Fridge Hub",                       "type": "fridge"},
    {"building": "The King - Store 02",           "device": "CCTHR30000347", "zid": 364,  "name": "364 - Freezer Hub",                      "type": "freezer"},
    {"building": "The King - Store 03",               "device": "CCTHR30000404", "zid": 337,  "name": "337 - Walk-in Freezer",                  "type": "freezer"},
    {"building": "The King - Store 03",               "device": "CCTHR30000404", "zid": 366,  "name": "366 - Walk-in Fridge",                   "type": "fridge",   "fallback_zid": 337},
    {"building": "The King - Store 04",               "device": "SCC647",        "zid": 452,  "name": "452 - Walk-in Fridge",                   "type": "fridge"},
    {"building": "The King - Store 04",               "device": "SCC647",        "zid": 453,  "name": "453 - Walk-in Freezer",                  "type": "freezer",  "fallback_zid": 452},
    {"building": "The King - Store 04",               "device": "SCC578",        "zid": 464,  "name": "464 - Walk-in Freezer (Outdoor)",         "type": "freezer"},
    {"building": "The King - Store 05",          "device": "SCC559",        "zid": 457,  "name": "457 - Walk-in Fridge",                   "type": "fridge"},
    {"building": "The King - Store 05",          "device": "SCC559",        "zid": 458,  "name": "458 - Walk-in Freezer",                  "type": "freezer",  "fallback_zid": 457},
    {"building": "The King - Store 06",          "device": "SCC634",        "zid": 469,  "name": "469 - Walk-in Fridge",                   "type": "fridge"},
    {"building": "The King - Store 06",          "device": "SCC634",        "zid": 470,  "name": "470 - Walk-in Freezer (Back)",            "type": "freezer",  "fallback_zid": 469},
    {"building": "The King - Store 06",          "device": "SCC654",        "zid": 471,  "name": "471 - Walk-in Freezer (Front)",           "type": "freezer"},
    {"building": "The King - Store 07",  "device": "SCC589",        "zid": 477,  "name": "477 - Walk-in Fridge",                   "type": "fridge"},
    {"building": "The King - Store 07",  "device": "SCC589",        "zid": 478,  "name": "478 - Walk-in Freezer",                  "type": "freezer",  "fallback_zid": 477},
    {"building": "The King - Store 08",       "device": "SCC624",        "zid": 484,  "name": "484 - Walk-in Freezer",                  "type": "freezer"},
    {"building": "The King - Store 08",       "device": "SCC624",        "zid": 485,  "name": "485 - Walk-in Fridge",                   "type": "fridge",   "fallback_zid": 484},
    {"building": "The King - Store 09",       "device": "SCC649",        "zid": 488,  "name": "488 - Walk-in Fridge",                   "type": "fridge"},
    {"building": "The King - Store 09",       "device": "SCC649",        "zid": 489,  "name": "489 - Walk-in Freezer",                  "type": "freezer",  "fallback_zid": 488},
    {"building": "The King - Store 10",     "device": "SCC502",        "zid": 490,  "name": "490 - Walk-in Fridge",                   "type": "fridge"},
    {"building": "The King - Store 10",     "device": "SCC502",        "zid": 491,  "name": "491 - Walk-in Freezer",                  "type": "freezer",  "fallback_zid": 490},
    # Donut
    {"building": "Donut - Store 01", "device": "CCTHR3000081", "zid": 399, "name": "399 - Walk-in Fridge",                  "type": "fridge"},
    {"building": "Donut - Store 01", "device": "CCTHR3000081", "zid": 400, "name": "400 - Walk-in Freezer",                 "type": "freezer",  "fallback_zid": 399},
    # Shwarma
    {"building": "Shwarma - Store 01", "device": "SCC584",   "zid": 1083, "name": "1083 - Walk-In Freezer",                "type": "freezer"},
    {"building": "Shwarma - Store 01", "device": "SCC584",   "zid": 1084, "name": "1084 - Walk-In Fridge",                 "type": "fridge",   "fallback_zid": 1083},
    {"building": "Shwarma - Store 02",        "device": "SCC563",   "zid": 1092, "name": "1092 - Walk-In Fridge",                 "type": "fridge"},
    # Pizza
    {"building": "Pizza - Store 01",                    "device": "SCC598",   "zid": 1247, "name": "1247 - Walk-In Fridge",                 "type": "fridge"},
    # Smoothie
    {"building": "Smoothie - Store 01",          "device": "SCC570",   "zid": 1259, "name": "1259 - Main Freezer",                   "type": "freezer"},
    {"building": "Smoothie - Store 01",          "device": "SCC570",   "zid": 1260, "name": "1260 - Back-up Freezer",                "type": "freezer",  "fallback_zid": 1259},
    {"building": "Smoothie - Store 01",          "device": "SCC656",   "zid": 1262, "name": "1262 - Drive Thru Hand Out Fridge",      "type": "fridge"},
]

_CONNECTIVITY_COLS = ["broker_connection", "activity", "power", "rssi", "rsrp", "rsrq", "sinr"]


def _load_cache(device: str, zid: int, fallback_zid: int | None = None) -> pd.DataFrame | None:
    files = sorted(Path.home().glob(f".cogcache/{device}Z{zid}-{t0}-{t1}.csv"))
    if not files and fallback_zid is not None:
        files = sorted(Path.home().glob(f".cogcache/{device}Z{fallback_zid}-{t0}-{t1}.csv"))
    if not files:
        return None
    df = pd.read_csv(files[0])
    df["datetime"] = (
        pd.to_datetime(df["t"], unit="s")
        .dt.tz_localize("UTC")
        .dt.tz_convert("America/New_York")
    )
    for col in df.columns:
        if col.endswith(".T") and ":" in col:
            df[col] = (df[col] * 0.005) * 9.0 / 5 + 32
    return df


def _pick_temp_col(df: pd.DataFrame, zone_type: str) -> str | None:
    expected_mid = EXPECTED_MID[zone_type]
    candidates = [c for c in df.columns if c.endswith(".T") and ":" in c]
    valid = [c for c in candidates if df[c].notna().sum() > 100]
    if not valid:
        return None
    return min(valid, key=lambda c: abs(df[c].dropna().median() - expected_mid))


def _extract_zone(zone: dict) -> pd.DataFrame | None:
    df = _load_cache(zone["device"], zone["zid"], zone.get("fallback_zid"))
    if df is None:
        log.warning("No cache file for %s zid=%s", zone["device"], zone["zid"])
        return None

    temp_col = _pick_temp_col(df, zone["type"])
    if temp_col is None:
        log.warning("No temperature sensor found for %s zid=%s", zone["device"], zone["zid"])
        return None

    connectivity = [c for c in _CONNECTIVITY_COLS if c in df.columns]
    keep = ["t", "datetime", temp_col, *connectivity]
    out = df[keep].copy().rename(columns={temp_col: "T"})
    out["mac"] = temp_col.split(".")[0]

    crl = SETPOINTS[zone["type"]]["crl"]
    crh = SETPOINTS[zone["type"]]["crh"]
    out["in_range"] = (out["T"] >= crl) & (out["T"] <= crh)

    out["building"] = zone["building"]
    out["zone_name"] = zone["name"]
    out["device_id"] = zone["device"]
    out["zone_id"] = zone["zid"]
    out["appliance_type"] = zone["type"]
    out["op_range_low"] = crl
    out["op_range_high"] = crh

    return out.reset_index(drop=True)


def build(force: bool = False) -> None:
    """Extract all zones from ~/.cogcache and save to parquet."""
    if SENSOR_PARQUET.exists() and not force:
        log.info("Parquet already exists at %s — skipping. Pass --force to rebuild.", SENSOR_PARQUET)
        return

    DATA_DIR.mkdir(exist_ok=True)

    frames = []
    for zone in ZONES:
        result = _extract_zone(zone)
        if result is not None:
            frames.append(result)
            log.info("Loaded %s zid=%s (%d rows)", zone["device"], zone["zid"], len(result))
        else:
            log.warning("Skipped %s zid=%s", zone["device"], zone["zid"])

    if not frames:
        log.error("No data loaded. Make sure ~/.cogcache has files for t0=%d t1=%d", t0, t1)
        return

    combined = pd.concat(frames, ignore_index=True)
    combined.to_parquet(SENSOR_PARQUET, index=False)
    log.info(
        "Saved %d rows, %d zones, %d buildings to %s",
        len(combined),
        len(frames),
        combined["building"].nunique(),
        SENSOR_PARQUET,
    )


def load() -> pd.DataFrame:
    """Return the parquet DataFrame, building it first if needed."""
    if not SENSOR_PARQUET.exists():
        build()
    return pd.read_parquet(SENSOR_PARQUET)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    build(force="--force" in sys.argv)
