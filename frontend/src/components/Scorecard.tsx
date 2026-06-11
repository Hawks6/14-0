"use client";

import { motion } from "motion/react";
import type { LeagueMatch } from "@/types/league";

// ─── Overs formatting ──────────────────────────────────────────────

function formatOvers(overs: number | undefined): string {
  if (overs !== undefined) {
    return `(${overs} ov)`;
  }
  return "";
}

// ─── Score display ──────────────────────────────────────────────────

function ScoreBlock({
  label,
  score,
  wickets,
  overs,
  isUser,
  isWinner,
}: {
  label: string;
  score: number;
  wickets: number;
  overs?: number;
  isUser: boolean;
  isWinner: boolean;
}) {
  return (
    <div className="flex flex-1 flex-col items-center gap-1">
      {/* Team label */}
      <div className="flex flex-col items-center gap-0.5">
        {isUser && (
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-accent-gold mb-0.5" />
        )}
        <span
          className={`max-w-[130px] text-center text-[11px] font-bold leading-snug line-clamp-2 ${
            isUser ? "text-amber-300" : "text-zinc-300"
          }`}
          title={label}
        >
          {label}
        </span>
      </div>

      {/* Score */}
      <div className="flex items-baseline gap-0.5">
        <motion.span
          key={score}
          initial={{ scale: 1.3, color: "#f5c518" }}
          animate={{ scale: 1, color: isWinner ? "#22c55e" : "#f0f0f5" }}
          transition={{ duration: 0.6 }}
          className="text-3xl font-black tabular-nums sm:text-4xl"
        >
          {score}
        </motion.span>
        <span className="text-lg font-semibold text-zinc-500">
          /{wickets}
        </span>
      </div>

      {/* Overs */}
      <span className="text-[10px] text-zinc-500">
        {formatOvers(overs)}
      </span>
    </div>
  );
}

// ─── Match status chip ──────────────────────────────────────────────

function StatusChip({
  winner,
  status,
}: {
  winner: LeagueMatch["winner"];
  status: LeagueMatch["status"];
}) {
  if (status !== "completed") {
    return (
      <div className="flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1">
        <motion.div
          className="h-2 w-2 rounded-full bg-amber-400"
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
        <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400">
          {status === "in_progress" ? "LIVE" : "UPCOMING"}
        </span>
      </div>
    );
  }

  const config = {
    user: {
      bg: "border-emerald-500/30 bg-emerald-500/10",
      text: "text-emerald-400",
      label: "WON",
      icon: "✓",
    },
    opponent: {
      bg: "border-red-500/30 bg-red-500/10",
      text: "text-red-400",
      label: "LOST",
      icon: "✗",
    },
    tie: {
      bg: "border-zinc-500/30 bg-zinc-500/10",
      text: "text-zinc-400",
      label: "TIE",
      icon: "=",
    },
  };

  const c = config[winner || "tie"];

  return (
    <div
      className={`flex items-center gap-1.5 rounded-full border px-3 py-1 ${c.bg}`}
    >
      <span className={`text-xs font-black ${c.text}`}>{c.icon}</span>
      <span
        className={`text-[10px] font-bold uppercase tracking-wider ${c.text}`}
      >
        {c.label}
      </span>
    </div>
  );
}

// ─── Scorecard Component ────────────────────────────────────────────

interface ScorecardProps {
  match: LeagueMatch;
  onClose?: () => void;
}

export default function Scorecard({ match, onClose }: ScorecardProps) {
  const isUserWinner = match.winner === "user";
  const isOpponentWinner = match.winner === "opponent";

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: 20 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="relative overflow-hidden rounded-2xl border border-white/10"
    >
      {/* Background layers */}
      <div className="absolute inset-0 broadcast-gradient" />
      <div className="absolute inset-0 scorecard-gradient" />

      {/* Shimmer effect on win */}
      {isUserWinner && (
        <div className="absolute inset-0 animate-shimmer pointer-events-none" />
      )}

      {/* Content */}
      <div className="relative z-10 p-5 sm:p-6">
        {/* Match header */}
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
              Match {match.match_number} of 14
            </span>
            <StatusChip winner={match.winner} status={match.status} />
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="flex h-7 w-7 items-center justify-center rounded-full border border-white/10 bg-white/5 text-xs text-zinc-400 transition-colors hover:bg-white/10 hover:text-white"
            >
              ✕
            </button>
          )}
        </div>

        {/* Score comparison */}
        <div className="flex items-center gap-4">
          <ScoreBlock
            label={match.user_team || "Your XI"}
            score={match.user_score}
            wickets={match.user_wickets}
            overs={match.user_overs}
            isUser={true}
            isWinner={isUserWinner}
          />

          {/* VS divider */}
          <div className="flex flex-col items-center gap-1">
            <span className="text-xs font-black text-zinc-600">VS</span>
            <div className="h-8 w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
          </div>

          <ScoreBlock
            label={match.opponent_team || "Opponent"}
            score={match.opponent_score}
            wickets={match.opponent_wickets}
            overs={match.opponent_overs}
            isUser={false}
            isWinner={isOpponentWinner}
          />
        </div>

        {/* Result summary */}
        {match.status === "completed" && match.winner && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-4 text-center"
          >
            <span
              className={`text-xs font-semibold ${
                isUserWinner
                  ? "text-emerald-400"
                  : isOpponentWinner
                  ? "text-red-400"
                  : "text-zinc-400"
              }`}
            >
              {isUserWinner &&
                `Won by ${
                  match.user_score > match.opponent_score
                    ? `${match.user_score - match.opponent_score} runs`
                    : `${10 - match.user_wickets} wickets`
                }`}
              {isOpponentWinner &&
                `Lost by ${
                  match.opponent_score > match.user_score
                    ? `${match.opponent_score - match.user_score} runs`
                    : `${10 - match.opponent_wickets} wickets`
                }`}
              {match.winner === "tie" && "Match Tied"}
            </span>
          </motion.div>
        )}

        {/* Bottom accent line */}
        <div
          className={`mt-4 h-0.5 w-full rounded-full ${
            isUserWinner
              ? "bg-gradient-to-r from-transparent via-emerald-500 to-transparent"
              : isOpponentWinner
              ? "bg-gradient-to-r from-transparent via-red-500 to-transparent"
              : "bg-gradient-to-r from-transparent via-zinc-600 to-transparent"
          }`}
        />
      </div>
    </motion.div>
  );
}
