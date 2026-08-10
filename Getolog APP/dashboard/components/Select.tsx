"use client";

import { Children, isValidElement, useEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { ChevronDown, Check } from "lucide-react";

interface Props {
  value?: string | number;
  onChange?: (e: { target: { value: string } }) => void;
  children?: ReactNode;
  className?: string;
  /** Tashqi (wrapping) div'ga qo'llanadi — masalan `sm:hidden` bilan butun
   * select'ni responsiv yashirish uchun. */
  wrapperClassName?: string;
  "aria-label"?: string;
  disabled?: boolean;
}

interface ParsedOption {
  key: string | number;
  value: string;
  label: ReactNode;
}

function parseOptions(children: ReactNode): ParsedOption[] {
  return Children.toArray(children).flatMap((child) => {
    if (isValidElement<{ value?: string | number; children?: ReactNode }>(child) && child.props.value !== undefined) {
      const value = String(child.props.value);
      return [{ value, label: child.props.children, key: child.key ?? value }];
    }
    return [];
  });
}

/** Bosilganda ochiladigan, chapida tanlangan qatorni urg'ulaydigan rangli
 * chiziq bilan ko'rsatiladigan custom dropdown (brauzerning o'z native
 * select ochilish oynasi stillashtirilmaydi, shuning uchun to'liq custom).
 * Paneli `document.body`ga portal qilinadi — aks holda `overflow-x-auto`
 * kabi bitta o'qli scroll cheklovi bo'lgan ota-element (CSS qoidasiga ko'ra
 * ikkinchi o'qni ham avtomatik "auto" qilib, kesib tashlaydi) panelni
 * ko'rinmas holga keltirib qo'yishi mumkin edi. */
export function Select({
  className = "",
  wrapperClassName = "",
  value,
  onChange,
  children,
  "aria-label": ariaLabel,
  disabled,
}: Props) {
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [rect, setRect] = useState<{ top: number; left: number; width: number } | null>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const options = parseOptions(children);
  const selected = options.find((o) => o.value === String(value));

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!open) return;
    function close() {
      setOpen(false);
    }
    window.addEventListener("scroll", close, { capture: true, passive: true });
    window.addEventListener("resize", close);
    return () => {
      window.removeEventListener("scroll", close, { capture: true });
      window.removeEventListener("resize", close);
    };
  }, [open]);

  function handleOpen() {
    const r = triggerRef.current?.getBoundingClientRect();
    if (r) setRect({ top: r.bottom + 6, left: r.left, width: r.width });
    setOpen(true);
  }

  return (
    <div className={`relative inline-block ${wrapperClassName}`}>
      <button
        ref={triggerRef}
        type="button"
        aria-label={ariaLabel}
        disabled={disabled}
        onClick={() => (open ? setOpen(false) : handleOpen())}
        className={`flex items-center justify-between gap-1.5 rounded-md border border-h-border bg-h-surface pr-2 pl-3 text-h-ink disabled:opacity-40 ${className}`}
      >
        <span className="truncate">{selected?.label ?? ""}</span>
        <ChevronDown size={14} strokeWidth={2} className="flex-shrink-0 text-h-muted" />
      </button>

      {open &&
        mounted &&
        rect &&
        createPortal(
          <>
            <button
              type="button"
              aria-label="Yopish"
              className="fixed inset-0 z-30 cursor-default"
              onClick={() => setOpen(false)}
            />
            <div
              className="dd-v4-panel fixed z-40 rounded-md border border-h-border bg-h-surface py-1 shadow-lg"
              style={{ top: rect.top, left: rect.left, minWidth: rect.width }}
            >
              {options.map((opt) => {
                const isSelected = opt.value === selected?.value;
                return (
                  <button
                    key={opt.key}
                    type="button"
                    onClick={() => {
                      onChange?.({ target: { value: opt.value } });
                      setOpen(false);
                    }}
                    className={`flex w-full items-center justify-between gap-3 whitespace-nowrap border-l-2 px-3 py-2 text-left text-sm transition-colors ${
                      isSelected
                        ? "border-h-accent bg-h-accent/5 font-medium text-h-accent"
                        : "border-transparent text-h-ink hover:bg-h-bg"
                    }`}
                  >
                    {opt.label}
                    {isSelected && <Check size={14} strokeWidth={2} className="flex-shrink-0" />}
                  </button>
                );
              })}
            </div>
          </>,
          document.body,
        )}
    </div>
  );
}
