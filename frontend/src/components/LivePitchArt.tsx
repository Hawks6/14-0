"use client";

import { motion } from "motion/react";
import { Player, RosterSlot } from "@/types/draft";

interface LivePitchArtProps {
  roster: RosterSlot[];
}

// 11 fixed fielding positions (x, y as percentages)
// 0: WK, 1-10: Fielders and Bowler
const FIELDING_POSITIONS = [
  { x: 50, y: 85, label: "WK" },
  { x: 50, y: 15, label: "BOWL" },
  { x: 30, y: 70, label: "SLIP" },
  { x: 15, y: 50, label: "PT" },
  { x: 25, y: 30, label: "COV" },
  { x: 45, y: 25, label: "MOFF" },
  { x: 55, y: 25, label: "MON" },
  { x: 75, y: 40, label: "MW" },
  { x: 85, y: 60, label: "SQL" },
  { x: 70, y: 80, label: "FL" },
  { x: 10, y: 80, label: "3M" },
];

export default function LivePitchArt({ roster }: LivePitchArtProps) {
  // Extract only slots that have an assigned player
  const activePlayers = roster
    .map((slot) => slot.player)
    .filter((player): player is Player => !!player);

  return (
    <div className="relative w-full h-full min-h-[600px] bg-accent-green rounded-sm border-4 border-surface-border overflow-hidden shadow-sm">
      {/* Pitch inner oval */}
      <div className="absolute inset-4 rounded-[100%] border-2 border-white/30" />
      <div className="absolute inset-12 rounded-[100%] border border-white/20" />
      
      {/* 30 yard circle equivalent */}
      <div className="absolute inset-20 rounded-[100%] border border-white/40 border-dashed" />

      {/* The Pitch (center rectangle) */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[15%] h-[50%] bg-[#d2b48c] border-2 border-white/50">
        {/* Creases */}
        <div className="absolute top-[10%] left-0 w-full h-px bg-white" />
        <div className="absolute bottom-[10%] left-0 w-full h-px bg-white" />
        {/* Stumps */}
        <div className="absolute top-[5%] left-1/2 -translate-x-1/2 w-4 h-1 bg-white/80" />
        <div className="absolute bottom-[5%] left-1/2 -translate-x-1/2 w-4 h-1 bg-white/80" />
      </div>

      {/* Render Fielders */}
      {activePlayers.map((player, index) => {
        // Find position based on role or just fill sequentially
        // For simplicity, we just place them in the 11 slots sequentially for now
        // Ideally WK goes to slot 0
        const isWK = player.role === "WK";
        // Just a hacky way to assign slots. First WK gets pos 0.
        // Others get remaining pos.
        let posIndex = index;
        if (isWK) posIndex = 0;
        else if (index === 0 && activePlayers.length > 1) posIndex = 1; // if someone else took 0

        // Modulo just in case
        const pos = FIELDING_POSITIONS[posIndex % FIELDING_POSITIONS.length];

        return (
          <motion.div
            key={player.player_season_id}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 15 }}
            className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center"
            style={{ left: `${pos.x}%`, top: `${pos.y}%` }}
          >
            <div className="w-4 h-4 bg-accent-gold rounded-full border-2 border-background shadow-sm z-10" />
            <div className="mt-1 bg-background px-1 border border-surface-border text-[8px] font-heading font-bold text-white whitespace-nowrap z-20">
              {player.name.split(" ").pop()}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
