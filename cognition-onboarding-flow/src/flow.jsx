import { useState } from "react";

// ─── Design tokens ──────────────────────────────────────────────────────────
const C = {
  bg: "#F7F7F5",
  surface: "#FFFFFF",
  border: "#E2E2DC",
  text: "#1A1A18",
  muted: "#444645",
  green: "#056a2f",
  greenLight: "#129a17",
  greenBg: "#EAF2ED",
  red: "#C0392B",
  redBg: "#ffffff",
  amber: "#c6822e",
  amberBg: "#ffffff",
  grey: "#020202",
  greyBg: "#F0F0EC",
  infoBg: "#f7f9f2",
  selected: "#2D5C45",
  selectedBg: "#EAF2ED",
  buttonselected: "#f0faf3",
};

const styles = {
  app: {
    minHeight: "100vh",
    background: C.bg,
    fontFamily: "'DM Sans', 'Helvetica Neue', sans-serif",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "0 16px 40px",
  },
  header: {
    width: "100%",
    maxWidth: 560,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    padding: "20px 0 16px",
    borderBottom: `1px solid ${C.border}`,
    marginBottom: 28,
  },
  headerLeft: { display: "flex", flexDirection: "column", gap: 2 },
  headerTitle: { fontSize: 13, fontWeight: 400, color: C.text, letterSpacing: "-0.01em" },
  headerPhone: { fontSize: 12, color: C.green },
  headerLink: { color: C.green, textDecoration: "none" },
  startOver: {
    fontSize: 11,
    fontWeight: 400,
    color: C.amber,
    cursor: "pointer",
    padding: "4px 10px",
    border: `1px solid ${C.amber}`,
    borderRadius: 6,
    background: "transparent",
  },
  card: {
    width: "100%",
    maxWidth: 560,
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 16,
    padding: "28px 28px 24px",
    boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
  },
  screenTitle: {
    fontSize: 20,
    fontWeight: 500,
    color: C.text,
    marginBottom: 6,
    letterSpacing: "-0.02em",
  },
  screenSub: { fontSize: 13, color: C.text, marginBottom: 24, lineHeight: 1.2 },
  label: { fontSize: 13, fontWeight: 600, color: C.text, marginBottom: 6, display: "block", letterSpacing: "0.01em" },
  hint: { fontSize: 12, color: C.green, marginTop: 4, lineHeight: 1.2 },
  input: {
    width: "100%",
    padding: "11px 14px",
    fontSize: 13,
    border: `1.5px solid ${C.border}`,
    borderRadius: 8,
    background: C.surface,
    color: C.text,
    outline: "none",
    boxSizing: "border-box",
    transition: "border-color 0.15s",
  },
  select: {
    width: "100%",
    padding: "11px 14px",
    fontSize: 13,
    border: `1.5px solid ${C.border}`,
    borderRadius: 8,
    background: C.surface,
    color: C.text,
    outline: "none",
    boxSizing: "border-box",
    appearance: "none",
    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%236B6B65' strokeWidth='1.5' fill='none' strokeLinecap='round'/%3E%3C/svg%3E")`,
    backgroundRepeat: "no-repeat",
    backgroundPosition: "right 14px center",
    paddingRight: 36,
    cursor: "pointer",
  },
  selectDone: {
    backgroundColor: C.greyBg,
    color: "#0d471d", 
    border: `1.5px solid ${C.green}`,
    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%236B6B65' strokeWidth='1.5' fill='none' strokeLinecap='round'/%3E%3C/svg%3E")`,
    backgroundRepeat: "no-repeat",
    backgroundPosition: "right 14px center",
  },
  btnPrimary: {
    width: "100%",
    padding: "14px",
    fontSize: 13,
    fontWeight: 400,
    color: "#fff",
    background: C.green,
    border: "none",
    borderRadius: 10,
    cursor: "pointer",
    letterSpacing: "-0.01em",
    transition: "background 0.15s",
  },
  btnSecondary: {
    width: "100%",
    padding: "14px",
    fontSize: 13,
    fontWeight: 500,
    color: C.text,
    background: C.greyBg,
    border: `1px solid ${C.border}`,
    borderRadius: 10,
    cursor: "pointer",
    letterSpacing: "-0.01em",
    transition: "background 0.15s",
  },
  btnRow: { display: "flex", gap: 10, marginTop: 20 },
  divider: { height: 1, background: C.border, margin: "20px 0" },
  noteBlue: {
    fontSize: 13,
    color: "#1A5276",
    background: "#EBF5FB",
    border: "1px solid #AED6F1",
    borderRadius: 8,
    padding: "10px 14px",
    lineHeight: 1.2,
    marginTop: 12,
  },
  noteAmber: {
    fontSize: 13,
    color: C.muted,
    background: C.amberBg,
    border: "2px solid #ebba3e",
    borderRadius: 8,
    padding: "10px 14px",
    lineHeight: 1.2,
    marginTop: 12,
  },
  noteRed: {
    fontSize: 13,
    color: C.red,
    background: C.redBg,
    border: "2px solid #f0533e",
    borderRadius: 8,
    padding: "10px 14px",
    lineHeight: 1.2,
    marginTop: 12,
  },
  noteGreen: {
    fontSize: 13,
    color: C.green,
    background: C.greenBg,
    border: "2px solid #A8D5BC",
    borderRadius: 8,
    padding: "10px 14px",
    lineHeight: 1.2,
    marginTop: 12,
  },
  progress: {
    width: "100%",
    maxWidth: 560,
    display: "flex",
    alignItems: "center",
    gap: 8,
    marginBottom: 20,
  },
  progressBar: {
    flex: 1,
    height: 4,
    background: C.border,
    borderRadius: 2,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    background: C.green,
    borderRadius: 2,
    transition: "width 0.35s ease",
  },
  progressLabel: { fontSize: 12, color: C.muted, whiteSpace: "nowrap" },
  fieldGroup: { marginBottom: 18 },
  checkRow: { display: "flex", alignItems: "center", gap: 10, cursor: "pointer" },
  checkbox: {
    width: 18,
    height: 18,
    border: `2px solid ${C.border}`,
    borderRadius: 4,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    transition: "all 0.15s",
    cursor: "pointer",
  },
  radioRow: { display: "flex", gap: 10, marginTop: 8 },
  radioBtn: (active) => ({
    flex: 1,
    padding: "12px",
    fontSize: 13,
    fontWeight: active ? 600 : 400,
    color: active ? C.green : C.text,
    background: active ? C.greyBg : C.greyBg,
    border: `1.5px solid ${active ? C.green : C.buttonselected}`,
    borderRadius: 8,
    cursor: "pointer",
    textAlign: "center",
    transition: "all 0.15s",
  }),
  optionBtn: (active) => ({
    width: "100%",
    padding: "14px 16px",
    fontSize: 13,
    fontWeight: active ? 600 : 400,
    color: active ? C.green : C.text,
    background: active ? C.greyBg : C.greyBg,
    border: `1.5px solid ${active ? C.green : C.buttonselected}`,
    borderRadius: 10,
    cursor: "pointer",
    textAlign: "left",
    marginBottom: 8,
    transition: "all 0.15s",
  }),
  optionBtnDestructive: {
    width: "100%",
    padding: "14px 16px",
    fontSize: 13,
    fontWeight: 400,
    color: C.text,
    background: C.greyBg,
    border: `1.5px solid ${C.border}`,
    borderRadius: 10,
    cursor: "pointer",
    textAlign: "center",
    marginBottom: 8,
  },
  sectionHead: {
    fontSize: 12,
    fontWeight: 700,
    color: C.text,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    marginBottom: 10,
    marginTop: 20,
  },
  reviewRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    padding: "8px 0",
    borderBottom: `1px solid ${C.border}`,
    fontSize: 11,
  },
  reviewKey: { color: C.muted, flex: "0 0 120px" },
  reviewVal: { color: C.text, fontWeight: 500, textAlign: "right", flex: 1 },
  wiringGrid: {
    display: "flex",
    gap: 6,
    flexWrap: "wrap",
    background: "#1E3A2F",
    padding: "14px 16px",
    borderRadius: 10,
    marginTop: 10,
  },
  wiringTerminal: (active) => ({
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 5,
    cursor: "pointer",
    padding: "6px 4px",
    borderRadius: 6,
    background: active ? C.greenLight : "rgba(255,255,255,0.08)",
    transition: "all 0.15s",
    minWidth: 36,
  }),
  wiringLabel: { fontSize: 10, color: "rgb(255, 255, 255)", letterSpacing: "0.04em" },
  wiringCheckbox: (active) => ({
    width: 16,
    height: 16,
    border: `2px solid ${active ? "#31c024" : "rgba(255, 255, 255, 0.74)"}`,
    borderRadius: 3,
    background: active ? "#fcfcfc" : "transparent",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  }),
  infoBox: {
    background: C.infoBg,
    border: `2px solid ${C.border}`,
    borderRadius: 10,
    padding: "14px 16px",
    marginTop: 12,
  },
  infoTitle: { fontSize: 13, fontWeight: 700, color: C.text, marginBottom: 8 },
  infoRow: { display: "flex", gap: 12, fontSize: 12, color: C.muted, marginBottom: 4, lineHeight: 1.2 },
  stepDot: (active, done) => ({
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: done ? C.green : active ? C.green : C.border,
    opacity: done || active ? 1 : 0.5,
    transition: "all 0.2s",
  }),
};

// ─── Terminals ───────────────────────────────────────────────────────────────
const TERMINALS = ["C", "AC-", "AC+", "G", "Y1", "Y2", "E", "W1", "W2", "O/B", "Rh", "Rc"];

const SCREENS = {
  WELCOME:        0,
  INSTALL_SELECT: 1,
  POWER_CHECK:    2,
  POWER_ISSUE:    3,
  POWER_FAILED:   4,
  WIRING:         5,
  EQUIPMENT:      6,
  SENSORS:        7,
  SENSOR_PAIR:    8,
  SENSOR_INSTALL: 9,
  SENSOR_CONFIRM: 10,
  ZONE_INFO:      11,
  COMFORT:           12,
  REVIEW:            13,
  CONNECTIVITY:      14,
  FF_HUB_INSTALL:    15,
  FF_POWER_CHECK:    16,
  FF_POWER_ISSUE:    17,
  FF_SENSOR_INSTALL: 18,
  FF_EQUIP_CONFIG:   19,
  TRACKER:           20,
  TROUBLESHOOTING:   21,
  SCAN_QR:           22,
  CEILING_INSTALL:   23,
};

const FLOW_STEPS = [
  { label: "Install Type", screens: [SCREENS.WELCOME, SCREENS.INSTALL_SELECT] },
  { label: "Power",     screens: [SCREENS.POWER_CHECK, SCREENS.POWER_ISSUE, SCREENS.POWER_FAILED, SCREENS.FF_HUB_INSTALL, SCREENS.CEILING_INSTALL, SCREENS.FF_POWER_CHECK, SCREENS.FF_POWER_ISSUE] },
  { label: "Wiring",    screens: [SCREENS.WIRING] },
  { label: "Equipment", screens: [SCREENS.EQUIPMENT, SCREENS.FF_EQUIP_CONFIG] },
  { label: "Sensors",   screens: [SCREENS.SENSORS, SCREENS.SENSOR_PAIR, SCREENS.SENSOR_INSTALL, SCREENS.SENSOR_CONFIRM, SCREENS.FF_SENSOR_INSTALL] },
  { label: "Zone Info", screens: [SCREENS.ZONE_INFO] },
  { label: "Review",    screens: [SCREENS.REVIEW, SCREENS.CONNECTIVITY] },
  { label: "Tracker",   screens: [SCREENS.TRACKER, SCREENS.TROUBLESHOOTING] },
];

