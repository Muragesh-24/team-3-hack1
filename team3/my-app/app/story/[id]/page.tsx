"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useParams } from "next/navigation";

export default function StoryViewer() {
  const [isEditing, setIsEditing] = useState(false);
  const [storyText, setStoryText] = useState<string>(
    "Once upon a time... your story will appear here."
  );
  const router = useRouter();
  const params = useParams();
  const id = params.id;

  //useeffect and fetch story and images from story.ts
  console.log(id);
  //edit save function

  const editsavefunction = () => {
    setIsEditing(false);

    //then save in the .ts
  };
  return (
    <div className="min-h-screen bg-[#ECEEDF] flex flex-col">
      {/* Top Bar */}
      <div className="bg-[#BBDCE5] p-4 shadow-md flex justify-between items-center">
        <h1 className="text-xl font-semibold text-[#2F2F2F]">Story Viewer</h1>
        <button
          className="px-4 py-2 rounded-lg bg-[#D9C4B0] text-[#2F2F2F] hover:bg-[#CFAB8D]"
          onClick={() => router.push("/")}
        >
          Home
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 gap-6">
        {/* Media Section */}
        <div className="w-full max-w-3xl h-64 bg-[#BBDCE5] rounded-2xl shadow-lg flex items-center justify-center text-gray-700">
          <p>Image / Sound Placeholder</p>
          {/* add start button */}
        </div>

        {/* Text Section */}
        <div className="w-full max-w-3xl bg-[#D9C4B0] rounded-2xl shadow-lg p-4">
          {isEditing ? (
            <textarea
              className="w-full h-48 p-3 rounded-lg bg-[#ECEEDF] border border-[#CFAB8D] text-black focus:outline-none"
              value={storyText}
              onChange={(e) => setStoryText(e.target.value)}
            />
          ) : (
            <p className="text-gray-800 whitespace-pre-wrap">{storyText}</p>
          )}
        </div>

        {/* Buttons */}
        <div className="flex gap-4 self-start">
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="px-6 py-2 rounded-lg bg-[#CFAB8D] text-white hover:bg-[#B07A56]"
          >
            {isEditing ? "Cancel" : "Edit"}
          </button>
          {isEditing && (
            <button
              onClick={editsavefunction}
              className="px-6 py-2 rounded-lg bg-[#BBDCE5] text-[#2F2F2F] hover:bg-[#97BFCF]"
            >
              Save
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
