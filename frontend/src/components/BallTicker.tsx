"use client";

import { useRef, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import type { BallEvent } from "@/types/league";

// ─── Ball outcome styling ───────────────────────────────────────────

interface BallStyle {
  bg: string;
  text: string;
  label: string;
  glow?: string;
}

function getBallStyle(event: BallEvent): BallStyle {
  if (event.wicket_type) {
    return {
      bg: "bg-red-500",
      text: "text-white font-black",
      label: "W",
      glow: "shadow-[0_0_12px_rgba(239,68,68,0.6)]",
    };
  }
  if (event.extras > 0) {
    return {
      bg: "bg-orange-500",
      text: "text-white font-bold",
      label: `${event.runs_scored + event.extras}`,
    };
  }
  switch (event.runs_scored) {
    case 0:
      return {
        bg: "bg-zinc-600",
        text: "text-zinc-300",
        label: "•",
      };
    case 1:
      return {
        bg: "bg-zinc-400",
        text: "text-zinc-900 font-semibold",
        label: "1",
      };
    case 2:
      return {
        bg: "bg-emerald-500",
        text: "text-white font-bold",
        label: "2",
      };
    case 3:
      return {
        bg: "bg-emerald-400",
        text: "text-white font-bold",
        label: "3",
      };
    case 4:
      return {
        bg: "bg-blue-500",
        text: "text-white font-black",
        label: "4",
        glow: "shadow-[0_0_10px_rgba(59,130,246,0.5)]",
      };
    case 6:
      return {
        bg: "bg-purple-500",
        text: "text-white font-black",
        label: "6",
        glow: "shadow-[0_0_14px_rgba(168,85,247,0.6)]",
      };
    default:
      return {
        bg: "bg-zinc-500",
        text: "text-white font-semibold",
        label: `${event.runs_scored}`,
      };
  }
}

// ─── Group events by over ───────────────────────────────────────────

function groupByOver(events: BallEvent[]): Map<number, BallEvent[]> {
  const overs = new Map<number, BallEvent[]>();
  for (const e of events) {
    const existing = overs.get(e.over_number) || [];
    existing.push(e);
    overs.set(e.over_number, existing);
  }
  return overs;
}

// ─── Ball Dot Component ─────────────────────────────────────────────

function BallDot({
  event,
  index,
}: {
  event: BallEvent;
  index: number;
}) {
  const style = getBallStyle(event);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{
        type: "spring",
        stiffness: 500,
        damping: 25,
        delay: index * 0.03,
      }}
      className="relative flex-shrink-0"
    >
      <div
        className={`
          flex h-8 w-8 items-center justify-center rounded-full
          ${style.bg} ${style.text} ${style.glow || ""}
          text-xs transition-transform hover:scale-110
        `}
        title={`Over ${event.over_number}, Ball ${event.ball_number}${
          event.wicket_type ? ` — ${event.wicket_type}` : ""
        }`}
      >
        {style.label}
      </div>

      {/* Wicket indicator pulse */}
      {event.wicket_type && (
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-red-400"
          initial={{ scale: 1, opacity: 0.8 }}
          animate={{ scale: 1.6, opacity: 0 }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      )}
    </motion.div>
  );
}

// ─── Legend ──────────────────────────────────────────────────────────

function TickerLegend() {
  const items = [
    { color: "bg-zinc-600", label: "Dot" },
    { color: "bg-zinc-400", label: "1" },
    { color: "bg-emerald-500", label: "2/3" },
    { color: "bg-blue-500", label: "4" },
    { color: "bg-purple-500", label: "6" },
    { color: "bg-red-500", label: "W" },
    { color: "bg-orange-500", label: "Extras" },
  ];

  return (
    <div className="flex flex-wrap items-center gap-3 text-[10px] text-zinc-500">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-1">
          <div className={`h-2.5 w-2.5 rounded-full ${item.color}`} />
          <span>{item.label}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Over Summary ───────────────────────────────────────────────────

function OverSummary({ balls }: { balls: BallEvent[] }) {
  const runs = balls.reduce((s, b) => s + b.runs_scored + b.extras, 0);
  const wickets = balls.filter((b) => b.wicket_type).length;

  return (
    <div className="flex flex-col items-center gap-0.5 px-1">
      <span className="text-[10px] font-bold text-accent-gold">{runs}</span>
      {wickets > 0 && (
        <span className="text-[9px] font-semibold text-red-400">
          {wickets}W
        </span>
      )}
    </div>
  );
}

// ─── BallTicker Component ───────────────────────────────────────────

interface BallTickerProps {
  events: BallEvent[];
  compact?: boolean;
}

export default function BallTicker({ events, compact = false }: BallTickerProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const overs = groupByOver(events);

  // Auto-scroll to the latest ball
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollLeft = scrollRef.current.scrollWidth;
    }
  }, [events.length]);

  if (events.length === 0) {
    return (
      <div className="flex items-center justify-center rounded-xl border border-white/8 bg-white/[0.02] p-6">
        <span className="text-sm text-zinc-500">
          No ball-by-ball data available
        </span>
      </div>
    );
  }

  const sortedOvers = Array.from(overs.entries()).sort(
    ([a], [b]) => a - b
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-3"
    >
      {/* Header */}
      {!compact && (
        <div className="flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm font-bold text-white">
            <span className="inline-block h-2 w-2 rounded-full bg-accent-gold animate-pulse" />
            Ball-by-Ball
          </h3>
          <TickerLegend />
        </div>
      )}

      {/* Scrollable ticker */}
      <div
        ref={scrollRef}
        className="ball-ticker-scroll overflow-x-auto overflow-y-hidden rounded-xl border border-white/8 bg-white/[0.02] p-3"
      >
        <div className="flex items-center gap-1 min-w-max">
          <AnimatePresence mode="popLayout">
            {sortedOvers.map(([overNum, balls], overIdx) => (
              <div key={overNum} className="flex items-center gap-1">
                {/* Over number label */}
                <div className="flex flex-col items-center px-1.5">
                  <span className="text-[9px] font-semibold uppercase tracking-wider text-zinc-500">
                    OV
                  </span>
                  <span className="text-xs font-bold text-accent-gold">
                    {overNum}
                  </span>
                </div>

                {/* Balls in this over */}
                {balls.map((event, ballIdx) => (
                  <BallDot
                    key={`${overNum}-${event.ball_number}`}
                    event={event}
                    index={overIdx * 6 + ballIdx}
                  />
                ))}

                {/* Over summary */}
                <OverSummary balls={balls} />

                {/* Over separator */}
                {overIdx < sortedOvers.length - 1 && (
                  <div className="mx-1 h-8 w-px bg-white/10" />
                )}
              </div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Summary stats */}
      {!compact && (
        <div className="flex items-center gap-4 text-xs text-zinc-400">
          <span>
            Total: <strong className="text-white">{events.reduce((s, e) => s + e.runs_scored + e.extras, 0)}</strong> runs
          </span>
          <span>
            Wickets: <strong className="text-red-400">{events.filter((e) => e.wicket_type).length}</strong>
          </span>
          <span>
            Boundaries: <strong className="text-blue-400">
              {events.filter((e) => e.runs_scored === 4).length}×4
            </strong>{" "}
            <strong className="text-purple-400">
              {events.filter((e) => e.runs_scored === 6).length}×6
            </strong>
          </span>
        </div>
      )}
    </motion.div>
  );
}
