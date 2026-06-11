"use client";

import { motion, AnimatePresence } from "motion/react";
import { Player } from "@/types/draft";

// ─── Role badge styling ─────────────────────────────────────────────
const ROLE_MAP: Record<string, string> = {
  WK: "WK",
  WICKETKEEPER: "WK",
  BAT: "BAT",
  BATSMAN: "BAT",
  BOWL: "BWL",
  BOWLER: "BWL",
  AR: "AR",
  ALLROUNDER: "AR",
};

// ─── Country flag helper ────────────────────────────────────────────
function countryToIso(nationality: string): string {
  const map: Record<string, string> = {
    "INDIAN": "in",
    "AUSTRALIAN": "au",
    "ENGLISH": "gb-eng",
    "SOUTH AFRICAN": "za",
    "NEW ZEALANDER": "nz",
    "WEST INDIAN": "jm", // Defaulting to Jamaica for WI
    "SRI LANKAN": "lk",
    "PAKISTANI": "pk",
    "BANGLADESHI": "bd",
    "AFGHAN": "af",
    "ZIMBABWEAN": "zw",
    "IRISH": "ie",
    "NEPALESE": "np",
    "DUTCH": "nl",
    "SINGAPOREAN": "sg",
  };
  return map[nationality?.toUpperCase()] || "un";
}

// ─── Deterministic Face Helper ──────────────────────────────────────
function getFaceIndex(playerId: string): number {
  const hex = playerId.replace(/-/g, "").substring(0, 8);
  const num = parseInt(hex, 16);
  return (num % 5) + 1;
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
  const role = ROLE_MAP[player.role] || "AR";
  const faceIndex = getFaceIndex(player.player_id);

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
        relative cursor-pointer overflow-hidden
        w-full max-w-[280px] mx-auto select-none
        ${
          canPick
            ? "opacity-100"
            : "cursor-not-allowed opacity-60 grayscale-[0.5]"
        }
      `}
      style={{
        background: "#313638",
        border: "4px solid #1a1c1d",
        borderRadius: "8px",
        padding: "4px",
      }}
    >
      {/* Inner Card Area */}
      <div className="relative bg-[#c29b76] h-full flex flex-col border-[3px] border-[#a07c5b] rounded-[4px] p-2">
        <div 
          className="absolute inset-0 opacity-20 pointer-events-none"
          style={{
            backgroundImage: "radial-gradient(#5a4231 1.5px, transparent 1px)",
            backgroundSize: "6px 6px"
          }}
        />

        <div className="relative z-10 flex flex-col h-full">
          {/* Top Banner (Name) */}
          <div className="bg-[#e4d4b9] border-2 border-[#1a1c1d] rounded-sm py-0.5 px-2 text-center mb-2 shadow-[2px_2px_0_#1a1c1d]">
            <h3 className="text-[1.1rem] font-body text-[#1a1c1d] uppercase tracking-wider leading-none mt-1 whitespace-nowrap overflow-hidden text-ellipsis">
              {player.name}
            </h3>
          </div>

          {/* Portrait Section */}
          <div className="flex justify-between items-start mb-2">
            {/* Left Col: Role & Flag */}
            <div className="flex flex-col gap-1 w-[36px]">
              <div className="bg-white border-2 border-[#1a1c1d] text-[#1a1c1d] text-center font-body text-lg font-black leading-none py-1 shadow-[2px_2px_0_#1a1c1d]">
                {role}
              </div>
              <div className="bg-white border-2 border-[#1a1c1d] text-center py-1 shadow-[2px_2px_0_#1a1c1d] flex items-center justify-center">
                <img 
                  src={`https://flagcdn.com/w40/${countryToIso(player.country)}.png`} 
                  alt={player.country}
                  className="w-[24px] border border-[#1a1c1d]"
                  style={{ imageRendering: "pixelated" }}
                />
              </div>
            </div>

            {/* Center: Face Image */}
            <div className="relative w-[120px] h-[120px]">
              <img 
                src={`/faces/face_${faceIndex}.png`} 
                alt="Player Face" 
                className="w-full h-full object-cover border-4 border-white drop-shadow-[4px_4px_0_rgba(0,0,0,0.5)] bg-[#eedcc0]"
                style={{ imageRendering: "pixelated" }}
              />
            </div>

            {/* Right Col: Rating & Overseas Airplane */}
            <div className="flex flex-col gap-1 w-[44px] items-center">
              <div className="bg-[#1a1c1d] text-accent-gold border-2 border-[#4a3b32] text-center font-body text-xl font-bold px-1 py-1 shadow-[2px_2px_0_#4a3b32] leading-none">
                {player.prime_rating}
              </div>
              {player.is_overseas && (
                <div className="mt-1 text-xl animate-pulse">
                  ✈️
                </div>
              )}
            </div>
          </div>

          {/* Stats Box - Clean layout */}
          <div className="bg-[#1a1c1d] border-2 border-[#4a3b32] p-3 shadow-[inset_0_0_8px_rgba(0,0,0,0.5)]">
            <div className="grid grid-cols-2 gap-y-2 text-white font-body text-[16px] leading-none mb-3">
              <div className="flex items-center gap-2">
                <span className="text-xl">🏏</span> {player.percentile_batting}
              </div>
              <div className="flex items-center gap-2 justify-end">
                <span className="text-xl">🎯</span> {player.percentile_bowling}
              </div>
              <div className="col-span-2 flex items-center justify-center text-[#e4d4b9] mt-1">
                Season R. {player.season_rating}
              </div>
            </div>
            
            {/* Cost row inline */}
            <div className="flex justify-between items-center pt-2 border-t-2 border-[#4a3b32] border-dotted">
              <span className="font-body text-[#a07c5b] text-[16px]">COST</span>
              <span className="font-body text-accent-gold text-2xl leading-none">{player.credit_cost} CR</span>
            </div>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {isSelected && (
          <motion.div
            className="absolute inset-0 border-[6px] border-accent-gold pointer-events-none mix-blend-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          />
        )}
      </AnimatePresence>

      {isSelected && (
        <div className="absolute top-1 left-1 text-2xl animate-bounce z-20">
          ⭐
        </div>
      )}
    </motion.div>
  );
}
