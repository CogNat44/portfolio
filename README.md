# Portfolio — Natalie Elliott

A selection of projects built for Cognition Controls.

---

## index.html — Website Home Page Revamp

Revamped the Cognition Controls home page with a focus on trust and conversion.

- Used Nano Banana to generate an AI video for the hero banner that showcases the hardware in a QSR setting and a user interacting with the Cognition Dashboard
- Organized page content to demonstrate trust including customer logos and reviews, and to highlight product differentiators and application for different customer types
- Structured the page to guide visitors from awareness to action

**[View live →](https://cognat44.github.io/portfolio/)**

---

## support-call-analytics/ — AI-Powered Support Call Analytics Pipeline

Built an end-to-end pipeline to analyze 245 support call recordings and surface automation opportunities.

- **Transcription** (`transcribe.py`): Used OpenAI Whisper (medium model) + pyannote speaker diarization to convert MP3 recordings to speaker-labeled transcripts, with PyTorch MPS (Apple GPU) acceleration and post-processing to enforce clean 2-speaker output
- **Structured analysis** (`analysis_prompt.md` + `combine_results.py`): Ran 10 parallel Claude agents against the transcripts to extract 22 structured fields per call (issue category, complexity, resolution path, emotional tone, etc.), then combined and normalized agent output into a clean CSV
- **Insight matching** (`insight_match.py`): Fuzzy-matched the 195-call audit against 6,138 system monitoring events using building name similarity, 4-day date windowing, and device ID correlation, identifying which customer calls had already been flagged by the system before the customer reached out
- **Output** (`Support Call Audit - With Insights.csv`): Final audit with insight match data, showing that a significant portion of calls were preventable with proactive outreach

---

## cognition-purchase-flow/ — Customer Purchase Flow

Mocked up an interactive purchase flow in React, designed to guide different customer types (existing customer, new customer, and prospect with a customer code) through slightly tailored buying experiences.

To run locally:

```bash
cd cognition-purchase-flow
npm install && npm start
```

---

## cognition-onboarding-flow/ — Installer Onboarding Flow

Rebuilt the configuration and onboarding flow using React. The experience begins when an installer scans the unque QR code on the hardware. This takes them to this flow. The intent with the rebuild was to rememdy some of the issues uncovered in from the support call analysis work, as well as streamline and provide better info in-flow.

- Supports both HVAC and Refrigeration hardware installs (branch at the beginning)
- Prompts through power check, wiring (HVAC), equipment config, sensor pairing, zone setup, connectivity tracking, and troubleshooting
- Built with React and inline styles, displayed in a mobile phone frame
- Information gathered during config prompts internal team that install is beginning and enables tracking for proactive assistance if required. 

To run locally:

```bash
cd cognition-onboarding-flow
npm install && npm start
```

---

## cognition-case-studies.html — Case Study Template & Content

Developed a reusable case study format and wrote five case studies covering relevant customer types and problem areas.

- Built a page template for structure consistency: hero image, stat cards, challenge block, body sections, trusted brands strip, and CTA
- Wrote case studies for customer and issue coverage, including retail multi-site rollout, QSR refrigeration & HVAC, municipal public buildings, automotive dealership, and refrigeration monitoring

**[View live →](https://cognat44.github.io/portfolio/cognition-case-studies.html)**

---

## ff-equipment-analytics/ — F/F Equipment Analytics

Exploratory data analysis on commercial refrigeration equipment (fridges and freezers). 3.5 months of temperature data from 28 units; readings every 2 minutes. Goal was to build a richer picture of equipment health — how stable each unit is, how it compares to the fleet — and feed those insights into the dashboard experience.

All location names are anonymized. Sensor data is included in `data/ff_sensors.parquet` — no additional setup needed.

- **Fleet narrative** (`story.py`): A sequence of charts that builds a complete picture of fleet health — operating temperature position, temperature stability (IQR), short OOR event rate, and a 2D health map (variability vs. position) that immediately shows which units are outliers
- **OOR escalation detail** (`analysis_oor.py`): OOR events ≥90 consecutive minutes — count and hour-of-day dot plot per location, coloured by duration; identifies locations with chronic problems
- **Temperature activity patterns** (`temperature_raster.py`): Calendar heatmap and weekly rhythm views of raw equipment temperature, separating mechanical cycles (defrost, compressor) from human operational patterns
- **Monthly customer health report** (`customer_report.py`): Three-panel summary per unit — avg temperature vs. fleet, variability vs. fleet, and escalation count with trend — sorted red → yellow → green so a customer with 20 units can scan it in under a minute

To run:

```bash
cd ff-equipment-analytics
python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib scipy astropy pyarrow
python3 story.py   # or any other analysis script
```

Outputs are saved to `outputs/`.
