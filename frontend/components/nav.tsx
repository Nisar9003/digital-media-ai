"use client";
import Link from "next/link";

export default function Nav({ active = "" }: { active?: string }) {
  return (
    <nav style={{
      background: "#fff", borderBottom: "1px solid var(--border)",
      padding: "0 40px", height: 68,
      display: "flex", alignItems: "center", justifyContent: "space-between",
      position: "sticky", top: 0, zIndex: 100,
    }}>
      <Link href="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
        <div style={{
          width: 36, height: 36, borderRadius: 9,
          background: "linear-gradient(135deg, #008080, #00A3A3)",
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "#fff", fontWeight: 800, fontSize: 15, fontFamily: "'Plus Jakarta Sans', sans-serif",
        }}>K</div>
        <div>
          <div style={{ fontWeight: 800, fontSize: 15, color: "var(--ink)", fontFamily: "'Plus Jakarta Sans', sans-serif", lineHeight: 1.1 }}>
            KeyDevs <span style={{ color: "var(--teal)" }}>MediaAI</span>
          </div>
          <div style={{ fontSize: 10, color: "var(--muted)", letterSpacing: 0.4 }}>SOCIAL CONTENT ENGINE</div>
        </div>
      </Link>

      <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
        <Link href="/" style={{
          fontSize: 13.5, fontWeight: 600, textDecoration: "none",
          color: active === "dashboard" ? "var(--teal)" : "var(--body)",
        }}>Dashboard</Link>
        <a href="https://keydevs.pk" target="_blank" style={{
          fontSize: 13.5, fontWeight: 600, textDecoration: "none", color: "var(--body)",
        }}>keydevs.pk ↗</a>
        <Link href="/create" style={{
          background: "var(--teal)", color: "#fff", textDecoration: "none",
          padding: "9px 20px", borderRadius: 8, fontSize: 13.5, fontWeight: 700,
        }}>+ New Post</Link>
      </div>
    </nav>
  );
}