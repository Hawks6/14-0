"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { motion, useAnimation, AnimatePresence, useMotionValue, useTransform } from "motion/react";
import { FRANCHISE_COLORS, SpinResult } from "@/types/draft";

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
];

const YEARS = Array.from({ length: 17 }, (_, i) => 2008 + i); // 2008 - 2024

interface SpinWheelProps {
  onSpinStart: () => void;
  onSpinComplete: (result: SpinResult) => void;
  isSpinning: boolean;
  disabled: boolean;
  spinResult: SpinResult | null;
}

// ─── Particle Burst Effect ──────────────────────────────────────────

function ParticleBurst({ active }: { active: boolean }) {
  const particles = useMemo(() => {
    return Array.from({ length: 20 }, (_, i) => {
      const angle = (i / 20) * Math.PI * 2;
      const distance = 60 + Math.random() * 80;
      return {
        id: i,
        tx: Math.cos(angle) * distance,
        ty: Math.sin(angle) * distance,
        size: 3 + Math.random() * 5,
        color: ["#f5c518", "#f97316", "#a855f7", "#3b82f6", "#22c55e"][
          Math.floor(Math.random() * 5)
        ],
        delay: Math.random() * 0.3,
      };
    });
  }, []);

  if (!active) return null;

  return (
    <div className="pointer-events-none absolute inset-0 z-30 flex items-center justify-center">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full"
          style={{
            width: p.size,
            height: p.size,
            backgroundColor: p.color,
          }}
          initial={{ x: 0, y: 0, scale: 1, opacity: 1 }}
          animate={{
            x: p.tx,
            y: p.ty,
            scale: 0,
            opacity: 0,
          }}
          transition={{
            duration: 0.8,
            delay: p.delay,
            ease: "easeOut",
          }}
        />
      ))}
    </div>
  );
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
    <div className="flex flex-col gap-1.5">
      <p className="text-center text-[10px] font-semibold uppercase tracking-[0.2em] text-zinc-500">
        {label}
      </p>
      <div
        className={`relative h-[80px] overflow-hidden rounded-xl border bg-black/60 backdrop-blur-md transition-all duration-500 ${
          hasLanded
            ? "border-amber-400/40 shadow-[0_0_25px_rgba(245,197,24,0.2)]"
            : spinning
            ? "border-amber-500/20 reel-container-glow"
            : "border-white/10"
        }`}
      >
        {/* Top / bottom fade gradients */}
        <div className="pointer-events-none absolute inset-x-0 top-0 z-10 h-8 bg-gradient-to-b from-black/90 via-black/50 to-transparent" />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-8 bg-gradient-to-t from-black/90 via-black/50 to-transparent" />

        {/* Selection indicator line */}
        <div className="pointer-events-none absolute inset-x-0 top-1/2 z-20 -translate-y-1/2">
          <div
            className={`mx-1 h-[2px] rounded-full transition-all duration-300 ${
              hasLanded
                ? "bg-gradient-to-r from-transparent via-amber-300 to-transparent shadow-[0_0_20px_rgba(251,191,36,0.8)]"
                : "bg-gradient-to-r from-transparent via-amber-400/60 to-transparent shadow-[0_0_12px_rgba(251,191,36,0.4)]"
            }`}
          />
        </div>

        {/* Side tick marks */}
        <div className="pointer-events-none absolute left-0 top-1/2 z-20 -translate-y-1/2">
          <div className="h-3 w-1 rounded-r-full bg-amber-400/50" />
        </div>
        <div className="pointer-events-none absolute right-0 top-1/2 z-20 -translate-y-1/2">
          <div className="h-3 w-1 rounded-l-full bg-amber-400/50" />
        </div>

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
              className="absolute inset-0 z-20 bg-amber-400/10"
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
  isSpinning,
  disabled,
  spinResult,
}: SpinWheelProps) {
  const [internalSpinning, setInternalSpinning] = useState(false);
  const [landed, setLanded] = useState(false);
  const [showParticles, setShowParticles] = useState(false);
  const [pendingResult, setPendingResult] = useState<SpinResult | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pulseCount = useMotionValue(0);
  const buttonGlow = useTransform(
    pulseCount,
    [0, 0.5, 1],
    [
      "0 0 20px rgba(245,158,11,0.1)",
      "0 0 40px rgba(245,158,11,0.3)",
      "0 0 20px rgba(245,158,11,0.1)",
    ]
  );

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
    setShowParticles(false);
    setInternalSpinning(true);
    onSpinStart();
  }, [disabled, internalSpinning, onSpinStart]);

  // When we get a spin result from the API while animation is running, store it
  // and let the animation finish
  useEffect(() => {
    if (spinResult && internalSpinning) {
      setPendingResult(spinResult);
      timeoutRef.current = setTimeout(() => {
        setInternalSpinning(false);
        setLanded(true);
        setShowParticles(true);
        onSpinComplete(spinResult);
        setPendingResult(null);
        // Hide particles after animation
        setTimeout(() => setShowParticles(false), 1000);
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

  const resultColors =
    landed && spinResult
      ? FRANCHISE_COLORS[spinResult.franchise_code] || {
          primary: "#D4AF37",
          secondary: "#1a1a2e",
          glow: "rgba(212,175,55,0.4)",
        }
      : null;

  return (
    <div className="flex flex-col items-center gap-6">
      {/* Spin Machine */}
      <motion.div
        className="relative w-full max-w-md rounded-2xl border border-white/10 bg-gradient-to-b from-zinc-900/90 to-black/95 p-6 shadow-2xl backdrop-blur-xl"
        animate={
          landed && resultColors
            ? {
                boxShadow: `0 0 60px ${resultColors.glow}, 0 0 120px ${resultColors.glow}`,
                borderColor: resultColors.primary,
              }
            : internalSpinning
            ? {
                boxShadow: "0 0 30px rgba(245,197,24,0.15), 0 0 60px rgba(245,197,24,0.05)",
              }
            : {}
        }
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        {/* Animated background on spin */}
        {internalSpinning && (
          <motion.div
            className="pointer-events-none absolute inset-0 rounded-2xl"
            style={{
              background:
                "radial-gradient(ellipse at center, rgba(245,197,24,0.05) 0%, transparent 70%)",
            }}
            animate={{ opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}

        {/* Header */}
        <div className="mb-5 text-center">
          <motion.h2
            className="bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-400 bg-clip-text text-xs font-bold uppercase tracking-[0.3em] text-transparent animate-gradient-text"
            animate={internalSpinning ? { opacity: [0.7, 1, 0.7] } : {}}
            transition={{ duration: 1, repeat: Infinity }}
          >
            IPL Time Machine
          </motion.h2>
          <p className="mt-1.5 text-[11px] text-zinc-500">
            Spin to reveal your franchise & era
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
              <span className="text-lg font-bold text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.2)]">
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
              <span className="font-mono text-2xl font-black text-amber-400 drop-shadow-[0_0_8px_rgba(245,197,24,0.3)]">
                {item.label}
              </span>
            )}
          />
        </div>

        {/* Landed result banner */}
        <AnimatePresence>
          {landed && spinResult && (
            <motion.div
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              className="mt-5 overflow-hidden rounded-xl border border-white/10"
              style={
                resultColors
                  ? {
                      background: `linear-gradient(135deg, ${resultColors.primary}15, ${resultColors.secondary}10)`,
                      borderColor: `${resultColors.primary}30`,
                    }
                  : {}
              }
            >
              <div className="relative p-4 text-center">
                {/* Franchise color bar */}
                {resultColors && (
                  <div
                    className="absolute inset-x-0 top-0 h-0.5"
                    style={{
                      background: `linear-gradient(90deg, transparent, ${resultColors.primary}, transparent)`,
                    }}
                  />
                )}
                <motion.p
                  className="text-base font-black"
                  style={{ color: resultColors?.primary || "#f5c518" }}
                  initial={{ letterSpacing: "0.1em" }}
                  animate={{ letterSpacing: "0.02em" }}
                  transition={{ delay: 0.2, duration: 0.4 }}
                >
                  {spinResult.franchise_name}
                </motion.p>
                <p className="mt-1 text-xs text-zinc-400">
                  Season {spinResult.year} •{" "}
                  <span className="font-semibold text-zinc-300">
                    {spinResult.players.length}
                  </span>{" "}
                  players available
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Particle burst on landing */}
        <ParticleBurst active={showParticles} />

        {/* Decorative corner accents */}
        <div className="pointer-events-none absolute left-3 top-3 h-5 w-5 rounded-tl-lg border-l-2 border-t-2 border-amber-500/30" />
        <div className="pointer-events-none absolute right-3 top-3 h-5 w-5 rounded-tr-lg border-r-2 border-t-2 border-amber-500/30" />
        <div className="pointer-events-none absolute bottom-3 left-3 h-5 w-5 rounded-bl-lg border-b-2 border-l-2 border-amber-500/30" />
        <div className="pointer-events-none absolute bottom-3 right-3 h-5 w-5 rounded-br-lg border-b-2 border-r-2 border-amber-500/30" />

        {/* Horizontal decorative dividers */}
        <div className="pointer-events-none absolute left-6 right-6 top-0 h-px bg-gradient-to-r from-transparent via-amber-500/20 to-transparent" />
        <div className="pointer-events-none absolute bottom-0 left-6 right-6 h-px bg-gradient-to-r from-transparent via-amber-500/20 to-transparent" />
      </motion.div>

      {/* Spin Button */}
      <motion.button
        id="spin-button"
        onClick={handleSpin}
        disabled={disabled || internalSpinning}
        className="group relative overflow-hidden rounded-full px-10 py-4 text-sm font-bold uppercase tracking-widest text-black shadow-lg transition-all disabled:cursor-not-allowed disabled:opacity-40"
        whileHover={{ scale: 1.06, y: -2 }}
        whileTap={{ scale: 0.94 }}
        style={{
          background:
            "linear-gradient(135deg, #FFD700 0%, #FFA500 40%, #FFD700 70%, #FFEC80 100%)",
          boxShadow: "0 4px 30px rgba(255,165,0,0.25), 0 0 60px rgba(255,215,0,0.1)",
        }}
      >
        {/* Shine sweep */}
        <motion.div
          className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/30 to-transparent"
          animate={
            !disabled && !internalSpinning
              ? { translateX: ["-100%", "200%"] }
              : {}
          }
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
        />
        {/* Bottom edge highlight */}
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-white/40 to-transparent" />
        <span className="relative z-10 flex items-center gap-2">
          {internalSpinning ? (
            <>
              <motion.span
                animate={{ rotate: 360 }}
                transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
                className="inline-block"
              >
                ⚡
              </motion.span>
              Spinning…
            </>
          ) : (
            <>
              <span className="text-base">🎰</span>
              Spin the Wheel
            </>
          )}
        </span>
      </motion.button>
    </div>
  );
}
