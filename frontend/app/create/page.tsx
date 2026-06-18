// Post Creator — user enters goal and platform
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

const PLATFORMS = ["linkedin", "instagram", "facebook", "tiktok"];

export default function CreatePost() {
  const router   = useRouter();
  const [goal,     setGoal]     = useState("");
  const [platform, setPlatform] = useState("linkedin");
  const [loading,  setLoading]  = useState(false);

  async function handleSubmit() {
    setLoading(true);
    const res = await fetch("/api/posts/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal, platform, campaign_id: "default" })
    });
    const data = await res.json();
    router.push(`/review/${data.run_id}`);
  }

  return (
    <main className="p-8 max-w-xl mx-auto">
      <h1 className="text-2xl font-semibold mb-6">Create New Post</h1>
      <label className="block text-sm font-medium mb-1">Goal</label>
      <textarea
        className="w-full border rounded-lg p-3 mb-4 text-sm"
        rows={4}
        placeholder="e.g. Announce our AI product launch"
        value={goal}
        onChange={e => setGoal(e.target.value)}
      />
      <label className="block text-sm font-medium mb-1">Platform</label>
      <select
        className="w-full border rounded-lg p-3 mb-6 text-sm"
        value={platform}
        onChange={e => setPlatform(e.target.value)}
      >
        {PLATFORMS.map(p => (
          <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
        ))}
      </select>
      <button
        onClick={handleSubmit}
        disabled={loading || !goal}
        className="w-full bg-black text-white py-3 rounded-lg font-medium disabled:opacity-50"
      >
        {loading ? "Agents working..." : "Generate Post"}
      </button>
    </main>
  );
}
