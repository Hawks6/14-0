"use client";

import { motion, AnimatePresence } from "motion/react";
import { RosterSlot, PlayerRole, MAX_BUDGET, MAX_OVERSEAS, ROSTER_SIZE } from "@/types/draft";

// ─── Role styling ───────────────────────────────────────────────────

const ROLE_STYLE: Record<
  PlayerRole,
  { gradient: string; border: string; icon: string; label: string }
> = {
  WK: {
    gradient: "from-emerald-500/20 to-emerald-800/10",
    border: "border-emerald-500/20",
    icon: "🧤",
    label: "WK",
  },
  BAT: {
    gradient: "from-sky-500/20 to-sky-800/10",
    border: "border-sky-500/20",
    icon: "🏏",
    label: "BAT",
  },
  BOWL: {
    gradient: "from-rose-500/20 to-rose-800/10",
    border: "border-rose-500/20",
    icon: "🎯",
    label: "BOWL",
  },
  AR: {
    gradient: "from-purple-500/20 to-purple-800/10",
    border: "border-purple-500/20",
    icon: "⚡",
    label: "AR",
  },
};

// ─── Budget Bar ─────────────────────────────────────────────────────

function BudgetBar({ remaining }: { remaining: number }) {
  const pct = (remaining / MAX_BUDGET) * 100;
  const isLow = pct < 20;

  return (
    <div className="rounded-xl border border-white/8 bg-white/[0.03] p-4">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">
          💰 Budget
        </span>
        <span
          className={`font-mono text-lg font-black ${
            isLow ? "text-rose-400" : "text-amber-400"
          }`}
        >
          {remaining}
          <span className="ml-0.5 text-xs font-normal text-amber-400/50">
            / {MAX_BUDGET}
          </span>
        </span>
      </div>
      <div className="relative h-2 overflow-hidden rounded-full bg-white/5">
        <motion.div
          className={`absolute inset-y-0 left-0 rounded-full ${
            isLow
              ? "bg-gradient-to-r from-rose-500 to-red-400"
              : "bg-gradient-to-r from-amber-500 to-yellow-400"
          }`}
          animate={{ width: `${pct}%` }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
        {/* Shine */}
        <div className="absolute inset-0 bg-gradient-to-b from-white/10 to-transparent" />
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
          <h2 className="text-sm font-bold uppercase tracking-wider text-white">
            Your XI
          </h2>
          <p className="text-[11px] text-zinc-500">
            {picksCount}/{ROSTER_SIZE} players drafted
          </p>
        </div>
        {/* Overseas counter */}
        <div className="flex items-center gap-2 rounded-lg border border-white/8 bg-white/[0.03] px-3 py-1.5">
          <span className="text-xs">🌍</span>
          <span
            className={`font-mono text-sm font-bold ${
              overseasCount >= MAX_OVERSEAS ? "text-rose-400" : "text-zinc-300"
            }`}
          >
            {overseasCount}/{MAX_OVERSEAS}
          </span>
          <span className="text-[10px] text-zinc-600">OS</span>
        </div>
      </div>

      {/* Budget */}
      <BudgetBar remaining={budgetRemaining} />

      {/* Roster Grid */}
      <div className="grid grid-cols-1 gap-2">
        {roster.map((slot, idx) => {
          const roleStyle = slot.requiredRole
            ? ROLE_STYLE[slot.requiredRole]
            : null;

          return (
            <motion.div
              key={slot.index}
              layout
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.04 }}
              className={`
                group relative overflow-hidden rounded-lg border p-3
                transition-all duration-200
                ${
                  slot.player
                    ? "border-white/10 bg-white/[0.04]"
                    : `border-dashed ${
                        roleStyle?.border || "border-white/8"
                      } bg-gradient-to-r ${
                        roleStyle?.gradient || "from-white/[0.02] to-transparent"
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
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/5 text-sm">
                      {roleStyle?.icon || "🌟"}
                    </div>
                    {/* Player info */}
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold text-white">
                        {slot.player.name}
                      </p>
                      <div className="flex items-center gap-2">
                        <span
                          className={`text-[10px] font-semibold ${
                            roleStyle
                              ? roleStyle.border.replace("border-", "text-").replace("/20", "")
                              : "text-zinc-400"
                          }`}
                        >
                          {slot.player.role}
                        </span>
                        {slot.player.is_overseas && (
                          <span className="text-[9px] font-bold text-amber-500/70">
                            OS
                          </span>
                        )}
                      </div>
                    </div>
                    {/* Cost */}
                    <span className="font-mono text-xs font-bold text-amber-400/80">
                      {slot.player.credit_cost}cr
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
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-dashed border-white/10 text-sm text-zinc-600">
                      {roleStyle?.icon || "?"}
                    </div>
                    <span className="text-xs text-zinc-600">{slot.label}</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>

      {/* Progress ring */}
      <div className="flex items-center justify-center pt-2">
        <div className="relative h-16 w-16">
          <svg viewBox="0 0 36 36" className="h-16 w-16 -rotate-90">
            <circle
              cx="18"
              cy="18"
              r="15.5"
              fill="none"
              stroke="rgba(255,255,255,0.05)"
              strokeWidth="2"
            />
            <motion.circle
              cx="18"
              cy="18"
              r="15.5"
              fill="none"
              stroke="url(#progress-grad)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeDasharray="97.4"
              animate={{
                strokeDashoffset: 97.4 - (picksCount / ROSTER_SIZE) * 97.4,
              }}
              transition={{ type: "spring", stiffness: 100, damping: 20 }}
            />
            <defs>
              <linearGradient id="progress-grad">
                <stop offset="0%" stopColor="#f59e0b" />
                <stop offset="100%" stopColor="#eab308" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="font-mono text-sm font-black text-white">
              {picksCount}
              <span className="text-[10px] text-zinc-500">/{ROSTER_SIZE}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
