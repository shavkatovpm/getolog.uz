/**
 * Mobil klaviatura (ayniqsa Telegram Mini App ichida) ochilganda ko'rinadigan
 * balandlik kamayadi — agar interfeys qobig'i shu "jonli" balandlikka
 * bog'langan bo'lsa, header/pastki panel klaviatura tepasiga "sakrab" chiqadi.
 *
 * Telegram SDK'ning `viewportStableHeight`iga tayanish ishonchsiz chiqdi —
 * SDK tayyor bo'lmasligi yoki hodisa o'z vaqtida kelmasligi mumkin. Shuning
 * uchun butunlay boshqa, hech narsaga bog'liq bo'lmagan usul: balandlikni
 * `window.innerHeight`dan o'qib, uni CSS o'zgaruvchisiga "qulflab" qo'yamiz.
 * Klaviatura ochilganda balandlik faqat KAMAYADI — shuni butunlay e'tiborsiz
 * qoldiramiz. Balandlik OSHGANDA esa (ekran aylantirilganda yoki klaviatura
 * yopilganda) qiymatni yangilaymiz — shunda haqiqiy o'lcham o'zgarishlari
 * (masalan portrait/landscape) baribir to'g'ri ishlaydi.
 *
 * Klaviatura ochiq holda SCROLL qilinganda ba'zi mobil brauzerlarda manzil
 * paneli vaqtincha yashirinib, `window.innerHeight` bir zumga haqiqiydan
 * kattaroq qiymat berishi mumkin — shu "oshish" haqiqiy deb qabul qilinsa,
 * balandlik noto'g'ri qulflanib, panel o'z joyidan siljib qoladi. Shuning
 * uchun scroll davom etayotganda balandlik oshishini e'tiborsiz qoldiramiz —
 * faqat scroll to'xtagandan keyin (va klaviatura ham yopiq bo'lsa) haqiqiy
 * oshishlarni qabul qilamiz.
 */
export function lockAppShellHeight(): () => void {
  if (typeof window === "undefined") return () => {};

  let maxHeight = window.innerHeight;
  let scrolling = false;
  let scrollEndTimer: ReturnType<typeof setTimeout> | null = null;

  function apply(height: number) {
    document.documentElement.style.setProperty("--app-shell-height", `${height}px`);
  }

  apply(maxHeight);

  function handleResize() {
    if (scrolling) return;
    if (window.innerHeight > maxHeight) {
      maxHeight = window.innerHeight;
      apply(maxHeight);
    }
  }

  function handleScroll() {
    scrolling = true;
    if (scrollEndTimer) clearTimeout(scrollEndTimer);
    scrollEndTimer = setTimeout(() => {
      scrolling = false;
      handleResize();
    }, 150);
  }

  window.addEventListener("resize", handleResize);
  window.addEventListener("scroll", handleScroll, { capture: true, passive: true });
  return () => {
    window.removeEventListener("resize", handleResize);
    window.removeEventListener("scroll", handleScroll, { capture: true });
    if (scrollEndTimer) clearTimeout(scrollEndTimer);
  };
}
