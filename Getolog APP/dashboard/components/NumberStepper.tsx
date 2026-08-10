"use client";

import { Minus, Plus } from "lucide-react";

interface Props {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  suffix?: string;
}

function clamp(v: number, min?: number, max?: number) {
  let n = v;
  if (min != null) n = Math.max(min, n);
  if (max != null) n = Math.min(max, n);
  return n;
}

/** Native `<input type="number">` strelkalari brauzerlararo notekis va kichkina
 * ko'rinadi — shuning uchun o'zimizning +/- tugmali stepper. */
export function NumberStepper({ value, onChange, min, max, step = 1, suffix }: Props) {
  return (
    <div className="inline-flex items-center rounded-md border border-h-border bg-h-surface">
      <button
        type="button"
        onClick={() => onChange(clamp(value - step, min, max))}
        disabled={min != null && value <= min}
        aria-label="Kamaytirish"
        className="flex h-8 w-8 flex-shrink-0 items-center justify-center text-h-muted transition-colors hover:text-h-ink disabled:opacity-30 disabled:hover:text-h-muted"
      >
        <Minus size={14} strokeWidth={2.5} />
      </button>
      <input
        type="number"
        inputMode="numeric"
        value={value}
        onChange={(e) => {
          const n = Number(e.target.value);
          if (!Number.isNaN(n)) onChange(clamp(n, min, max));
        }}
        className="w-9 border-x border-h-border bg-transparent py-1 text-center text-sm text-h-ink [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
      />
      <button
        type="button"
        onClick={() => onChange(clamp(value + step, min, max))}
        disabled={max != null && value >= max}
        aria-label="Ko'paytirish"
        className="flex h-8 w-8 flex-shrink-0 items-center justify-center text-h-muted transition-colors hover:text-h-ink disabled:opacity-30 disabled:hover:text-h-muted"
      >
        <Plus size={14} strokeWidth={2.5} />
      </button>
      {suffix && <span className="pr-3 pl-1.5 text-sm text-h-muted">{suffix}</span>}
    </div>
  );
}