const SCREEN_LABELS = {
  [SCREENS.FF_HUB_INSTALL]:    "Hub Install",
  [SCREENS.CEILING_INSTALL]:   "Hub Install",
  [SCREENS.FF_SENSOR_INSTALL]: "Sensor Install",
  [SCREENS.FF_EQUIP_CONFIG]:   "Configure",
  [SCREENS.TRACKER]:           "Tracker",
  [SCREENS.TROUBLESHOOTING]:   "Troubleshoot",
};

function getStepIndex(screenIdx) {
  for (let i = 0; i < FLOW_STEPS.length; i++) {
    if (FLOW_STEPS[i].screens.includes(screenIdx)) return i;
  }
  return 0;
}

// ─── Header ──────────────────────────────────────────────────────────────────
function Header({ onStartOver, onTracker, showTracker, screenIdx }) {
  const showStartOver = screenIdx > 0 && screenIdx !== 14;
  return (
    <div style={styles.header}>
      <div style={styles.headerLeft}>
        <span style={styles.headerTitle}>Cognition Controls — Set Up</span>
        <span style={styles.headerPhone}>
          Support: <a href="tel:8446564822" style={styles.headerLink}>(844) 656-4822</a>
        </span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
        {showStartOver && (
          <button style={styles.startOver} onClick={onStartOver}>Start Over</button>
        )}
        {showTracker && (
          <button style={{ ...styles.startOver, color: C.green }} onClick={onTracker}>Tracker</button>
        )}
      </div>
    </div>
  );
}

// ─── Progress Bar ─────────────────────────────────────────────────────────────
function Progress({ screenIdx }) {
  if (screenIdx === 0) return null;
  const stepIdx = getStepIndex(screenIdx);
  const pct = Math.round(((stepIdx) / (FLOW_STEPS.length - 1)) * 100);
  return (
    <div style={styles.progress}>
      {FLOW_STEPS.map((s, i) => (
        <div key={s.label} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
          <div style={styles.stepDot(i === stepIdx, i < stepIdx)} />
        </div>
      ))}
      <div style={{ ...styles.progressBar, marginLeft: 4 }}>
        <div style={{ ...styles.progressFill, width: `${pct}%` }} />
      </div>
      <span style={styles.progressLabel}>{SCREEN_LABELS[screenIdx] ?? FLOW_STEPS[stepIdx]?.label}</span>
    </div>
  );
}

// ─── Reversing Valve Info ─────────────────────────────────────────────────────
function RevValveInfoBox() {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ marginTop: 6 }}>
      <button
        onClick={() => setOpen(!open)}
        style={{ background: "none", border: "none", color: C.amber, fontSize: 13, cursor: "pointer", fontWeight: 600, display: "flex", alignItems: "center", gap: 5 }}
      >
        <span style={{ fontWeight: 700, fontSize: 15, lineHeight: 1 }}>ⓘ</span> What is this? {open ? "▲" : "▼"}
      </button>
      {open && (
        <div style={styles.infoBox}>
          <div style={styles.infoTitle}>Reversing Valve (O/B Terminal)</div>
          <div style={styles.infoRow}>The reversing valve switches a heat pump between heating and cooling mode. The O/B terminal controls it.</div>
          <div style={{ ...styles.infoRow, marginTop: 8 }}>
            <span style={{ fontWeight: 600, color: C.text, minWidth: 60 }}>Heat (O)</span>
            <span>Valve energizes in heating mode — common on Carrier, Bryant, Payne equipment.</span>
          </div>
          <div style={styles.infoRow}>
            <span style={{ fontWeight: 600, color: C.text, minWidth: 60 }}>Cool (B)</span>
            <span>Valve energizes in cooling mode — common on Trane, Lennox, Rheem, Ruud equipment.</span>
          </div>
          <div style={{ ...styles.hint, marginTop: 8 }}>Check your equipment documentation or thermostat wiring label if unsure.</div>
        </div>
      )}
    </div>
  );
}

// ─── Wiring Grid ─────────────────────────────────────────────────────────────
function WiringGrid({ selected, onToggle }) {
  return (
    <div style={styles.wiringGrid}>
      {TERMINALS.map((t) => (
        <div key={t} style={styles.wiringTerminal(selected.includes(t))} onClick={() => onToggle(t)}>
          <span style={styles.wiringLabel}>{t}</span>
          <div style={styles.wiringCheckbox(selected.includes(t))}>
            {selected.includes(t) && (
              <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                <path d="M1 4l3 3 5-6" stroke="#011f13" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Wiring Info Modal ────────────────────────────────────────────────────────
function WiringInfoBox() {
  const [open, setOpen] = useState(false);
  const wires = [
    ["W1", "Primary heating", "White"],
    ["Y1", "Primary cooling", "Yellow"],
    ["G", "Fan control", "Green"],
    ["O/B", "Heat pump reversing valve", "Orange"],
    ["Rc", "Power – cooling", "Red"],
    ["Rh", "Power – heating", "Red"],
    ["C", "Common wire (required)", "Black/Blue"],
  ];
  return (
    <div style={{ marginTop: 10 }}>
      <button
        onClick={() => setOpen(!open)}
        style={{ background: "none", border: "none", color: C.amber, fontSize: 13, cursor: "pointer", fontWeight: 600, display: "flex", alignItems: "center", gap: 5 }}
      >
        <span style={{ fontWeight: 700, fontSize: 15, lineHeight: 1 }}>ⓘ</span> Wiring guide {open ? "▲" : "▼"}
      </button>
      {open && (
        <div style={styles.infoBox}>
          <div style={styles.infoTitle}>Terminal Reference</div>
          {wires.map(([t, use, color]) => (
            <div key={t} style={styles.infoRow}>
              <span style={{ fontWeight: 700, color: C.text, minWidth: 36 }}>{t}</span>
              <span style={{ flex: 1 }}>{use}</span>
              <span style={{ color: C.muted }}>{color}</span>
            </div>
          ))}
          <div style={{ ...styles.hint, marginTop: 8 }}>
            C-wire must be 24VAC. If only one wire for Rh/Rc, connect both with the included jumper. 
          </div>
        </div>
      )}
    </div>
  );
}

const SAMPLE_BUILDINGS = [
  "123 Main St — Building A",
  "456 Commerce Ave — HQ",
  "789 Industrial Blvd — Warehouse",
];

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [screen, setScreen] = useState(0);
  const [installType, setInstallType] = useState(null);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [jumperRemoved, setJumperRemoved] = useState(null);
  const [wiringSelected, setWiringSelected] = useState([]);
  const [heatEquip, setHeatEquip] = useState("");
  const [coolEquip, setCoolEquip] = useState("");
  const [equipMode, setEquipMode] = useState("");
  const [backupHeat, setBackupHeat] = useState("");
  const [revValve, setRevValve] = useState("");
  const [backupSwitchover, setBackupSwitchover] = useState("");
  const [installedDevices, setInstalledDevices] = useState([]);
  const [ffRefrigType, setFfRefrigType] = useState("");
  const [ffRangeLow, setFfRangeLow] = useState("");
  const [ffRangeHigh, setFfRangeHigh] = useState("");
  const [ffUnitName, setFfUnitName] = useState("");
  const [showFfEquipErrors, setShowFfEquipErrors] = useState(false);
  const [ffSensors, setFfSensors] = useState([]);
  const [sensorType, setSensorType] = useState(null);
  const [sensorLocation, setSensorLocation] = useState("");
  const [sensorSymbol, setSensorSymbol] = useState(null);
  const [sensorSticker, setSensorSticker] = useState(null);
  const [showSensorErrors, setShowSensorErrors] = useState(false);
  const [showDiffuserImg, setShowDiffuserImg] = useState(false);
  const [showGrilleImg, setShowGrilleImg] = useState(false);
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [troubleshootContext, setTroubleshootContext] = useState("device"); // "device" | "sensor_hvac" | "sensor_ff"
  const [wifiChoice, setWifiChoice] = useState(""); // "" | "compatible" | "not_compatible"
  const [sensorSuggestedLoc, setSensorSuggestedLoc] = useState(null);
  const [addAnotherSensor, setAddAnotherSensor] = useState(false);
  const [zoneName, setZoneName] = useState("");
  const [buildingSelected, setBuildingSelected] = useState("");
  const [addrStreet, setAddrStreet] = useState("");
  const [addrSuite, setAddrSuite] = useState("");
  const [addrZip, setAddrZip] = useState("");
  const [addrCity, setAddrCity] = useState("");
  const [addrCountry, setAddrCountry] = useState("USA");
  const [zoneCharacteristics, setZoneCharacteristics] = useState([]);
  const [showZoneErrors, setShowZoneErrors] = useState(false);
  const [tempMin, setTempMin] = useState("70");
  const [tempMax, setTempMax] = useState("74");
  const [flashBtn, setFlashBtn] = useState(null);

  const flash = (id, fn) => { setFlashBtn(id); setTimeout(() => { setFlashBtn(null); fn(); }, 280); };

  const isHeatPump = heatEquip.includes("Heat Pump");
  const wiringError = wiringSelected.includes("W1") && isHeatPump
    ? ["W1 is not compatible with Heat Pump equipment", "Heat Pump requires O/B terminal"]
    : [];

  function toggleWire(t) {
    setWiringSelected(prev =>
      prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t]
    );
  }


  function startOver() {
    setScreen(SCREENS.WELCOME);
    setInstallType(null);
    setPhoneNumber("");
    setJumperRemoved(null);
    setWiringSelected([]);
    setHeatEquip(""); setCoolEquip(""); setEquipMode("");
    setBackupHeat(""); setBackupSwitchover(""); setRevValve("");
    setSensorType(null); setSensorLocation(""); setSensorSymbol(null); setSensorSticker(null);
    setSensorSuggestedLoc(null); setAddAnotherSensor(false);
    setZoneName(""); setBuildingSelected("");
    setAddrStreet(""); setAddrSuite(""); setAddrZip(""); setAddrCity(""); setAddrCountry("USA");
    setZoneCharacteristics([]);
    setTempMin("70"); setTempMax("74");
    setBackupSwitchover(""); setInstalledDevices([]);
    setFfRefrigType(""); setFfRangeLow(""); setFfRangeHigh(""); setFfUnitName(""); setShowFfEquipErrors(false);
    setFfSensors([]);
    setTroubleshootContext("device"); setWifiChoice("");
  }

  function go(n) { setScreen(n); window.scrollTo(0,0); }

  // ── Screen renderers ────────────────────────────────────────────────────────

  function renderInstallType() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Proactive-Support Opt-in:</div>
        <div style={styles.screenSub}>
          We will text you with install updates, or if we detect an install issue. Enter your phone number to opt-in:
        </div>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>Phone number (optional)</label>
          <input
            style={styles.input}
            placeholder="xxx-xxx-xxxx"
            value={phoneNumber}
            onChange={e => setPhoneNumber(e.target.value)}
          />
        </div>

        <div style={{ ...styles.noteAmber, marginBottom: 16 }}>
          Please do not click your browser back button. Please use the Back buttons provided, or the Start Over option in the top right of each screen.
        </div>
        <button style={styles.btnPrimary} onClick={() => go(SCREENS.INSTALL_SELECT)}>
          Start Install
        </button>
      </div>
    );
  }

  function renderInstallSelect() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>What type of install is this?</div>
        <div style={{ ...styles.divider, margin: "0 0 16px" }} />

        <button
          style={styles.optionBtn(installType === "hvac")}
          onClick={() => { setInstallType("hvac"); flash("hvac", () => go(SCREENS.POWER_CHECK)); }}
        >
          <span style={{ fontWeight: 600 }}>HVAC Device</span>
          <div style={{ fontSize: 12, color: installType === "hvac" ? C.green : C.muted, marginTop: 2 }}>
            HVAC equipment control and monitoring
          </div>
        </button>
        <button
          style={styles.optionBtn(installType === "ff")}
          onClick={() => { setInstallType("ff"); flash("ff", () => go(SCREENS.FF_HUB_INSTALL)); }}
        >
          <span style={{ fontWeight: 600 }}>Fridge / Freezer Device</span>
          <div style={{ fontSize: 12, color: installType === "ff" ? C.green : C.muted, marginTop: 2 }}>
            Refrigeration monitoring
          </div>
        </button>
      </div>
    );
  }

  function renderPowerCheck() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Power Check</div>
        <div style={styles.noteBlue}>
          <strong>Is the bar in the top-right corner of the device moving?</strong>
          <div style={{ marginTop: 4 }}>The bar shifts position every 1–3 seconds when powered.</div>
        </div>
        
        <div style={styles.screenSub}>
        <div style={{ marginTop: 15 }}></div>
          When powered, cellular connectivity automatically initiates. Connectivity can take up to 15 minutes to complete.
        </div>

        <div style={{ height: 20 }} />

        <button style={{ ...styles.btnSecondary, marginBottom: 10, ...(flashBtn === "bar-moving" ? { borderColor: C.green, background: C.greenBg, color: C.green } : {}) }} onClick={() => flash("bar-moving", () => go(SCREENS.WIRING))}>
          Bar is moving — device is powered
        </button>
        <button style={{ ...styles.btnSecondary, ...(flashBtn === "bar-not-moving" ? { borderColor: C.green, background: C.greenBg, color: C.green } : {}) }} onClick={() => flash("bar-not-moving", () => go(SCREENS.POWER_ISSUE))}>
          Bar is not moving
        </button>
      </div>
    );
  }

  function renderPowerIssue() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Check C-Wire Power</div>
        <div style={styles.screenSub}>
          The device is powered by the HVAC equipment via the C-wire.
        </div>

        <div style={{ ...styles.noteAmber, marginTop:15 }}>
          <strong>Note:</strong> 
          <div style={styles.infoRow}>•  Rh must be connected to 24VAC</div>
          <div style={styles.infoRow}>•  Cooling-only equipment - do not remove the jumper between Rh/Rc</div>
          <div style={styles.infoRow}>•  Dual transforer set-up - C must come from the heating cable bundle.</div>
        </div>
        
        <div style={{ ...styles.sectionHead, marginTop: 30 }}>Using a multimeter:</div>
        <div style={styles}>
          <div style={styles.infoRow}>•  Set multimeter to V~ (AC voltage)</div>
          <div style={styles.infoRow}>•  Measure voltage between Rh and C</div>
          <div style={styles.infoRow}>•  C-wire range required:<strong>20–30 VAC</strong></div>
        </div>

        
        

        <div style={{ height: 20, marginTop: 20 }} />
        <button style={{ ...styles.btnPrimary, marginBottom: 10 }} onClick={() => go(SCREENS.WIRING)}>
          20–30 VAC detected
        </button>
        <button style={styles.btnSecondary} onClick={() => go(SCREENS.POWER_FAILED)}>
          20-30 VAC NOT detected
        </button>
      </div>
    );
  }

  function renderPowerFailed() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Power Issue Detected</div>
        <div style={{ ...styles.noteRed, marginBottom: 20, marginTop: 0 }}>
          {installType === "ff"
            ? "The underlying power issue must be resolved before completing this install."
            : "There is an issue with the power from this HVAC equipment. The underlying power issue must be resolved before completing this install."}
        </div>

        <button style={{ ...styles.btnSecondary, marginBottom: 10 }} onClick={() => go(SCREENS.WELCOME)}>
          Start a New Equipment Install
        </button>
        <button style={{ ...styles.btnSecondary, marginBottom: 10 }}
          onClick={() => alert("Thank you — our team will follow up to understand the power issue and schedule a completion.")}>
          Exit Set-Up (cannot proceed)
        </button>
        <button style={styles.optionBtnDestructive} onClick={() => go(installType === "ff" ? SCREENS.FF_POWER_ISSUE : SCREENS.POWER_ISSUE)}>← Back</button>
      </div>
    );
  }

  function renderWiring() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Enter Wiring Information</div>
        <div style={styles.screenSub}>
          On the interactive panel below, tap each terminal where a wire is installed. If a wire is jumpered at the equipment, select that terminal too.
        </div>
        <WiringInfoBox />

        <label style={{ ...styles.label, marginTop: 15}}>Select installed terminals</label>
        <WiringGrid selected={wiringSelected} onToggle={toggleWire} />

        {wiringSelected.length > 0 && (
          <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 6 }}>
            {wiringSelected.map(t => (
              <span key={t} style={{ fontSize: 12, fontWeight: 700, color: C.green, background: C.greenBg, border: `1px solid ${C.green}`, borderRadius: 20, padding: "3px 10px" }}>
                {t}
              </span>
            ))}
          </div>
        )}

        {wiringError.length > 0 && (
          <div style={styles.noteRed}>
            {wiringError.map(e => <div key={e}>⚠ {e}</div>)}
          </div>
        )}

 <div style={{ ...styles.fieldGroup, marginTop: 20}}>
          <label style={styles.label}>Rh/Rc Jumper</label>
          <div style={styles.radioRow}>
            <div style={styles.radioBtn(jumperRemoved === false)} onClick={() => setJumperRemoved(false)}>Jumper installed</div>
            <div style={styles.radioBtn(jumperRemoved === true)} onClick={() => setJumperRemoved(true)}>I removed it</div>
          </div>
        </div>

        

