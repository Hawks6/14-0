"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { motion, useAnimation, AnimatePresence } from "motion/react";
import { SpinResult } from "@/types/draft";

// ─── Franchise data for the reels ──────────────────────────────────

const FRANCHISES = [
  { code: "CSK", name: "Chennai Super Kings", emoji: "🦁" },
  { code: "MI", name: "Mumbai Indians", emoji: "🏏" },
  { code: "RCB", name: "Royal Challengers Bengaluru", emoji: "🔴" },
  { code: "KKR", name: "Kolkata Knight Riders", emoji: "⚡" },
  { code: "DC", name: "Delhi Capitals", emoji: "🦅" },
  { code: "PBKS", name: "Punjab Kings", emoji: "👑" },
  { code: "RR", name: "Rajasthan Royals", emoji: "💎" },
  { code: "SRH", name: "Sunrisers Hyderabad", emoji: "🌅" },
  { code: "GT", name: "Gujarat Titans", emoji: "⚔️" },
  { code: "LSG", name: "Lucknow Super Giants", emoji: "🐺" },
  { code: "DEC", name: "Deccan Chargers", emoji: "🛡️" },
  { code: "DD", name: "Delhi Daredevils", emoji: "🌪️" },
  { code: "KXIP", name: "Kings XI Punjab", emoji: "🦁" },
  { code: "KTK", name: "Kochi Tuskers Kerala", emoji: "🐘" },
  { code: "PWI", name: "Pune Warriors India", emoji: "⚔️" },
  { code: "GL", name: "Gujarat Lions", emoji: "🦁" },
  { code: "RPS", name: "Rising Pune Supergiant", emoji: "⚡" },
  { code: "RPS2", name: "Rising Pune Supergiants", emoji: "⚡" },
  { code: "RCBB", name: "Royal Challengers Bengaluru", emoji: "🔴" },
];

const YEARS = Array.from({ length: 19 }, (_, i) => 2008 + i); // 2008 - 2026

interface SpinWheelProps {
  onSpinStart: () => void;
  onSpinComplete: (result: SpinResult) => void;
  isSpinning: boolean;
  disabled: boolean;
  spinResult: SpinResult | null;
}



// ─── Single Slot Reel ──────────────────────────────────────────────

