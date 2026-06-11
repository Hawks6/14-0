"use client";

import { motion } from "motion/react";
import type { LeagueMatch } from "@/types/league";

// ─── Match result badge ─────────────────────────────────────────────

function ResultBadge({ winner }: { winner: LeagueMatch["winner"] }) {
  if (!winner) return null;

  const config = {
    user: {
      label: "W",
      border: "border-emerald-500/40",
      bg: "bg-emerald-500/15",
      text: "text-emerald-400",
    },
    opponent: {
      label: "L",
      border: "border-red-500/40",
      bg: "bg-red-500/15",
      text: "text-red-400",
    },
    tie: {
      label: "T",
      border: "border-zinc-500/40",
      bg: "bg-zinc-500/15",
      text: "text-zinc-400",
    },
  };

  const c = config[winner];

  return (
    <div
      className={`flex h-8 w-8 items-center justify-center rounded-lg border ${c.border} ${c.bg}`}
    >
      <span className={`text-sm font-black ${c.text}`}>{c.label}</span>
    </div>
  );
}

// ─── Match number indicator ─────────────────────────────────────────

function MatchNumber({ num, winner }: { num: number; winner: LeagueMatch["winner"] }) {
  const borderColor =
    winner === "user"
      ? "border-emerald-500/30 bg-emerald-500/5"
      : winner === "opponent"
      ? "border-red-500/30 bg-red-500/5"
      : "border-white/10 bg-white/[0.02]";

  return (
    <div
      className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl border ${borderColor}`}
    >
      <span className="text-sm font-black text-zinc-300">
        #{num}
      </span>
    </div>
  );
}

// ─── Score line ─────────────────────────────────────────────────────

function ScoreLine({
  label,
  score,
  wickets,
  overs,
  isUser,
  highlight,
}: {
  label: string;
  score: number;
  wickets: number;
  overs?: number;
  isUser: boolean;
  highlight: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <span
        className={`text-[11px] font-semibold uppercase tracking-wider ${
          isUser ? "text-accent-gold" : "text-zinc-500"
        }`}
      >
        {label}
      </span>
      <div className="flex items-baseline gap-0.5">
        <span
          className={`text-sm font-black tabular-nums ${
            highlight ? "text-emerald-400" : "text-white"
          }`}
        >
          {score}/{wickets}
        </span>
        {overs !== undefined && (
          <span className="ml-1 text-[10px] text-zinc-500">
            ({overs} ov)
          </span>
        )}
      </div>
    </div>
  );
}

// ─── MatchCard Component ────────────────────────────────────────────

interface MatchCardProps {
  match: LeagueMatch;
  onSelect: (match: LeagueMatch) => void;
  index: number;
}

export default function MatchCard({ match, onSelect, index }: MatchCardProps) {
  const isWin = match.winner === "user";
  const isLoss = match.winner === "opponent";
  const isCompleted = match.status === "completed";

  const accentBorder = isWin
    ? "border-emerald-500/20 hover:border-emerald-500/40"
    : isLoss
    ? "border-red-500/20 hover:border-red-500/40"
    : "border-white/8 hover:border-white/15";

  return (
    <motion.button
      id={`match-card-${match.match_number}`}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        type: "spring",
        stiffness: 400,
        damping: 30,
        delay: index * 0.04,
      }}
      whileHover={{ y: -3, scale: 1.01 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect(match)}
      className={`
        group relative w-full overflow-hidden rounded-xl border
        bg-white/[0.02] p-4 text-left transition-colors
        ${accentBorder}
      `}
    >
      {/* Win/Loss accent line at top */}
      {isCompleted && (
        <div
          className={`absolute inset-x-0 top-0 h-0.5 ${
            isWin
              ? "bg-gradient-to-r from-emerald-500 via-green-400 to-emerald-500"
              : isLoss
              ? "bg-gradient-to-r from-red-500 via-rose-400 to-red-500"
              : "bg-gradient-to-r from-zinc-500 via-zinc-400 to-zinc-500"
          }`}
        />
      )}

      {/* Content */}
      <div className="flex items-start gap-3">
        <MatchNumber num={match.match_number} winner={match.winner} />

        <div className="min-w-0 flex-1 space-y-1.5">
          <ScoreLine
            label={match.user_team || "Your XI"}
            score={match.user_score}
            wickets={match.user_wickets}
            overs={match.user_overs}
            isUser={true}
            highlight={isWin}
          />
          <ScoreLine
            label={match.opponent_team || "Opponent"}
            score={match.opponent_score}
            wickets={match.opponent_wickets}
            overs={match.opponent_overs}
            isUser={false}
            highlight={isLoss}
          />
        </div>

        <ResultBadge winner={match.winner} />
      </div>

      {/* Match status */}
      {!isCompleted && (
        <div className="mt-2 flex items-center gap-1.5">
          <motion.div
            className="h-1.5 w-1.5 rounded-full bg-amber-400"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          <span className="text-[10px] font-semibold uppercase tracking-wider text-amber-400">
            {match.status === "in_progress" ? "In Progress" : "Scheduled"}
          </span>
        </div>
      )}

      {/* Hover shine effect */}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
    </motion.button>
  );
}
