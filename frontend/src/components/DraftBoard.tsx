"use client";

import { motion, AnimatePresence } from "motion/react";
import { RosterSlot, MAX_BUDGET, MAX_OVERSEAS, ROSTER_SIZE } from "@/types/draft";

// ─── Role styling ───────────────────────────────────────────────────

const ROLE_STYLE: Record<
  string,
  { bg: string; border: string; icon: string; label: string; text: string }
> = {
  WK: {
    bg: "bg-emerald-900/40",
    border: "border-emerald-500",
    text: "text-emerald-400",
    icon: "🧤",
    label: "WK",
  },
  WICKETKEEPER: {
    bg: "bg-emerald-900/40",
    border: "border-emerald-500",
    text: "text-emerald-400",
    icon: "🧤",
    label: "WK",
  },
  BAT: {
    bg: "bg-sky-900/40",
    border: "border-sky-500",
    text: "text-sky-400",
    icon: "🏏",
    label: "BAT",
  },
  BATSMAN: {
    bg: "bg-sky-900/40",
    border: "border-sky-500",
    text: "text-sky-400",
    icon: "🏏",
    label: "BAT",
  },
  BOWL: {
    bg: "bg-rose-900/40",
    border: "border-rose-500",
    text: "text-rose-400",
    icon: "🎯",
    label: "BOWL",
  },
  BOWLER: {
    bg: "bg-rose-900/40",
    border: "border-rose-500",
    text: "text-rose-400",
    icon: "🎯",
    label: "BOWL",
  },
  AR: {
    bg: "bg-purple-900/40",
    border: "border-purple-500",
    text: "text-purple-400",
    icon: "⚡",
    label: "AR",
  },
  ALLROUNDER: {
    bg: "bg-purple-900/40",
    border: "border-purple-500",
    text: "text-purple-400",
    icon: "⚡",
    label: "AR",
  },
};


// ─── Budget Bar ─────────────────────────────────────────────────────

function BudgetBar({ remaining }: { remaining: number }) {
  const pct = (remaining / MAX_BUDGET) * 100;
  const isLow = pct < 20;

  return (
    <div className="border-2 border-surface-border bg-surface p-4">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-heading font-bold uppercase tracking-widest text-text-secondary">
          BUDGET
        </span>
        <span
          className={`font-body text-xl font-black ${
            isLow ? "text-accent-red" : "text-accent-gold"
          }`}
        >
          {remaining}
          <span className="ml-1 text-sm font-heading font-normal opacity-50">
            CR
          </span>
        </span>
      </div>
      <div className="relative h-4 overflow-hidden bg-background border border-surface-border">
        <motion.div
          className={`absolute inset-y-0 left-0 border-r border-background ${
            isLow
              ? "bg-accent-red"
              : "bg-accent-gold"
          }`}
          animate={{ width: `${pct}%` }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
      </div>
    </div>
  );
}

// ─── DraftBoard ─────────────────────────────────────────────────────

interface DraftBoardProps {
  roster: RosterSlot[];
  budgetRemaining: number;
  overseasCount: number;
  picksCount: number;
}

export default function DraftBoard({
  roster,
  budgetRemaining,
  overseasCount,
  picksCount,
}: DraftBoardProps) {
  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-heading font-bold uppercase tracking-wider text-white">
            YOUR XI
          </h2>
          <p className="text-sm font-body text-text-secondary uppercase">
            {picksCount}/{ROSTER_SIZE} DRAFTED
          </p>
        </div>
        {/* Overseas counter */}
        <div className="flex items-center gap-2 border-2 border-surface-border bg-surface px-3 py-1.5">
          <span className="text-sm">🌍</span>
          <span
            className={`font-body text-lg font-bold ${
              overseasCount >= MAX_OVERSEAS ? "text-accent-red" : "text-white"
            }`}
          >
            {overseasCount}/{MAX_OVERSEAS}
          </span>
          <span className="text-sm font-heading text-text-muted">OS</span>
        </div>
      </div>

      {/* Budget */}
      <BudgetBar remaining={budgetRemaining} />

      {/* Roster Grid */}
      <div className="grid grid-cols-1 gap-2">
        {roster.map((slot, idx) => {
          const roleStyle = slot.requiredRole
            ? (ROLE_STYLE[slot.requiredRole] || ROLE_STYLE.AR)
            : null;

          return (
            <motion.div
              key={slot.index}
              layout
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.04 }}
              className={`
                group relative overflow-hidden border-2 p-3
                transition-all duration-200
                ${
                  slot.player
                    ? "border-surface-border bg-surface"
                    : `border-dashed ${
                        roleStyle?.border || "border-surface-border"
                      } ${
                        roleStyle?.bg || "bg-background"
                      }`
                }
              `}
            >
              <AnimatePresence mode="wait">
                {slot.player ? (
                  <motion.div
                    key="filled"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    className="flex items-center gap-3"
                  >
                    {/* Role icon */}
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center border-2 border-surface-border bg-background text-sm">
                      {roleStyle?.icon || "🌟"}
                    </div>
                    {/* Player info */}
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-lg font-heading font-bold text-white uppercase tracking-wide">
                        {slot.player.name}
                      </p>
                      <div className="flex items-center gap-2">
                        <span
                          className={`text-xs font-heading font-bold uppercase ${
                            roleStyle
                              ? roleStyle.text
                              : "text-text-secondary"
                          }`}
                        >
                          {slot.player.role}
                        </span>
                        {slot.player.is_overseas && (
                          <span className="text-xs font-heading font-bold text-accent-gold">
                            OS
                          </span>
                        )}
                      </div>
                    </div>
                    {/* Cost */}
                    <span className="font-body text-lg font-bold text-accent-gold">
                      {slot.player.credit_cost}
                    </span>
                  </motion.div>
                ) : (
                  <motion.div
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center gap-3"
                  >
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center border-2 border-dashed border-surface-border text-sm text-text-muted">
                      {roleStyle?.icon || "?"}
                    </div>
                    <span className="text-sm font-heading uppercase text-text-muted">{slot.label}</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
