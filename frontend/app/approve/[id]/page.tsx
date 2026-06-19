"use client";
import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Nav from "../../../components/Nav";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function FinalApprove() {
  const { id } = useParams();
  const router = useRouter();
  const [post, setPost]         = useState<any>(null);
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading]   = useState(false);
  const [action, setAction]     = useState("");

  useEffect(() => {
    fetch(`${BASE_URL}/api/posts/${id}`).then(r => r.json()).then(setPost);
  }, [id]);

  async function handleDecision(approved: boolean) {
    setLoading(true);
    setAction(approved ? "approve" : "reject");
    const res = await fetch(`${BASE_URL}/api/posts/${id}/approve`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approved, content_feedback: feedback }),
    });
    const data = await res.json();
    if (approved) {
      router.push(`/publish/${id}`);
    } else {
      setPost((p: any) => ({ ...p, content: data.content }));
      setFeedback(""); setLoading(false); setAction("");
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-soft)" }}>
      <Nav />

      <div style={{ maxWidth: 1080, margin: "0 auto", padding: "40px 24px 80px" }}>

        <p style={{ color: "#0A6E8C", fontWeight: 700, fontSize: 12.5, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 8 }}>Step 3 of 3 — Final Approval</p>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: "var(--ink)", marginBottom: 32 }}>Review Complete Post</h1>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: 28 }}>

          <div>
            <p style={{ fontSize: 11.5, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 12 }}>Approved Image</p>
            <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 16, overflow: "hidden", aspectRatio: "1" }}>
              {post?.image_url
                ? <img src={post.image_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                : <div className="skeleton" style={{ width: "100%", height: "100%" }} />
              }
            </div>
          </div>

          <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 16, padding: 26, display: "flex", flexDirection: "column", gap: 18 }}>

            {post?.platform && (
              <div>
                <span style={{ fontSize: 11.5, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, fontWeight: 700 }}>Platform — </span>
                <span style={{ fontSize: 13.5, fontWeight: 700, textTransform: "capitalize", color: "var(--ink)" }}>{post.platform}</span>
              </div>
            )}

            <div>
              <p style={{ fontSize: 11.5, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 10 }}>Generated Content</p>
              <div style={{ background: "var(--bg-soft)", border: "1px solid var(--border)", borderRadius: 11, padding: 18, fontSize: 13.5, lineHeight: 1.8, minHeight: 140, color: "var(--ink)" }}>
                {post?.content
                  ? <pre style={{ whiteSpace: "pre-wrap", fontFamily: "Inter, sans-serif", fontSize: 13.5 }}>{post.content}</pre>
                  : <div className="skeleton" style={{ height: 100 }} />
                }
              </div>
            </div>

            <div>
              <label style={{ fontSize: 11.5, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.5, display: "block", marginBottom: 10 }}>Revision Notes (if rejecting)</label>
              <textarea
                value={feedback}
                onChange={e => setFeedback(e.target.value)}
                placeholder="What should be changed in the content?"
                rows={3}
                style={{
                  width: "100%", background: "var(--bg-soft)", border: "1.5px solid var(--border)",
                  borderRadius: 11, padding: 14, color: "var(--ink)", fontSize: 13.5,
                  lineHeight: 1.6, resize: "vertical", outline: "none", fontFamily: "Inter, sans-serif",
                }}
                onFocus={e => e.target.style.borderColor = "var(--teal)"}
                onBlur={e => e.target.style.borderColor = "var(--border)"}
              />
            </div>

            <div style={{ display: "flex", gap: 10 }}>
              <button onClick={() => handleDecision(false)} disabled={loading} style={{
                flex: 1, background: "#fff", border: "1.5px solid #E0533D", color: "#C0452F",
                borderRadius: 11, padding: 14, fontSize: 13.5, fontWeight: 700, cursor: "pointer",
                opacity: loading && action !== "reject" ? 0.5 : 1,
              }}>{loading && action === "reject" ? "Revising…" : "✕ Reject"}</button>
              <button onClick={() => handleDecision(true)} disabled={loading} className="btn-primary" style={{
                flex: 1.5, borderRadius: 11, padding: 14, fontSize: 13.5,
                opacity: loading && action !== "approve" ? 0.5 : 1,
              }}>{loading && action === "approve" ? "Approving…" : "✓ Approve & Proceed →"}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}