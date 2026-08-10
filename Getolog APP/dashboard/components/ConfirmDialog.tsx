"use client";

import { useEffect } from "react";

interface Props {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  confirming?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

/** `window.confirm()` o'rniga — dizaynga mos, tema (dark/light)ga moslashadigan
 * modal tasdiqlash oynasi. Yopish: fon bosilganda, Escape tugmasida yoki
 * "Bekor qilish"da. */
export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "O'chirish",
  cancelLabel = "Bekor qilish",
  confirming = false,
  onConfirm,
  onCancel,
}: Props) {
  useEffect(() => {
    if (!open) return;
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onCancel();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        aria-label="Yopish"
        onClick={onCancel}
        className="animate-modal-backdrop absolute inset-0 bg-black/50"
      />
      <div className="animate-modal-panel relative w-full max-w-sm rounded-lg border border-h-border bg-h-surface p-5 shadow-xl">
        <h2 className="mb-2 text-sm font-medium text-h-ink">{title}</h2>
        <p className="mb-5 text-sm text-h-muted">{message}</p>
        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md px-3 py-1.5 text-sm text-h-muted transition-colors hover:bg-h-bg"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={confirming}
            className="rounded-md bg-h-danger px-3 py-1.5 text-sm text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {confirming ? "..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
