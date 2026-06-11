"use client";

import { motion, AnimatePresence } from "motion/react";
import { Player, PlayerRole } from "@/types/draft";

// ─── Role badge styling ─────────────────────────────────────────────

const ROLE_CONFIG: Record<
  PlayerRole,
  { label: string; color: string; bg: string; icon: string }
> = {
  WK: {
    label: "WK",
    color: "text-emerald-300",
    bg: "bg-emerald-500/15 border-emerald-500/30",
    icon: "🧤",
  },
  BAT: {
    label: "BAT",
    color: "text-sky-300",
    bg: "bg-sky-500/15 border-sky-500/30",
    icon: "🏏",
  },
  BOWL: {
    label: "BOWL",
    color: "text-rose-300",
    bg: "bg-rose-500/15 border-rose-500/30",
    icon: "🎯",
  },
  AR: {
    label: "AR",
    color: "text-purple-300",
    bg: "bg-purple-500/15 border-purple-500/30",
    icon: "⚡",
  },
};

// ─── Country flag helper ────────────────────────────────────────────

function countryToFlag(country: string): string {
  const map: Record<string, string> = {
    IND: "🇮🇳",
    AUS: "🇦🇺",
    ENG: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    SA: "🇿🇦",
    NZ: "🇳🇿",
    WI: "🇯🇲",
    SL: "🇱🇰",
    PAK: "🇵🇰",
    BAN: "🇧🇩",
    AFG: "🇦🇫",
    ZIM: "🇿🇼",
    IRE: "🇮🇪",
    NEP: "🇳🇵",
    UAE: "🇦🇪",
  };
  return map[country?.toUpperCase()] || "🏳️";
}

// ─── Stat Bar ───────────────────────────────────────────────────────

function StatBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-8 text-[10px] font-medium uppercase tracking-wider text-zinc-500">
        {label}
      </span>
      <div className="relative h-1.5 flex-1 overflow-hidden rounded-full bg-white/5">
        <motion.div
          className={`absolute inset-y-0 left-0 rounded-full ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
        />
      </div>
      <span className="w-7 text-right text-[10px] font-bold text-zinc-400">
        {value}
      </span>
    </div>
  );
}

// ─── PlayerCard ─────────────────────────────────────────────────────

interface PlayerCardProps {
  player: Player;
  onSelect: (player: Player) => void;
  isSelected: boolean;
  canPick: boolean;
  index: number;
}

export default function PlayerCard({
  player,
  onSelect,
  isSelected,
  canPick,
  index,
}: PlayerCardProps) {
  const role = ROLE_CONFIG[player.role];

  return (
    <motion.div
      id={`player-card-${player.player_season_id}`}
      layout
      initial={{ opacity: 0, y: 30, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8, y: -20 }}
      transition={{
        type: "spring",
        stiffness: 400,
        damping: 30,
        delay: index * 0.06,
      }}
      whileHover={canPick ? { y: -4, scale: 1.02 } : {}}
      whileTap={canPick ? { scale: 0.98 } : {}}
      onClick={() => canPick && onSelect(player)}
      className={`
        group relative cursor-pointer overflow-hidden rounded-xl border
        transition-colors duration-200
        ${
          isSelected
            ? "border-amber-400/60 bg-amber-500/10 shadow-[0_0_20px_rgba(251,191,36,0.15)]"
            : canPick
            ? "border-white/8 bg-white/[0.03] hover:border-white/15 hover:bg-white/[0.06]"
            : "cursor-not-allowed border-white/5 bg-white/[0.02] opacity-50"
        }
      `}
    >
      {/* Overseas badge */}
      {player.is_overseas && (
        <div className="absolute right-2 top-2 z-10">
          <div className="rounded-md border border-amber-500/30 bg-amber-500/10 px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider text-amber-400">
            OS
          </div>
        </div>
      )}

      {/* Card content */}
      <div className="p-4">
        {/* Header: name + flag */}
        <div className="mb-3 flex items-start gap-2">
          <span className="text-xl">{countryToFlag(player.country)}</span>
          <div className="min-w-0 flex-1">
            <h3 className="truncate text-sm font-bold text-white group-hover:text-amber-200 transition-colors">
              {player.name}
            </h3>
            <div className="mt-1 flex items-center gap-1.5">
              <span
                className={`inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[10px] font-semibold ${role.bg} ${role.color}`}
              >
                {role.icon} {role.label}
              </span>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="mb-3 space-y-1.5">
          {player.percentile_batting > 0 && (
            <StatBar
              label="BAT"
              value={player.percentile_batting}
              color="bg-gradient-to-r from-sky-500 to-cyan-400"
            />
          )}
          {player.percentile_bowling > 0 && (
            <StatBar
              label="BWL"
              value={player.percentile_bowling}
              color="bg-gradient-to-r from-rose-500 to-pink-400"
            />
          )}
        </div>

        {/* Cost */}
        <div className="flex items-center justify-between border-t border-white/5 pt-2">
          <span className="text-[10px] uppercase tracking-wider text-zinc-500">
            Cost
          </span>
          <span className="font-mono text-sm font-black text-amber-400">
            {player.credit_cost}
            <span className="ml-0.5 text-[10px] font-normal text-amber-400/60">
              cr
            </span>
          </span>
        </div>
      </div>

      {/* Selection glow */}
      <AnimatePresence>
        {isSelected && (
          <motion.div
            className="absolute inset-0 rounded-xl border-2 border-amber-400/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          />
        )}
      </AnimatePresence>

      {/* Hover shine */}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
    </motion.div>
  );
}
