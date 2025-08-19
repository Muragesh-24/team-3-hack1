import Navbar from "@/components/Navbar";
import StoryGeneratorForm from "@/components/StoryGeneratorForm";
import StoryCard from "@/components/StoryCard";

export default function Home() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: "#ECEEDF" }}>
      <Navbar />

      <main className="p-6">
        <StoryGeneratorForm />

        {/* Example Stories */}
        <div className="mt-8">
          <StoryCard
            title="The Lost Kingdom"
            snippet="Once upon a time in a faraway land..."
          />
          <StoryCard
            title="AI Meets Humanity"
            snippet="In the year 2077, machines began to dream..."
          />
        </div>
      </main>
    </div>
  );
}