function SlotReel({
  items,
  targetIndex,
  spinning,
  delay,
  renderItem,
  label,
}: {
  items: { label: string; sub?: string }[];
  targetIndex: number;
  spinning: boolean;
  delay: number;
  renderItem: (item: { label: string; sub?: string }, idx: number) => React.ReactNode;
  label: string;
}) {
  const controls = useAnimation();
  const ITEM_H = 80;
  const totalItems = items.length;
  const loopCount = 3;
  const totalTravel = loopCount * totalItems * ITEM_H + targetIndex * ITEM_H;
  const [hasLanded, setHasLanded] = useState(false);

  useEffect(() => {
    if (spinning) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setHasLanded(false);
      controls.start({
        y: -totalTravel,
        transition: {
          duration: 2.5 + delay * 0.6,
          ease: [0.12, 0.82, 0.32, 1.04], // anticipation → overshoot → settle
          delay: delay * 0.12,
        },
      }).then(() => {
        setHasLanded(true);
      });
    } else {
      controls.set({ y: 0 });
      setHasLanded(false);
    }
  }, [spinning, controls, totalTravel, delay]);

  const strip = useMemo(() => {
    const arr: { label: string; sub?: string }[] = [];
    for (let i = 0; i <= loopCount; i++) {
      arr.push(...items);
    }
    return arr;
  }, [items]);

  return (
    <div className="flex flex-col gap-2">
      <p className="text-center text-sm font-heading font-bold uppercase tracking-widest text-text-secondary">
        {label}
      </p>
      <div
        className={`relative h-[80px] overflow-hidden border-2 bg-background transition-all duration-500 ${
          hasLanded
            ? "border-accent-gold"
            : spinning
            ? "border-accent-orange"
            : "border-surface-border"
        }`}
      >
        {/* Selection indicator line */}
        <div className="pointer-events-none absolute inset-x-0 top-1/2 z-20 -translate-y-1/2 border-t border-b border-surface-border bg-surface-bright/20 h-20" />

        <motion.div animate={controls} className="flex flex-col">
          {strip.map((item, idx) => (
            <div
              key={`${idx}`}
              className="flex h-[80px] shrink-0 items-center justify-center"
            >
              {renderItem(item, idx)}
            </div>
          ))}
        </motion.div>

        {/* Landing flash overlay */}
        <AnimatePresence>
          {hasLanded && (
            <motion.div
              className="absolute inset-0 z-20 bg-accent-gold/20"
              initial={{ opacity: 1 }}
              animate={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// ─── Main SpinWheel ────────────────────────────────────────────────

export default function SpinWheel({
  onSpinStart,
  onSpinComplete,
  disabled,
  spinResult,
}: SpinWheelProps) {
  const [internalSpinning, setInternalSpinning] = useState(false);
  const [landed, setLanded] = useState(false);
  const [pendingResult, setPendingResult] = useState<SpinResult | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const franchiseItems = useMemo(
    () =>
      FRANCHISES.map((f) => ({
        label: `${f.emoji} ${f.code}`,
        sub: f.name,
      })),
    []
  );

  const yearItems = useMemo(
    () => YEARS.map((y) => ({ label: String(y) })),
    []
  );

  const handleSpin = useCallback(() => {
    if (disabled || internalSpinning) return;
    setLanded(false);
    setInternalSpinning(true);
    onSpinStart();
  }, [disabled, internalSpinning, onSpinStart]);

  useEffect(() => {
    if (spinResult && internalSpinning) {
      // eslint-disable-next-line react-hooks/exhaustive-deps
      setPendingResult(spinResult);
      timeoutRef.current = setTimeout(() => {
        setInternalSpinning(false);
        setLanded(true);
        onSpinComplete(spinResult);
        setPendingResult(null);
      }, 3500);
    }
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [spinResult, internalSpinning, onSpinComplete]);

  const targetFranchiseIdx = pendingResult
    ? FRANCHISES.findIndex((f) => f.code === pendingResult.franchise_code)
    : Math.floor(Math.random() * FRANCHISES.length);

  const targetYearIdx = pendingResult
    ? YEARS.indexOf(pendingResult.year)
    : Math.floor(Math.random() * YEARS.length);

  return (
    <div className="flex flex-col items-center gap-6 w-full">
      {/* Spin Machine */}
      <div className="relative w-full max-w-md border-2 border-surface-border bg-surface p-6 shadow-sm">
        
        {/* Header */}
        <div className="mb-6 text-center border-b-2 border-surface-border pb-4">
          <h2 className="font-heading text-2xl font-bold uppercase tracking-widest text-accent-gold">
            TIME MACHINE
          </h2>
          <p className="mt-1 text-sm font-body text-text-secondary uppercase">
            SPIN TO REVEAL FRANCHISE & ERA
          </p>
        </div>

        {/* Reels */}
        <div className="grid grid-cols-2 gap-4">
          {/* Franchise Reel */}
          <SlotReel
            items={franchiseItems}
            targetIndex={targetFranchiseIdx >= 0 ? targetFranchiseIdx : 0}
            spinning={internalSpinning}
            delay={0}
            label="Franchise"
            renderItem={(item) => (
              <span className="text-2xl font-heading font-bold text-white tracking-widest">
                {item.label}
              </span>
            )}
          />

          {/* Year Reel */}
          <SlotReel
            items={yearItems}
            targetIndex={targetYearIdx >= 0 ? targetYearIdx : 0}
            spinning={internalSpinning}
            delay={1}
            label="Season"
            renderItem={(item) => (
              <span className="font-body text-4xl font-black text-accent-gold">
                &apos;{item.label.slice(2)}
              </span>
            )}
          />
        </div>

        {/* Landed result banner */}
        <AnimatePresence>
          {landed && spinResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-6 border-2 border-accent-gold bg-accent-gold-dim"
            >
              <div className="p-4 text-center">
                <p className="text-2xl font-heading font-bold text-accent-gold uppercase">
                  {spinResult.franchise_name}
                </p>
                <p className="mt-1 text-sm font-body text-text-secondary uppercase">
                  SEASON {spinResult.year} • {spinResult.players.length} PLAYERS
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Spin Button */}
      <motion.button
        id="spin-button"
        onClick={handleSpin}
        disabled={disabled || internalSpinning}
        className="btn-primary w-full max-w-md py-4 text-xl"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <span className="relative z-10 flex items-center justify-center gap-2">
          {internalSpinning ? (
            <>
              <motion.span animate={{ rotate: 360 }} transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}>
                ⏳
              </motion.span>
              SPINNING...
            </>
          ) : (
            <>SPIN THE WHEEL</>
          )}
        </span>
      </motion.button>
    </div>
  );
}
