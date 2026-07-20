import { useState, useMemo } from "react";

const G = {
  dark: "#1A3828", mid: "#2D6A4F", accent: "#7dc02c",
  light: "#D8F3DC", lighter: "#F0FAF2", border: "#7dc02c",
};

const fmt = n => Number(n).toLocaleString();

const whySteps = [
  { title: "Pays for Itself", subtitle: "By reducing energy and service costs.", desc: "Dashboard data and tools to tailor settings, target issues, and reduce unnecessary costs.", bg: "linear-gradient(135deg, #1a3828 0%, #2d6a4f 60%, #52b788 100%)", pattern: "dashboard", image: "/ff-operations.jpg" },
  { title: "24/7 Monitoring", subtitle: "Intelligence that gets ahead of issues.", desc: "Target maintenance, manage on-site requests, and avoid unnecessary service calls with continuous equipment monitoring.", bg: "linear-gradient(135deg, #1a3828 0%, #2d6a4f 60%, #52b788 100%)", pattern: "monitor", image: "/discovery-analyze-tab.jpg" },
  { title: "Energy Management", subtitle: "Reduce energy waste without sacrificing comfort.", desc: "Automated scheduling and control features to optimize savings during unoccupied hours, and practical tools for consistent implementation.", bg: "linear-gradient(135deg, #1a3828 0%, #2d6a4f 60%, #52b788 100%)", pattern: "energy", image: "/multi-insights-1.png" },
  { title: "Secure & Reliable", subtitle: "Long-life hardware. Connectivity without Wi-Fi exposure.", desc: "Hardware engineered for commercial settings. Cellular connectivity bypasses IT teams and headaches.", bg: "linear-gradient(135deg, #1a3828 0%, #2d6a4f 60%, #52b788 100%)", pattern: "dashboard", image: "https://blog.apnic.net/wp-content/uploads/2018/04/Cell-spotting-555x202.png" },
  { title: "Quick Install", subtitle: "Set up your site in hours.", desc: "Compatible with most 24V HVAC equipment. Your local HVAC Pro can complete the install — no other trades required.", bg: "linear-gradient(135deg, #1a3828 0%, #2d6a4f 60%, #52b788 100%)", pattern: "install", image: "/in-context-shot.jpg" },]

const platformOutcomes = [
  {
    statPrefix: "Up to", stat: "40%", label: "HVAC Runtime Reduction",
    bullets: ["Intelligent scheduling to maximize unoccupied savings.", "Practical tools for consistent implementation.", "Machine learning to automate optimal runtime and reduce cost."],
    bg: "linear-gradient(135deg,#1a3828,#2d6a4f)", pattern: "energy"
  },
  {
    statPrefix: "Up to", stat: "40% fewer", label: "Emergency Service Calls",
    bullets: ["Placeholder bullet one.", "Placeholder bullet two.", "Placeholder bullet three."],
    bg: "linear-gradient(135deg,#1B2F4E,#2563EB)", pattern: "calls"
  },
  {
    statPrefix: "Up to", stat: "XXX", label: "Placeholder",
    bullets: ["Placeholder bullet one.", "Placeholder bullet two.", "Placeholder bullet three."],
    bg: "linear-gradient(135deg,#312e81,#4f46e5)", pattern: "visibility"
  },
];

const faqs = [
  { q: "What hardware comes in the box?", a: "The Energy Management Kit includes a Cognition Smart Control and one wireless sensor. The Fridge/Freezer Monitoring Kit includes the Cognition device, a power bundle, and one waterproof sensor." },
  { q: "Do I need WiFi to use Cognition?", a: "No. Cognition uses secure cellular connectivity that works right out of the box, bypassing your IT team entirely." },
  { q: "How many sensors can I add to an HVAC device?", a: "Up to 4 sensors can be paired with each Cognition Smart Control — meaning up to 3 additional sensors per device. Sensors can be deployed for enhanced ambient temperature sensing, or supply/return air duct temperature monitoring." },
  { q: "How many sensors can I add to a Fridge/Freezer device?", a: "Fridge/Freezer devices support up to 4 total sensors, each within 15 feet of the device." },
  { q: "How is the platform priced?", a: "The Cognition Dashboard plan is billed annually. The platform fee includes: HVAC equipment data tracking and analysis, Secure cloud storage of data, Equipment alerts and reminders, Cognition Dashboard access for unlimited Users, Cognition Dashboard training, Friendly Cognition Support when you need it, Day of install support, Install preparation and project management support, Secure and reliable cellular connectivity." },
  { q: "Can multiple users access the dashboard?", a: "Yes — Cognition supports unlimited users with flexible permission levels." },
  { q: "Can I monitor both HVAC and Refrigeration on the same account?", a: "Absolutely. Your Cognition dashboard unifies all connected devices in one place." },
  { q: "What support is included?", a: "All customers receive friendly Cognition support. We'll reach out within 24 hours of your order to help with onboarding." },
  { q: "Who should install the Cognition solution?", a: "Your local HVAC Pro. Cognition can help project manage and connect you with a reputable HVAC Pro if required." },
  { q: "What HVAC equipment does Cognition not work with?", a: "Cognition does not support VAV, VRF, Mini-Splits, or line voltage systems." },
  { q: "What is the return policy?", a: "Cognition has a fair return policy. Reach out to sales@cognition.com with your return questions." },
];

