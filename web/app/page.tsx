import DemoSection from "@/components/demo/DemoSection";
import { Footer, Hero, HowItWorks, ManagerTeaser, Nav } from "@/components/sections/Landing";
import { loadAppData } from "@/lib/data";

export default function Home() {
  // Read ../json_page at build time: the same board.json the Raspberry Pi app uses.
  const data = loadAppData();
  return (
    <>
      <Nav />
      <main id="top">
        <Hero data={data} />
        <DemoSection data={data} />
        <ManagerTeaser />
        <HowItWorks />
      </main>
      <Footer />
    </>
  );
}
