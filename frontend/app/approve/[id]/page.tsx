"use client";
import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Nav from "../../../components/Nav";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function parseContent(raw: string) {
  try {
    const parsed = JSON.parse(raw);
    return parsed;
  } catch {
    return { caption: raw, hashtags: [], poster: {} };
  }
}

const trendingTips: Record<string, string> = {
  linkedin:  "💡 LinkedIn: Post Tuesday–Thursday 8–10am. 3-5 hashtags work best. Tag relevant people to boost reach 3x.",
  instagram: "💡 Instagram: 20-30 hashtags recommended. Post Tue/Wed/Fri 11am or 2pm. Use Stories to drive profile visits.",
  facebook:  "💡 Facebook: 2-3 hashtags max. Ask a question to drive comments. Videos get 3x more reach than images.",
  tiktok:    "💡 TikTok: Always include #fyp #foryoupage. First 1-2 seconds must hook viewers. Post 7-9pm for max views.",
};

export default function FinalApprove() {
  const { id }  = useParams();
  const router  = useRouter();
  const [post, setPost]         = useState<any>(null);
  const [parsed, setParsed]     = useState<any>(null);
  const [caption, setCaption]   = useState("");
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading]   = useState(false);
  const [action, setAction]     = useState("");
  const [copied, setCopied]     = useState(false);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    fetch(`${BASE_URL}/api/posts/${id}`)
      .then(r => r.json())
      .then(d => {
        setPost(d);
        const p = parseContent(d.content || "{}");
        setParsed(p);
        setCaption(p.caption || d.content || "");
      });
  }, [id]);

  async function handleDecision(approved: boolean) {
    setLoading(true);
    setAction(approved ? "approve" : "reject");
    const res = await fetch(`${BASE_URL}/api/posts/${id}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approved, content_feedback: feedback }),
    });
    const data = await res.json();
    if (approved) {
      router.push(`/publish/${id}`);
    } else {
      const p = parseContent(data.content || "{}");
      setParsed(p);
      setCaption(p.caption || data.content || "");
      setFeedback("");
      setLoading(false);
      setAction("");
    }
  }

  function handleCopy() {
    navigator.clipboard.writeText(caption);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-soft)" }}>
      <Nav />
      <div style={{ maxWidth: 1140, margin: "0 auto", padding: "40px 24px 80px" }}>

        <p style={{ color: "#0A6E8C", fontWeight: 700, fontSize: 12.5, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 8 }}>
          Step 3 of 3 — Final Approval
        </p>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: "var(--ink)", marginBottom: 32 }}>
          Review Complete Post
        </h1>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.35fr", gap: 28 }}>

          {/* ── Left: Image ── */}
          <div>
            <p style={{ fontSize: 11.5, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 12 }}>
              Approved Image
            </p>
            <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 16, overflow: "hidden", aspectRatio: "1" }}>
              {post?.image_url
                ? <img src={post.image_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                : <div className="skeleton" style={{ width: "100%", height: "100%" }} />
              }
            </div>

            {/* Trending tip */}
            {post?.platform && trendingTips[post.platform] && (
              <div style={{
                background: "#FBF1DC", border: "1px solid #F0D98C",
                borderRadius: 10, padding: "12px 16px", marginTop: 14,
              }}>
                <p style={{ fontSize: 12, color: "#7A5200", lineHeight: 1.6 }}>
                  {trendingTips[post.platform]}
                </p>
              </div>
            )}
          </div>

          {/* ── Right: Caption + Controls ── */}
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>

            {/* Platform badge */}
            {post?.platform && (
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 11.5, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, fontWeight: 700 }}>
                  Platform —
                </span>
                <span style={{
                  background: "var(--teal-light)", color: "var(--teal-dark)",
                  fontSize: 12.5, fontWeight: 700, textTransform: "capitalize",
                  padding: "3px 12px", borderRadius: 20,
                }}>{post.platform}</span>
              </div>
            )}

            {/* Caption block */}
            <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 14, overflow: "hidden" }}>

              {/* Header */}
              <div style={{
                display: "flex", justifyContent: "space-between", alignItems: "center",
                padding: "12px 16px", borderBottom: "1px solid var(--border)",
                background: "var(--bg-soft)",
              }}>
                <p style={{ fontSize: 11.5, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5 }}>
                  {editMode ? "Edit Caption" : "Generated Caption"}
                </p>
                <div style={{ display: "flex", gap: 8 }}>
                  <button onClick={() => setEditMode(!editMode)} style={{
                    background: "transparent", border: "1px solid var(--border)",
                    color: "var(--muted)", borderRadius: 7, padding: "4px 12px",
                    fontSize: 11.5, fontWeight: 600, cursor: "pointer",
                  }}>
                    {editMode ? "👁 Preview" : "✏️ Edit"}
                  </button>
                  <button onClick={handleCopy} style={{
                    background: copied ? "#1F8A40" : "var(--teal)",
                    color: "#fff", border: "none",
                    borderRadius: 7, padding: "4px 14px",
                    fontSize: 11.5, fontWeight: 700, cursor: "pointer",
                    transition: "background 0.2s",
                  }}>
                    {copied ? "✓ Copied!" : "📋 Copy"}
                  </button>
                </div>
              </div>

              {/* Caption content */}
              {editMode ? (
                <textarea
                  value={caption}
                  onChange={e => setCaption(e.target.value)}
                  style={{
                    width: "100%", minHeight: 320,
                    background: "#fff", border: "none", outline: "none",
                    padding: "16px", color: "var(--ink)", fontSize: 13.5,
                    lineHeight: 1.8, resize: "vertical",
                    fontFamily: "Inter, sans-serif",
                  }}
                />
              ) : (
                <div style={{ padding: "16px", maxHeight: 340, overflowY: "auto" }}>
                  {caption ? (
                    <pre style={{
                      whiteSpace: "pre-wrap", fontFamily: "Inter, sans-serif",
                      fontSize: 13.5, lineHeight: 1.8, color: "var(--ink)", margin: 0,
                    }}>
                      {caption}
                    </pre>
                  ) : (
                    <div className="skeleton" style={{ height: 200 }} />
                  )}
                </div>
              )}
            </div>

            {/* Hashtags pills */}
            {parsed?.hashtags?.length > 0 && (
              <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 12, padding: "14px 16px" }}>
                <p style={{ fontSize: 11, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 10 }}>
                  Hashtags — click to check trending
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
                  {parsed.hashtags.map((tag: string, i: number) => (
                    <span
                      key={i}
                      onClick={() => window.open(`https://www.google.com/search?q=${encodeURIComponent(tag + " trending 2026")}`, "_blank")}
                      style={{
                        background: "var(--teal-light)", color: "var(--teal-dark)",
                        fontSize: 12, fontWeight: 600, padding: "5px 12px",
                        borderRadius: 20, cursor: "pointer",
                        border: "1px solid transparent",
                        transition: "all 0.15s",
                      }}
                      onMouseOver={e => (e.currentTarget.style.borderColor = "var(--teal)")}
                      onMouseOut={e => (e.currentTarget.style.borderColor = "transparent")}
                      title="Click to check if trending"
                    >{tag}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Revision notes */}
            <div>
              <label style={{
                fontSize: 11.5, fontWeight: 700, color: "var(--muted)",
                textTransform: "uppercase", letterSpacing: 0.5,
                display: "block", marginBottom: 10,
              }}>
                Revision Notes (if rejecting)
              </label>
              <textarea
                value={feedback}
                onChange={e => setFeedback(e.target.value)}
                placeholder="What should be changed in the content?"
                rows={3}
                style={{
                  width: "100%", background: "var(--bg-soft)",
                  border: "1.5px solid var(--border)", borderRadius: 11,
                  padding: 14, color: "var(--ink)", fontSize: 13.5,
                  lineHeight: 1.6, resize: "vertical", outline: "none",
                  fontFamily: "Inter, sans-serif",
                }}
                onFocus={e => e.target.style.borderColor = "var(--teal)"}
                onBlur={e => e.target.style.borderColor = "var(--border)"}
              />
            </div>

            {/* Action buttons */}
            <div style={{ display: "flex", gap: 10 }}>
              <button
                onClick={() => handleDecision(false)}
                disabled={loading}
                style={{
                  flex: 1, background: "#fff", border: "1.5px solid #E0533D",
                  color: "#C0452F", borderRadius: 11, padding: 14,
                  fontSize: 13.5, fontWeight: 700, cursor: "pointer",
                  opacity: loading && action !== "reject" ? 0.5 : 1,
                }}
              >
                {loading && action === "reject" ? "Revising…" : "✕ Reject"}
              </button>
              <button
                onClick={() => handleDecision(true)}
                disabled={loading}
                className="btn-primary"
                style={{
                  flex: 1.5, borderRadius: 11, padding: 14, fontSize: 13.5,
                  opacity: loading && action !== "approve" ? 0.5 : 1,
                }}
              >
                {loading && action === "approve" ? "Approving…" : "✓ Approve & Proceed →"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}