"use client";

import { useRouter } from "next/navigation";
import { useCallback, useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { createDraftSession } from "@/lib/api";
import { useDraftStore } from "@/store/draftStore";

/* ═══════════════════════════════════════════════════════════════════════
   14-0 Landing Page
   Premium hero with animated gradient, glassmorphism cards,
   smooth entrance animations, and a "Start Draft" CTA.
   ═══════════════════════════════════════════════════════════════════════ */

interface Particle {
  id: number;
  size: number;
  x: number;
  y: number;
  delay: number;
  duration: number;
  opacity: number;
}

function FloatingParticles() {
  const [particles, setParticles] = useState<Particle[]>([]);


  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => {
    setParticles(
      Array.from({ length: 24 }, (_, i) => ({
        id: i,
        size: Math.random() * 3 + 1,
        x: Math.random() * 100,
        y: Math.random() * 100,
        delay: Math.random() * 8,
        duration: Math.random() * 6 + 8,
        opacity: Math.random() * 0.3 + 0.1,
      }))
    );
  }, []);

  if (particles.length === 0) return null;

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full"
          style={{
            width: p.size,
            height: p.size,
            left: `${p.x}%`,
            top: `${p.y}%`,
            background: `rgba(245, 197, 24, ${p.opacity})`,
          }}
          animate={{
            y: [0, -30, 10, -20, 0],
            x: [0, 10, -10, 5, 0],
            opacity: [p.opacity, p.opacity * 2, p.opacity, p.opacity * 1.5, p.opacity],
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}

// ─── Stats Row ───────────────────────────────────────────────────────
const stats = [
  { label: "IPL Seasons", value: "17+", icon: "🏏" },
  { label: "Players", value: "500+", icon: "⭐" },
  { label: "Franchises", value: "10", icon: "🏆" },
  { label: "Matches Simulated", value: "14", icon: "🎯" },
];

function StatsRow() {
  return (
    <motion.div
      className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 w-full max-w-3xl mx-auto"
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: 0.1, delayChildren: 0.8 } },
      }}
    >
      {stats.map((stat) => (
        <motion.div
          key={stat.label}
          className="stat-badge"
          variants={{
            hidden: { opacity: 0, y: 20, scale: 0.9 },
            visible: { opacity: 1, y: 0, scale: 1 },
          }}
          transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        >
          <span className="text-xl sm:text-2xl">{stat.icon}</span>
          <span className="text-xl sm:text-2xl font-bold font-heading text-accent-gold">
            {stat.value}
          </span>
          <span className="text-xs text-text-secondary uppercase tracking-wider">
            {stat.label}
          </span>
        </motion.div>
      ))}
    </motion.div>
  );
}

// ─── Feature Cards ───────────────────────────────────────────────────
const features = [
  {
    title: "SPIN & DRAFT",
    description:
      "SPIN FOR A RANDOM HISTORICAL FRANCHISE ERA. DRAFT LEGENDARY PLAYERS WITHIN A STRICT 100-CREDIT SALARY CAP.",
    icon: "🎰",
  },
  {
    title: "BUILD YOUR XI",
    description:
      "FILL 11 ROSTER SLOTS WITH ROLE CONSTRAINTS — 1 WK, 3+ BOWLERS, MAX 4 OVERSEAS. STRATEGY MATTERS.",
    icon: "📋",
  },
  {
    title: "SIMULATE & CONQUER",
    description:
      "WATCH YOUR SQUAD COMPETE THROUGH 14 PROBABILISTICALLY-RIGOROUS MATCHES. CAN YOU GO 14-0?",
    icon: "⚡",
  },
];

