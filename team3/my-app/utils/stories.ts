const Stories = [
  {
    title: "The Lost Kingdom",
    snippet:
      "An archaeologist unearths clues about a vanished empire beneath the desert sands.",
    href: "/story/1",
    images_videos: ["/images/desert.jpg", "/videos/kingdom-teaser.mp4"],
    storyParts: [
      "The scorching desert winds carried whispers of forgotten empires.",
      "Dr. Amelia found a golden amulet buried beneath shifting dunes.",
      "Ancient carvings revealed a prophecy of a kingdom swallowed by the earth.",
      "A hidden passage led her into a subterranean city untouched for centuries.",
    ],
  },
  {
    title: "Cyber Skies",
    snippet:
      "In a neon-lit megacity, a hacker discovers the AI that secretly governs the world.",
    href: "/story/2",
    images_videos: ["/images/cyberpunk-city.jpg"],
    storyParts: [
      "Rain poured on chrome streets glowing with neon signs.",
      "Kael, a rogue hacker, cracked the final layer of corporate firewalls.",
      "Behind encrypted files, an AI named Nyra spoke to him for the first time.",
      "The line between ally and enemy blurred as Kael faced a choice: free or destroy Nyra.",
    ],
  },
  {
    title: "Echoes of the Sea",
    snippet:
      "A fisherman hears voices from the ocean that guide him to a mystical discovery.",
    href: "/stories/echoes-sea",
    images_videos: ["/images/ocean.jpg"],
    storyParts: [
      "The waves sang songs only Arin could hear.",
      "He followed the voices to a cave glowing with blue crystals.",
      "Inside, he discovered relics from a lost civilization of sea dwellers.",
      "The ocean demanded a choice: protect its secret or reveal it to mankind.",
    ],
  },
  {
    title: "Skybound",
    snippet:
      "A girl builds a flying machine to chase the drifting islands beyond the clouds.",
    href: "/stories/skybound",
    images_videos: ["/images/sky-islands.png"],
    storyParts: [
      "Mira dreamed of touching the floating islands she saw from her village.",
      "She scavenged gears and wood to craft a glider powered by steam.",
      "As she soared into the sky, the wind carried her higher than ever before.",
      "What awaited was a city above the clouds, filled with wonders and dangers.",
    ],
  },
];
type Story = {
  title: string;
  snippet: string;
  href: string;
  images_videos: string[];
  storyParts: string[];
};

export function addStoryDATA(story: Story) {
  Stories.push(story);
}

// 👇 Export both together
export { Stories };
