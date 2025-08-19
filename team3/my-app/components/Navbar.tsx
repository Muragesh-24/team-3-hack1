"use client";

export default function Navbar() {
  return (
    <nav
      className="flex justify-between p-4 rounded-b-2xl shadow-md"
      style={{ backgroundColor: "#BBDCE5" }}
    >
      <h1 className="text-xl font-bold" style={{ color: "#CFAB8D" }}>
        Dashboard
      </h1>
      <div className="space-x-4">
        <button style={{ color: "#D9C4B0" }} className="hover:text-[#CFAB8D]">
          Create
        </button>
        <button style={{ color: "#D9C4B0" }} className="hover:text-[#CFAB8D]">
          Read Story
        </button>
        <button style={{ color: "#D9C4B0" }} className="hover:text-[#CFAB8D]">
          Edit
        </button>
      </div>
    </nav>
  );
}
