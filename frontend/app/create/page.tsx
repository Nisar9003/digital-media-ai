"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "../../components/Nav";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PLATFORMS = [
  { id: "linkedin",  label: "LinkedIn",  code: "in", color: "#0A66C2" },
  { id: "instagram", label: "Instagram", code: "ig", color: "#C13584" },
  { id: "facebook",  label: "Facebook",  code: "fb", color: "#1877F2" },
  { id: "tiktok",    label: "TikTok",    code: "tt", color: "#111111" },
];

const GOAL_EXAMPLES = [
  "Announce our new client project launch",
  "Share a behind-the-scenes look at our dev team",
  "Promote our app development cost calculator",
  "Celebrate 110 successful projects delivered",
];

export default function CreatePost() {
  const router = useRouter();
  const [goal, setGoal]         = useState("");
  const [platform, setPlatform] = useState("linkedin");
  const [loading, setLoading]   = useState(false);
  const [stage, setStage]       = useState("");
  const [error, setError]       = useState("");

  const stages = [
    "Supervisor analyzing goal…",
    "Planner crafting brief…",
    "Writing content…",
    "Generating image…",
    "Quality checking…",
  ];

  async function handleCreate() {
    if (!goal.trim()) return;
    setLoading(true);
    setError("");

    let idx = 0;
    setStage(stages[0]);
    const interval = setInterval(() => {
      idx = Math.min(idx + 1, stages.length - 1);
      setStage(stages[idx]);
    }, 2200);

    try {
      const res = await fetch(`${BASE_URL}/api/posts/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal, platform, campaign_id: "default" }),
      });
      const data = await res.json();
      clearInterval(interval);
      if (data.post_id) router.push(`/review/${data.post_id}`);
      else { setError(data.detail || "Something went wrong"); setLoading(false); }
    } catch {
      clearInterval(interval);
      setError("Could not connect to backend.");
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-soft)" }}>
      <Nav />

      <div style={{ maxWidth: 680, margin: "0 auto", padding: "48px 24px 80px" }}>

        <p style={{ color: "var(--teal)", fontWeight: 700, fontSize: 12.5, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 8 }}>New Campaign Post</p>
        <h1 style={{ fontSize: 26, fontWeight: 800, color: "var(--ink)", marginBottom: 10 }}>Create AI Post</h1>
        <p style={{ color: "var(--body)", fontSize: 14, lineHeight: 1.6, marginBottom: 36 }}>
          Describe your goal — the agent swarm handles strategy, writing, and image generation automatically.
        </p>

        <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 16, padding: 28 }}>

          <label style={{ fontSize: 11.5, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, display: "block", marginBottom: 12 }}>Target Platform</label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10, marginBottom: 26 }}>
            {PLATFORMS.map(p => (
              <button key={p.id} onClick={() => setPlatform(p.id)} style={{
                background: platform === p.id ? "var(--teal-light)" : "var(--bg-soft)",
                border: `1.5px solid ${platform === p.id ? "var(--teal)" : "var(--border)"}`,
                borderRadius: 11, padding: "14px 8px", cursor: "pointer",
                display: "flex", flexDirection: "column", alignItems: "center", gap: 7,
              }}>
                <div style={{ width: 34, height: 34, borderRadius: 8, background: platform === p.id ? p.color : "#D8DEE2", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: "#fff" }}>{p.code}</div>
                <span style={{ fontSize: 12, fontWeight: 600, color: platform === p.id ? "var(--ink)" : "var(--muted)" }}>{p.label}</span>
              </button>
            ))}
          </div>

          <label style={{ fontSize: 11.5, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, display: "block", marginBottom: 12 }}>Post Goal</label>
          <textarea
            value={goal}
            onChange={e => setGoal(e.target.value)}
            placeholder="e.g. Announce our new client project launch and highlight key results…"
            rows={5}
            style={{
              width: "100%", background: "var(--bg-soft)", border: "1.5px solid var(--border)",
              borderRadius: 11, padding: 16, color: "var(--ink)", fontSize: 14, lineHeight: 1.6,
              resize: "vertical", outline: "none", fontFamily: "Inter, sans-serif", marginBottom: 14,
            }}
            onFocus={e => e.target.style.borderColor = "var(--teal)"}
            onBlur={e => e.target.style.borderColor = "var(--border)"}
          />

          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 28 }}>
            {GOAL_EXAMPLES.map(ex => (
              <button key={ex} onClick={() => setGoal(ex)} style={{
                background: "#fff", border: "1px solid var(--border)", color: "var(--muted)",
                padding: "5px 14px", borderRadius: 20, fontSize: 11.5, cursor: "pointer",
              }}>{ex}</button>
            ))}
          </div>

          {error && (
            <div style={{ background: "#FBE6E1", border: "1px solid #E0533D", borderRadius: 10, padding: "12px 16px", marginBottom: 18, color: "#C0452F", fontSize: 13 }}>{error}</div>
          )}

          {loading && (
            <div style={{ background: "var(--teal-light)", border: "1px solid #B8E0E0", borderRadius: 12, padding: "18px 20px", marginBottom: 18 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
                <div style={{ width: 16, height: 16, border: "2px solid var(--teal)", borderTopColor: "transparent", borderRadius: "50%" }} className="spin" />
                <span style={{ fontSize: 13, color: "var(--teal-dark)", fontWeight: 600 }}>{stage}</span>
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                {stages.map((s, i) => (
                  <div key={i} style={{ flex: 1, height: 3, borderRadius: 2, background: stages.indexOf(stage) >= i ? "var(--teal)" : "#D8E8E8" }} />
                ))}
              </div>
            </div>
          )}

          <button onClick={handleCreate} disabled={loading || !goal.trim()} className="btn-primary" style={{
            width: "100%", borderRadius: 11, padding: 16, fontSize: 15,
          }}>
            {loading ? "Agents working…" : "Generate Post with AI →"}
          </button>
        </div>
      </div>
    </div>
  );
}