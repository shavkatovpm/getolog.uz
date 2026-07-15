"use client";

import { useState } from "react";
import { apiFetchBlobUrl } from "@/lib/api";

export function ReceiptImage({ paymentId }: { paymentId: number }) {
  const [url, setUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (url) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={url} alt="To'lov cheki" className="mt-2 max-h-64 rounded border" />;
  }

  return (
    <button
      onClick={async () => {
        setLoading(true);
        try {
          setUrl(await apiFetchBlobUrl(`/api/payments/${paymentId}/receipt`));
        } finally {
          setLoading(false);
        }
      }}
      disabled={loading}
      className="text-sm text-blue-600 underline disabled:opacity-50"
    >
      {loading ? "Yuklanmoqda..." : "Chekni ko'rish"}
    </button>
  );
}
