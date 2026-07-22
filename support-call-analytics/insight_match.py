import csv
import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher

INSIGHTS_CSV = "/Users/natalieelliott/Support Automation work/Dash + Cogs Insights.csv"
AUDIT_CSV = "/Users/natalieelliott/Support Automation work/Support Call Audit.csv"
OUTPUT_CSV = "/Users/natalieelliott/Support Automation work/Support Call Audit - With Insights.csv"

LOOKBACK_DAYS = 4


def normalize(s):
    """Normalize a building name for matching."""
    s = s.lower().strip()
    # Remove common suffixes/prefixes
    for remove in ["napa auto parts -", "napa auto parts", "napa -", "burger king -", "- bk", "- napa", "- calvert county"]:
        s = s.replace(remove, "")
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def fuzzy_score(a, b):
    """Score similarity between two building names."""
    na = normalize(a)
    nb = normalize(b)

    # Exact normalized match
    if na == nb:
        return 1.0

    # One contains the other
    if na in nb or nb in na:
        return 0.9

    # Check if key address components match (street numbers, street names)
    nums_a = set(re.findall(r'\d+', na))
    nums_b = set(re.findall(r'\d+', nb))
    if nums_a and nums_b and nums_a & nums_b:
        # Shared street number — likely same building
        return max(0.8, SequenceMatcher(None, na, nb).ratio())

    # General fuzzy match
    return SequenceMatcher(None, na, nb).ratio()


def parse_insight_date(date_str):
    """Parse insight date like '4/15/2026 8:50:00'."""
    try:
        return datetime.strptime(date_str.strip(), "%m/%d/%Y %H:%M:%S")
    except ValueError:
        return None


def parse_call_date(date_str):
    """Parse call date like '2025-08-27'."""
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        return None


def split_buildings(buildings_str):
    """Split a buildings field into individual building names."""
    if not buildings_str or buildings_str.strip() == "N/A":
        return []
    # Split on semicolons, commas, or " and "
    parts = re.split(r'[;,]|\band\b', buildings_str)
    return [p.strip() for p in parts if p.strip() and p.strip() != "N/A"]


def split_zones(zones_str):
    """Split a zones field into individual zone names."""
    if not zones_str or zones_str.strip() == "N/A":
        return []
    parts = re.split(r'[;,]', zones_str)
    return [p.strip() for p in parts if p.strip() and p.strip() != "N/A"]


def zone_match(call_zones, insight_zone):
    """Check if any call zone fuzzy-matches the insight zone."""
    if not call_zones or not insight_zone:
        return False
    iz = normalize(insight_zone)
    for cz in call_zones:
        ncz = normalize(cz)
        if ncz in iz or iz in ncz:
            return True
        if SequenceMatcher(None, ncz, iz).ratio() > 0.6:
            return True
    return False


def main():
    # Load insights
    print("Loading insights...")
    insights = []
    with open(INSIGHTS_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = parse_insight_date(row["Incident Date"])
            if dt:
                insights.append({
                    "date": dt,
                    "date_only": dt.date(),
                    "identifier": row.get("Insight Identifier", ""),
                    "type": row.get("Insight Type", ""),
                    "building": row.get("Building Name", ""),
                    "zone": row.get("Zone", ""),
                    "device": row.get("Device ID", ""),
                })
    print(f"  Loaded {len(insights)} insights")

    # Load call audit
    print("Loading call audit...")
    calls = []
    with open(AUDIT_CSV) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            calls.append(row)
    print(f"  Loaded {len(calls)} calls")

    # Match
    print("Matching...")
    results = []
    match_count = 0

    for call in calls:
        call_date = parse_call_date(call.get("Call/Text Date", ""))
        if not call_date:
            call["Insight Match"] = "No"
            call["Insight Count"] = "0"
            call["Insight Details"] = ""
            results.append(call)
            continue

        call_buildings = split_buildings(call.get("Buildings Mentioned", ""))
        call_zones = split_zones(call.get("Zone Names Mentioned", ""))
        call_device = call.get("Device ID", "").strip()

        # Date window: call_date - 4 days to call_date (inclusive)
        window_start = (call_date - timedelta(days=LOOKBACK_DAYS)).date()
        window_end = call_date.date()

        matches = []
        for insight in insights:
            # Date filter
            if not (window_start <= insight["date_only"] <= window_end):
                continue

            # Building match
            best_building_score = 0
            for cb in call_buildings:
                score = fuzzy_score(cb, insight["building"])
                best_building_score = max(best_building_score, score)

            # Device ID match (strong signal)
            device_match = False
            if call_device and call_device != "N/A":
                for dev in call_device.split(";"):
                    dev = dev.strip()
                    if dev and dev in insight.get("device", ""):
                        device_match = True
                        break

            # Accept if building score > 0.6 or device match
            if best_building_score >= 0.6 or device_match:
                days_before = (call_date.date() - insight["date_only"]).days
                zone_matched = zone_match(call_zones, insight["zone"])
                matches.append({
                    "score": best_building_score,
                    "device_match": device_match,
                    "zone_match": zone_matched,
                    "days_before": days_before,
                    "insight_date": insight["date"].strftime("%Y-%m-%d %H:%M"),
                    "insight_type": insight["type"],
                    "insight_building": insight["building"],
                    "insight_zone": insight["zone"],
                    "insight_id": insight["identifier"],
                })

        if matches:
            match_count += 1
            # Sort by score descending, then days_before ascending
            matches.sort(key=lambda m: (-m["score"], m["days_before"]))
            # Take top 5 matches
            top = matches[:5]
            details = " | ".join(
                f"{m['insight_date']} - {m['insight_type']} - {m['insight_building']} - {m['insight_zone']} ({m['days_before']}d before)"
                for m in top
            )
            call["Insight Match"] = "Yes"
            call["Insight Count"] = str(len(matches))
            call["Insight Details"] = details
        else:
            call["Insight Match"] = "No"
            call["Insight Count"] = "0"
            call["Insight Details"] = ""

        results.append(call)

    # Write output
    out_fields = fieldnames + ["Insight Match", "Insight Count", "Insight Details"]
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults:")
    print(f"  Total calls: {len(results)}")
    print(f"  Calls with matching insights: {match_count}")
    print(f"  Calls without matches: {len(results) - match_count}")
    print(f"\nOutput: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
