import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KeyDevs MediaAI | Social Content Engine",
  description: "AI-powered social media content creation, built by KeyDevs Technologies",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}