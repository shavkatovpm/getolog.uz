"use client";

interface Props {
  /** Faqat raqamlardan iborat xom qiymat (masalan "12000") — vergul bu yerda
   * saqlanmaydi, faqat ko'rsatishda qo'shiladi. */
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

function formatWithCommas(digits: string): string {
  if (!digits) return "";
  return digits.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/** Faqat raqam kiritishga ruxsat beradi (harflar/belgilar avtomatik olib
 * tashlanadi) va minglik xonalarni vergul bilan ajratib ko'rsatadi
 * (12000 -> 12,000) — narx kiritishda o'qish osonroq bo'lishi uchun. */
export function CurrencyInput({ value, onChange, placeholder, className = "" }: Props) {
  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    onChange(e.target.value.replace(/\D/g, ""));
  }

  return (
    <div className={`flex items-center rounded-md border border-h-border bg-h-surface px-2 ${className}`}>
      <input
        type="text"
        inputMode="numeric"
        value={formatWithCommas(value)}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full min-w-0 bg-transparent py-1 text-h-ink placeholder:text-h-muted focus:outline-none"
      />
      <span className="flex-shrink-0 pl-1.5 text-sm text-h-muted">so&apos;m</span>
    </div>
  );
}