<div style={{ ...styles.btnRow, marginTop: 40 }}>
          <button style={{ ...styles.btnSecondary, flex: 1 }} onClick={() => go(SCREENS.POWER_CHECK)}>Back</button>
          <button
            style={{ ...styles.btnPrimary, flex: 2, opacity: wiringSelected.length === 0 || jumperRemoved === null ? 0.5 : 1 }}
            disabled={wiringSelected.length === 0 || jumperRemoved === null}
            onClick={() => go(SCREENS.EQUIPMENT)}
          >
            Next — Equipment Info
          </button>
        </div>
      </div>
    );
  }

  function renderEquipment() {
    return (
      <div style={styles.card}>
        <div style={{ ...styles.screenTitle, marginBottom: 20 }}>Equipment Configuration</div>

        <div style={styles.fieldGroup}>
          <label style={styles.label}>Heat Equipment</label>
          <select style={{ ...styles.select, ...(heatEquip ? styles.selectDone : {}) }} value={heatEquip} onChange={e => setHeatEquip(e.target.value)}>
            <option value="">Select type</option>
            <option>Forced Air – Gas</option>
            <option>Forced Air – Electric</option>
            <option>Forced Air – Hydronic</option>
            <option>Heat Pump</option>
            <option>Unit Heater</option>
            <option>Other</option>
            <option>None</option>
          </select>
        </div>

        {heatEquip === "Unit Heater" && (
          <div style={{ ...styles.infoBox, borderColor: C.amber, background: C.amberBg, marginTop: -4, marginBottom: 12 }}>
            <div style={{ ...styles.infoTitle, color: C.amber }}>⚠ C-Wire Polarity — Unit Heater</div>
            <div style={{ ...styles.infoRow, marginBottom: 6 }}>It is critical to install the C-wire correctly on a unit heater.</div>
            {[
              "Identify the 24V transformer",
              "Find the low-voltage terminal strip or control board inside the heater unit",
              <>Connect the C-wire to the low-voltage terminal that is <strong>NOT</strong> connected to the R (hot) wire</>,
              "Run this wire alongside existing wiring to the thermostat location",
            ].map((step, i) => (
              <div key={i} style={{ ...styles.infoRow, alignItems: "flex-start", gap: 8 }}>
                <span style={{ fontWeight: 700, color: C.amber, minWidth: 18 }}>{i + 1}.</span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        )}

        {wiringError.length > 0 && (
          <div style={{ ...styles.noteRed, marginBottom: 12 }}>
            <strong>Configuration error:</strong>
            {wiringError.map(e => <div key={e}>• {e}</div>)}
            <button
              onClick={() => go(SCREENS.WIRING)}
              style={{ marginTop: 10, width: "100%", padding: "10px 14px", background: C.red, color: "white", border: "none", borderRadius: 8, fontWeight: 700, fontSize: 13, cursor: "pointer" }}
            >
              Review wiring →
            </button>
          </div>
        )}
        
        {isHeatPump && (
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Backup Heat System</label>
            <select style={{ ...styles.select, ...(backupHeat ? styles.selectDone : {}) }} value={backupHeat} onChange={e => { setBackupHeat(e.target.value); setBackupSwitchover(""); }}>
              <option value="">Select type</option>
              <option>Forced Air – Gas</option>
              <option>Forced Air – Electric or Electric Resistive</option>
              <option>Other</option>
            </select>
          </div>
        )}

        {isHeatPump && backupHeat && (
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Back-up Switchover</label>
            <div style={styles.radioRow}>
              <div style={styles.radioBtn(backupSwitchover === "Switchover")} onClick={() => setBackupSwitchover("Switchover")}>Switchover</div>
              <div style={styles.radioBtn(backupSwitchover === "Supplemental")} onClick={() => setBackupSwitchover("Supplemental")}>Supplemental</div>
            </div>
          </div>
        )}

        <div style={styles.fieldGroup}>
          <label style={styles.label}>Cool Equipment</label>
          <select style={{ ...styles.select, ...(coolEquip ? styles.selectDone : {}) }} value={coolEquip} onChange={e => setCoolEquip(e.target.value)}>
            <option value="">Select type</option>
            <option>Forced Air – Electric</option>
            <option>Forced Air – Hydronic</option>
            <option>Heat Pump</option>
            <option>Other</option>
            <option>None</option>
          </select>
        </div>

        {isHeatPump && (
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Reversing Valve Energized On</label>
            <RevValveInfoBox />
            <div style={styles.radioRow}>
              <div style={styles.radioBtn(revValve === "Heat")} onClick={() => setRevValve("Heat")}>Heat</div>
              <div style={styles.radioBtn(revValve === "Cool")} onClick={() => setRevValve("Cool")}>Cool</div>
            </div>
          </div>
        )}


        <div style={{ ...styles.divider }} />

        <div style={styles.fieldGroup}>
          <label style={styles.label}>Equipment Operating Mode</label>
          <select style={{ ...styles.select, ...(equipMode ? styles.selectDone : {}) }} value={equipMode} onChange={e => setEquipMode(e.target.value)}>
            <option value="">Select mode</option>
            <option>Auto (Heat and Cool)</option>
            <option>Heat</option>
            <option>Cool</option>
            <option>Fan</option>
            <option>Off</option>
          </select>
        </div>
         <div style={styles.fieldGroup}>
          <label style={styles.label}>Default Comfort Range</label>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <select style={{ ...styles.select, flex: 1 }} value={tempMin} onChange={e => setTempMin(e.target.value)}>
              {Array.from({ length: 21 }, (_, i) => 60 + i).map(t => <option key={t}>{t}</option>)}
            </select>
            <span style={{ color: C.muted, fontSize: 13 }}>to</span>
            <select style={{ ...styles.select, flex: 1 }} value={tempMax} onChange={e => setTempMax(e.target.value)}>
              {Array.from({ length: 21 }, (_, i) => 60 + i).map(t => <option key={t}>{t}</option>)}
            </select>
            <span style={{ color: C.muted, fontSize: 13 }}>°F</span>
          </div>
          <div style={styles.hint}>Sets the default range until adjusted in the dashboard.</div>
        </div>

        <div style={{ ...styles.btnRow, marginTop: 30 }}>
          <button style={{ ...styles.btnSecondary, flex: 1 }} onClick={() => go(SCREENS.WIRING)}>Back</button>
          <button
            style={{ ...styles.btnPrimary, flex: 2, opacity: (!heatEquip || !coolEquip || (isHeatPump && backupHeat && !backupSwitchover)) ? 0.5 : 1 }}
            disabled={!heatEquip || !coolEquip || (isHeatPump && backupHeat && !backupSwitchover)}
            onClick={() => go(SCREENS.SENSORS)}
          >
            Next — Sensors
          </button>
        </div>
      </div>
    );
  }

  function renderSensors() {
    const opts = [
      { id: "ambient", label: "Ambient Air", desc: "Measures temperature when thermostat is poorly placed, or manages many discrete areas" },
      { id: "supply", label: "Supply Air Duct", desc: "Measures temperature of supply air in the ductwork", refImg: "/HVAC-Diffuser-Application.jpeg", refAlt: "Diffuser application guide", showState: showDiffuserImg, toggleFn: () => setShowDiffuserImg(v => !v) },
      { id: "return", label: "Return Air Duct", desc: "Measures temperature of air returning to the HVAC unit", refImg: "/HVAC-Air-Grille-Application.jpeg", refAlt: "Air grille application guide", showState: showGrilleImg, toggleFn: () => setShowGrilleImg(v => !v) },
      { id: "none", label: "No Sensor Required", desc: "" },
    ];
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Pair Sensors</div>
        <div style={styles.screenSub}>Do you have sensors to pair with this device?</div>

        {opts.map(o => {
          const baseStyle = o.id === "none"
            ? { ...styles.optionBtn(false), color: C.text, borderStyle: "dashed", background: C.greyBg }
            : styles.optionBtn(flashBtn === o.id);
          return (
            <div key={o.id} style={{ ...baseStyle, marginBottom: 8, cursor: "pointer", textAlign: "left" }}
              onClick={() => {
                if (o.id === "none") { flash("none", () => go(SCREENS.ZONE_INFO)); return; }
                setSensorType(o.id);
                flash(o.id, () => go(SCREENS.SENSOR_PAIR));
              }}
            >
              <span style={{ fontWeight: 700 }}>{o.label}</span>
              {o.desc && <div style={{ fontSize: 12, color: C.muted, marginTop: 2, fontWeight: 400 }}>{o.desc}</div>}
              {o.refImg && (
                <div style={{ marginTop: 10 }} onClick={e => e.stopPropagation()}>
                  <button
                    onClick={o.toggleFn}
                    style={{ background: "none", border: "none", color: C.green, fontSize: 12, cursor: "pointer", fontWeight: 600, display: "flex", alignItems: "center", gap: 4, padding: 0 }}
                  >
                    <span style={{ fontWeight: 700, fontSize: 14, lineHeight: 1 }}>ⓘ</span> Reference Image {o.showState ? "▲" : "▼"}
                  </button>
                  {o.showState && (
                    <img src={o.refImg} alt={o.refAlt} style={{ marginTop: 8, width: "100%", borderRadius: 10 }} />
                  )}
                </div>
              )}
            </div>
          );
        })}

        <div style={{ height: 4 }} />
        <button style={styles.btnSecondary} onClick={() => go(SCREENS.EQUIPMENT)}>← Back</button>
      </div>
    );
  }

  function renderSensorPair() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Select Sensor Identifier</div>
        <div style={styles.screenSub}>
          Select the symbol printed on the back of the sensor. 
        </div>

        <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
          <select style={{ ...styles.select, flex: 1 }}>
            <option>Select Color</option>
            <option>Green</option>
            <option>Orange</option>
            <option>Blue</option>
            <option>Purple</option>
          </select>
          <select style={{ ...styles.select, flex: 1 }}>
            <option>Select Shape</option>
            <option>Triangle</option>
            <option>Star</option>
            <option>Chess piece</option>
          </select>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 20 }}>
          {[
            { color: "#2D7A45", shape: "▲", label: "Green Triangle" },
            { color: "#D4820A", shape: "▲", label: "Orange Triangle" },
            { color: "#1A5FA6", shape: "★", label: "Blue Star" },
            { color: "#6B3A8A", shape: "♜", label: "Purple Chess" },
          ].map(s => (
            <div
              key={s.label}
              onClick={() => { setSensorSymbol(s.label); setSensorSticker(null); flash(s.label, () => go(installType === "ff" ? SCREENS.FF_SENSOR_INSTALL : SCREENS.SENSOR_INSTALL)); }}
              style={{
                padding: 20,
                border: `2px solid ${flashBtn === s.label ? C.green : C.border}`,
                background: flashBtn === s.label ? C.greenBg : C.surface,
                borderRadius: 12,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 8,
                cursor: "pointer",
                transition: "all 0.15s",
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = C.green; e.currentTarget.style.background = C.greenBg; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.background = C.surface; }}
            >
              <span style={{ fontSize: 32, color: s.color }}>{s.shape}</span>
              <span style={{ fontSize: 12, color: C.muted }}>{s.label}</span>
            </div>
          ))}
        </div>

        <button style={styles.btnSecondary} onClick={() => go(installType === "ff" ? SCREENS.FF_POWER_CHECK : SCREENS.SENSORS)}>← Back</button>
      </div>
    );
  }

  function renderSensorInstall() {
    const isAmbient = sensorType === "ambient";
    const isSupply = sensorType === "supply";
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>
          {isAmbient ? "Ambient" : isSupply ? "Supply Air Duct" : "Return Air Duct"} — Instructions
        </div>

        {!isAmbient && (
          <div style={styles.noteAmber}>
            {isSupply ? "Supply" : "Return"} air ductwork is typically along the ceiling. A ladder may be required for this installation.
          </div>
        )}

        <div style={{ marginTop: 16 }}>
          <div style={{ marginBottom: 8 }}>
            <div style={styles.sectionHead}>Steps</div>
          </div>

          <div style={styles.infoBox}>
            <div style={{ fontSize: 13, fontWeight: 700, color: C.text, marginBottom: 6 }}>1. Pull the clear plastic tab</div>
            <div style={{ fontSize: 13, color: C.muted, lineHeight: 1.3 }}></div>
            <div style={{ ...styles.noteRed, marginTop: 8, marginBottom: 0 }}>⚠ Sensor will not work if tab is not removed before installing</div>
          </div>

          <div style={styles.infoBox}>
            <div style={{ fontSize: 13, fontWeight: 700, color: C.text, marginBottom: 6 }}>2. Identify a suitable location</div>
            {isAmbient ? (
              <div style={{ fontSize: 13, color: C.muted, lineHeight: 1.3 }}>
                • Within 40 ft of the device it is paired with<br />
                • ~5 ft off the ground<br />
                • Avoid direct sunlight or proximity to heat/cool emitting equipment<br />
                • Do not place between multiple walls
              </div>
            ) : (
              <div style={{ fontSize: 13, color: C.muted, lineHeight: 1.3 }}>
                • Ensure ductwork is associated with the HVAC equipment this device and sensor manage<br />
                • Sensor is within 40 ft of device <br />
              </div>
            )}
          </div>

          <div style={styles.infoBox}>
            <div style={{ fontSize: 13, fontWeight: 700, color: C.text, marginBottom: 6 }}>3. Install the sensor</div>
            <div style={{ fontSize: 13, color: C.muted, lineHeight: 1.3 }}>
              {isAmbient
                ? "• Attach using the provided adhesive or anchor screw"
                : <>
                    • {isSupply ? "Remove diffuser to access ductwork" : "Remove grille to access ductwork"}<br />
                    • Remove adhesive backing<br />
                    • Secure along ductwork horizontal run
                  </>
              }
            </div>
          </div>

          {!isAmbient && (
            <div style={styles.infoBox}>
              <div style={{ fontSize: 13, fontWeight: 700, color: C.text, marginBottom: 6 }}>4. Mark the location</div>
              <div style={{ fontSize: 13, color: C.muted }}>Place the provided green sticker on the {isSupply ? "diffuser" : "grille"} to indicate sensor placement.</div>
            </div>
          )}
        </div>

        <div style={{ ...styles.divider, marginTop: 20 }} />

        <div style={styles.fieldGroup}>
          <label style={{ ...styles.label, ...(showSensorErrors && !sensorLocation ? { color: C.red } : {}) }}>Describe the sensor location</label>
          <input
            style={{ ...styles.input, ...(showSensorErrors && !sensorLocation ? { borderColor: C.red } : {}) }}
            placeholder="e.g. Diffuser closest to door"
            value={sensorLocation}
            onChange={e => setSensorLocation(e.target.value)}
          />
        </div>

        {!isAmbient && (
          <div style={styles.fieldGroup}>
            <label style={{ ...styles.label, ...(showSensorErrors && sensorSticker === null ? { color: C.red } : {}) }}>Did you place a sticker at the {isSupply ? "diffuser" : "grille"} location?</label>
            <div style={styles.radioRow}>
              <div style={styles.radioBtn(sensorSticker === true)} onClick={() => setSensorSticker(true)}>Yes</div>
              <div style={styles.radioBtn(sensorSticker === false)} onClick={() => setSensorSticker(false)}>No</div>
            </div>
          </div>
        )}

        <div style={styles.btnRow}>
          <button style={{ ...styles.btnSecondary, flex: 1 }} onClick={() => { setShowSensorErrors(false); go(SCREENS.SENSOR_PAIR); }}>Back</button>
          <button
            style={{ ...styles.btnPrimary, flex: 2, opacity: (sensorLocation && (isAmbient || sensorSticker !== null)) ? 1 : 0.5 }}
            onClick={() => {
              const valid = sensorLocation && (isAmbient || sensorSticker !== null);
              if (!valid) { setShowSensorErrors(true); return; }
              setShowSensorErrors(false);
              go(SCREENS.SENSOR_CONFIRM);
            }}
          >
            Submit
          </button>
        </div>
      </div>
    );
  }

  function renderSensorConfirm() {
    return (
      <div style={styles.card}>
        <div style={{ ...styles.noteAmber, marginBottom: 20 }}>
        <strong>Sensor connectivity is reviewed later.</strong>
        </div>
        <div style={styles.screenTitle}>Add another sensor?</div>
        <div style={styles.screenSub}>Does this zone need another wireless sensor?</div>

        <button style={{ ...styles.btnSecondary, marginBottom: 10, ...(flashBtn === "pair-another" ? { borderColor: C.green, background: C.greenBg, color: C.green } : {}) }} onClick={() => {
          if (installType === "ff") {
            setFfSensors(prev => [...prev, { symbol: sensorSymbol, refrigType: ffRefrigType, rangeLow: ffRangeLow, rangeHigh: ffRangeHigh, unitName: ffUnitName }]);
            setFfRefrigType(""); setFfRangeLow(""); setFfRangeHigh(""); setFfUnitName(""); setShowFfEquipErrors(false);
          }
          setSensorType(null); setSensorLocation(""); setSensorSymbol(null); setSensorSticker(null); setSensorSuggestedLoc(null);
          flash("pair-another", () => go(installType === "ff" ? SCREENS.SENSOR_PAIR : SCREENS.SENSORS));
        }}>
          Yes — pair another sensor
        </button>
        <button style={{ ...styles.btnSecondary, ...(flashBtn === "no-more-sensors" ? { borderColor: C.green, background: C.greenBg, color: C.green } : {}) }} onClick={() => {
          if (installType === "ff") {
            setFfSensors(prev => [...prev, { symbol: sensorSymbol, refrigType: ffRefrigType, rangeLow: ffRangeLow, rangeHigh: ffRangeHigh, unitName: ffUnitName }]);
          }
          flash("no-more-sensors", () => go(installType === "ff" ? SCREENS.REVIEW : SCREENS.ZONE_INFO));
        }}>
          {installType === "ff" ? "No — continue to Review" : "No — continue to Zone Info"}
        </button>
      </div>
    );
  }

  function renderZoneInfo() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Zone Information</div>
        <div style={styles.screenSub}>Tell us about this zone for the dashboard.</div>

        <div style={styles.fieldGroup}>
          <label style={{ ...styles.label, ...(showZoneErrors && !zoneName ? { color: C.red } : {}) }}>Zone Name</label>
          <input
            style={{ ...styles.input, ...(showZoneErrors && !zoneName ? { borderColor: C.red } : {}) }}
            placeholder="e.g. 'Steve's Office' or 'Front Warehouse'"
            value={zoneName}
            onChange={e => setZoneName(e.target.value)}
            maxLength={40}
          />
          <div style={styles.hint}>Max 40 characters. Appears in Cognition dashboard.</div>
        </div>

        <div style={styles.fieldGroup}>
          <label style={{ ...styles.label, ...(showZoneErrors && !buildingSelected ? { color: C.red } : {}) }}>Building Address</label>
          <select
            style={{ ...styles.select, ...(buildingSelected ? styles.selectDone : {}), ...(showZoneErrors && !buildingSelected ? { borderColor: C.red } : {}) }}
            value={buildingSelected}
            onChange={e => setBuildingSelected(e.target.value)}
          >
            <option value="">Select a building</option>
            <option value="new">Enter New Address</option>
            {SAMPLE_BUILDINGS.map(b => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>

        {buildingSelected === "new" && (
          <>
            <div style={styles.fieldGroup}>
              <label style={styles.label}>Street Address</label>
              <input style={styles.input} placeholder="e.g. 123 Main St" value={addrStreet} onChange={e => setAddrStreet(e.target.value)} />
            </div>
            <div style={styles.fieldGroup}>
              <label style={styles.label}>Suite / Unit <span style={{ color: C.muted, fontWeight: 400 }}>(optional)</span></label>
              <input style={styles.input} placeholder="e.g. Suite 200" value={addrSuite} onChange={e => setAddrSuite(e.target.value)} />
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              <div style={{ ...styles.fieldGroup, flex: 1 }}>
                <label style={styles.label}>City</label>
                <input style={styles.input} placeholder="City" value={addrCity} onChange={e => setAddrCity(e.target.value)} />
              </div>
              <div style={{ ...styles.fieldGroup, flex: 1 }}>
                <label style={styles.label}>ZIP / Postal Code</label>
                <input style={styles.input} placeholder="e.g. 90210" value={addrZip} onChange={e => setAddrZip(e.target.value)} />
              </div>
            </div>
            <div style={styles.fieldGroup}>
              <label style={styles.label}>Country</label>
              <select style={{ ...styles.select, ...(addrCountry ? styles.selectDone : {}) }} value={addrCountry} onChange={e => setAddrCountry(e.target.value)}>
                <option value="USA">USA</option>
                <option value="Canada">Canada</option>
              </select>
            </div>
          </>
        )}

        <div style={styles.fieldGroup}>
          <label style={{ ...styles.label, ...(showZoneErrors && zoneCharacteristics.length === 0 ? { color: C.red } : {}) }}>Zone Characteristics</label>
          <div style={{ fontSize: 12, color: C.muted, marginBottom: 8 }}>Does this zone have any of the following?</div>
          {[
            { id: "kitchen",   label: "Commercial Kitchen",  desc: "Significant heat emitting equipment" },
            { id: "warehouse", label: "Warehouse",           desc: "Open concept with bay doors" },
            { id: "none",      label: "None",                desc: "No special characteristics" },
          ].map(c => {
            const active = zoneCharacteristics.includes(c.id);
            return (
              <div
                key={c.id}
                onClick={() => {
                  if (c.id === "none") {
                    setZoneCharacteristics(["none"]);
                  } else {
                    setZoneCharacteristics(prev => {
                      const without = prev.filter(x => x !== "none");
                      return active ? without.filter(x => x !== c.id) : [...without, c.id];
                    });
                  }
                }}
                style={{
                  display: "flex", alignItems: "flex-start", gap: 12,
                  padding: "12px 14px", marginBottom: 8,
                  border: `1.5px solid ${active ? C.green : C.border}`,
                  borderRadius: 10,
                  background: active ? C.greenBg : C.surface,
                  cursor: "pointer", transition: "all 0.15s",
                }}
              >
                <div style={{ ...styles.checkbox, borderColor: active ? C.green : C.border, background: active ? C.green : "transparent", marginTop: 2 }}>
                  {active && <svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4l3 3 5-6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: C.text }}>{c.label}</div>
                  <div style={{ fontSize: 12, color: C.muted, marginTop: 2, lineHeight: 1.2 }}>{c.desc}</div>
                </div>
              </div>
            );
          })}
        </div>

        <div style={styles.btnRow}>
          <button style={{ ...styles.btnSecondary, flex: 1 }} onClick={() => { setShowZoneErrors(false); go(SCREENS.SENSOR_CONFIRM); }}>Back</button>
          <button
            style={{ ...styles.btnPrimary, flex: 2, opacity: (zoneName && buildingSelected && zoneCharacteristics.length > 0) ? 1 : 0.5 }}
            onClick={() => {
              const valid = zoneName && buildingSelected && zoneCharacteristics.length > 0;
              if (!valid) { setShowZoneErrors(true); return; }
              setShowZoneErrors(false);
              go(SCREENS.REVIEW);
            }}
          >
            Next — Review & Submit
          </button>
        </div>
      </div>
    );
  }

  function renderReview() {
    const buildingDisplay = buildingSelected === "new"
      ? [addrStreet, addrSuite, addrCity, addrZip, addrCountry].filter(Boolean).join(", ") || "—"
      : buildingSelected || "—";
    const sensorTypeLabel = sensorType === "ambient" ? "Ambient Air" : sensorType === "supply" ? "Supply Air Duct" : "Return Air Duct";
    const zoneCharLabel = zoneCharacteristics.includes("none") ? "None" : zoneCharacteristics.join(", ") || "—";
    const stickerMap = {
      "Green Triangle":  { shape: "▲", color: "#2D7A45" },
      "Orange Triangle": { shape: "▲", color: "#D4820A" },
      "Blue Star":       { shape: "★", color: "#1A5FA6" },
      "Purple Chess":    { shape: "♜", color: "#6B3A8A" },
    };
    const stickerInfo = stickerMap[sensorSymbol];

    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Review Configuration</div>
        <div style={styles.screenSub}>Confirm all details before submitting.</div>

        <div style={styles.reviewRow}>
          <span style={styles.reviewKey}>Install</span>
          <span style={styles.reviewVal}>{installType === "hvac" ? "HVAC" : installType === "ff" ? "F/F Hub" : "—"}</span>
        </div>
        <div style={styles.reviewRow}>
          <span style={styles.reviewKey}>Power</span>
          <span style={styles.reviewVal}>20-30 VAC confirmed</span>
        </div>

        {installType === "ff" ? (
          <>
            <div style={styles.reviewRow}>
              <span style={styles.reviewKey}>Building</span>
              <span style={styles.reviewVal}>{buildingDisplay}</span>
            </div>
            {ffSensors.map((s, i) => {
              const si = stickerMap[s.symbol];
              return (
                <div key={i} style={{ borderTop: i === 0 ? `1px solid ${C.border}` : "none", marginTop: i === 0 ? 4 : 0 }}>
                  <div style={{ ...styles.sectionHead, marginTop: 8 }}>Sensor {ffSensors.length > 1 ? i + 1 : ""}</div>
                  <div style={styles.reviewRow}>
                    <span style={styles.reviewKey}>Fridge / Freezer Name</span>
                    <span style={styles.reviewVal}>{s.unitName || "—"}</span>
                  </div>
                  <div style={styles.reviewRow}>
                    <span style={styles.reviewKey}>Type</span>
                    <span style={styles.reviewVal}>{s.refrigType || "—"}</span>
                  </div>
                  <div style={styles.reviewRow}>
                    <span style={styles.reviewKey}>Operating Range</span>
                    <span style={styles.reviewVal}>{s.rangeLow && s.rangeHigh ? `${s.rangeLow}–${s.rangeHigh}°F` : "—"}</span>
                  </div>
                  <div style={styles.reviewRow}>
                    <span style={styles.reviewKey}>Sensor</span>
                    <span style={{ ...styles.reviewVal, display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 5 }}>
                      {si && <span style={{ fontSize: 14, color: si.color, lineHeight: 1 }}>{si.shape}</span>}
                      {s.symbol || "—"}
                    </span>
                  </div>
                </div>
              );
            })}
          </>
        ) : (
          <>
            <div style={styles.reviewRow}>
              <span style={styles.reviewKey}>Zone Name</span>
              <span style={styles.reviewVal}>{zoneName || "—"}</span>
            </div>

            <div style={styles.sectionHead}>Wiring</div>
            <div style={styles.reviewRow}>
              <span style={styles.reviewKey}>Terminals</span>
              <span style={styles.reviewVal}>{wiringSelected.length ? wiringSelected.join(", ") : "—"}</span>
            </div>
            <div style={styles.reviewRow}>
              <span style={styles.reviewKey}>Rh/Rc Jumper</span>
              <span style={styles.reviewVal}>{jumperRemoved === true ? "Removed" : jumperRemoved === false ? "Installed" : "—"}</span>
            </div>

            <div style={styles.sectionHead}>Equipment</div>
            <div style={styles.reviewRow}>
              <span style={styles.reviewKey}>Heat</span>
              <span style={styles.reviewVal}>{heatEquip || "—"}</span>
            </div>
            <div style={styles.reviewRow}>
              <span style={styles.reviewKey}>Cool</span>
              <span style={styles.reviewVal}>{coolEquip || "—"}</span>
            </div>
            {isHeatPump && (
              <div style={styles.reviewRow}>
                <span style={styles.reviewKey}>Backup Heat</span>
                <span style={styles.reviewVal}>{backupHeat || "—"}</span>
              </div>
            )}
            {isHeatPump && (
              <div style={styles.reviewRow}>
                <span style={styles.reviewKey}>O/B</span>
                <span style={styles.reviewVal}>{revValve ? `Energized on ${revValve}` : "—"}</span>
              </div>
            )}
            <div style={styles.reviewRow}>
              <span style={styles.reviewKey}>Operating Mode</span>
              <span style={styles.reviewVal}>{equipMode || "—"}</span>
            </div>
            <div style={styles.reviewRow}>
              <span style={styles.reviewKey}>Default Range</span>
              <span style={styles.reviewVal}>{tempMin}°F – {tempMax}°F</span>
            </div>
            <div style={styles.reviewRow}>
              <span style={styles.reviewKey}>Building</span>
              <span style={styles.reviewVal}>{buildingDisplay}</span>
            </div>
            <div style={styles.reviewRow}>
              <span style={styles.reviewKey}>Zone Characteristics</span>
              <span style={styles.reviewVal}>{zoneCharLabel}</span>
            </div>
            {sensorType && sensorType !== "none" && (
              <div style={styles.reviewRow}>
                <span style={styles.reviewKey}>Sensors Installed</span>
                <span style={{ ...styles.reviewVal, display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 5 }}>
                  {stickerInfo && <span style={{ fontSize: 14, color: stickerInfo.color, lineHeight: 1 }}>{stickerInfo.shape}</span>}
                  {sensorTypeLabel}{sensorLocation ? ` — ${sensorLocation}` : ""}
                </span>
              </div>
            )}
          </>
        )}

        {wiringError.length > 0 && (
          <div style={{ ...styles.noteRed, margin: "16px 0" }}>
            ⚠ Configuration errors must be resolved before submitting.
            {wiringError.map(e => <div key={e}>• {e}</div>)}
          </div>
        )}

        <div style={{ marginTop: 20 }}>
          <div style={{ ...styles.btnRow, marginTop: 0, marginBottom: 10 }}>
            <button style={{ ...styles.btnSecondary, flex: 1 }} onClick={() => go(installType === "ff" ? SCREENS.FF_EQUIP_CONFIG : SCREENS.ZONE_INFO)}>Back</button>
            <button style={{ ...styles.btnPrimary, flex: 2 }} onClick={() => go(SCREENS.TRACKER)}>
              Check Connectivity
            </button>
          </div>
          <button style={{ ...styles.btnSecondary, width: "100%" }} onClick={() => go(SCREENS.SCAN_QR)}>
            Next Install
          </button>
        </div>
      </div>
    );
  }

  function renderConnectivity() {
    const stickerMap = {
      "Green Triangle":  { shape: "▲", color: "#2D7A45" },
      "Orange Triangle": { shape: "▲", color: "#D4820A" },
      "Blue Star":       { shape: "★", color: "#1A5FA6" },
      "Purple Chess":    { shape: "♜", color: "#6B3A8A" },
    };
    const MOCK_SENSOR_STATUSES = ["complete", "inprogress", "complete", "inprogress"];

    function StatusBadge({ status }) {
      const cfg = {
        complete:   { color: C.green,   label: "Complete" },
        inprogress: { color: "#D4820A", label: "In Progress" },
        failed:     { color: C.red,     label: "Failed" },
      }[status] || { color: C.muted, label: "—" };
      return (
        <span style={{ display: "flex", alignItems: "center", gap: 5, flexShrink: 0 }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: cfg.color, display: "inline-block" }} />
          <span style={{ fontSize: 11, color: cfg.color, fontWeight: 600 }}>{cfg.label}</span>
        </span>
      );
    }

    function DeviceRow({ label, status, indent }) {
      return (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingLeft: indent ? 16 : 0, paddingTop: 8, paddingBottom: 8, borderBottom: `1px solid ${C.border}` }}>
          <span style={{ fontSize: indent ? 12 : 13, color: indent ? C.muted : C.text, fontWeight: indent ? 400 : 600, flex: 1, marginRight: 8 }}>{label}</span>
          <StatusBadge status={status} />
        </div>
      );
    }

    const hvacDeviceLabel = zoneName ? `HVAC — ${zoneName}` : "HVAC Unit";
    const sensorTypeLabel = sensorType === "ambient" ? "Ambient Air" : sensorType === "supply" ? "Supply Air Duct" : "Return Air Duct";
    const sensorSI = stickerMap[sensorSymbol];
    const sensorLabel = `${sensorSI ? sensorSI.shape + " " : ""}${sensorSymbol ? sensorSymbol + " · " : ""}${sensorTypeLabel}${sensorLocation ? " — " + sensorLocation : ""}`;

    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Connectivity</div>
        <div style={{ fontSize: 12, color: C.muted, marginBottom: 20 }}>Connectivity is confirmed once each device and sensor shows Complete.</div>

        {installType === "ff" ? (
          <>
            <DeviceRow label="F/F Hub" status="complete" indent={false} />
            {ffSensors.map((s, i) => {
              const si = stickerMap[s.symbol];
              const label = `${si ? si.shape + " " : ""}${s.symbol ? s.symbol + " · " : ""}${s.unitName || "—"} (${s.refrigType || "—"})`;
              return <DeviceRow key={i} label={label} status={MOCK_SENSOR_STATUSES[i % MOCK_SENSOR_STATUSES.length]} indent={true} />;
            })}
          </>
        ) : (
          <>
            <DeviceRow label={hvacDeviceLabel} status="complete" indent={false} />
            {sensorSymbol || sensorType ? (
              <DeviceRow label={sensorLabel} status={MOCK_SENSOR_STATUSES[0]} indent={true} />
            ) : null}
          </>
        )}

        <div style={{ marginTop: 30 }}>
          <button style={{ ...styles.btnPrimary, marginBottom: 10 }} onClick={() => go(SCREENS.TRACKER)}>
            Next Install
          </button>
          <button style={styles.btnSecondary} onClick={() => go(SCREENS.WELCOME)}>
            Building Install Complete
          </button>
        </div>
      </div>
    );
  }

  // ── Tracker & Troubleshooting ────────────────────────────────────────────────

  function renderTracker() {
    const mockDevices = [
      {
        name: "Zone A — Main Office",
        building: "123 Main St — Building A",
        deviceStatus: "complete",
        deviceType: "hvac",
        sensors: [
          { label: "▲ Ambient Air — Near east window", status: "issue_identified" },
        ],
      },
      {
        name: "Zone B — Conference Room",
        building: "123 Main St — Building A",
        deviceStatus: "complete",
        deviceType: "hvac",
        sensors: [
          { label: "★ Supply Air Duct — Main duct", status: "complete" },
        ],
      },
      {
        name: "Zone C — Warehouse",
        building: "123 Main St — Building A",
        deviceStatus: "issue_identified",
        deviceType: "hvac",
        sensors: [
          { label: "▲ Return Air Duct — West wall", status: "inprogress" },
        ],
      },
      {
        name: "F/F Hub",
        building: "123 Main St — Building A",
        deviceStatus: "complete",
        deviceType: "ff",
        sensors: [
          { label: "♜ Walk-In #1 — Fridge", status: "issue_identified" },
          { label: "▲ Walk-In #2 — Freezer", status: "complete" },
        ],
      },
    ];

    function StatusBadge({ status, onIssueClick }) {
      if (status === "issue_identified") {
        return (
          <button onClick={onIssueClick} style={{ display: "flex", alignItems: "center", gap: 5, flexShrink: 0, background: "transparent", color: C.red, border: `1.5px solid ${C.red}`, borderRadius: 6, padding: "3px 8px", cursor: "pointer", fontSize: 11, fontWeight: 600 }}>
            Issue Identified →
          </button>
        );
      }
      const cfg = {
        complete:   { color: C.green,   label: "Complete" },
        inprogress: { color: "#D4820A", label: "In Progress" },
      }[status] || { color: C.muted, label: "—" };
      return (
        <span style={{ display: "flex", alignItems: "center", gap: 5, flexShrink: 0 }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: cfg.color, display: "inline-block" }} />
          <span style={{ fontSize: 11, color: cfg.color, fontWeight: 600 }}>{cfg.label}</span>
        </span>
      );
    }

    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Connectivity Tracker</div>
        <div style={{ fontSize: 11, color: C.muted, marginBottom: 16 }}>{mockDevices[0].building}</div>

        {/* Legend */}
        <div style={{ border: `1px solid ${C.border}`, borderRadius: 10, padding: "10px 14px", marginBottom: 20 }}>
          {/* Complete row with inline expand */}
          <div style={{ paddingBottom: showCompleteModal ? 10 : 0 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: C.green, display: "inline-block" }} />
                <span style={{ fontSize: 12, fontWeight: 600, color: C.text }}>Complete</span>
              </div>
              <button onClick={() => setShowCompleteModal(v => !v)} style={{ background: "none", border: "none", color: C.text, fontSize: 10, fontWeight: 400, cursor: "pointer", display: "flex", alignItems: "center", gap: 3 }}>
                More {showCompleteModal ? "▲" : "▼"}
              </button>
            </div>
            {showCompleteModal && (
              <div style={{ marginTop: 12 }}>
                <div style={{ marginBottom: 14 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: C.text, marginBottom: 4 }}>HVAC Connectivity</div>
                  <div style={{ fontSize: 11, color: C.muted, lineHeight: 1.5, marginBottom: 8 }}>Complete when the Home Screen appears on the device:</div>
                  <img src="/Home Screen HVAC.png" alt="HVAC Home Screen" style={{ width: "70%", borderRadius: 10, display: "block", margin: "0 auto" }} />
                </div>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: C.text, marginBottom: 4 }}>F/F Connectivity</div>
                  <div style={{ fontSize: 11, color: C.muted, lineHeight: 1.5, marginBottom: 8 }}>Complete when the Home Screen appears and all sensors have temperature readings:</div>
                  <img src="/Home Screen FF.png" alt="F/F Home Screen" style={{ width: "70%", borderRadius: 10, display: "block", margin: "0 auto" }} />
                </div>
              </div>
            )}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, paddingTop: 8, borderTop: `1px solid ${C.border}` }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#D4820A", display: "inline-block" }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: C.text }}>In Progress</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, paddingTop: 8, borderTop: `1px solid ${C.border}`, marginTop: 8 }}>
            <span style={{ border: `1.5px solid ${C.red}`, borderRadius: 6, padding: "1px 6px", fontSize: 11, fontWeight: 600, color: C.red }}>Issue Identified</span>
          </div>
        </div>

        {mockDevices.map((device, di) => (
          <div key={di} style={{ marginBottom: 20 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: 6, borderBottom: `1px solid ${C.border}` }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: C.text }}>{device.name}</div>
              <StatusBadge status={device.deviceStatus} onIssueClick={() => { setTroubleshootContext("device"); setWifiChoice(""); go(SCREENS.TROUBLESHOOTING); }} />
            </div>
            {device.sensors.map((s, si) => (
              <div key={si} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingLeft: 14, paddingTop: 6, paddingBottom: 6, borderBottom: `1px solid ${C.border}` }}>
                <span style={{ fontSize: 12, color: C.muted, flex: 1, marginRight: 8 }}>{s.label}</span>
                <StatusBadge status={s.status} onIssueClick={() => { setTroubleshootContext(device.deviceType === "ff" ? "sensor_ff" : "sensor_hvac"); go(SCREENS.TROUBLESHOOTING); }} />
              </div>
            ))}
          </div>
        ))}

        <div style={{ marginTop: 8 }}>
          <button style={{ ...styles.btnPrimary, marginBottom: 10 }} onClick={() => go(SCREENS.SCAN_QR)}>
            Next Install
          </button>
          <button style={styles.btnSecondary} onClick={() => go(SCREENS.WELCOME)}>
            Building Install Complete
          </button>
        </div>
      </div>
    );
  }

  function renderTroubleshooting() {
    const imgStyle = { width: "70%", borderRadius: 10, display: "block", margin: "8px auto 0" };
    const bullet = { fontSize: 12, color: C.muted, lineHeight: 1.6 };
    const subBullet = { ...bullet, paddingLeft: 16 };
    const stepTitle = { fontSize: 13, fontWeight: 700, color: C.text, marginBottom: 6 };

    function DeviceContent() {
      return (
        <>
          <div style={{ fontSize: 12, color: C.muted, marginBottom: 16, lineHeight: 1.5 }}>
            If cellular is not connecting, a WiFi network can be used.
          </div>

          <div style={styles.infoBox}>
            <div style={stepTitle}>Step 1 — Confirm WiFi network is compatible</div>
            <div style={bullet}>• On your phone, open <strong>Settings</strong> and navigate to <strong>WiFi</strong></div>
            <div style={bullet}>• Join the network — if it opens a page to agree to terms and conditions or enter an email, it <strong>cannot</strong> be used</div>
          </div>

          <div style={{ fontSize: 12, fontWeight: 600, color: C.text, margin: "16px 0 8px" }}>Next Step</div>
          <div style={styles.radioRow}>
            <div style={styles.radioBtn(wifiChoice === "compatible")} onClick={() => setWifiChoice("compatible")}>WiFi Compatible</div>
            <div style={styles.radioBtn(wifiChoice === "not_compatible")} onClick={() => setWifiChoice("not_compatible")}>WiFi Not Compatible</div>
          </div>

          {wifiChoice === "compatible" && (
            <div style={{ marginTop: 16 }}>
              <div style={{ ...styles.noteBlue, marginBottom: 12 }}>Note the Wifi network name and password before proceeding.</div>
              <div style={styles.infoBox}>
                <div style={stepTitle}>On the Device</div>
                <div style={bullet}>• Use the buttons to select <strong>More Options</strong></div>
                <div style={bullet}>• Select <strong>WiFi Setup</strong></div>
                <div style={bullet}>• Screen will show <em>"Initializing Wi-Fi"</em></div>
                <div style={bullet}>• A new QR code will appear</div>
              </div>
              <div style={styles.infoBox}>
                <div style={stepTitle}>On Your Phone</div>
                <div style={bullet}>• Scan QR code to connect to the <strong>cognition_controls</strong> network</div>
                <div style={bullet}>• Enter the network password (if required)</div>
                <div style={bullet}>• <strong>"Connection Successful"</strong> will appear on your phone</div>
              </div>
                <div style={styles.infoBox}>
                <div style={stepTitle}>Confirm Connection</div>
                <div style={bullet}>• The device screen will show <em>"Connecting to WiFi"</em></div>
                <div style={bullet}>• Wait 2 minutes — install is complete when the Home Screen appears (see images below)</div>
              </div>
              <div style={{ fontSize: 12, fontWeight: 600, color: C.text, marginTop: 12, marginBottom: 4 }}>HVAC Home Screen</div>
              <img src="/Home Screen HVAC.png" alt="HVAC Home Screen" style={imgStyle} />
              <div style={{ fontSize: 12, fontWeight: 600, color: C.text, marginTop: 12, marginBottom: 4 }}>F/F Home Screen</div>
              <img src="/Home Screen FF.png" alt="F/F Home Screen" style={imgStyle} />
            </div>
          )}

          {wifiChoice === "not_compatible" && (
            <div style={{ marginTop: 16 }}>
              <div style={{ ...styles.noteBlue, marginBottom: 12 }}><strong>Complete an Offline Set-Up:</strong> In Offline mode the device will continue to try and establish a cellular connection.</div>
              <div style={{ fontSize: 12, color: C.muted, marginBottom: 12, lineHeight: 1.5 }}>This requires two smartphones — one as a temporary hotspot, one to connect the device to it.</div>
              <div style={styles.infoBox}>
                <div style={stepTitle}>1. With Phone #1:</div>
                <div style={bullet}>• Turn on the phone hotspot</div>
                <div style={bullet}>• Note the Hotspot Name and Password</div>
              </div>
              <div style={styles.infoBox}>
                <div style={stepTitle}>2. On the Device</div>
                <div style={bullet}>• Use the buttons to find and select <strong>More Options</strong></div>
                <div style={bullet}>• Select <strong>Offline Setup</strong></div>
                <div style={bullet}>• After 10 seconds a new QR code will appear</div>
              </div>
              <div style={styles.infoBox}>
                <div style={stepTitle}>3. With Phone #2</div>
                <div style={bullet}>• Scan the QR code — your phone will connect to <strong>cognition_controls</strong></div>
                <div style={bullet}>• You will be redirected to the Cognition Controls portal</div>
                <div style={bullet}>• Enter the Hotspot Name and Password from Phone #1</div>
              </div>
              <div style={styles.infoBox}>
                <div style={stepTitle}>4. Confirm Offline Mode</div>
                <div style={bullet}>• The device screen indicates <strong>"Connection Successful"</strong></div>
                <div style={bullet}>• The device screen changes to the Home Screen (see images below)</div>
              </div>
              <div style={{ fontSize: 12, fontWeight: 600, color: C.text, marginTop: 12, marginBottom: 4 }}>HVAC Home Screen</div>
              <img src="/Home Screen HVAC.png" alt="HVAC Home Screen" style={imgStyle} />
              <div style={{ fontSize: 12, fontWeight: 600, color: C.text, marginTop: 12, marginBottom: 4 }}>F/F Home Screen</div>
              <img src="/Home Screen FF.png" alt="F/F Home Screen" style={imgStyle} />
            </div>
          )}
        </>
      );
    }

    function SensorHvacContent() {
      return (
        <div style={styles.infoBox}>
          <div style={stepTitle}>Ensure the sensor meets the installation criteria</div>
          <div style={bullet}>• Sensor must be within <strong>40 ft</strong> of the paired device</div>
          <div style={bullet}>• No more than <strong>2 walls</strong> between the sensor and the device it is paired with</div>
        </div>
      );
    }

    function SensorFfContent() {
      return (
        <div style={styles.infoBox}>
          <div style={stepTitle}>Ensure the sensor meets the installation criteria</div>
          <div style={bullet}>• Hub must be within <strong>10 ft</strong> of the walk-in fridge/freezer door</div>
          <div style={bullet}>• The sensor <strong>green sticker must face the Hub</strong></div>
          <div style={bullet}>• Sensor must be no more than <strong>15 ft</strong> from the Hub</div>
        </div>
      );
    }

    const titles = { device: "Connectivity — Next Steps", sensor_hvac: "HVAC Sensor Connectivity", sensor_ff: "F/F Sensor Connectivity" };

    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Troubleshooting</div>
        <div style={{ fontSize: 12, fontWeight: 600, color: C.muted, marginBottom: 16 }}>{titles[troubleshootContext]}</div>

        {troubleshootContext === "device" && <DeviceContent />}
        {troubleshootContext === "sensor_hvac" && <SensorHvacContent />}
        {troubleshootContext === "sensor_ff" && <SensorFfContent />}

        <div style={{ ...styles.btnRow, marginTop: 24 }}>
          <button style={{ ...styles.btnSecondary, flex: 1 }} onClick={() => go(SCREENS.TRACKER)}>← Back to Tracker</button>
        </div>
      </div>
    );
  }

  function renderScanQR() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Next Install</div>
        <div style={{ fontSize: 13, color: C.muted, marginBottom: 24 }}>Scan the QR code on the next device to be installed.</div>
        <div style={{ fontSize: 12, color: C.muted, lineHeight: 1.5 }}>
          QR codes are unique to each device. Scanning will automatically begin the install flow.
        </div>
        <div style={{ marginTop: 30 }}>
          <button style={{ ...styles.btnSecondary, width: "100%" }} onClick={() => go(SCREENS.TRACKER)}>← Back to Tracker</button>
        </div>
      </div>
    );
  }

  // ── F/F Screens ─────────────────────────────────────────────────────────────

  function renderFFHubInstall() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>F/F Hub Install</div>

        <div style={{ ...styles.noteAmber, marginBottom: 16 }}>
          <div style={{ fontWeight: 700, marginBottom: 4 }}>⚠ PLACEMENT REQUIREMENT</div>
          <div><strong>Hub must be placed within 10ft</strong> of the walk-in fridges/freezers it will monitor.</div>
          <div style={{ marginTop: 6 }}>Hub can monitor up to <strong>4</strong> fridges/freezers (4 sensors).</div>
        </div>

        <div style={styles.sectionHead}>Instructions</div>

        <div style={styles.infoBox}>
          <div style={{ fontSize: 14, fontWeight: 700, color: C.text, marginBottom: 6 }}>1. Mount the plate:</div>
          <div style={{ fontSize: 12, color: C.muted }}>Use screws to mount the wall plate to the wall.
          </div>
        </div>

        <div style={styles.infoBox}>
          <div style={{ fontSize: 14, fontWeight: 700, color: C.text, marginBottom: 6 }}>2. Attach Hub to wall plate</div>
        </div>

        <div style={styles.infoBox}>
          <div style={{ fontSize: 14, fontWeight: 700, color: C.text, marginBottom: 4 }}>3. Connect power</div>
          <div style={{ fontSize: 12, color: C.muted }}>Insert power brick into outlet and connect USB-C cable to brick.</div>
        </div>

        <div style={styles.infoBox}>
          <div style={{ fontSize: 14, fontWeight: 700, color: C.text, marginBottom: 4 }}>4. Route USB-C cable</div>
          <div style={{ fontSize: 12, color: C.muted }}>Route USB-C cable to the port on the right hand side of the Hub.</div>
          <div style={{ ...styles.noteAmber, marginTop: 10, marginBottom: 0 }}>
            ⚠ Ensure cable is secure and will not be unplugged.
          </div>
        </div>

        <div style={{ ...styles.btnRow, marginTop: 16 }}>
          <button style={{ ...styles.btnSecondary, flex: 1 }} onClick={() => go(SCREENS.CEILING_INSTALL)}>
            No Outlet
          </button>
          <button style={{ ...styles.btnPrimary, flex: 2 }} onClick={() => go(SCREENS.FF_POWER_CHECK)}>
            Next
          </button>
        </div>
      </div>
    );
  }

  function renderCeilingInstall() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Ceiling Install</div>
        <div style={{ fontSize: 12, color: C.muted, lineHeight: 1.5, marginBottom: 16 }}>
          The Hub can be installed in a ceiling above the Fridge/Freezer:
        </div>
        {[
          "Ensure that an outlet can reach the ceiling location",
          "Place hub in ceiling above the fridge/freezer",
          "Hub must face down toward the fridge/freezer",
          <>It should <strong>NOT</strong> be in the fridge/freezer</>,
          <><strong>Required:</strong> Use a spacer (e.g. cardboard) to create a gap between the fridge/freezer roof and the hub for better connectivity</>,
          "Power the Hub — insert power brick into outlet, connect brick to Hub using USB-C cable",
          "Scan QR Code and complete configuration",
        ].map((step, i) => (
          <div key={i} style={{ ...styles.infoBox, marginBottom: 8 }}>
            <div style={{ display: "flex", gap: 8 }}>
              <span style={{ fontSize: 13, color: C.green, fontWeight: 700, minWidth: 16 }}>{i + 1}.</span>
              <span style={{ fontSize: 13, color: C.muted, lineHeight: 1.5 }}>{step}</span>
            </div>
          </div>
        ))}
        <div style={{ ...styles.btnRow, marginTop: 16 }}>
          <button style={{ ...styles.btnSecondary, flex: 1 }} onClick={() => go(SCREENS.FF_HUB_INSTALL)}>Back</button>
          <button style={{ ...styles.btnPrimary, flex: 2 }} onClick={() => go(SCREENS.FF_POWER_CHECK)}>Next</button>
        </div>
      </div>
    );
  }

  function renderFFPowerCheck() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Power Check</div>
        <div style={styles.noteBlue}>
          <strong>Is the bar in the top-right corner of the device moving?</strong>
          <div style={{ marginTop: 4 }}>The bar shifts position every 1–3 seconds when powered.</div>
        </div>
        <div style={styles.screenSub}>
          <div style={{ marginTop: 15 }} />
          When powered, cellular connectivity automatically initiates. Connectivity can take up to 15 minutes to complete.
        </div>
        <div style={{ height: 20 }} />
        <button style={{ ...styles.btnSecondary, marginBottom: 10, ...(flashBtn === "ff-bar-moving" ? { borderColor: C.green, background: C.greenBg, color: C.green } : {}) }}
          onClick={() => flash("ff-bar-moving", () => go(SCREENS.SENSOR_PAIR))}>
          Bar is moving — device is powered
        </button>
        <button style={{ ...styles.btnSecondary, ...(flashBtn === "ff-bar-not-moving" ? { borderColor: C.green, background: C.greenBg, color: C.green } : {}) }}
          onClick={() => flash("ff-bar-not-moving", () => go(SCREENS.FF_POWER_ISSUE))}>
          Bar is not moving
        </button>
      </div>
    );
  }

  function renderFFPowerIssue() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Check Hub Power</div>
        <div style={{ ...styles.screenSub, marginTop: 15, marginBottom: 6 }}>Check that:</div>
        <div style={{ marginTop: 0 }}>
          <div style={styles.infoRow}>• USB-C power brick is fully plugged into the outlet</div>
          <div style={styles.infoRow}>• USB-C cable is completely plugged into the power brick and the port on the Hub</div>
        </div>
        <div>
  
        </div>
        <div style={{ height: 20, marginTop: 20 }} />
        <button style={{ ...styles.btnPrimary, marginBottom: 10 }} onClick={() => go(SCREENS.SENSOR_PAIR)}>
          Hub has Power
        </button>
        <button style={styles.btnSecondary} onClick={() => go(SCREENS.POWER_FAILED)}>
          No Power
        </button>
      </div>
    );
  }

  function renderFFSensorInstall() {
    return (
      <div style={styles.card}>
        <div style={styles.screenTitle}>Sensor Install</div>

        <div style={styles.infoBox}>
          <div style={{ fontSize: 14, fontWeight: 700, color: C.text, marginBottom: 8 }}>Placement</div>
          <div style={{ fontSize: 13, color: C.muted, lineHeight: 1.4 }}>
            <div style={{ marginBottom: 4 }}>• <strong>Position:</strong> Front underside of a shelf, where the pole meets the shelf</div>
            <div style={{ marginBottom: 4 }}>• <strong>Depth:</strong> Middle to front</div>
            <div style={{ marginBottom: 4 }}>• <strong>Height:</strong> Mid-wall height</div>
            <div style={{ marginBottom: 4 }}>• Use the zip ties to secure the sensor</div>
            <div>• If no shelving available, adhere sensor to wall adhering to placement guidance</div>
          </div>
        </div>

        <div style={{ ...styles.noteAmber, marginBottom: 12 }}>
          ⚠ <strong>ENSURE GREEN STICKER ON SENSOR FACES HUB</strong>
        </div>

        <img src="/placement-image.png" alt="Sensor placement guide" style={{ width: "100%", borderRadius: 10, marginBottom: 16 }} />

        <div style={styles.btnRow}>
          <button style={{ ...styles.btnSecondary, flex: 1 }} onClick={() => go(SCREENS.SENSOR_PAIR)}>Back</button>
          <button style={{ ...styles.btnPrimary, flex: 2 }} onClick={() => go(SCREENS.FF_EQUIP_CONFIG)}>
            Next — Equipment Config
          </button>
        </div>
      </div>
    );
  }

  function renderFFEquipConfig() {
    const fridgeTemps = Array.from({ length: 26 }, (_, i) => 25 + i);   // 25–50
    const freezerTemps = Array.from({ length: 41 }, (_, i) => -15 + i); // -15–25
    const tempOptions = ffRefrigType === "Fridge" ? fridgeTemps : ffRefrigType === "Freezer" ? freezerTemps : [];
    const valid = ffRefrigType && ffRangeLow && ffRangeHigh && ffUnitName && buildingSelected;

    return (
      <div style={{ ...styles.card, marginBottom: 20 }}>
        <div style={styles.screenTitle}>Equipment Configuration</div>

        <div style={styles.fieldGroup}>
          <label style={{ ...styles.label, marginTop: 30,...(showFfEquipErrors && !ffRefrigType ? { color: C.red } : {}) }}>Refrigeration Type</label>
          <div style={styles.radioRow}>
            <div style={styles.radioBtn(ffRefrigType === "Fridge")} onClick={() => { setFfRefrigType("Fridge"); setFfRangeLow(""); setFfRangeHigh(""); }}>Fridge</div>
            <div style={styles.radioBtn(ffRefrigType === "Freezer")} onClick={() => { setFfRefrigType("Freezer"); setFfRangeLow(""); setFfRangeHigh(""); }}>Freezer</div>
          </div>
        </div>

        <div style={styles.fieldGroup}>
          <label style={{ ...styles.label, marginTop: 20, ...(showFfEquipErrors && (!ffRangeLow || !ffRangeHigh) ? { color: C.red } : {}) }}>Operating Range</label>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <select
              style={{ ...styles.select, flex: 1, ...(ffRangeLow ? styles.selectDone : {}), ...(showFfEquipErrors && !ffRangeLow ? { borderColor: C.red } : {}) }}
              value={ffRangeLow}
              onChange={e => setFfRangeLow(e.target.value)}
              disabled={!ffRefrigType}
            >
              <option value="">{ffRefrigType ? "Lower" : "—"}</option>
              {tempOptions.map(t => <option key={t}>{t}</option>)}
            </select>
            <span style={{ color: C.muted, fontSize: 13 }}>to</span>
            <select
              style={{ ...styles.select, flex: 1, ...(ffRangeHigh ? styles.selectDone : {}), ...(showFfEquipErrors && !ffRangeHigh ? { borderColor: C.red } : {}) }}
              value={ffRangeHigh}
              onChange={e => setFfRangeHigh(e.target.value)}
              disabled={!ffRefrigType}
            >
              <option value="">{ffRefrigType ? "Upper" : "—"}</option>
              {tempOptions.map(t => <option key={t}>{t}</option>)}
            </select>
            <span style={{ color: C.muted, fontSize: 13 }}>°F</span>
          </div>
          <div style={styles.hint}>Sets the target operating range.</div>
        </div>

        <div style={styles.fieldGroup}>
          <label style={{ ...styles.label, marginTop: 20, ...(showFfEquipErrors && !ffUnitName ? { color: C.red } : {}) }}>Fridge / Freezer Name</label>
          <input
            style={{ ...styles.input, ...(showFfEquipErrors && !ffUnitName ? { borderColor: C.red } : {}) }}
            placeholder="e.g. Walk-in Freezer A"
            value={ffUnitName}
            onChange={e => setFfUnitName(e.target.value)}
            maxLength={40}
          />
          <div style={styles.hint}>Max 40 characters. Appears in Cognition dashboard.</div>
        </div>

        <div style={styles.fieldGroup}>
          <label style={{ ...styles.label, marginTop: 20, ...(showFfEquipErrors && !buildingSelected ? { color: C.red } : {}) }}>Building Address</label>
          <select
            style={{ ...styles.select, ...(buildingSelected ? styles.selectDone : {}), ...(showFfEquipErrors && !buildingSelected ? { borderColor: C.red } : {}) }}
            value={buildingSelected}
            onChange={e => setBuildingSelected(e.target.value)}
          >
            <option value="">Select a building</option>
            <option value="new">Enter New Address</option>
            {SAMPLE_BUILDINGS.map(b => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>

        {buildingSelected === "new" && (
          <>
            <div style={styles.fieldGroup}>
              <label style={styles.label}>Street Address</label>
              <input style={styles.input} placeholder="e.g. 123 Main St" value={addrStreet} onChange={e => setAddrStreet(e.target.value)} />
            </div>
            <div style={styles.fieldGroup}>
              <label style={styles.label}>Suite / Unit <span style={{ color: C.muted, fontWeight: 400 }}>(optional)</span></label>
              <input style={styles.input} placeholder="e.g. Suite 200" value={addrSuite} onChange={e => setAddrSuite(e.target.value)} />
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              <div style={{ ...styles.fieldGroup, flex: 1 }}>
                <label style={styles.label}>City</label>
                <input style={styles.input} placeholder="City" value={addrCity} onChange={e => setAddrCity(e.target.value)} />
              </div>
              <div style={{ ...styles.fieldGroup, flex: 1 }}>
                <label style={styles.label}>ZIP / Postal Code</label>
                <input style={styles.input} placeholder="e.g. 90210" value={addrZip} onChange={e => setAddrZip(e.target.value)} />
              </div>
            </div>
            <div style={styles.fieldGroup}>
              <label style={styles.label}>Country</label>
              <select style={{ ...styles.select, ...(addrCountry ? styles.selectDone : {}) }} value={addrCountry} onChange={e => setAddrCountry(e.target.value)}>
                <option value="USA">USA</option>
                <option value="Canada">Canada</option>
              </select>
            </div>
          </>
        )}

        <div style={styles.btnRow}>
          <button style={{ ...styles.btnSecondary, flex: 1 }} onClick={() => go(SCREENS.FF_SENSOR_INSTALL)}>Back</button>
          <button
            style={{ ...styles.btnPrimary, flex: 2, opacity: valid ? 1 : 0.5 }}
            onClick={() => {
              if (!valid) { setShowFfEquipErrors(true); return; }
              setShowFfEquipErrors(false);
              go(SCREENS.SENSOR_CONFIRM);
            }}
          >
            Next — Review
          </button>
        </div>
      </div>
    );
  }

  // ── Screen router ───────────────────────────────────────────────────────────
  const screens = [
    renderInstallType,    // 0: welcome
    renderInstallSelect,  // 1: install type selection
    renderPowerCheck,     // 2
    renderPowerIssue,     // 3
    renderPowerFailed,    // 4
    renderWiring,         // 5
    renderEquipment,      // 6
    renderSensors,        // 7
    renderSensorPair,     // 8
    renderSensorInstall,  // 9
    renderSensorConfirm,  // 10
    renderZoneInfo,       // 11
    renderReview,         // 12 (comfort removed)
    renderReview,         // 13
    renderConnectivity,   // 14
    renderFFHubInstall,   // 15
    renderFFPowerCheck,   // 16
    renderFFPowerIssue,   // 17
    renderFFSensorInstall,// 18
    renderFFEquipConfig,  // 19
    renderTracker,        // 20
    renderTroubleshooting,// 21
    renderScanQR,         // 22
    renderCeilingInstall, // 23
  ];

  // Note: screen 12 is "review" = index 12 → maps to renderReview (index 12 in array above: renderReview is at 12, renderConnectivity at 13)

  return (
  <div style={{ display: "flex", justifyContent: "center", background: "#e5e5e5", minHeight: "100vh", padding: "24px 0" }}>
    <div style={{ width: 390, background: C.bg, borderRadius: 40, overflow: "hidden", boxShadow: "0 20px 60px rgba(0,0,0,0.3)" }}>
      <div style={styles.app}>
        <Header onStartOver={startOver} onTracker={() => go(SCREENS.TRACKER)} showTracker={installedDevices.length > 0} screenIdx={screen} />
        <Progress screenIdx={screen} />
        {screens[screen] ? screens[screen]() : <div>Unknown screen</div>}
      </div>
    </div>
  </div>
);

}