function PatternBG({ type, opacity = 20 }) {
  const ps = {
    install: <svg viewBox="0 0 200 120" className="absolute inset-0 w-full h-full"><circle cx="44" cy="50" r="6" fill="white"/><circle cx="84" cy="40" r="6" fill="white"/><circle cx="124" cy="55" r="6" fill="white"/><circle cx="164" cy="45" r="6" fill="white"/><path d="M44 50 L84 40 L124 55 L164 45" stroke="white" strokeWidth="2" fill="none" strokeDasharray="4 2"/><rect x="20" y="80" width="160" height="8" rx="2" fill="white"/><rect x="40" y="55" width="8" height="25" rx="2" fill="white"/><rect x="80" y="45" width="8" height="35" rx="2" fill="white"/><rect x="120" y="60" width="8" height="20" rx="2" fill="white"/><rect x="160" y="50" width="8" height="30" rx="2" fill="white"/></svg>,
    control: <svg viewBox="0 0 200 120" className="absolute inset-0 w-full h-full"><rect x="30" y="25" width="140" height="70" rx="8" stroke="white" strokeWidth="2" fill="none"/><circle cx="100" cy="60" r="20" stroke="white" strokeWidth="2" fill="none"/><circle cx="100" cy="60" r="6" fill="white"/><line x1="100" y1="40" x2="100" y2="45" stroke="white" strokeWidth="2"/><line x1="100" y1="75" x2="100" y2="80" stroke="white" strokeWidth="2"/><line x1="80" y1="60" x2="85" y2="60" stroke="white" strokeWidth="2"/><line x1="115" y1="60" x2="120" y2="60" stroke="white" strokeWidth="2"/></svg>,
    dashboard: <svg viewBox="0 0 200 120" className="absolute inset-0 w-full h-full"><rect x="15" y="20" width="80" height="50" rx="4" stroke="white" strokeWidth="1.5" fill="none"/><rect x="20" y="25" width="70" height="15" rx="2" fill="white" opacity="0.3"/><rect x="20" y="44" width="30" height="4" rx="1" fill="white"/><rect x="105" y="20" width="80" height="23" rx="4" stroke="white" strokeWidth="1.5" fill="none"/><path d="M110 65 L125 55 L140 62 L155 52 L170 58 L180 53" stroke="white" strokeWidth="2" fill="none"/><rect x="105" y="47" width="80" height="23" rx="4" stroke="white" strokeWidth="1.5" fill="none"/></svg>,
    monitor: <svg viewBox="0 0 200 120" className="absolute inset-0 w-full h-full"><circle cx="100" cy="60" r="40" stroke="white" strokeWidth="1.5" fill="none"/><circle cx="100" cy="60" r="28" stroke="white" strokeWidth="1" fill="none" strokeDasharray="3 3"/><circle cx="100" cy="60" r="4" fill="white"/><line x1="100" y1="56" x2="100" y2="35" stroke="white" strokeWidth="2"/><line x1="100" y1="56" x2="118" y2="64" stroke="white" strokeWidth="1.5"/></svg>,
    secure: <svg viewBox="0 0 200 120" className="absolute inset-0 w-full h-full"><path d="M100 15 L145 35 L145 75 Q145 98 100 110 Q55 98 55 75 L55 35 Z" stroke="white" strokeWidth="2" fill="none"/><circle cx="100" cy="62" r="10" stroke="white" strokeWidth="2" fill="none"/><rect x="94" y="62" width="12" height="10" rx="2" fill="white" opacity="0.6"/><path d="M93 62 Q93 52 100 52 Q107 52 107 62" stroke="white" strokeWidth="2" fill="none"/></svg>,
    energy: <svg viewBox="0 0 300 140" className="absolute inset-0 w-full h-full"><path d="M20 100 Q75 40 150 70 Q225 100 280 30" stroke="white" strokeWidth="2" fill="none" opacity="0.6"/><rect x="40" y="75" width="6" height="35" rx="2" fill="white" opacity="0.3"/><rect x="80" y="55" width="6" height="55" rx="2" fill="white" opacity="0.3"/><rect x="120" y="65" width="6" height="45" rx="2" fill="white" opacity="0.3"/><rect x="160" y="45" width="6" height="65" rx="2" fill="white" opacity="0.3"/><rect x="200" y="60" width="6" height="50" rx="2" fill="white" opacity="0.3"/><rect x="240" y="40" width="6" height="70" rx="2" fill="white" opacity="0.3"/></svg>,
    calls: <svg viewBox="0 0 300 140" className="absolute inset-0 w-full h-full"><circle cx="150" cy="70" r="45" stroke="white" strokeWidth="1.5" fill="none" opacity="0.4"/><circle cx="150" cy="70" r="30" stroke="white" strokeWidth="1" fill="none" opacity="0.3"/><circle cx="150" cy="70" r="5" fill="white" opacity="0.8"/><line x1="150" y1="65" x2="150" y2="35" stroke="white" strokeWidth="2" opacity="0.8"/><line x1="150" y1="65" x2="172" y2="76" stroke="white" strokeWidth="1.5" opacity="0.6"/></svg>,
    visibility: <svg viewBox="0 0 300 140" className="absolute inset-0 w-full h-full"><rect x="20" y="20" width="120" height="80" rx="6" stroke="white" strokeWidth="1.5" fill="none" opacity="0.4"/><rect x="30" y="30" width="100" height="20" rx="3" fill="white" opacity="0.15"/><rect x="160" y="20" width="120" height="37" rx="6" stroke="white" strokeWidth="1.5" fill="none" opacity="0.4"/><path d="M170 40 L185 30 L200 36 L215 26 L230 32 L245 24 L260 28 L270 22" stroke="white" strokeWidth="2" fill="none" opacity="0.6"/><rect x="160" y="65" width="120" height="35" rx="6" stroke="white" strokeWidth="1.5" fill="none" opacity="0.4"/></svg>,
  };
  return <div className="absolute inset-0 overflow-hidden rounded-xl" style={{ opacity: opacity / 100 }}>{ps[type] || null}</div>;
}

function Stepper({ value, onChange, min = 0, max = 999 }) {
  return (
    <div className="flex items-center gap-2">
      <button onClick={() => onChange(Math.max(min, value - 1))} className="w-7 h-7 rounded-full border border-slate-300 bg-white flex items-center justify-center text-slate-600 hover:bg-slate-50 cursor-pointer font-bold text-sm">−</button>
      <span className="w-8 text-center font-semibold text-slate-900 text-sm">{value}</span>
      <button onClick={() => onChange(Math.min(max, value + 1))} className="w-7 h-7 rounded-full border border-slate-300 bg-white flex items-center justify-center text-slate-600 hover:bg-slate-50 cursor-pointer font-bold text-sm">+</button>
    </div>
  );
}

// ── Modals ───────────────────────────────────────────────────────────────────
function EntryModal({ onSelect }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.5)" }}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        <div className="px-8 py-6" style={{ background: `linear-gradient(135deg, ${G.dark}, ${G.mid})` }}>
          <div className="flex items-center gap-2 mb-3"><div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: G.accent }}><span className="text-white font-bold text-xs">C</span></div><span className="text-white font-bold">Cognition</span></div>
          <h2 className="text-xl font-bold text-white">Welcome. Let's get you set up.</h2>
          <p className="text-green-100 text-sm mt-1">How would you like to continue?</p>
        </div>
        <div className="p-6 space-y-3">
          {[
            { id: "existing", icon: "👤", label: "I'm an Existing Customer", sub: "Log in with your Dashboard credentials" },
            { id: "new", icon: "✨", label: "I'm a New Customer", sub: "Explore Cognition and purchase your first kit" },
            { id: "partner", icon: "🤝", label: "I have a Partner Code", sub: "Access exclusive partner pricing" },
          ].map(o => (
            <button key={o.id} onClick={() => onSelect(o.id)} className="w-full flex items-center gap-4 p-4 rounded-xl border-2 border-slate-200 hover:border-green-400 bg-white text-left transition-all cursor-pointer">
              <span className="text-2xl">{o.icon}</span>
              <div><div className="font-semibold text-slate-900 text-sm">{o.label}</div><div className="text-xs text-slate-500 mt-0.5">{o.sub}</div></div>
              <span className="ml-auto text-slate-300">→</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function AuthModal({ onSuccess, onBack }) {
  const [u, setU] = useState(""); const [p, setP] = useState(""); const [err, setErr] = useState(false);
  const cls = "w-full border border-slate-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-green-500";
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.5)" }}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden">
        <div className="px-8 py-6" style={{ background: `linear-gradient(135deg, ${G.dark}, ${G.mid})` }}>
          <div className="flex items-center gap-2 mb-3"><div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: G.accent }}><span className="text-white font-bold text-xs">C</span></div><span className="text-white font-bold">Cognition</span></div>
          <h2 className="text-xl font-bold text-white">Sign in to your Dashboard</h2>
          <p className="text-green-100 text-sm mt-1">Use your Cognition Dashboard credentials</p>
        </div>
        <div className="p-6 space-y-3">
          <input placeholder="Username or Email" value={u} onChange={e => { setU(e.target.value); setErr(false); }} className={cls} />
          <input placeholder="Password" type="password" value={p} onChange={e => { setP(e.target.value); setErr(false); }} className={cls} />
          {err && <p className="text-red-500 text-xs">Please enter your username and password.</p>}
          <button onClick={() => { if (u && p) onSuccess(u); else setErr(true); }} className="w-full text-white font-semibold py-3 rounded-xl border-0 cursor-pointer hover:opacity-90" style={{ background: G.mid }}>Sign In →</button>
          <button onClick={onBack} className="w-full text-slate-500 text-sm py-2 bg-transparent border-0 cursor-pointer hover:text-slate-700">← Back</button>
        </div>
      </div>
    </div>
  );
}

