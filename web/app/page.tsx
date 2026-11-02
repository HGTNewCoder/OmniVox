import DemoSection from "@/components/demo/DemoSection";
import { Features, Footer, Hardware, Hero, Highlights, HowItWorks, Nav, RunIt } from "@/components/sections/Landing";
import { loadAppData } from "@/lib/data";

export default function Home() {
  // Read ../json_page at build time — the same files the Raspberry Pi app uses.
  const data = loadAppData();
  return (
    <>
      <Nav />
      <main id="top">
        <Hero data={data} />
        <DemoSection data={data} />
        <Features data={data} />
        <Highlights />
        <HowItWorks />
        <Hardware />
        <RunIt />
      </main>
      <Footer />
    </>
  );
}
