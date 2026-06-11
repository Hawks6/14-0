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
      bg: "bg-emerald-500/20",
      text: "text-emerald-400",
      glow: "shadow-[0_0_12px_rgba(52,211,153,0.3)]",
    },
    opponent: {
      label: "L",
      border: "border-red-500/40",
      bg: "bg-red-500/20",
      text: "text-red-400",
      glow: "shadow-[0_0_12px_rgba(239,68,68,0.3)]",
    },
    tie: {
      label: "T",
      border: "border-zinc-500/40",
      bg: "bg-zinc-500/15",
      text: "text-zinc-400",
      glow: "",
    },
  };

  const c = config[winner];

  return (
    <div
      className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg border ${c.border} ${c.bg} ${c.glow}`}
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
      className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg border ${borderColor}`}
    >
      <span className="text-xs font-black text-zinc-400">
        #{num}
      </span>
    </div>
  );
}

// ─── Team row ───────────────────────────────────────────────────────

function TeamRow({
  name,
  score,
  wickets,
  overs,
  isUser,
  isWinner,
}: {
  name: string;
  score: number;
  wickets: number;
  overs?: number;
  isUser: boolean;
  isWinner: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-2">
      {/* Team identity */}
      <div className="flex min-w-0 items-center gap-1.5">
        {/* Color dot */}
        <div
          className={`h-1.5 w-1.5 flex-shrink-0 rounded-full ${
            isUser ? "bg-amber-400" : "bg-zinc-500"
          }`}
        />
        {/* Team name */}
        <span
          className={`truncate text-[11px] font-bold leading-tight ${
            isUser
              ? "text-amber-300"
              : isWinner
              ? "text-white"
              : "text-zinc-400"
          }`}
          title={name}
        >
          {name}
        </span>
      </div>

      {/* Score */}
      <div className="flex flex-shrink-0 items-baseline gap-1">
        <span
          className={`text-sm font-black tabular-nums ${
            isWinner ? "text-emerald-400" : isUser ? "text-white" : "text-zinc-300"
          }`}
        >
          {score}/{wickets}
        </span>
        {overs !== undefined && (
          <span className="text-[9px] text-zinc-600">({overs}ov)</span>
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
    ? "border-emerald-500/20 hover:border-emerald-500/50"
    : isLoss
    ? "border-red-500/20 hover:border-red-500/50"
    : "border-white/8 hover:border-white/20";

  const userTeamName = match.user_team || "Your XI";
  const opponentTeamName = match.opponent_team || "Opponent";

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
      whileHover={{ y: -3, scale: 1.015 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect(match)}
      className={`
        group relative w-full overflow-hidden rounded-xl border
        bg-white/[0.02] p-3.5 text-left transition-all duration-200
        ${accentBorder}
      `}
    >
      {/* Win/Loss accent line at top */}
      {isCompleted && (
        <div
          className={`absolute inset-x-0 top-0 h-[2px] ${
            isWin
              ? "bg-gradient-to-r from-transparent via-emerald-400 to-transparent"
              : isLoss
              ? "bg-gradient-to-r from-transparent via-red-500 to-transparent"
              : "bg-gradient-to-r from-transparent via-zinc-500 to-transparent"
          }`}
        />
      )}

      {/* Content */}
      <div className="flex items-start gap-3">
        <MatchNumber num={match.match_number} winner={match.winner} />

        {/* Scores */}
        <div className="min-w-0 flex-1 space-y-2">
          <TeamRow
            name={userTeamName}
            score={match.user_score}
            wickets={match.user_wickets}
            overs={match.user_overs}
            isUser={true}
            isWinner={isWin}
          />

          {/* Divider */}
          <div className="flex items-center gap-2">
            <div className="h-px flex-1 bg-white/5" />
            <span className="text-[9px] font-bold uppercase tracking-widest text-zinc-700">vs</span>
            <div className="h-px flex-1 bg-white/5" />
          </div>

          <TeamRow
            name={opponentTeamName}
            score={match.opponent_score}
            wickets={match.opponent_wickets}
            overs={match.opponent_overs}
            isUser={false}
            isWinner={isLoss}
          />
        </div>

        <ResultBadge winner={match.winner} />
      </div>

      {/* Match status for non-completed */}
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
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/[0.03] via-transparent to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
    </motion.button>
  );
}
