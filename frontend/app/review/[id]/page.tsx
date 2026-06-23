"use client";
import { useState, useEffect, useRef } from "react";
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

  const [positioning, setPositioning] = useState(false);
  const [logoPos, setLogoPos]         = useState({ x: 0.78, y: 0.78 });
  const [logoScale, setLogoScale]     = useState(0.16);
  const [savingPos, setSavingPos]     = useState(false);
  const imgWrapRef = useRef<HTMLDivElement>(null);
  const dragging   = useRef(false);

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
      setPost((p: any) => ({ ...p, image_url: data.image_url, raw_image_url: data.raw_image_url, composed_image_url: data.composed_image_url }));
      setFeedback(""); setLoading(false); setAction(null);
    }
  }

  function getFractionFromEvent(e: React.MouseEvent) {
    const wrap = imgWrapRef.current;
    if (!wrap) return null;
    const rect = wrap.getBoundingClientRect();
    let x = (e.clientX - rect.left) / rect.width;
    let y = (e.clientY - rect.top) / rect.height;
    x = Math.max(0, Math.min(1, x));
    y = Math.max(0, Math.min(1, y));
    return { x, y };
  }

  function handlePointerDown(e: React.MouseEvent) {
    if (!positioning) return;
    dragging.current = true;
    const frac = getFractionFromEvent(e);
    if (frac) setLogoPos(frac);
  }
  function handlePointerMove(e: React.MouseEvent) {
    if (!positioning || !dragging.current) return;
    const frac = getFractionFromEvent(e);
    if (frac) setLogoPos(frac);
  }
  function handlePointerUp() {
    dragging.current = false;
  }

  async function saveLogoPosition() {
    setSavingPos(true);
    try {
      const res = await fetch(`${BASE_URL}/api/posts/${id}/logo-position`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ x: logoPos.x, y: logoPos.y, scale: logoScale }),
      });
      const data = await res.json();
      setPost((p: any) => ({ ...p, image_url: data.image_url }));
      setPositioning(false);
    } catch {
      alert("Could not save logo position. Try again.");
    } finally {
      setSavingPos(false);
    }
  }

  const displayImage = positioning ? (post?.composed_image_url || post?.raw_image_url || post?.image_url) : post?.image_url;

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
            <div
              ref={imgWrapRef}
              onMouseDown={handlePointerDown}
              onMouseMove={handlePointerMove}
              onMouseUp={handlePointerUp}
              onMouseLeave={handlePointerUp}
              style={{
                background: "#fff", border: "1px solid var(--border)", borderRadius: 16,
                overflow: "hidden", aspectRatio: "1", display: "flex", alignItems: "center", justifyContent: "center",
                position: "relative", cursor: positioning ? "crosshair" : "default", userSelect: "none",
              }}>
              {displayImage
                ? <img src={displayImage} alt="Generated" draggable={false} style={{ width: "100%", height: "100%", objectFit: "cover", pointerEvents: "none" }} />
                : <div className="skeleton" style={{ width: "85%", height: "85%" }} />
              }
              {positioning && (post?.composed_image_url || post?.raw_image_url) && (
                <img
                  src="/logo.png"
                  alt="logo preview"
                  draggable={false}
                  style={{
                    position: "absolute",
                    left: `${logoPos.x * 100}%`,
                    top: `${logoPos.y * 100}%`,
                    width: `${logoScale * 100}%`,
                    pointerEvents: "none",
                    border: "2px dashed var(--teal)",
                    borderRadius: 4,
                  }}
                />
              )}
            </div>

            {(post?.composed_image_url || post?.raw_image_url) && (
              <div style={{ marginTop: 14 }}>
                {!positioning ? (
                  <button onClick={() => setPositioning(true)} style={{
                    width: "100%", background: "var(--teal-light)", border: "1.5px solid var(--teal)",
                    color: "var(--teal-dark)", borderRadius: 10, padding: 11, fontSize: 13, fontWeight: 700, cursor: "pointer",
                  }}>Reposition Logo</button>
                ) : (
                  <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 12, padding: 16 }}>
                    <p style={{ fontSize: 12, color: "var(--body)", marginBottom: 12 }}>
                      Click or drag anywhere on the image to place the logo.
                    </p>
                    <label style={{ fontSize: 11, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", display: "block", marginBottom: 6 }}>
                      Logo Size
                    </label>
                    <input
                      type="range" min={0.06} max={0.35} step={0.01}
                      value={logoScale}
                      onChange={e => setLogoScale(parseFloat(e.target.value))}
                      style={{ width: "100%", marginBottom: 14 }}
                    />
                    <div style={{ display: "flex", gap: 8 }}>
                      <button onClick={() => setPositioning(false)} style={{
                        flex: 1, background: "#fff", border: "1px solid var(--border)", color: "var(--muted)",
                        borderRadius: 9, padding: 10, fontSize: 12.5, fontWeight: 600, cursor: "pointer",
                      }}>Cancel</button>
                      <button onClick={saveLogoPosition} disabled={savingPos} className="btn-primary" style={{
                        flex: 1, borderRadius: 9, padding: 10, fontSize: 12.5,
                      }}>{savingPos ? "Saving..." : "Save Position"}</button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {post?.image_url && !positioning && (
              <a href={post.image_url} target="_blank" style={{ display: "block", textAlign: "center", marginTop: 12, fontSize: 12, color: "var(--teal)", fontWeight: 600, textDecoration: "none" }}>Open full resolution &#8599;</a>
            )}
          </div>

          <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 16, padding: 26, display: "flex", flexDirection: "column", gap: 18 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 11.5, color: "var(--muted)", fontWeight: 600 }}>Post ID: {String(id).slice(0,12)}...</span>
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
                placeholder="e.g. Make background darker, add a corporate tech feel..."
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
              <button onClick={() => handleDecision(true)} disabled={loading || positioning} style={{
                background: "#1F8A40", color: "#fff", border: "none", borderRadius: 11,
                padding: 14, fontSize: 14, fontWeight: 700, cursor: (loading || positioning) ? "not-allowed" : "pointer",
                opacity: (loading && action !== "approve") || positioning ? 0.5 : 1,
              }}>{loading && action === "approve" ? "Moving forward..." : "Approve Image"}</button>

              <button onClick={() => handleDecision(false)} disabled={loading || positioning} style={{
                background: "#fff", border: "1.5px solid #B8780C", color: "#B8780C", borderRadius: 11,
                padding: 14, fontSize: 14, fontWeight: 700, cursor: (loading || positioning) ? "not-allowed" : "pointer",
                opacity: (loading && action !== "reject") || positioning ? 0.5 : 1,
              }}>{loading && action === "reject" ? "Regenerating..." : "Regenerate with Feedback"}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}