function FeatureCards() {
  return (
    <motion.div
      className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-5xl mx-auto"
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: 0.15, delayChildren: 0.5 } },
      }}
    >
      {features.map((feature) => (
        <motion.div
          key={feature.title}
          className="border-4 border-surface-border bg-surface p-6 sm:p-8 cursor-default group hover:border-accent-gold transition-colors"
          variants={{
            hidden: { opacity: 0, y: 30 },
            visible: { opacity: 1, y: 0 },
          }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          whileHover={{ scale: 1.02 }}
        >
          <div className="relative z-10">
            <span className="text-4xl sm:text-5xl mb-6 block">{feature.icon}</span>
            <h3 className="text-xl font-bold font-heading text-accent-gold mb-4 uppercase tracking-widest">
              {feature.title}
            </h3>
            <p className="text-base text-text-secondary leading-relaxed font-body uppercase">
              {feature.description}
            </p>
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────
export default function HomePage() {
  const router = useRouter();
  const initSession = useDraftStore((s) => s.initSession);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartDraft = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const session = await createDraftSession();
      initSession(session.id, session.budget_remaining);
      router.push("/draft");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to start draft. Is the server running?"
      );
    } finally {
      setIsLoading(false);
    }
  }, [initSession, router]);

  return (
    <div className="relative flex flex-col min-h-screen bg-background font-body text-text-primary overflow-hidden">
      {/* ── Background Grid ──────────────────────────────────────── */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: "radial-gradient(var(--text-secondary) 1px, transparent 1px)",
            backgroundSize: "32px 32px",
          }}
        />
      </div>

      {/* ── Content ──────────────────────────────────────────────── */}
      <main className="relative z-10 flex flex-col items-center flex-1 w-full">
        {/* ── Hero Section ───────────────────────────────────────── */}
        <section className="flex flex-col items-center justify-center text-center px-5 pt-20 sm:pt-28 md:pt-36 pb-10 sm:pb-16 w-full border-b-4 border-surface-border bg-surface">
          {/* Main Title */}
          <motion.h1
            className="font-heading font-black tracking-widest leading-none mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
          >
            <span className="block text-7xl sm:text-8xl md:text-[120px] text-accent-gold drop-shadow-[4px_4px_0_rgba(0,0,0,1)]">
              14-0
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            className="mt-4 sm:mt-6 text-xl sm:text-2xl md:text-3xl text-white font-heading uppercase tracking-widest"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
          >
            DRAFT LEGENDARY SQUADS. SIMULATE PERFECTION.
          </motion.p>
          <motion.p
            className="mt-4 text-text-secondary font-body uppercase tracking-widest text-lg sm:text-xl"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.45 }}
          >
            CAN YOU GO UNBEATEN ACROSS 14 MATCHES?
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            className="mt-12 flex flex-col sm:flex-row gap-6 items-center"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <motion.button
              id="start-draft-btn"
              className="btn-primary text-xl px-12 py-6"
              onClick={handleStartDraft}
              disabled={isLoading}
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.97 }}
            >
              {isLoading ? (
                <span>INITIALIZING...</span>
              ) : (
                <>INSERT COIN TO START DRAFT</>
              )}
            </motion.button>
          </motion.div>

          {/* Error message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mt-8 px-6 py-4 border-4 border-accent-red bg-background text-accent-red text-lg font-heading uppercase tracking-widest"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>
        </section>

        {/* ── Stats Section ──────────────────────────────────────── */}
        <section className="w-full px-5 py-12 border-b-4 border-surface-border bg-background">
          <StatsRow />
        </section>

        {/* ── Features Section ───────────────────────────────────── */}
        <section className="w-full px-5 py-16 sm:py-24 bg-background">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9, duration: 0.5 }}
          >
            <h2 className="text-3xl sm:text-5xl font-heading font-black text-white uppercase tracking-widest">
              THE ULTIMATE EXPERIENCE
            </h2>
          </motion.div>
          <FeatureCards />
        </section>

        {/* ── Footer ─────────────────────────────────────────────── */}
        <footer className="w-full px-5 py-8 text-center border-t-4 border-surface-border bg-surface">
          <p className="text-text-muted font-heading tracking-widest uppercase text-sm">
            14-0 DRAFT SIMULATOR — POWERED BY MARKOV CHAINS
          </p>
        </footer>
      </main>
    </div>
  );
}