function PartnerModal({ onSuccess, onBack }) {
  const [code, setCode] = useState(""); const [err, setErr] = useState(false);
  const cls = "w-full border border-slate-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-green-500 font-mono tracking-widest uppercase";
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.5)" }}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden">
        <div className="px-8 py-6" style={{ background: `linear-gradient(135deg, ${G.dark}, ${G.mid})` }}>
          <div className="flex items-center gap-2 mb-3"><div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: G.accent }}><span className="text-white font-bold text-xs">C</span></div><span className="text-white font-bold">Cognition</span></div>
          <h2 className="text-xl font-bold text-white">Enter your Partner Code</h2>
          <p className="text-green-100 text-sm mt-1">Your code unlocks exclusive partner pricing</p>
        </div>
        <div className="p-6 space-y-3">
          <input placeholder="e.g. COOP-2024" value={code} onChange={e => { setCode(e.target.value); setErr(false); }} className={cls} />
          {err && <p className="text-red-500 text-xs">Please enter your partner code.</p>}
          <button onClick={() => { if (code.trim()) onSuccess("Brewery Partner"); else setErr(true); }} className="w-full text-white font-semibold py-3 rounded-xl border-0 cursor-pointer hover:opacity-90" style={{ background: G.mid }}>Apply Code →</button>
          <button onClick={onBack} className="w-full text-slate-500 text-sm py-2 bg-transparent border-0 cursor-pointer hover:text-slate-700">← Back</button>
        </div>
      </div>
    </div>
  );
}

