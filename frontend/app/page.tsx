"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import Nav from "../components/Nav";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PLATFORM_META: Record<string, { code: string; color: string }> = {
  linkedin:  { code: "in", color: "#0A66C2" },
  instagram: { code: "ig", color: "#C13584" },
  facebook:  { code: "fb", color: "#1877F2" },
  tiktok:    { code: "tt", color: "#111111" },
};

const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  draft:              { label: "Draft",         color: "#8896A3", bg: "#F1F3F5" },
  image_review:       { label: "Image Review",  color: "#B8780C", bg: "#FBF1DC" },
  image_regenerating: { label: "Regenerating",  color: "#B8780C", bg: "#FBF1DC" },
  final_review:       { label: "Final Review",  color: "#0A6E8C", bg: "#E1F1F5" },
  content_revision:   { label: "Revising",      color: "#C0452F", bg: "#FBE6E1" },
  approved:           { label: "Approved",      color: "#1F8A40", bg: "#E3F5E8" },
  publishing:         { label: "Publishing",    color: "#006666", bg: "#E6F5F5" },
  published:          { label: "Published",     color: "#1F8A40", bg: "#E3F5E8" },
};

const PIPELINE_STEPS = ["Create", "Image Review", "Final Review", "Approved", "Published"];

export default function Dashboard() {
  const [posts, setPosts]     = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter]   = useState("all");

  const fetchPosts = async () => {
    try {
      const url = filter === "all" ? `${BASE_URL}/api/posts/` : `${BASE_URL}/api/posts/?status=${filter}`;
      const res = await fetch(url);
      const data = await res.json();
      setPosts(Array.isArray(data) ? data : []);
    } catch { setPosts([]); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchPosts(); }, [filter]);

  async function handleDelete(postId: string) {
    if (!confirm("Delete this post permanently? This cannot be undone.")) return;
    try {
      await fetch(`${BASE_URL}/api/posts/${postId}`, { method: "DELETE" });
      setPosts(prev => prev.filter(p => p.id !== postId));
    } catch {
      alert("Could not delete post. Try again.");
    }
  }

  const stats = {
    total:     posts.length,
    published: posts.filter(p => p.status === "published").length,
    pending:   posts.filter(p => ["image_review", "final_review"].includes(p.status)).length,
    drafts:    posts.filter(p => p.status === "draft").length,
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-soft)" }}>
      <Nav active="dashboard" />

      <div style={{ maxWidth: 1240, margin: "0 auto", padding: "40px 32px 80px" }}>

        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 32 }}>
          <div>
            <p style={{ color: "var(--teal)", fontWeight: 700, fontSize: 12.5, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 6 }}>
              Content Operations
            </p>
            <h1 style={{ fontSize: 28, fontWeight: 800, color: "var(--ink)" }}>Campaign Dashboard</h1>
          </div>
          <button onClick={fetchPosts} style={{
            background: "#fff", border: "1px solid var(--border)", color: "var(--body)",
            padding: "9px 18px", borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: "pointer",
          }}>↻ Refresh</button>
        </div>

        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 18, marginBottom: 28 }}>
          {[
            { label: "Total Posts", value: stats.total,     color: "var(--teal)" },
            { label: "Published",   value: stats.published, color: "#1F8A40" },
            { label: "In Review",   value: stats.pending,   color: "#B8780C" },
            { label: "Drafts",      value: stats.drafts,    color: "#5B6B7B" },
          ].map(s => (
            <div key={s.label} style={{
              background: "#fff", border: "1px solid var(--border)", borderRadius: 14,
              padding: "22px 24px", borderLeft: `4px solid ${s.color}`,
            }}>
              <p style={{ color: "var(--muted)", fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: 0.4, marginBottom: 10 }}>{s.label}</p>
              <p style={{ fontSize: 30, fontWeight: 800, color: "var(--ink)" }}>{s.value}</p>
            </div>
          ))}
        </div>

        {/* Pipeline */}
        <div style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 14, padding: "22px 28px", marginBottom: 32 }}>
          <p style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 0.4, marginBottom: 18 }}>Production Pipeline</p>
          <div style={{ display: "flex", alignItems: "center" }}>
            {PIPELINE_STEPS.map((step, i, arr) => (
              <div key={step} style={{ display: "flex", alignItems: "center", flex: i < arr.length - 1 ? 1 : "none" }}>
                <div style={{
                  width: 28, height: 28, borderRadius: "50%",
                  background: i === 0 ? "var(--teal)" : "var(--bg-soft)",
                  border: i === 0 ? "none" : "2px solid var(--border)",
                  color: i === 0 ? "#fff" : "var(--muted)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 12, fontWeight: 700, flexShrink: 0,
                }}>{i + 1}</div>
                <span style={{ fontSize: 12.5, fontWeight: 600, color: i === 0 ? "var(--ink)" : "var(--muted)", marginLeft: 8, whiteSpace: "nowrap" }}>{step}</span>
                {i < arr.length - 1 && <div style={{ flex: 1, height: 2, background: "var(--border)", margin: "0 14px" }} />}
              </div>
            ))}
          </div>
        </div>

        {/* Filters */}
        <div style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
          {["all", "image_review", "final_review", "approved", "published"].map(f => (
            <button key={f} onClick={() => setFilter(f)} style={{
              background: filter === f ? "var(--teal)" : "#fff",
              border: `1px solid ${filter === f ? "var(--teal)" : "var(--border)"}`,
              color: filter === f ? "#fff" : "var(--body)",
              padding: "7px 18px", borderRadius: 20, fontSize: 12.5, fontWeight: 600,
              cursor: "pointer", textTransform: "capitalize",
            }}>{f === "all" ? "All Posts" : f.replace(/_/g, " ")}</button>
          ))}
        </div>

        {/* Posts */}
        {loading ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 18 }}>
            {[1,2,3].map(i => (
              <div key={i} style={{ background: "#fff", border: "1px solid var(--border)", borderRadius: 14, padding: 22 }}>
                <div className="skeleton" style={{ height: 16, width: "55%", marginBottom: 14 }} />
                <div className="skeleton" style={{ height: 130, marginBottom: 14 }} />
                <div className="skeleton" style={{ height: 36 }} />
              </div>
            ))}
          </div>
        ) : posts.length === 0 ? (
          <div style={{
            textAlign: "center", padding: "90px 24px", background: "#fff",
            border: "1px dashed var(--border)", borderRadius: 16,
          }}>
            <div style={{
              width: 56, height: 56, borderRadius: "50%", background: "var(--teal-light)",
              display: "flex", alignItems: "center", justifyContent: "center",
              margin: "0 auto 20px", fontSize: 24,
            }}>📋</div>
            <p style={{ fontSize: 18, fontWeight: 700, color: "var(--ink)", marginBottom: 8 }}>No posts yet</p>
            <p style={{ fontSize: 14, color: "var(--muted)", marginBottom: 26 }}>Spin up your first AI-generated campaign post.</p>
            <Link href="/create" className="btn-primary" style={{
              padding: "11px 26px", borderRadius: 9, fontSize: 14, textDecoration: "none", display: "inline-block",
            }}>+ Create First Post</Link>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(330px,1fr))", gap: 18 }}>
            {posts.map((post, i) => {
              const sc = STATUS_CONFIG[post.status] || { label: post.status, color: "#8896A3", bg: "#F1F3F5" };
              const pm = PLATFORM_META[post.platform] || { code: post.platform?.slice(0,2).toUpperCase(), color: "#555" };
              return (
                <div key={post.id} className="fade-up card-hover" style={{
                  background: "#fff", border: "1px solid var(--border)", borderRadius: 14,
                  padding: 20, animationDelay: `${i * 0.04}s`,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div style={{
                        width: 34, height: 34, borderRadius: 9, background: pm.color,
                        display: "flex", alignItems: "center", justifyContent: "center",
                        color: "#fff", fontSize: 12, fontWeight: 700,
                      }}>{pm.code}</div>
                      <div>
                        <p style={{ fontSize: 13.5, fontWeight: 700, textTransform: "capitalize", color: "var(--ink)" }}>{post.platform}</p>
                        <p style={{ fontSize: 10.5, color: "var(--muted)" }}>{post.id?.slice(0,8)}…</p>
                      </div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ background: sc.bg, color: sc.color, fontSize: 11, fontWeight: 700, padding: "4px 10px", borderRadius: 20 }}>{sc.label}</span>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(post.id); }}
                        title="Delete post"
                        style={{
                          background: "transparent", border: "1px solid var(--border)", color: "var(--muted)",
                          width: 24, height: 24, borderRadius: 6, cursor: "pointer",
                          display: "flex", alignItems: "center", justifyContent: "center",
                          fontSize: 13, lineHeight: 1, padding: 0,
                        }}
                        onMouseOver={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = "#E0533D"; (e.currentTarget as HTMLButtonElement).style.color = "#E0533D"; }}
                        onMouseOut={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--border)"; (e.currentTarget as HTMLButtonElement).style.color = "var(--muted)"; }}
                      >✕</button>
                    </div>
                  </div>

                  {post.image_url && (
                    <div style={{ borderRadius: 10, overflow: "hidden", marginBottom: 12, background: "var(--bg-soft)", height: 150 }}>
                      <img src={post.image_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                    </div>
                  )}

                  {post.content && (
                    <p style={{ fontSize: 12.5, color: "var(--body)", lineHeight: 1.6, marginBottom: 14, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{post.content}</p>
                  )}

                  <p style={{ fontSize: 10.5, color: "var(--muted)", marginBottom: 14 }}>
                    {post.created_at ? new Date(post.created_at).toLocaleString() : "—"}
                  </p>

                  {post.status === "image_review" && (
                    <Link href={`/review/${post.id}`} style={{ display: "block", textAlign: "center", background: "#FBF1DC", color: "#B8780C", padding: 9, borderRadius: 8, fontSize: 12.5, fontWeight: 700, textDecoration: "none" }}>Review Image →</Link>
                  )}
                  {post.status === "final_review" && (
                    <Link href={`/approve/${post.id}`} style={{ display: "block", textAlign: "center", background: "#E1F1F5", color: "#0A6E8C", padding: 9, borderRadius: 8, fontSize: 12.5, fontWeight: 700, textDecoration: "none" }}>Final Approval →</Link>
                  )}
                  {post.status === "approved" && (
                    <Link href={`/publish/${post.id}`} style={{ display: "block", textAlign: "center", background: "var(--teal)", color: "#fff", padding: 9, borderRadius: 8, fontSize: 12.5, fontWeight: 700, textDecoration: "none" }}>Publish Now →</Link>
                  )}
                  {post.status === "published" && (
                    <div style={{ textAlign: "center", background: "#E3F5E8", color: "#1F8A40", padding: 9, borderRadius: 8, fontSize: 12.5, fontWeight: 700 }}>✓ Published</div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}