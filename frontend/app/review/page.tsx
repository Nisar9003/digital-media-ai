import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export default function ImageReview() {
  const { id } = useParams();
  const router = useRouter();
  const [post, setPost] = useState<any>(null);
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);
  const [action, setAction] = useState<"approve"|"reject"|null>(null);
  const [iteration, setIteration] = useState(1);
  useEffect(() => {
    fetch(`${BASE_URL}/api/posts/${id}`).then(r => r.json()).then(setPost);
  }, [id]);
  async function handleDecision(approved: boolean) {
    setLoading(true); setAction(approved ? "approve" : "reject");
    const res = await fetch(`${BASE_URL}/api/posts/${id}/image-feedback`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback, approved }),
    });"use client";
import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Nav from "../../../components/Nav";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ImageReview() {
  const { id } = useParams();
  const router = useRouter();
  const [post, setPost]         = useState<any>(null);
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading]   = useState(false);
  const [action, setAction]     = useState<"approve"|"reject"|null>(null);
  const [iteration, setIteration] = useState(1);

  useEffect(() => {
    fetch(`${BASE_URL}/api/posts/${id}`).then(r => r.json()).then(setPost);
  }, [id]);

  async function handleDecision(approved: boolean) {
    setLoading(true);
    setAction(approved ? "approve" : "reject");
    const res = await fetch(`${BASE_URL}/api/posts/${id}/image-feedback`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback, approved }),
    });
    const data = await res.json();
    if (approved) {
      router.push(`/approve/${id}`);
    } else {
      setIteration(data.iteration || iteration + 1);
      setPost((p: any) => ({ ...p, image_url: data.image_url }));
      setFeedback(""); setLoading(false); setAction(null);
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-soft)" }}>
      <Nav />

      <div style={{ maxWidth: 1020, margin: "0 auto", padding: "40px 24px 80px" }}>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <p style={{ color: "#B8780C", fontWeight: 700, fontSize: 12.5, letterSpacing: 0.6, textTransform: "uppercase" }}>Step 2 of 3 — Image Review</p>
          <span style={{ background: "#FBF1DC", color: "#B8780C", fontSize: 11, fontWeight: 700, padding: "4px 12px", borderRadius: 20 }}>Iteration {iteration}</span>
        </div>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: "var(--ink)", marginBottom: 32 }}>Review Generated Image</h1>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28 }}>

          <div>
            <div style={{
              background: "#fff", border: "1px solid var(--border)", borderRadius: 16,
              overflow: "hidden", aspectRatio: "1", display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              {post?.image_url
                ? <img src={post.image_url} alt="Generated" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                : <div className="skeleton" style={{ width: "85%", height: "85%" }} />
              }
            </div>
            {post?.image_url && (
              <a href={post.image_url} target="_blank" style={{ display: "block", textAlign: "center", marginTop: 12, fontSize: 12, color: "var(--teal)", fontWeight: 600, textDecoration: "none" }}>Open full resolution ↗</a>
            )}
          </div>

          <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 16, padding: 26, display: "flex", flexDirection: "column", gap: 18 }}>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 11.5, color: "var(--muted)", fontWeight: 600 }}>Post ID: {String(id).slice(0,12)}…</span>
              {post?.platform && (
                <span style={{ background: "var(--bg-soft)", padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 700, textTransform: "capitalize", color: "var(--ink)" }}>{post.platform}</span>
              )}
            </div>

            <p style={{ color: "var(--body)", fontSize: 13.5, lineHeight: 1.7 }}>
              Approve to move forward to final review, or describe what to change for a fresh regeneration.
            </p>

            <div>
              <label style={{ fontSize: 11.5, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, display: "block", marginBottom: 10 }}>Feedback for Regeneration</label>
              <textarea
                value={feedback}
                onChange={e => setFeedback(e.target.value)}
                placeholder="e.g. Make background darker, add a corporate tech feel…"
                rows={4}
                style={{
                  width: "100%", background: "var(--bg-soft)", border: "1.5px solid var(--border)",
                  borderRadius: 11, padding: 14, color: "var(--ink)", fontSize: 13.5,
                  lineHeight: 1.6, resize: "vertical", outline: "none", fontFamily: "Inter, sans-serif",
                }}
                onFocus={e => e.target.style.borderColor = "var(--teal)"}
                onBlur={e => e.target.style.borderColor = "var(--border)"}
              />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: "auto" }}>
              <button onClick={() => handleDecision(true)} disabled={loading} style={{
                background: "#1F8A40", color: "#fff", border: "none", borderRadius: 11,
                padding: 14, fontSize: 14, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
                opacity: loading && action !== "approve" ? 0.5 : 1,
              }}>{loading && action === "approve" ? "Moving forward…" : "✓ Approve Image"}</button>

              <button onClick={() => handleDecision(false)} disabled={loading} style={{
                background: "#fff", border: "1.5px solid #B8780C", color: "#B8780C", borderRadius: 11,
                padding: 14, fontSize: 14, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
                opacity: loading && action !== "reject" ? 0.5 : 1,
              }}>{loading && action === "reject" ? "Regenerating…" : "↺ Regenerate with Feedback"}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
    const data = await res.json();
    if (approved) { router.push(`/approve/${id}`); }
    else { setIteration(data.iteration || iteration + 1); setPost((p: any) => ({ ...p, image_url: data.image_url })); setFeedback(""); setLoading(false); setAction(null); }
  }
  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <nav style={{ background: "var(--surface)", borderBottom: "1px solid var(--border)", padding: "0 32px", height: 60, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Link href="/" style={{ color: "var(--muted)", textDecoration: "none", fontSize: 13 }}>← Dashboard</Link>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#F59E0B" }} />
          <span style={{ fontSize: 13, color: "#F59E0B", fontWeight: 500 }}>Image Review</span>
        </div>
        <div style={{ fontFamily: "monospace", fontSize: 11, color: "var(--muted)" }}>iter {iteration}</div>
      </nav>
      <div style={{ maxWidth: 960, margin: "0 auto", padding: "40px 24px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
          <div>
            <p style={{ fontSize: 11, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 12 }}>Generated Image</p>
            <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 12, overflow: "hidden", aspectRatio: "1", display: "flex", alignItems: "center", justifyContent: "center" }}>
              {post?.image_url ? <img src={post.image_url} alt="Generated" style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : <div style={{ color: "var(--muted)", fontSize: 13 }}>Loading image...</div>}
            </div>
            {post?.image_url && <a href={post.image_url} target="_blank" style={{ display: "block", textAlign: "center", marginTop: 10, fontSize: 11, color: "var(--muted)", textDecoration: "none" }}>Open full image ↗</a>}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div>
              <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 6 }}>Review Image</h2>
              <p style={{ color: "var(--muted)", fontSize: 13, lineHeight: 1.6 }}>Approve to move to final review, or give feedback to regenerate.</p>
            </div>
            <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: "10px 14px", fontFamily: "monospace", fontSize: 11, color: "var(--muted)" }}>
              POST ID: {String(id)}
            </div>
            {post?.platform && (
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 11, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1 }}>Platform:</span>
                <span style={{ background: "var(--border)", padding: "3px 10px", borderRadius: 20, fontSize: 12, fontWeight: 600, textTransform: "capitalize" }}>{post.platform}</span>
              </div>
            )}
            <div>
              <label style={{ fontSize: 11, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1, display: "block", marginBottom: 10 }}>Feedback for regeneration</label>
              <textarea value={feedback} onChange={e => setFeedback(e.target.value)} placeholder="e.g. Make background darker, add tech vibe..." rows={4} style={{ width: "100%", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 10, padding: 14, color: "var(--text)", fontSize: 13, lineHeight: 1.6, resize: "vertical", outline: "none", fontFamily: "Inter, sans-serif" }} />
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <button onClick={() => handleDecision(true)} disabled={loading} style={{ background: "#10B981", color: "#fff", border: "none", borderRadius: 10, padding: 14, fontSize: 14, fontWeight: 600, cursor: loading ? "not-allowed" : "pointer", opacity: loading && action !== "approve" ? 0.5 : 1 }}>
                {loading && action === "approve" ? "Moving to review..." : "✓ Approve Image"}
              </button>
              <button onClick={() => handleDecision(false)} disabled={loading} style={{ background: "transparent", border: "1px solid #F59E0B", color: "#F59E0B", borderRadius: 10, padding: 14, fontSize: 14, fontWeight: 600, cursor: loading ? "not-allowed" : "pointer", opacity: loading && action !== "reject" ? 0.5 : 1 }}>
                {loading && action === "reject" ? "Regenerating..." : "↺ Regenerate with Feedback"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
