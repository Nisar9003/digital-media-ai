// Dashboard — shows all posts and their statuses
"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

export default function Dashboard() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetch("/api/posts")
      .then(r => r.json())
      .then(setPosts);
  }, []);

  return (
    <main className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-semibold mb-6">Digital Media AI Dashboard</h1>
      <Link href="/create" className="bg-black text-white px-4 py-2 rounded-lg text-sm mb-6 inline-block">
        + New Post
      </Link>
      <div className="grid gap-4 mt-6">
        {posts.map((post: any) => (
          <div key={post.id} className="border rounded-xl p-4 flex items-center justify-between">
            <div>
              <p className="font-medium capitalize">{post.platform}</p>
              <p className="text-sm text-gray-500">{post.status}</p>
            </div>
            {post.status === "image_review" && (
              <Link href={`/review/${post.id}`} className="text-blue-600 text-sm">Review Image →</Link>
            )}
            {post.status === "approved" && (
              <Link href={`/approve/${post.id}`} className="text-green-600 text-sm">Final Approve →</Link>
            )}
          </div>
        ))}
      </div>
    </main>
  );
}