// ── Why Cognition ────────────────────────────────────────────────────────────
function WhyCognition() {
  const [active, setActive] = useState(0);
  return (
    <section className="py-16 px-6 bg-slate-100 border-b border-slate-200">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-10"><h2 className="text-4xl font-bold text-slate-900 mb-3">Save thousands of dollars with Cognition</h2><p className="text-slate-500">Achieve real operational outcomes across your portfolio of buildings.</p></div>
        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex md:flex-col gap-2 overflow-x-auto md:overflow-visible md:w-56 flex-shrink-0">
            {whySteps.map((s, i) => (
              <button key={i} onClick={() => setActive(i)}
                className="flex items-center gap-2 px-4 py-3 rounded-xl border-2 text-left transition-all cursor-pointer flex-shrink-0 w-48 md:w-full"
                style={active === i
                  ? { borderColor: G.accent, background: G.lighter, color: G.dark }
                  : { borderColor: "#E2E8F0", background: "#F8FAFC", color: "#475569" }}>
                <span className="text-sm font-semibold leading-tight">{s.title}</span>
              </button>
            ))}
          </div>
          <div className="flex-1 rounded-2xl overflow-hidden relative min-h-56" style={{ background: whySteps[active].bg }}>
            {whySteps[active].image && (
              <img src={whySteps[active].image} alt="" className="absolute inset-0 w-full h-full object-cover opacity-25" />
            )}
            <div className="relative z-10 p-8 flex flex-col justify-between h-full min-h-56">
              <div>
                <h3 className="text-2xl font-bold text-white mb-1">{whySteps[active].title}</h3>
                <p className="text-white/80 font-medium mb-2">{whySteps[active].subtitle}</p>
                <p className="text-white/70 text-sm leading-relaxed">{whySteps[active].desc}</p>
              </div>
              <div className="flex items-center gap-3 mt-5">
                <button onClick={() => setActive(Math.max(0, active - 1))} disabled={active === 0} className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white cursor-pointer border-0 disabled:opacity-30 hover:bg-white/30">←</button>
                <div className="flex gap-2">{whySteps.map((_, i) => <button key={i} onClick={() => setActive(i)} className="w-2 h-2 rounded-full border-0 cursor-pointer" style={{ background: active === i ? "white" : "rgba(255,255,255,0.4)" }} />)}</div>
                <button onClick={() => setActive(Math.min(whySteps.length - 1, active + 1))} disabled={active === whySteps.length - 1} className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white cursor-pointer border-0 disabled:opacity-30 hover:bg-white/30">→</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ── Platform Outcomes ────────────────────────────────────────────────────────
function PlatformOutcomes() {
  return (
    <section className="py-10 px-6 border-b border-slate-100" style={{ background: G.lighter }}>
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-8"><h2 className="text-4xl font-bold text-slate-900 mb-2">Save thousands of dollars with Cognition</h2><p className="text-slate-500">Achieve real operational outcomes across your portfolio of buildings.</p></div>
        <div className="flex flex-col gap-4">
          {platformOutcomes.map((o, i) => (
            <div key={i} className="rounded-2xl overflow-hidden relative flex flex-col md:flex-row" style={{ background: o.bg, minHeight: 120 }}>
              <PatternBG type={o.pattern} opacity={14} />
              {/* Left — stat + label */}
              <div className="relative z-10 p-6 md:w-56 flex-shrink-0 flex flex-col justify-center border-b border-white/10 md:border-b-0 md:border-r md:border-white/10">
                <div className="text-4xl font-bold text-white mb-1">
  {o.statPrefix && <span className="text-sm font-normal block">{o.statPrefix}</span>}
  {o.stat}
</div>
              <div className="font-bold text-white/90 text-sm leading-snug">{o.label}</div>
              </div>
              {/* Right — bullets */}
              <div className="relative z-10 p-6 flex flex-col justify-center gap-2">
                {o.bullets.map((b, j) => (
                  <div key={j} className="flex items-start gap-2">
                    <span className="text-white/60 mt-0.5 text-xs">→</span>
                    <span className="text-white/80 text-sm leading-relaxed">{b}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function LeadGateModal({ onSuccess, onDismiss }) {
  const [name, setName] = useState(""); const [email, setEmail] = useState(""); const [err, setErr] = useState(false);
  const cls = "w-full border border-slate-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-green-500";
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.5)" }}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden">
        <div className="px-8 py-6" style={{ background: `linear-gradient(135deg, ${G.dark}, ${G.mid})` }}>
          <div className="flex items-center gap-2 mb-3"><div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: G.accent }}><span className="text-white font-bold text-xs">C</span></div><span className="text-white font-bold">Cognition</span></div>
          <h2 className="text-xl font-bold text-white">Create Your Cognition Account</h2>
          <p className="text-green-100 text-sm mt-1">Enter your details to unlock options and pricing.</p>
        </div>
        <div className="p-6 space-y-3">
          <input placeholder="First & Last Name" value={name} onChange={e => { setName(e.target.value); setErr(false); }} className={cls} />
          <input placeholder="Work Email" type="email" value={email} onChange={e => { setEmail(e.target.value); setErr(false); }} className={cls} />
          {err && <p className="text-red-500 text-xs">Please enter your name and email to continue.</p>}
          <button onClick={() => { if (name.trim() && email.trim()) onSuccess({ name, email }); else setErr(true); }} className="w-full text-white font-semibold py-3 rounded-xl border-0 cursor-pointer hover:opacity-90" style={{ background: G.mid }}>Unlock Pricing →</button>
          <button onClick={onDismiss} className="w-full text-slate-500 text-sm py-2 bg-transparent border-0 cursor-pointer hover:text-slate-700">Cancel</button>
        </div>
      </div>
    </div>
  );
}

// ── Hardware Cards ───────────────────────────────────────────────────────────
function HardwareSection({ path, leadCaptured = true, hvacQty, setHvacQty, hvacSensors, setHvacSensors, ffQty, setFfQty, ffSensors, setFfSensors, monitoring, setMonitoring }) {
  const baseHVAC = 455, baseFF = 555;
  const showHVAC = monitoring === "hvac" || monitoring === "both";
  const showFF = monitoring === "ff" || monitoring === "both";
  const hvacSensorTotal = hvacSensors.ambient + hvacSensors.supply + hvacSensors.returnAir;
  const sensorError = hvacSensorTotal > hvacQty * 3;
  const setS = (key, val) => setHvacSensors(p => ({ ...p, [key]: Math.max(0, val) }));
  const showPrice = path !== "existing" && (path !== "new" || leadCaptured);
  const [imgModal, setImgModal] = useState(null);
  const [compatModal, setCompatModal] = useState(false);

  return (
    <>
      <section className="py-14 px-6 border-b border-slate-200 relative overflow-hidden" style={{ backgroundImage: "url('/DSC00730.JPG')", backgroundSize: "75%", backgroundPosition: "center", backgroundRepeat: "no-repeat" }}>
        <div className="absolute inset-0 bg-slate-900/45" />
        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-3">What Are You Monitoring?</h2>
          <p className="text-white/70 mb-8">Choose the hardware and platform to suit your setup.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { id: "hvac", label: "HVAC", desc: "Intelligent energy management for unitary HVAC equipment" },
              { id: "ff", label: "Refrigeration", desc: "Temperature and trend monitoring for walk-in fridges and freezers" },
              { id: "both", label: "Both", desc: "Full coverage — HVAC and refrigeration monitoring" },
            ].map(opt => (
              <button key={opt.id} onClick={() => setMonitoring(opt.id)}
                className="p-6 rounded-xl border-2 text-left transition-all cursor-pointer bg-white"
                style={monitoring === opt.id ? { borderColor: G.accent, background: G.lighter } : { borderColor: "#E2E8F0" }}>
                <div className="font-bold text-slate-900 mb-1">{opt.label}</div>
                <div className="text-xs text-slate-500">{opt.desc}</div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {monitoring && (
        <section className="py-14 px-6 border-b border-slate-200 bg-slate-100">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-10"><h2 className="text-4xl font-bold text-slate-900">Select Your Hardware</h2></div>
            <div className="flex flex-col gap-6">

              {showHVAC && (
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="relative px-8 py-6" style={{ background: `linear-gradient(135deg, ${G.dark}, ${G.mid})` }}>
                    <PatternBG type="control" opacity={12} />
                    <div className="relative z-10 flex items-end justify-between">
                      <div><div className="text-white/60 text-xs uppercase tracking-widest mb-1">Cognition</div><h3 className="text-xl font-bold text-white">Energy Management Kit</h3></div>
                      <div className="text-right">
                        {path === "partner" ? (<><div className="line-through text-green-300 text-sm">${fmt(baseHVAC)} / kit</div><div className="text-white text-2xl font-bold">${fmt(Math.round(baseHVAC * 0.85))}<span className="text-sm font-normal text-white/70"> / kit</span></div></>) : showPrice && (
                          <div className="text-white text-2xl font-bold">${fmt(baseHVAC)}<span className="text-sm font-normal text-white/70"> / kit</span></div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="p-6">
                    <div className="flex gap-4 items-start mb-3">
                      <div className="flex-1">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">What's in the Box</p>
                        <div className="grid grid-cols-2 gap-x-6">
                          {["Cognition Smart Control", "1× Wireless Sensor included", "Cellular — no WiFi needed", "All mounting hardware"].map(f => (
                            <div key={f} className="flex items-center gap-2 text-sm text-slate-600 mb-2"><span style={{ color: G.accent }}>✓</span>{f}</div>
                          ))}
                        </div>
                      </div>
                      <div className="flex-shrink-0 flex flex-col items-center gap-1">
                        <button onClick={() => setImgModal("hvac")} className="w-20 h-20 rounded-lg overflow-hidden border border-slate-200 cursor-pointer bg-transparent p-0">
                          <img src="/DSC00719.JPG" alt="What's in the box" className="w-full h-full object-cover" />
                        </button>
                        <span className="text-xs text-slate-400">Click to enlarge</span>
                      </div>
                    </div>
                    <button onClick={() => setCompatModal(true)} className="mb-4 text-xs font-semibold px-4 py-2 rounded-lg text-white cursor-pointer border-0 hover:opacity-90" style={{ background: `linear-gradient(135deg, ${G.dark}, ${G.mid})` }}>Equipment Compatibility Details ↗</button>
                    <div className="flex items-center justify-between py-4 border-t border-slate-100">
                      <div><div className="text-sm font-semibold text-slate-800">Number of kits</div><div className="text-xs text-slate-400 mt-0.5">Each kit includes 1 Smart Control + 1 sensor</div></div>
                      <Stepper value={hvacQty} onChange={setHvacQty} min={1} />
                    </div>
                    <div className="pt-4 border-t border-slate-100">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-sm font-semibold text-slate-800">Add sensors {showPrice && <span className="font-normal text-slate-400">($49/ea)</span>}</div>
                        <div className="text-xs text-slate-400">{hvacSensorTotal} added</div>
                      </div>
                      <p className="text-xs text-slate-500 mb-3">Sensors can be deployed for enhanced ambient temperature sensing, or supply/return air duct temperature monitoring. <br /> Each Kit includes one sensor. Up to a total of 4 sensors can be paired with each Smart Control.</p>
                      <div className="space-y-2">
                        {[["ambient", "Ambient Air Sensor"], ["supply", "Supply Air Duct Sensor"], ["returnAir", "Return Air Duct Sensor"]].map(([key, label]) => (
                          <div key={key} className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-50">
                            <span className="text-sm text-slate-700">{label}</span>
                            <div className="flex items-center gap-3">
                              <Stepper value={hvacSensors[key]} onChange={v => setS(key, v)} />
                              {showPrice && <span className="text-sm text-slate-400 w-10 text-right">${fmt(hvacSensors[key] * 49)}</span>}
                            </div>
                          </div>
                        ))}
                      </div>
                      {sensorError && (
                        <div className="mt-3 flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
                          <span className="text-red-500 text-sm mt-0.5">⚠</span>
                          <p className="text-red-700 text-sm">Up to 4 sensors can be paired with each Smart Control. Your selections exceed the limit for {hvacQty} device{hvacQty > 1 ? "s" : ""} (max {hvacQty * 3} additional). Please reduce your sensor quantity.</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {showFF && (
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="relative px-8 py-6" style={{ background: "linear-gradient(135deg, #1e3a5f 0%, #0f4c75 100%)" }}>
                    <PatternBG type="visibility" opacity={12} />
                    <div className="relative z-10 flex items-end justify-between">
                      <div><div className="text-white/60 text-xs uppercase tracking-widest mb-1">Cognition</div><h3 className="text-xl font-bold text-white">Fridge/Freezer Monitoring Kit</h3></div>
                      <div className="text-right">
                        {path === "partner" ? (<><div className="line-through text-blue-300 text-sm">${fmt(baseFF)} / kit</div><div className="text-white text-2xl font-bold">${fmt(Math.round(baseFF * 0.85))}<span className="text-sm font-normal text-white/70"> / kit</span></div></>) : showPrice && (
                          <div className="text-white text-2xl font-bold">${fmt(baseFF)}<span className="text-sm font-normal text-white/70"> / kit</span></div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="p-6">
                    <div className="flex gap-4 items-start mb-5">
                      <div className="flex-1">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">What's in the Box</p>
                        <div className="grid grid-cols-2 gap-x-6">
                          {["Cognition Refrigeration Monitor", "Power bundle included", "1× Waterproof Sensor", "Cellular — no WiFi needed", "All mounting hardware"].map(f => (
                            <div key={f} className="flex items-center gap-2 text-sm text-slate-600 mb-2"><span style={{ color: G.accent }}>✓</span>{f}</div>
                          ))}
                        </div>
                      </div>
                      <div className="flex-shrink-0 flex flex-col items-center gap-1">
                        <button onClick={() => setImgModal("ff")} className="w-20 h-20 rounded-lg overflow-hidden border border-slate-200 cursor-pointer bg-transparent p-0">
                          <img src="/DSC00724.JPG" alt="What's in the box" className="w-full h-full object-cover" />
                        </button>
                        <span className="text-xs text-slate-400">Click to enlarge</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between py-4 border-t border-slate-100">
                      <div><div className="text-sm font-semibold text-slate-800">Number of kits</div><div className="text-xs text-slate-400 mt-0.5">Each kit monitors one fridge or freezer unit</div></div>
                      <Stepper value={ffQty} onChange={setFfQty} min={1} />
                    </div>
                    <div className="pt-4 border-t border-slate-100">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-sm font-semibold text-slate-800">Add waterproof sensors {showPrice && <span className="font-normal text-slate-400">($49/ea)</span>}</div>
                        <div className="text-xs text-slate-400">{ffSensors} added</div>
                      </div>
                      <p className="text-xs text-slate-500 mb-3">Up to 3 additional sensors per device (4 total). Must be within 15 feet of the device to pair.</p>
                      <div className="py-2 px-3 rounded-lg bg-slate-50 flex items-center justify-between">
                        <span className="text-sm text-slate-700">Additional Waterproof Sensors</span>
                        <div className="flex items-center gap-3">
                          <Stepper value={ffSensors} onChange={v => setFfSensors(Math.min(v, ffQty * 3))} max={ffQty * 3} />
                          {showPrice && <span className="text-sm text-slate-400 w-10 text-right">${fmt(ffSensors * 49)}</span>}
                        </div>
                      </div>
                      <div className="text-xs text-slate-400 mt-2">Max {ffQty * 3} additional sensors for {ffQty} device{ffQty > 1 ? "s" : ""}.</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      )}
      {compatModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.6)" }} onClick={() => setCompatModal(false)}>
          <div className="relative w-full max-w-2xl mx-4 bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[85vh] flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <h2 className="text-lg font-bold text-slate-900">Equipment Compatibility</h2>
              <button onClick={() => setCompatModal(false)} className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 font-bold text-sm cursor-pointer border-0 hover:bg-slate-200">✕</button>
            </div>
            <div className="overflow-y-auto px-6 py-5 space-y-4">
              <p className="text-sm text-slate-600 leading-relaxed">The Cognition Smart Control works with most 24V heating and cooling systems, including packaged rooftop units, split systems, heat pump units, boilers, unit heaters, and air handler units. It offers 3 stages of heat and 2 stages of cooling for heat pump and conventional wiring scenarios, as well as support for accessories such as humidifiers and dehumidifiers.</p>
              <div className="divide-y divide-slate-100 border border-slate-100 rounded-xl overflow-hidden">
                {[
                  ["Compatibility", "Works with most 24V heating and cooling systems, including packaged rooftop units, furnaces, air conditioners, boilers, and heat pumps with forced air or radiant delivery."],
                  ["Application", "Conventional Furnace, Heat Pump - Air Source, Heat Pump - Water Source, Geothermal, Electrical Radiant"],
                  ["Stages", "3 heat / 2 cool — Heat Pump; 3 heat / 2 cool — Conventional Systems"],
                  ["Terminals", "Rh, Rc, C, W1, W2, Y1, Y2, O/B, G, E, AC+, AC-"],
                  ["Accessory Support", "Wireless Temperature & Humidity Sensors; compatible with additional accessories"],
                  ["Input Voltage", "20–30Vac"],
                  ["Operating Temperature", "32°–122°F (0–50°C)"],
                  ["Operating Humidity", "0–90% Relative Humidity"],
                  ["Display", "2.7\" (68.58 mm) E-Paper Display"],
                  ["Size", "4.50\" × 4.50\" × 1.14\" (114.30 mm × 114.30 mm × 28.96 mm)"],
                  ["Weight", "6.72 oz (190.41 g)"],
                  ["IP Rating", "IP40"],
                  ["Cellular", "LTE-M multi-carrier"],
                  ["Wi-Fi", "2.4GHz (802.11 b/g/n)"],
                  ["Battery Backup", "Built-in rechargeable 780mAh lithium polymer battery (safe shutdown only)"],
                  ["Remote Sensors", "Wireless Temperature & Humidity Sensors"],
                  ["Additional Notes", "FCC certified · ICC certified · 24VAC transient fuse protection · Max 2.4W draw (100mA @ 24VAC)"],
                  ["Warranty", "Limited Lifetime Warranty"],
                ].map(([label, value]) => (
                  <div key={label} className="flex gap-4 px-4 py-3 bg-white hover:bg-slate-50">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide w-36 flex-shrink-0 pt-0.5">{label}</span>
                    <span className="text-sm text-slate-700">{value}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-400 pb-2">If you have technical questions regarding equipment compatibility please contact the Cognition Support Team at <a href="mailto:support@cognitioncontrols.com" className="text-green-600 hover:underline">support@cognitioncontrols.com</a></p>
            </div>
          </div>
        </div>
      )}
      {imgModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.6)" }} onClick={() => setImgModal(null)}>
          <div className="relative w-full max-w-2xl mx-4" onClick={e => e.stopPropagation()}>
            <button onClick={() => setImgModal(null)} className="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 flex items-center justify-center text-slate-700 font-bold text-sm cursor-pointer border-0 z-10 hover:bg-white">✕</button>
            <img src={imgModal === "hvac" ? "/DSC00719.JPG" : "/DSC00724.JPG"} alt="What's in the box" className="w-full rounded-2xl shadow-2xl" />
          </div>
        </div>
      )}
    </>
  );
}

// ── FAQ ──────────────────────────────────────────────────────────────────────
function FAQSection() {
  const [open, setOpen] = useState(null);
  return (
    <>
      <section className="py-14 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10"><h2 className="text-4xl font-bold text-slate-900 mb-3">Frequently Asked Questions</h2><p className="text-slate-500"></p></div>
          <div className="space-y-3">
            {faqs.map((f, i) => (
              <div key={i} className="border rounded-xl overflow-hidden" style={{ borderColor: open === i ? G.accent : "#E2E8F0" }}>
                <button onClick={() => setOpen(open === i ? null : i)} className="w-full text-left px-6 py-4 flex items-center justify-between hover:bg-slate-50 cursor-pointer bg-white border-0">
                  <span className="font-semibold text-slate-800 text-sm">{f.q}</span>
                  <span className="text-slate-400 ml-4 text-xs">{open === i ? "▲" : "▼"}</span>
                </button>
                {open === i && <div className="px-6 pb-4 pt-4 text-sm text-slate-600 leading-relaxed border-t border-slate-100" style={{ background: G.lighter }}>{f.a}</div>}
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="py-10 px-6 bg-slate-100 border-t border-slate-200">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-slate-900 mb-2">Have more questions?  Give us a call:</p>
          <p className="text-slate-500 text-sm">Monday – Friday, 8am – 5pm EST</p>
          <p className="text-lg font-bold text-slate-900 mt-1">1-855-604-2875</p>
        </div>
      </section>
    </>
  );
}

// ── New / Partner flow ───────────────────────────────────────────────────────
function NewPartnerFlow({ path, partnerName }) {
  const [monitoring, setMonitoring] = useState(null);
  const [hvacQty, setHvacQty] = useState(1);
  const [hvacSensors, setHvacSensors] = useState({ ambient: 0, supply: 0, returnAir: 0 });
  const [ffQty, setFfQty] = useState(1);
  const [ffSensors, setFfSensors] = useState(0);
  const [billing, setBilling] = useState("annual");
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({ name: "", email: "", company: "", address: "", city: "", state: "", zip: "" });
  const [leadGate, setLeadGate] = useState(null);
  const [leadCaptured, setLeadCaptured] = useState(false);

  const handleMonitoringSelect = (val) => {
    setMonitoring(val);
    if (path === "new" && !leadCaptured) setLeadGate(val);
  };

  const baseHVAC = 455, baseFF = 555, sp = 49, ppd = 10;
  const showHVAC = monitoring === "hvac" || monitoring === "both";
  const showFF = monitoring === "ff" || monitoring === "both";
  const hvacSensorTotal = hvacSensors.ambient + hvacSensors.supply + hvacSensors.returnAir;
  const sensorError = hvacSensorTotal > hvacQty * 3;
  const devCount = useMemo(() => Math.max((showHVAC ? hvacQty : 0) + (showFF ? ffQty : 0), 1), [showHVAC, showFF, hvacQty, ffQty]);
  const monthlyP = devCount * ppd;
  const annualP = Math.round(devCount * ppd * 0.9 * 12);
  const dispP = billing === "annual" ? annualP : monthlyP * 12;
  const hvacHW = showHVAC ? baseHVAC * hvacQty + hvacSensorTotal * sp : 0;
  const ffHW = showFF ? baseFF * ffQty + ffSensors * sp : 0;
  const sub = hvacHW + ffHW + dispP;
  const disc = path === "partner" ? sub * 0.15 : 0;
  const total = sub - disc;
  const inp = "w-full border border-slate-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-green-500";

  return (
    <>
      {/* Partner case study — comes first on partner path */}
      {path === "partner" && (
        <section className="py-12 px-6 border-b border-slate-100" style={{ background: G.lighter }}>
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <span className="text-xs font-bold px-3 py-1 rounded-full" style={{ background: G.light, color: G.dark }}>Partner Results</span>
              <h2 className="text-4xl font-bold text-slate-900 mt-3">{partnerName} results with Cognition Controls:</h2>
            </div>
            <div className="grid grid-cols-3 gap-4">
              {[{ stat: "$5K", label: "Utility Bill Cost Avoidance", sub: "per site, per year" }, { stat: "$2K", label: "Emergency Call Avoidance", sub: "per site, per year" }, { stat: "—", label: "Coming Soon", sub: "per site" }].map((c, i) => (
                <div key={i} className="bg-white rounded-2xl border p-6 text-center" style={{ borderColor: G.border }}>
                  <div className="text-4xl font-bold mb-1" style={{ color: c.stat === "—" ? "#5ebf5c" : G.mid }}>{c.stat}</div>
                  <div className="font-semibold text-slate-800 text-sm mb-1">{c.label}</div>
                  <div className="text-xs text-slate-400">{c.sub}</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <HardwareSection path={path} leadCaptured={leadCaptured} hvacQty={hvacQty} setHvacQty={setHvacQty} hvacSensors={hvacSensors} setHvacSensors={setHvacSensors} ffQty={ffQty} setFfQty={setFfQty} ffSensors={ffSensors} setFfSensors={setFfSensors} monitoring={monitoring} setMonitoring={handleMonitoringSelect} />

      {/* Platform plan */}
      {monitoring && <section className="py-14 px-6 bg-white border-b border-slate-100">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-slate-900 mb-3">Cognition Dashboard Plan</h2>
          <p className="text-slate-500 mb-6">Billed annually.</p>
          <div className="rounded-2xl border-2 p-8" style={{ borderColor: G.accent, background: G.lighter }}>
            <div className="text-4xl font-bold mb-1" style={{ color: G.mid }}>${fmt(annualP)}<span className="text-lg text-slate-400 font-normal">/yr</span></div>
            <div className="text-sm text-slate-400 mb-1">Billed annually</div>
            {path === "partner" && <div className="mt-3 text-sm font-semibold" style={{ color: G.mid }}>15% partner discount applied at checkout</div>}
          </div>
        </div>
      </section>}

      {/* Order + checkout */}
      {monitoring && (
        <section className="py-14 px-6 border-b border-slate-100" style={{ background: G.lighter }}>
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold text-slate-900 mb-8 text-center">Your Order</h2>
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-6 border-b border-slate-100">
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-4">Order Summary</div>
                {showHVAC && <div className="flex justify-between text-sm mb-2"><span className="text-slate-700">Energy Management Kit Hardware  ×  {hvacQty}{hvacSensorTotal > 0 ? ` +  ${hvacSensorTotal} additional sensor(s)` : ""}</span><span className="font-semibold">${fmt(hvacHW)}</span></div>}
                {showFF && <div className="flex justify-between text-sm mb-2"><span className="text-slate-700">Fridge/Freezer Kit Hardware  ×  {ffQty}{ffSensors > 0 ? ` +  ${ffSensors} additional sensor(s)` : ""}</span><span className="font-semibold">${fmt(ffHW)}</span></div>}
                <div className="flex justify-between text-sm mb-2"><span className="text-slate-700">Cognition Dashboard Plan (annual)</span><span className="font-semibold">${fmt(annualP)}/yr</span></div>
                {disc > 0 && <div className="flex justify-between text-sm mb-2" style={{ color: G.mid }}><span>Partner discount (15%)</span><span>−${fmt(Math.round(disc))}</span></div>}
                <div className="border-t border-slate-100 mt-4 pt-4 flex justify-between font-bold text-slate-900"><span>Total</span><span>${fmt(Math.round(total))}</span></div>
              </div>
              {step === 0 && (
                <div className="p-6">
                  <button onClick={() => { if (!sensorError) setStep(1); }} className="w-full text-white font-semibold py-4 rounded-xl border-0 cursor-pointer hover:opacity-90" style={{ background: sensorError ? "#94a3b8" : G.mid }}>
                    {sensorError ? "Fix sensor quantity above to continue" : "Create Account & Checkout →"}
                  </button>
                </div>
              )}
              {step >= 1 && (
                <div className="p-6">
                  <div className="flex items-center gap-1.5 mb-6 overflow-x-auto pb-1">
                    {["Account", "Address", "Review", "Payment", "Confirmation"].map((s, i) => (
                      <div key={s} className="flex items-center gap-1.5 flex-shrink-0">
                        <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white" style={{ background: step > i+1 ? G.accent : step === i+1 ? G.mid : "#CBD5E1" }}>{step > i+1 ? "✓" : i+1}</div>
                        <span className={`text-xs ${step === i+1 ? "font-semibold text-slate-900" : "text-slate-400"}`}>{s}</span>
                        {i < 4 && <span className="text-slate-200 text-xs mx-1">—</span>}
                      </div>
                    ))}
                  </div>
                  {step === 1 && (
                    <div className="space-y-3">
                      <div className="text-sm font-semibold text-slate-700">Create Your Account</div>
                      <input placeholder="First & Last Name" value={form.name} onChange={e => setForm({...form, name: e.target.value})} className={inp} />
                      <div className="grid grid-cols-2 gap-3">
                        <input placeholder="Work Email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} className={inp} />
                        <input placeholder="Company Name" value={form.company} onChange={e => setForm({...form, company: e.target.value})} className={inp} />
                      </div>
                      <button onClick={() => setStep(2)} className="w-full text-white font-semibold py-3 rounded-xl border-0 cursor-pointer hover:opacity-90" style={{ background: G.mid }}>Continue to Delivery →</button>
                    </div>
                  )}
                  {step === 2 && (
                    <div className="space-y-3">
                      <div className="text-sm font-semibold text-slate-700">Delivery Address</div>
                      <input placeholder="Street Address" value={form.address} onChange={e => setForm({...form, address: e.target.value})} className={inp} />
                      <div className="grid grid-cols-3 gap-3">
                        <input placeholder="City" value={form.city} onChange={e => setForm({...form, city: e.target.value})} className={inp} />
                        <input placeholder="State" value={form.state} onChange={e => setForm({...form, state: e.target.value})} className={inp} />
                        <input placeholder="ZIP" value={form.zip} onChange={e => setForm({...form, zip: e.target.value})} className={inp} />
                      </div>
                      <div className="flex gap-3">
                        <button onClick={() => setStep(1)} className="px-5 py-3 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white cursor-pointer">← Back</button>
                        <button onClick={() => setStep(3)} className="flex-1 text-white font-semibold py-3 rounded-xl border-0 cursor-pointer hover:opacity-90" style={{ background: G.mid }}>Review Order →</button>
                      </div>
                    </div>
                  )}
                  {step === 3 && (
                    <div>
                      <div className="text-sm font-semibold text-slate-700 mb-3">Review Your Order</div>
                      <div className="bg-slate-50 rounded-xl p-4 text-sm text-slate-600 space-y-1 mb-4">
                        <div><span className="font-medium">Name:</span> {form.name || "—"}</div>
                        <div><span className="font-medium">Email:</span> {form.email || "—"}</div>
                        <div><span className="font-medium">Company:</span> {form.company || "—"}</div>
                        <div><span className="font-medium">Ship to:</span> {[form.address, form.city, form.state, form.zip].filter(Boolean).join(", ") || "—"}</div>
                        <div className="pt-2 border-t border-slate-200"><span className="font-medium">Order total:</span> ${fmt(Math.round(total))}</div>
                      </div>
                      <div className="flex gap-3">
                        <button onClick={() => setStep(2)} className="px-5 py-3 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white cursor-pointer">← Back</button>
                        <button onClick={() => setStep(4)} className="flex-1 text-white font-semibold py-3 rounded-xl border-0 cursor-pointer hover:opacity-90" style={{ background: G.mid }}>Continue to Payment →</button>
                      </div>
                    </div>
                  )}
                  {step === 4 && (
                    <div className="space-y-3">
                      <div className="text-sm font-semibold text-slate-700">Payment Details</div>
                      <input placeholder="Card Number" className={inp} />
                      <div className="grid grid-cols-2 gap-3"><input placeholder="MM / YY" className={inp} /><input placeholder="CVV" className={inp} /></div>
                      <input placeholder="Name on Card" className={inp} />
                      <div className="text-xs text-slate-400">🔒 Payments are encrypted and secure.</div>
                      <div className="flex gap-3">
                        <button onClick={() => setStep(3)} className="px-5 py-3 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white cursor-pointer">← Back</button>
                        <button onClick={() => setStep(5)} className="flex-1 text-white font-semibold py-3 rounded-xl border-0 cursor-pointer hover:opacity-90" style={{ background: G.mid }}>Place Order — ${fmt(Math.round(total))}</button>
                      </div>
                    </div>
                  )}
                  {step === 5 && (
                    <div className="text-center py-4">
                      <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-4xl" style={{ background: G.lighter }}>✅</div>
                      <h3 className="text-xl font-bold text-slate-900 mb-2">Order Confirmed!</h3>
                      <p className="text-slate-500 text-sm mb-4">Thanks{form.name ? `, ${form.name.split(" ")[0]}` : ""}! Your Cognition kit is on its way.</p>
                      <div className="bg-slate-50 rounded-xl p-4 text-sm text-slate-600 text-left">
                        <div className="font-semibold mb-2">What's next:</div>
                        {[["📦","Hardware ships within 2–3 business days"],["📧","Platform access credentials sent by email"],["🎓","Cognition onboarding team will reach out within 24 hours"]].map(([ic,txt]) => (
                          <div key={txt} className="flex items-start gap-2 mb-1"><span style={{ color: G.mid }}>{ic}</span>{txt}</div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>
      )}
      <WhyCognition />
      <FAQSection />
      {leadGate && (
        <LeadGateModal
          onSuccess={() => { setLeadCaptured(true); setLeadGate(null); }}
          onDismiss={() => { setMonitoring(null); setLeadGate(null); }}
        />
      )}
    </>
  );
}

// ── Existing Customer flow ───────────────────────────────────────────────────
function ExistingFlow({ existingUser }) {
  const [monitoring, setMonitoring] = useState(null);
  const [hvacQty, setHvacQty] = useState(1);
  const [hvacSensors, setHvacSensors] = useState({ ambient: 0, supply: 0, returnAir: 0 });
  const [ffQty, setFfQty] = useState(1);
  const [ffSensors, setFfSensors] = useState(0);
  const [invStep, setInvStep] = useState(0);

  const baseHVAC = 455, baseFF = 505, sp = 49;
  const showHVAC = monitoring === "hvac" || monitoring === "both";
  const showFF = monitoring === "ff" || monitoring === "both";
  const hvacSensorTotal = hvacSensors.ambient + hvacSensors.supply + hvacSensors.returnAir;
  const sensorError = hvacSensorTotal > hvacQty * 3;
  const hvacHW = showHVAC ? baseHVAC * hvacQty + hvacSensorTotal * sp : 0;
  const ffHW = showFF ? baseFF * ffQty + ffSensors * sp : 0;
  const hwTotal = hvacHW + ffHW;

  return (
    <>
      <HardwareSection path="existing" hvacQty={hvacQty} setHvacQty={setHvacQty} hvacSensors={hvacSensors} setHvacSensors={setHvacSensors} ffQty={ffQty} setFfQty={setFfQty} ffSensors={ffSensors} setFfSensors={setFfSensors} monitoring={monitoring} setMonitoring={setMonitoring} />

      {monitoring && (
        <>

          {/* Order + invoice */}
          <section className="py-14 px-6 border-b border-slate-100" style={{ background: G.lighter }}>
            <div className="max-w-4xl mx-auto">
              <h2 className="text-4xl font-bold text-slate-900 mb-8 text-center">Your Order</h2>
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-4">Order Summary</div>
                  {showHVAC && <div className="text-sm mb-2 text-slate-700">Energy Management Kit  ×  {hvacQty}{hvacSensorTotal > 0 ? ` +  ${hvacSensorTotal} additional sensor(s)` : ""}</div>}
                  {showFF && <div className="text-sm mb-2 text-slate-700">Fridge/Freezer Kit  ×  {ffQty}{ffSensors > 0 ? ` +  ${ffSensors} additional sensor(s)` : ""}</div>}
                  <div className="text-sm italic text-slate-400">The Cognition Sales Team will review your order and provide an invoice reflecting the above hardware selections.</div>
                </div>
                {invStep === 0 && (
                  <div className="p-6">
                    <button onClick={() => { if (!sensorError) setInvStep(1); }} className="w-full text-white font-semibold py-4 rounded-xl border-0 cursor-pointer hover:opacity-90" style={{ background: sensorError ? "#94a3b8" : G.mid }}>
                      {sensorError ? "Fix sensor quantity above to continue" : "Send Invoice to Cognition Sales →"}
                    </button>
                  </div>
                )}
                {invStep === 1 && (
                  <div className="p-6">
                    <div className="bg-slate-50 rounded-xl p-4 text-sm text-slate-600 mb-4 space-y-1">
                      <div className="font-semibold text-slate-800 mb-2">Confirm your order</div>
                      <div><span className="font-medium">Account:</span> {existingUser}</div>
                      {showHVAC && <div><span className="font-medium">HVAC kits:</span> ×{hvacQty}{hvacSensorTotal > 0 ? ` + ${hvacSensorTotal} sensor(s)` : ""}</div>}
                      {showFF && <div><span className="font-medium">F/F kits:</span> ×{ffQty}{ffSensors > 0 ? ` + ${ffSensors} sensor(s)` : ""}</div>}
                      <div className="pt-2 border-t border-slate-200"><span className="font-medium">Pricing:</span> Confirmed by Sales</div>
                    </div>
                    <div className="flex gap-3">
                      <button onClick={() => setInvStep(0)} className="px-5 py-3 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white cursor-pointer">← Back</button>
                      <button onClick={() => setInvStep(2)} className="flex-1 text-white font-semibold py-3 rounded-xl border-0 cursor-pointer hover:opacity-90" style={{ background: G.mid }}>Confirm &amp; Send →</button>
                    </div>
                  </div>
                )}
                {invStep === 2 && (
                  <div className="p-8 text-center">
                    <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-4xl" style={{ background: G.lighter }}>✅</div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2">Invoice Request Sent!</h3>
                    <p className="text-slate-500 text-sm">Your order has been submitted to the Cognition Sales team. <br />They'll be in touch within one business day to confirm and process your order.</p>
                  </div>
                )}
              </div>
            </div>
          </section>
        </>
      )}
      <FAQSection />
    </>
  );
}

// ── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [modal, setModal] = useState(null);
  const [appPath, setAppPath] = useState(null);
  const [existingUser, setExistingUser] = useState(null);
  const [partnerName, setPartnerName] = useState("Brewery Partner");

  const reset = () => { setAppPath(null); setExistingUser(null); setModal(null); };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-1000">
      {modal === "entry" && <EntryModal onSelect={choice => {
        if (choice === "new") { setAppPath("new"); setModal(null); }
        else if (choice === "existing") setModal("auth");
        else if (choice === "partner") setModal("partner");
      }} />}
      {modal === "auth" && <AuthModal onSuccess={u => { setExistingUser(u); setAppPath("existing"); setModal(null); }} onBack={() => setModal("entry")} />}
      {modal === "partner" && <PartnerModal onSuccess={n => { setPartnerName(n); setAppPath("partner"); setModal(null); }} onBack={() => setModal("entry")} />}

      {/* NAV */}
      <nav className="bg-white sticky top-0 z-40" style={{ borderBottom: `1px solid ${G.border}` }}>
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer" onClick={reset}>
            <img src="/Color.png" alt="Cognition Controls" className="h-8 w-auto" />
            {appPath === "partner" && <span className="text-slate-400 ml-1">× {partnerName}</span>}
            {appPath === "existing" && <span className="text-slate-400 ml-1 text-sm">· {existingUser}</span>}
          </div>
          <div className="flex items-center gap-4">
            <a href="#" className="text-slate-600 text-sm hover:text-green-700">Products</a>
            <a href="#" className="text-slate-600 text-sm hover:text-green-700">Platform</a>
            <button onClick={() => setModal("entry")} className="text-white text-sm font-semibold px-5 py-2 rounded-lg border-0 cursor-pointer hover:opacity-90" style={{ background: G.mid }}>Purchase</button>
          </div>
        </div>
      </nav>

      {/* LANDING */}
      {!appPath && (
        <>
          <section className="py-24 px-6 text-center" style={{ background: `linear-gradient(135deg, ${G.dark} 0%, ${G.mid} 100%)` }}>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 max-w-4xl mx-auto leading-tight">Smart Controls for<br />HVAC & Refrigeration</h1>
            <p className="text-green-100 text-lg max-w-2xl mx-auto mb-10">Maximize control of your facility. <br />24/7 monitoring. Remote visibility and control. Consistent cost avoidance.</p>
            <button onClick={() => setModal("entry")} className="text-white font-semibold px-8 py-4 rounded-xl text-lg border-2 cursor-pointer hover:bg-white/10 bg-transparent" style={{ borderColor: G.accent }}>Get Started →</button>
          </section>
          <WhyCognition />
          <FAQSection />
        </>
      )}

      {/* NEW CUSTOMER HERO */}
      {appPath === "new" && (
        <section className="py-20 px-6 text-center" style={{ background: `linear-gradient(135deg, ${G.dark} 0%, ${G.mid} 100%)` }}>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 max-w-4xl mx-auto leading-tight">Smart Controls for<br />HVAC & Refrigeration</h1>
          <p className="text-green-100 text-lg max-w-2xl mx-auto">Maximize control of your facility. <br />24/7 monitoring. Remote visibility and control. Consistent cost avoidance.</p>
        </section>
      )}

      {/* PARTNER HERO */}
      {appPath === "partner" && (
        <section className="py-20 px-6 text-center" style={{ background: `linear-gradient(135deg, ${G.dark} 0%, ${G.mid} 100%)` }}>
          <div className="inline-flex items-center gap-2 bg-white/10 text-white text-sm px-4 py-2 rounded-full mb-6 border border-white/20">🤝 Exclusive offer for {partnerName} members</div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 max-w-4xl mx-auto leading-tight">Cognition × {partnerName}</h1>
          <p className="text-green-100 text-lg max-w-2xl mx-auto mb-4">{partnerName} members get exclusive preferred pricing. <br />Monitor, control, and protect your HVAC equipment from anywhere.</p>
          <div className="inline-flex items-center gap-3 bg-white/10 border border-white/20 rounded-xl px-6 py-3">
            <span className="text-green-200 text-sm">Partner discount:</span>
            <span className="text-xs font-bold px-2 py-1 rounded-full" style={{ background: G.light, color: G.dark }}>15% off — Active</span>
          </div>
        </section>
      )}

      {/* EXISTING HERO */}
      {appPath === "existing" && (
        <section className="py-14 px-6 text-center" style={{ background: `linear-gradient(135deg, ${G.dark} 0%, ${G.mid} 100%)` }}>
          <div className="inline-flex items-center gap-2 bg-white/10 text-white text-sm px-4 py-2 rounded-full mb-4 border border-white/20">👤 Signed in as {existingUser}</div>
          <h1 className="text-4xl md:text-4xl font-bold text-white mb-3">Order additional Cognition <br />hardware in a few simple steps.</h1>
          <p className="text-green-100 max-w-xl mx-auto text-sm">The Cognition Sales team will email an invoice with your preferred pricing in 24 hours.</p>
        </section>
      )}

      {/* FLOWS */}
      {(appPath === "new" || appPath === "partner") && <NewPartnerFlow path={appPath} partnerName={partnerName} />}
      {appPath === "existing" && <ExistingFlow existingUser={existingUser} />}

      {/* SALES BUBBLE */}
      <a href="tel:18556042875" className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-2.5 rounded-full shadow-lg text-white text-xs font-medium no-underline hover:opacity-90 transition-opacity" style={{ background: G.dark }}>
        <span style={{ fontSize: "14px" }}>📞</span>
        <span>Speak to sales: 1-855-604-2875</span>
      </a>

      {/* FOOTER */}
      <footer className="py-10 px-6 text-center text-sm" style={{ background: G.dark, color: "#86efac" }}>
        <div className="flex items-center justify-center gap-2 mb-3">
          <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: G.mid }}><span className="text-white font-bold text-xs">C</span></div>
          <span className="text-white font-semibold">Cognition Controls</span>
        </div>
        <p>© 2024 Cognition Controls. All rights reserved.</p>
        <div className="flex justify-center gap-6 mt-3">
          {["Privacy Policy", "Terms of Service", "Contact Us"].map(l => <a key={l} href="#" className="hover:text-white">{l}</a>)}
        </div>
      </footer>
    </div>
  );
}