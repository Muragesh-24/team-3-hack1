"use client";
import { useState, useEffect } from "react";

type Story = {
  title: string;
  storyParts: string[];
  images_video: string[];
};

export default function StoryGeneratorForm() {
  const [story, setStory] = useState<Story | null>(null);
  const [loading, setLoading] = useState(false);

  async function addStory() {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:5000/api/stories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: "A magical forest adventure", // you can grab this from textarea later
        }),
      });

      const data: Story = await response.json();
      setStory(data);
      console.log("Generated Story:", data);
    } catch (err) {
      console.error("Error generating story:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="p-6 rounded-2xl shadow-lg mt-6 max-w-lg mx-auto"
      style={{ backgroundColor: "#ECEEDF" }}
    >
      <textarea
        placeholder="Describe characters or idea..."
        className="w-full h-32 p-2 border rounded mb-4"
      />
      <button
        onClick={addStory}
        disabled={loading}
        className="px-4 py-2 rounded-xl transition"
        style={{
          backgroundColor: "#BBDCE5",
          color: "#CFAB8D",
          opacity: loading ? 0.6 : 1,
        }}
      >
        {loading ? "Generating..." : "Generate Story"}
      </button>
    </div>
  );
}
