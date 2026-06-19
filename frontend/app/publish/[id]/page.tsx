"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Nav from "../../../components/Nav";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PLATFORMS = [
  { id: "linkedin",  label: "LinkedIn",  code: "in", color: "#0A66C2" },
  { id: "instagram", label: "Instagram", code: "ig", color: "#C13584" },
  { id: "facebook",  label: "Facebook",  code: "fb", color: "#1877F2" },
  { id: "tiktok",    label: "TikTok",    code: "tt", color: "#111111" },
];

export default function PublishPost() {
  const { id } = useParams();
  const [post, setPost]         = useState<any>(null);
  const [platform, setPlatform] = useState("linkedin");
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState<any>(null);
  const [error, setError]       = useState("");

  useEffect(() => {
    fetch(`${BASE_URL}/api/posts/${id}`).then(r => r.json()).then(d => { setPost(d); if (d.platform) setPlatform(d.platform); });
  }, [id]);

  async function handlePublish() {
    setLoading(true); setError("");
    try {
      const res = await fetch(`${BASE_URL}/api/publish/`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ post_id: id, platform }),
      });
      const data = await res.json();
      if (res.ok) setResult(data); else setError(data.detail || "Publishing failed");
    } catch { setError("Could not connect to backend."); }
    finally { setLoading(false); }
  }

  if (result) return (
    <div style={{ minHeight: "100vh", background: "var(--bg-soft)" }}>
      <Nav />
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "100px 24px" }}>
        <div style={{ textAlign: "center", background: "#fff", border: "1px solid var(--border)", borderRadius: 20, padding: "48px 56px", maxWidth: 420 }}>
          <div style={{
            width: 64, height: 64, borderRadius: "50%", background: "#E3F5E8",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 22px", fontSize: 28,
          }}>✓</div>
          <h2 style={{ fontSize: 22, fontWeight: 800, color: "var(--ink)", marginBottom: 8 }}>Post Published!</h2>
          <p style={{ color: "var(--body)", fontSize: 14, marginBottom: 28 }}>Your content is now live on <strong style={{ textTransform: "capitalize" }}>{platform}</strong>.</p>
          <Link href="/" className="btn-primary" style={{ padding: "12px 28px", borderRadius: 10, textDecoration: "none", display: "inline-block", fontSize: 14 }}>← Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-soft)" }}>
      <Nav />

      <div style={{ maxWidth: 680, margin: "0 auto", padding: "48px 24px 80px" }}>
        <p style={{ color: "var(--teal)", fontWeight: 700, fontSize: 12.5, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 8 }}>Final Step</p>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: "var(--ink)", marginBottom: 10 }}>Publish Post</h1>
        <p style={{ color: "var(--body)", fontSize: 14, marginBottom: 32 }}>Confirm the platform and send your approved post live.</p>

        <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 16, padding: 26 }}>

          {post?.image_url && (
            <div style={{ display: "flex", gap: 0, borderRadius: 11, overflow: "hidden", border: "1px solid var(--border)", marginBottom: 26 }}>
              <img src={post.image_url} alt="" style={{ width: 110, height: 110, objectFit: "cover" }} />
              <div style={{ padding: "14px 18px", flex: 1, background: "var(--bg-soft)" }}>
                <p style={{ fontSize: 11, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", marginBottom: 6 }}>Content Preview</p>
                <p style={{ fontSize: 12.5, lineHeight: 1.6, color: "var(--body)", display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{post?.content}</p>
              </div>
            </div>
          )}

          <label style={{ fontSize: 11.5, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, display: "block", marginBottom: 12 }}>Publish to Platform</label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10, marginBottom: 26 }}>
            {PLATFORMS.map(p => (
              <button key={p.id} onClick={() => setPlatform(p.id)} style={{
                background: platform === p.id ? "var(--teal-light)" : "var(--bg-soft)",
                border: `1.5px solid ${platform === p.id ? "var(--teal)" : "var(--border)"}`,
                borderRadius: 11, padding: "12px 8px", cursor: "pointer",
                display: "flex", flexDirection: "column", alignItems: "center", gap: 6,
              }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: platform === p.id ? p.color : "#D8DEE2", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10.5, fontWeight: 700, color: "#fff" }}>{p.code}</div>
                <span style={{ fontSize: 11.5, fontWeight: 600, color: platform === p.id ? "var(--ink)" : "var(--muted)" }}>{p.label}</span>
              </button>
            ))}
          </div>

          {error && <div style={{ background: "#FBE6E1", border: "1px solid #E0533D", borderRadius: 10, padding: "12px 16px", marginBottom: 18, color: "#C0452F", fontSize: 13 }}>{error}</div>}

          <button onClick={handlePublish} disabled={loading} className="btn-primary" style={{ width: "100%", borderRadius: 11, padding: 16, fontSize: 15 }}>
            {loading ? "Publishing…" : `Publish to ${platform.charAt(0).toUpperCase() + platform.slice(1)} →`}
          </button>
        </div>
      </div>
    </div>
  );
}