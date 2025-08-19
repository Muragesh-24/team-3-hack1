"use client";

import Link from "next/link";

type StoryCardProps = {
  title: string;
  snippet: string;
  href: string; // where the card should link to
};

export default function StoryCard({ title, snippet, href }: StoryCardProps) {
  return (
    <Link href={href} className="block no-underline">
      <div
        className="p-6 rounded-2xl shadow-lg mt-6 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-xl cursor-pointer"
        style={{
          backgroundColor: "#ECEEDF",
          border: "1px solid #D9C4B0",
        }}
      >
        <h2
          className="text-2xl font-extrabold mb-2 tracking-wide"
          style={{ color: "#CFAB8D" }}
        >
          {title}
        </h2>
        <p className="text-base leading-relaxed" style={{ color: "#6B4F3D" }}>
          {snippet}
        </p>

        {/* Decorative underline */}
        <div
          className="mt-4 h-[3px] w-16 rounded-full"
          style={{ backgroundColor: "#BBDCE5" }}
        ></div>
      </div>
    </Link>
  );
}
