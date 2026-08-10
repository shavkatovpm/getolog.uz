"use client";

import { useMemo, useRef, useState } from "react";
import { GrowthSeries } from "@/lib/growth";

const UZ_MONTHS_SHORT = [
  "yan",
  "fev",
  "mar",
  "apr",
  "may",
  "iyn",
  "iyl",
  "avg",
  "sen",
  "okt",
  "noy",
  "dek",
];

function shortLabel(isoDate: string): string {
  const [, m, d] = isoDate.split("-").map(Number);
  return `${d}-${UZ_MONTHS_SHORT[m - 1]}`;
}

const WIDTH = 600;
const HEIGHT = 180;
const PAD_TOP = 16;
const PAD_BOTTOM = 24;
const PAD_X = 4;

export function GrowthChart({ series }: { series: GrowthSeries }) {
  const { points } = series;
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const maxValue = Math.max(1, ...points.map((p) => p.cumulative));
  const minValue = Math.min(...points.map((p) => p.cumulative));
  const plotTop = PAD_TOP;
  const plotBottom = HEIGHT - PAD_BOTTOM;
  const plotHeight = plotBottom - plotTop;
  const plotLeft = PAD_X;
  const plotRight = WIDTH - PAD_X;
  const plotWidth = plotRight - plotLeft;

  function xFor(i: number) {
    if (points.length <= 1) return plotLeft;
    return plotLeft + (i / (points.length - 1)) * plotWidth;
  }
  function yFor(value: number) {
    if (maxValue === minValue) return plotBottom;
    return plotBottom - ((value - minValue) / (maxValue - minValue)) * plotHeight;
  }

  const linePath = useMemo(
    () => points.map((p, i) => `${i === 0 ? "M" : "L"}${xFor(i).toFixed(2)},${yFor(p.cumulative).toFixed(2)}`).join(" "),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [points, maxValue, minValue]
  );
  const areaPath = `${linePath} L${xFor(points.length - 1).toFixed(2)},${plotBottom} L${xFor(0).toFixed(2)},${plotBottom} Z`;

  function handlePointerMove(e: React.PointerEvent<SVGSVGElement>) {
    const svg = svgRef.current;
    if (!svg || points.length === 0) return;
    const rect = svg.getBoundingClientRect();
    const relX = ((e.clientX - rect.left) / rect.width) * WIDTH;
    const ratio = (relX - plotLeft) / plotWidth;
    const idx = Math.round(ratio * (points.length - 1));
    setHoverIndex(Math.max(0, Math.min(points.length - 1, idx)));
  }

  const hovered = hoverIndex !== null ? points[hoverIndex] : null;
  const last = points[points.length - 1];

  // Label uchtasi: boshi, o'rtasi, oxiri — ortiqcha bandlik qilmasin.
  const labelIndices = points.length > 1 ? [0, Math.floor((points.length - 1) / 2), points.length - 1] : [0];

  return (
    <div className="relative">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="w-full touch-pan-y"
        onPointerMove={handlePointerMove}
        onPointerLeave={() => setHoverIndex(null)}
        role="img"
        aria-label={`Obunachilar o'sishi: ${series.startValue} dan ${series.endValue} gacha, ${series.windowDays} kun ichida`}
      >
        {/* Recessiv chegara chiziqlari: 0 va maksimum */}
        <line x1={plotLeft} y1={plotBottom} x2={plotRight} y2={plotBottom} stroke="var(--h-border)" strokeWidth={1} />
        {maxValue !== minValue && (
          <line x1={plotLeft} y1={plotTop} x2={plotRight} y2={plotTop} stroke="var(--h-border)" strokeWidth={1} />
        )}

        <path d={areaPath} fill="var(--h-accent)" opacity={0.1} stroke="none" />
        <path d={linePath} fill="none" stroke="var(--h-accent)" strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />

        {/* Oxirgi nuqta belgisi */}
        {last && (
          <circle
            cx={xFor(points.length - 1)}
            cy={yFor(last.cumulative)}
            r={4}
            fill="var(--h-accent)"
            stroke="var(--h-surface)"
            strokeWidth={2}
          />
        )}

        {/* Hover krossheyri */}
        {hovered && (
          <>
            <line
              x1={xFor(hoverIndex!)}
              y1={plotTop}
              x2={xFor(hoverIndex!)}
              y2={plotBottom}
              stroke="var(--h-muted)"
              strokeWidth={1}
              opacity={0.4}
            />
            <circle
              cx={xFor(hoverIndex!)}
              cy={yFor(hovered.cumulative)}
              r={4}
              fill="var(--h-accent)"
              stroke="var(--h-surface)"
              strokeWidth={2}
            />
          </>
        )}

        {/* X o'qi: chap, o'rta, o'ng sana */}
        {labelIndices.map((i) => (
          <text
            key={i}
            x={i === points.length - 1 ? xFor(i) - 2 : i === 0 ? xFor(i) + 2 : xFor(i)}
            y={HEIGHT - 6}
            fontSize={10}
            fill="var(--h-muted)"
            textAnchor={i === 0 ? "start" : i === points.length - 1 ? "end" : "middle"}
          >
            {shortLabel(points[i].date)}
          </text>
        ))}
      </svg>

      {hovered && hoverIndex !== null && (
        <div
          className="pointer-events-none absolute top-0 -translate-x-1/2 rounded-md border border-h-border bg-h-surface px-2.5 py-1.5 text-xs shadow-sm"
          style={{
            left: `${(xFor(hoverIndex) / WIDTH) * 100}%`,
            transform: `translateX(${hoverIndex === 0 ? "0%" : hoverIndex === points.length - 1 ? "-100%" : "-50%"})`,
          }}
        >
          <div className="font-medium text-h-ink">{hovered.cumulative} obunachi</div>
          <div className="text-h-muted">{shortLabel(hovered.date)}</div>
        </div>
      )}
    </div>
  );
}
