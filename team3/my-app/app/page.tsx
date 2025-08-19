import Navbar from "@/components/Navbar";
import StoryGeneratorForm from "@/components/StoryGeneratorForm";
import StoryCard from "@/components/StoryCard";
import { Stories } from "@/utils/stories";
export default function Home() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: "#ECEEDF" }}>
      <Navbar />

      <main className="p-6">
        <StoryGeneratorForm />

        {Stories.map((story) => {
          return (
            <StoryCard
              title={story.title}
              snippet={story.snippet}
              href={story.href}
            />
          );
        })}

        <div className="mt-8"></div>
      </main>
    </div>
  );
}
