interface Props {
  size?: number;
}

/** GETOLOG logotipi — fonsiz, chiziq rangi joriy temaga (dark/light) mos keladi. */
export function LogoMark({ size = 32 }: Props) {
  return (
    <svg viewBox="0 0 2000 2000" width={size} height={size} fill="none">
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M563 563H1437V1437H563V563ZM693 693V1307H1307V693H693Z"
        fill="var(--h-ink)"
      />
    </svg>
  );
}
