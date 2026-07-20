# Portfolio — Natalie Elliott

A selection of web projects built for Cognition Controls.

---

## index.html — Website Home Page Revamp

Revamped the Cognition Controls home page with a focus on trust and conversion.

- Used Nano Banana to generate an AI video for the hero banner that showcases the hardware in a QSR setting and a user interacting with the Cognition Dashboard
- Organized page content to demonstrate trust including customer logos and reviews,and to highlight product differentiators and application for different customer types
- Structured the page to guide visitors from awareness to action

---

## support-call-analytics/ — AI-Powered Support Call Analytics Pipeline

Built an end-to-end pipeline to analyze 245 support call recordings and surface automation opportunities.

- **Transcription** (`transcribe.py`): Used OpenAI Whisper (medium model) + pyannote speaker diarization to convert MP3 recordings to speaker-labeled transcripts, with PyTorch MPS (Apple GPU) acceleration and post-processing to enforce clean 2-speaker output
- **Structured analysis** (`analysis_prompt.md` + `combine_results.py`): Ran 10 parallel Claude agents against the transcripts to extract 22 structured fields per call (issue category, complexity, resolution path, emotional tone, etc.), then combined and normalized agent output into a clean CSV
- **Insight matching** (`insight_match.py`): Fuzzy-matched the 195-call audit against 6,138 system monitoring events using building name similarity, 4-day date windowing, and device ID correlation, identifying which customer calls had already been flagged by the system before the customer reached out
- **Output** (`Support Call Audit - With Insights.csv`): Final audit with insight match data, showing that a significant portion of calls were preventable with proactive outreach

---

## cognition-purchase-flow/ — Customer Purchase Flow

Mocked up an interactive purchase flow in React, designed to guide different customer types (existing customer, new customer, and prospect with a customer code) through tailored buying experiences.

To run: `npm install && npm start`

---

## cognition-onboarding-flow/ — Installer Onboarding Flow

Built an interactive installation flow in React for Cognition Controls field installers, covering HVAC and F/F (fridge/freezer) device setup end-to-end.

- Dual-path flow supporting HVAC thermostat installs and F/F hub + sensor installs
- Screens cover power check, wiring, equipment config, sensor pairing, zone setup, connectivity tracking, and troubleshooting
- Context-aware troubleshooting screens, scrollable temperature range inputs, multi-sensor support, and a mock connectivity tracker
- Built entirely with React and inline styles, displayed in a mobile phone frame

To run: `npm install && npm start`

---

## cognition-case-studies.html — Case Study Template & Content

Developed a reusable case study format and wrote five case studies covering relevant customer types and problem areas.

- Built a page template for structure consistency: hero image, stat cards, challenge block, body sections, trusted brands strip, and CTA
- Wrote case studies for customer and issue coverage, including retail multi-site rollout (NAPA), QSR refrigeration & HVAC (Burger King), municipal public buildings, automotive dealership, and refrigeration monitoring
