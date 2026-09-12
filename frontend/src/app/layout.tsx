import type { Metadata } from "next";
import "./globals.css";
import Shell from "./shell";
export const metadata: Metadata = { title: "Datahealth — Clarity for your data", description: "Profile, validate, and clean your datasets in one considered workspace." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      {/* Browser extensions may add __processed_* attributes before hydration.
          Limit suppression to the body itself; descendants remain checked. */}
      <body suppressHydrationWarning>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
