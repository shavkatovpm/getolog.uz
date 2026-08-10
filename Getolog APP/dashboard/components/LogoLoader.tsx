interface Props {
  size?: number;
  /** Bitta aylanish davomiyligi (ms). Debug uchun sekinlashtirishga qulay. */
  speedMs?: number;
}

/** GETOLOG logotipi — 4 tomon parallel chiziladi, so'ng ortidan (boshidan) o'chib boradi. */
export function LogoLoader({ size = 64, speedMs = 2400 }: Props) {
  const style = { animationDuration: `${speedMs}ms` };
  return (
    <svg viewBox="0 0 200 200" width={size} height={size}>
      {/* chap: pastdan tepaga */}
      <line x1="60" y1="140" x2="60" y2="60" pathLength={1} strokeDasharray="1" strokeWidth="10" strokeLinecap="square" stroke="var(--h-ink)" className="animate-logo-build" style={style} />
      {/* o'ng: tepadan pastga */}
      <line x1="140" y1="60" x2="140" y2="140" pathLength={1} strokeDasharray="1" strokeWidth="10" strokeLinecap="square" stroke="var(--h-ink)" className="animate-logo-build" style={style} />
      {/* tepa: chapdan o'ngga */}
      <line x1="60" y1="60" x2="140" y2="60" pathLength={1} strokeDasharray="1" strokeWidth="10" strokeLinecap="square" stroke="var(--h-ink)" className="animate-logo-build" style={style} />
      {/* past: o'ngdan chapga */}
      <line x1="140" y1="140" x2="60" y2="140" pathLength={1} strokeDasharray="1" strokeWidth="10" strokeLinecap="square" stroke="var(--h-ink)" className="animate-logo-build" style={style} />
    </svg>
  );
}
