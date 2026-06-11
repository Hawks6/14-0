"use client";

import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { createDraftSession } from "@/lib/api";
import { useDraftStore } from "@/store/draftStore";

/* ═══════════════════════════════════════════════════════════════════════
   14-0 Landing Page
   Premium hero with animated gradient, glassmorphism cards,
   smooth entrance animations, and a "Start Draft" CTA.
   ═══════════════════════════════════════════════════════════════════════ */

// ─── Floating Particle Component ─────────────────────────────────────
function FloatingParticles() {
  const particles = Array.from({ length: 24 }, (_, i) => ({
    id: i,
    size: Math.random() * 3 + 1,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 8,
    duration: Math.random() * 6 + 8,
    opacity: Math.random() * 0.3 + 0.1,
  }));

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
    title: "Spin & Draft",
    description:
      "Spin for a random historical franchise era. Draft legendary players within a strict 100-credit salary cap.",
    icon: "🎰",
    gradient: "from-accent-gold/20 to-accent-orange/10",
    borderGlow: "hover:border-accent-gold/30",
  },
  {
    title: "Build Your XI",
    description:
      "Fill 11 roster slots with role constraints — 1 WK, 3+ bowlers, max 4 overseas. Strategy matters.",
    icon: "📋",
    gradient: "from-accent-blue/20 to-accent-cyan/10",
    borderGlow: "hover:border-accent-blue/30",
  },
  {
    title: "Simulate & Conquer",
    description:
      "Watch your squad compete through 14 probabilistically-rigorous matches. Can you go 14-0?",
    icon: "⚡",
    gradient: "from-accent-purple/20 to-accent-pink/10",
    borderGlow: "hover:border-accent-purple/30",
  },
];

function FeatureCards() {
  return (
    <motion.div
      className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 w-full max-w-4xl mx-auto"
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: 0.15, delayChildren: 1.0 } },
      }}
    >
      {features.map((feature) => (
        <motion.div
          key={feature.title}
          className={`glass-card p-6 sm:p-8 cursor-default group ${feature.borderGlow}`}
          variants={{
            hidden: { opacity: 0, y: 30 },
            visible: { opacity: 1, y: 0 },
          }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          whileHover={{ scale: 1.02 }}
        >
          {/* Gradient overlay inside card */}
          <div
            className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} rounded-[var(--radius-lg)] opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
          />
          <div className="relative z-10">
            <span className="text-3xl sm:text-4xl mb-4 block">{feature.icon}</span>
            <h3 className="text-lg font-bold font-heading text-text-primary mb-2">
              {feature.title}
            </h3>
            <p className="text-sm text-text-secondary leading-relaxed">
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
    <div className="relative flex flex-col min-h-screen overflow-hidden">
      {/* ── Animated Background ─────────────────────────────────── */}
      <div className="animated-gradient-bg fixed inset-0 z-0" />
      <FloatingParticles />

      {/* ── Noise texture ────────────────────────────────────────── */}
      <div className="noise-overlay fixed inset-0 z-[1] pointer-events-none" />

      {/* ── Radial glow behind hero ──────────────────────────────── */}
      <div className="hero-glow fixed left-1/2 top-1/3 -translate-x-1/2 -translate-y-1/2 z-[2]" />

      {/* ── Content ──────────────────────────────────────────────── */}
      <main className="relative z-10 flex flex-col items-center flex-1">
        {/* ── Hero Section ───────────────────────────────────────── */}
        <section className="flex flex-col items-center justify-center text-center px-5 pt-20 sm:pt-28 md:pt-36 pb-10 sm:pb-16 w-full">
          {/* Tagline chip */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mb-6"
          >
            <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase bg-accent-gold/10 text-accent-gold border border-accent-gold/20">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-gold animate-pulse" />
              IPL Draft Simulator
            </span>
          </motion.div>

          {/* Main Title */}
          <motion.h1
            className="font-heading font-black tracking-tighter leading-none"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
          >
            <span className="block text-6xl sm:text-8xl md:text-9xl bg-gradient-to-r from-accent-gold via-accent-orange-warm to-accent-gold bg-clip-text text-transparent">
              14-0
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            className="mt-4 sm:mt-6 text-lg sm:text-xl md:text-2xl text-text-secondary max-w-xl font-body leading-relaxed"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
          >
            Draft legendary squads. Simulate perfection.
            <br />
            <span className="text-text-muted text-base sm:text-lg">
              Can you go unbeaten across 14 matches?
            </span>
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            className="mt-8 sm:mt-10 flex flex-col sm:flex-row gap-4 items-center"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <motion.button
              id="start-draft-btn"
              className="btn-primary text-base sm:text-lg px-8 sm:px-10 py-4"
              onClick={handleStartDraft}
              disabled={isLoading}
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.97 }}
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <motion.span
                    className="w-5 h-5 border-2 border-current border-t-transparent rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
                  />
                  Creating Draft…
                </span>
              ) : (
                <>
                  🏏 Start Draft
                </>
              )}
            </motion.button>

            <motion.button
              className="btn-secondary"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              How it Works ↓
            </motion.button>
          </motion.div>

          {/* Error message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mt-4 px-4 py-2 rounded-lg bg-accent-red/10 border border-accent-red/20 text-accent-red text-sm max-w-md"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>
        </section>

        {/* ── Stats Section ──────────────────────────────────────── */}
        <section className="w-full px-5 py-6 sm:py-10">
          <StatsRow />
        </section>

        {/* ── Features Section ───────────────────────────────────── */}
        <section className="w-full px-5 py-10 sm:py-16">
          <motion.div
            className="text-center mb-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9, duration: 0.5 }}
          >
            <h2 className="text-2xl sm:text-3xl font-heading font-bold text-text-primary">
              The Ultimate IPL Experience
            </h2>
            <p className="mt-2 text-text-secondary text-sm sm:text-base">
              Three steps to fantasy cricket glory
            </p>
          </motion.div>
          <FeatureCards />
        </section>

        {/* ── Bottom CTA ─────────────────────────────────────────── */}
        <section className="w-full px-5 py-16 sm:py-24">
          <motion.div
            className="glass-card max-w-2xl mx-auto p-8 sm:p-12 text-center relative overflow-hidden"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.3, duration: 0.7 }}
          >
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-accent-gold/5 via-transparent to-accent-purple/5 rounded-[var(--radius-lg)]" />
            <div className="relative z-10">
              <h2 className="text-2xl sm:text-3xl font-heading font-bold text-text-primary mb-3">
                Ready to Chase Perfection?
              </h2>
              <p className="text-text-secondary mb-6 max-w-md mx-auto text-sm sm:text-base">
                Draft your dream XI from historical IPL squads and simulate an
                entire 14-match season. The odds are against you.
              </p>
              <motion.button
                id="bottom-start-draft-btn"
                className="btn-primary"
                onClick={handleStartDraft}
                disabled={isLoading}
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.97 }}
              >
                {isLoading ? "Starting…" : "🎯 Begin Your Campaign"}
              </motion.button>
            </div>
          </motion.div>
        </section>

        {/* ── Footer ─────────────────────────────────────────────── */}
        <footer className="w-full px-5 py-8 text-center border-t border-surface-border/30">
          <p className="text-text-muted text-xs">
            14-0 IPL Draft & Simulation Platform — A game of skill, powered by
            Markov chain simulation
          </p>
        </footer>
      </main>
    </div>
  );
}
