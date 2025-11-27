// =======================================================================
// /src/app/layout.jsx
// This is the final, corrected root layout for your entire application.
// =======================================================================

import { GeistSans } from "geist/font/sans";
import { Playfair_Display } from "next/font/google";
import { AuthProvider } from '@/context/AuthContext';
import { ChatProvider } from '@/context/ChatContext'; 
import "./globals.css";

// Configure the font for the logo from your mockup
const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-playfair-display',
});

export const metadata = {
  title: "Unmask - Reveal on Your Terms",
  description: "Consent-first photo sharing. Your photos, your control, your network.",
};

export default function RootLayout({ children }) {
  return (
    // We remove the "dark" className to default to the light theme
    <html lang="en">
      <body
        // We combine the font classes and set the new default background color
        className={`${GeistSans.variable} ${playfair.variable} antialiased bg-background`}
      >
        <AuthProvider>
          <ChatProvider>
          {children}
          </ChatProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
