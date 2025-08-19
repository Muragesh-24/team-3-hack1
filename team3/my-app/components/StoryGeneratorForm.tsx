"use client";
import { useState } from "react";
import { addStoryDATA, Stories } from "@/utils/stories";

type Story = {
  title: string;
  snippet: string;
  href: string;
  images_videos: string[];
  storyParts: string[];
};

export default function StoryGeneratorForm() {
  const [story, setStory] = useState<Story | null>(null);
  const [loading, setLoading] = useState(false);
  const [prompt, setPrompt] = useState("");
  let finalAddition: Story;

  async function addStory() {
    setLoading(true);
    try {
      // For now just fetch a single story (mock)
      const response = await fetch("http://localhost:4000/api/stories", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      });

      const data: Story = await response.json();
      setStory(data);
      finalAddition = data;
      addStoryDATA(data);
      console.log(data);
      // Add the story to the global Stories array
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
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
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
