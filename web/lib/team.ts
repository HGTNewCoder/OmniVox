// Everything shown on the Team page (/team). Edit this file to update it.
//
// Text in [square brackets] is a placeholder: replace it, or delete the line.
// Team photo: put one picture of the whole team at web/public/team/team.jpg
// (.jpg, .jpeg, .png or .webp). Until then the page shows an empty frame.

export interface Person {
  name: string;
  role: string;
  email?: string;
  github?: string;   // GitHub username, e.g. "HGTNewCoder"
  linkedin?: string; // full LinkedIn profile address
}

export interface Thanks {
  who: string;
  why: string;
}

export const TEAM_PHOTO_CAPTION = "The OmniVox team";

export const TEAM: Person[] = [
  { name: "Thinh Ha", role: "Back-end Developer", email: "tgh26@fsu.edu", github: "HGTNewCoder",
    linkedin: "https://www.linkedin.com/in/hgtnewcoder/" },
  { name: "Kha Hoang", role: "Front-end Developer", email: "mkha4622@gmail.com", github: "khaminh4622" },
  { name: "Long Pham", role: "Electrical Engineer", email: "longmadridista10@gmail.com",
    linkedin: "https://www.linkedin.com/in/long-pham-a59170360" },
  { name: "Duong Le", role: "Patient Liaison", email: "thaiduongle2008@gmail.com" },
];

export const THANKS: Thanks[] = [
  { who: "Dr. Sirichai Chayasirisobhon", why: "For supporting and guiding the project." },
  { who: "Rev. Dr. Victor Chayasirisobhon", why: "For supporting and guiding the project." },
  { who: "Mr. D and his family", why: "Whose needs inspired OmniVox." },
];
