import { LogoLoader } from "@/components/LogoLoader";

/** Har qanday sahifada bir xil balandlik/markazlashuv bilan ko'rsatiladi —
 * shunda foydalanuvchi qaysi bo'limga o'tmasin, loader har doim aynan bir
 * joyda (ekran markazida) chiqadi. */
export function PageLoader() {
  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <LogoLoader size={140} />
    </div>
  );
}
