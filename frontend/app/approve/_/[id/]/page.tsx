// Final Approval Board — content + image side by side
"use client";
import { useState } from "react";
import { useRouter, useParams } from "next/navigation";

export default function FinalApprove() {
  const { id }  = useParams();
  const router  = useRouter();
  const [feedback, setFeedback] = useState("");
  const [loading,  setLoading]  = useState(false);

  async function handleDecision(approved: boolean) {
    setLoading(true);
    await fetch(`/api/posts/${id}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approved, content_feedback: feedback })
    });
    if (approved) {
      router.push("/");
    } else {
      setLoading(false);
      setFeedback("");
      alert("Content is being revised...");
    }
  }

  return (
    <main className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold mb-6">Final Approval</h1>
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="border rounded-xl bg-gray-50 h-64 flex items-center justify-center">
          <p className="text-gray-400 text-sm">Approved image</p>
        </div>
        <div className="border rounded-xl p-4">
          <p className="text-xs text-gray-400 mb-2 font-medium uppercase tracking-wide">Caption</p>
          <p className="text-sm text-gray-700">Generated content appears here...</p>
        </div>
      </div>
      <label className="block text-sm font-medium mb-1">Revision notes (if rejecting)</label>
      <textarea
        className="w-full border rounded-lg p-3 mb-4 text-sm"
        rows={3}
        placeholder="What should be changed in the content?"
        value={feedback}
        onChange={e => setFeedback(e.target.value)}
      />
      <div className="flex gap-3">
        <button
          onClick={() => handleDecision(false)}
          disabled={loading}
          className="flex-1 border rounded-lg py-3 text-sm font-medium"
        >
          Reject — Revise Content
        </button>
        <button
          onClick={() => handleDecision(true)}
          disabled={loading}
          className="flex-1 bg-black text-white rounded-lg py-3 text-sm font-medium"
        >
          Approve & Publish →
        </button>
      </div>
    </main>
  );
}
