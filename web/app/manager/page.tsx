import type { Metadata } from "next";
import CardManager from "@/components/manager/CardManager";
import { bundledAssets, loadAppData } from "@/lib/data";
import "./manager.css";

export const metadata: Metadata = {
  title: "Card Manager · OmniVox",
  description:
    "The OmniVox master program: find every OmniVox on the Wi-Fi and edit its cards, sub-cards, names and pictures. Try it here with simulated devices.",
};

export default function ManagerPage() {
  // Built at build time from the same json_page/board.json the device uses.
  const data = loadAppData();
  return <CardManager translations={data.translations} base={data.board} bundled={bundledAssets()} />;
}
