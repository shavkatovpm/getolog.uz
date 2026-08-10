import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Script from "next/script";
import { ThemeProvider } from "@/lib/theme-context";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "GETOLOG Dashboard",
  description: "GETOLOG admin va owner boshqaruv paneli",
};

// `viewportFit: "cover"` bo'lmasa, iOS Safari `env(safe-area-inset-*)`ni doim
// 0 deb hisoblaydi — shuning uchun pastki panel Home Indicator'ga yopishib qoladi.
//
// `interactiveWidget: "overlays-content"` — standart holatda (`resizes-visual`)
// klaviatura ochilganda brauzer "ko'rinadigan maydon"ni qisqartiradi va
// `position: fixed` elementlar (navbar, pastki panel) shu yangi qisqargan
// maydonga moslashib, klaviatura TEPASIGA "suzib chiqadi" — panel joyidan
// siljib ketganday tuyuladi. `overlays-content` esa klaviaturani sahifa
// ustiga oddiy qoplama (overlay) sifatida ko'rsatadi — sahifa o'lchami
// umuman o'zgarmaydi, shuning uchun panel har doim aynan bir joyda qoladi
// (klaviatura ochilganda uning bir qismi shunchaki klaviatura ostida qolishi
// mumkin, lekin hech qachon "sakramaydi").
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  interactiveWidget: "overlays-content",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="uz"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        {/* Oddiy (next/script emas) inline skript — brauzer HTML'ni parse qilayotganda
            darhol, sinxron bajariladi, shuning uchun React yuklanguncha ham
            `data-theme` to'g'ri o'rnatiladi va tema miltillashi (FOUC) bo'lmaydi. */}
        <script
          suppressHydrationWarning
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('getolog_theme')||'dark';document.documentElement.setAttribute('data-theme',t);}catch(e){}})();`,
          }}
        />
        <Script src="https://telegram.org/js/telegram-web-app.js" strategy="beforeInteractive" />
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
