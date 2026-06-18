// Image Review — human-in-the-loop pause state
"use client";
import { useState } from "react";
import { useRouter, useParams } from "next/navigation";

export default function ImageReview() {
  const { id }   = useParams();
  const router   = useRouter();
  const [feedback, setFeedback] = useState("");
  const [loading,  setLoading]  = useState(false);

  async function handleDecision(approved: boolean) {
    setLoading(true);
    await fetch(`/api/posts/${id}/image-feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback, approved })
    });
    if (approved) {
      router.push(`/approve/${id}`);
    } else {
      setLoading(false);
      setFeedback("");
      alert("Image is being regenerated with your feedback...");
    }
  }

  return (
    <main className="p-8 max-w-xl mx-auto">
      <h1 className="text-2xl font-semibold mb-2">Review Generated Image</h1>
      <p className="text-gray-500 text-sm mb-6">Post ID: {id}</p>
      <div className="border rounded-xl bg-gray-50 h-64 flex items-center justify-center mb-6">
        <p className="text-gray-400 text-sm">Image preview loads here</p>
      </div>
      <label className="block text-sm font-medium mb-1">Feedback (optional)</label>
      <textarea
        className="w-full border rounded-lg p-3 mb-4 text-sm"
        rows={3}
        placeholder="e.g. Make background darker, add tech vibe..."
        value={feedback}
        onChange={e => setFeedback(e.target.value)}
      />
      <div className="flex gap-3">
        <button
          onClick={() => handleDecision(false)}
          disabled={loading}
          className="flex-1 border rounded-lg py-3 text-sm font-medium"
        >
          Regenerate
        </button>
        <button
          onClick={() => handleDecision(true)}
          disabled={loading}
          className="flex-1 bg-black text-white rounded-lg py-3 text-sm font-medium"
        >
          Approve Image →
        </button>
      </div>
    </main>
  );
}
