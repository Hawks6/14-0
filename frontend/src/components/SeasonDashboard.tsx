"use client";

import { useMemo } from "react";
import { motion, AnimatePresence } from "motion/react";
import type { LeagueMatch, StandingsEntry } from "@/types/league";

// ─── Generate standings from matches ────────────────────────────────

function computeStandings(matches: LeagueMatch[]): StandingsEntry[] {
  const completedMatches = matches.filter((m) => m.status === "completed");

  // User team entry
  const userWins = completedMatches.filter((m) => m.winner === "user").length;
  const userLosses = completedMatches.filter((m) => m.winner === "opponent").length;
  const userTies = completedMatches.filter((m) => m.winner === "tie").length;

  // Calculate NRR (simplified: total runs scored / overs faced - runs conceded / overs bowled)
  const userRunsScored = completedMatches.reduce((s, m) => s + m.user_score, 0);
  const userRunsConceded = completedMatches.reduce((s, m) => s + m.opponent_score, 0);
  const totalOvers = completedMatches.length * 20; // T20 format
  const userNRR =
    totalOvers > 0
      ? (userRunsScored / totalOvers - userRunsConceded / totalOvers) * 20
      : 0;

  const userEntry: StandingsEntry = {
    team: "Your Dream XI",
    played: completedMatches.length,
    won: userWins,
    lost: userLosses,
    tied: userTies,
    points: userWins * 2 + userTies,
    nrr: Math.round(userNRR * 1000) / 1000,
    isUser: true,
  };

  // Generate simulated opponent entries for standings context
  const opponentTeams = [
    "Mumbai Indians",
    "Chennai Super Kings",
    "Royal Challengers",
    "Kolkata Knight Riders",
    "Delhi Capitals",
    "Rajasthan Royals",
    "Punjab Kings",
    "Sunrisers Hyderabad",
    "Gujarat Titans",
  ];

  const opponents: StandingsEntry[] = opponentTeams.map((team, i) => {
    // Create plausible W/L records based on position
    const baseWins = Math.max(0, 14 - Math.floor(i * 1.5) - Math.floor(Math.random() * 3));
    const won = Math.min(14, baseWins);
    const lost = 14 - won;
    return {
      team,
      played: 14,
      won,
      lost,
      tied: 0,
      points: won * 2,
      nrr: Math.round((Math.random() * 2 - 0.5) * 1000) / 1000,
      isUser: false,
    };
  });

  const all = [userEntry, ...opponents];
  all.sort((a, b) => {
    if (b.points !== a.points) return b.points - a.points;
    return b.nrr - a.nrr;
  });

  return all;
}

// ─── Season stat card ───────────────────────────────────────────────

function StatCard({
  label,
  value,
  sub,
  color,
  delay,
}: {
  label: string;
  value: string | number;
  sub?: string;
  color: string;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, type: "spring", stiffness: 300, damping: 25 }}
      className="flex flex-col items-center gap-1 rounded-xl border border-white/8 bg-white/[0.02] p-4"
    >
      <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
        {label}
      </span>
      <span className={`text-2xl font-black tabular-nums ${color}`}>
        {value}
      </span>
      {sub && <span className="text-[10px] text-zinc-500">{sub}</span>}
    </motion.div>
  );
}

// ─── Confetti particle ──────────────────────────────────────────────

function ConfettiParticle({ index }: { index: number }) {
  const colors = [
    "bg-amber-400",
    "bg-emerald-400",
    "bg-blue-400",
    "bg-purple-400",
    "bg-pink-400",
    "bg-cyan-400",
  ];
  const color = colors[index % colors.length];
  const left = `${Math.random() * 100}%`;
  const delay = Math.random() * 3;
  const duration = 2 + Math.random() * 3;
  const size = 4 + Math.random() * 6;

  return (
    <motion.div
      className={`absolute rounded-sm ${color}`}
      style={{
        left,
        top: "-5%",
        width: `${size}px`,
        height: `${size * 0.6}px`,
      }}
      initial={{ y: "-10vh", rotate: 0, opacity: 1 }}
      animate={{
        y: "110vh",
        rotate: 720,
        opacity: [1, 1, 0],
      }}
      transition={{
        duration,
        delay,
        repeat: Infinity,
        ease: "linear",
      }}
    />
  );
}

// ─── Perfect season celebration ─────────────────────────────────────

function PerfectCelebration() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      className="relative overflow-hidden rounded-2xl border-2 border-amber-500/40 bg-gradient-to-br from-amber-500/10 via-yellow-500/5 to-amber-500/10 p-8 text-center"
    >
      {/* Confetti background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        {Array.from({ length: 30 }).map((_, i) => (
          <ConfettiParticle key={i} index={i} />
        ))}
      </div>

      {/* Pulsing glow */}
      <motion.div
        className="absolute inset-0 rounded-2xl"
        style={{ boxShadow: "inset 0 0 60px rgba(245,197,24,0.1)" }}
        animate={{
          boxShadow: [
            "inset 0 0 60px rgba(245,197,24,0.05)",
            "inset 0 0 80px rgba(245,197,24,0.15)",
            "inset 0 0 60px rgba(245,197,24,0.05)",
          ],
        }}
        transition={{ duration: 2, repeat: Infinity }}
      />

      {/* Content */}
      <div className="relative z-10">
        <motion.div
          className="mb-4 text-6xl"
          animate={{ scale: [1, 1.15, 1], rotate: [0, -5, 5, 0] }}
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
        >
          🏆
        </motion.div>

        <motion.h2
          className="mb-2 bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-400 bg-clip-text text-4xl font-black text-transparent sm:text-5xl"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          14-0 ACHIEVED!
        </motion.h2>

        <motion.p
          className="text-sm text-amber-300/80"
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          The perfect season. Every match won. Unstoppable. Legendary.
        </motion.p>
      </div>
    </motion.div>
  );
}

// ─── Standings table ────────────────────────────────────────────────

function StandingsTable({ standings }: { standings: StandingsEntry[] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-white/8">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-white/8 bg-white/[0.03]">
            <th className="px-3 py-2.5 text-left font-semibold uppercase tracking-wider text-zinc-500">
              #
            </th>
            <th className="px-3 py-2.5 text-left font-semibold uppercase tracking-wider text-zinc-500">
              Team
            </th>
            <th className="px-3 py-2.5 text-center font-semibold uppercase tracking-wider text-zinc-500">
              P
            </th>
            <th className="px-3 py-2.5 text-center font-semibold uppercase tracking-wider text-zinc-500">
              W
            </th>
            <th className="px-3 py-2.5 text-center font-semibold uppercase tracking-wider text-zinc-500">
              L
            </th>
            <th className="px-3 py-2.5 text-center font-semibold uppercase tracking-wider text-zinc-500">
              Pts
            </th>
            <th className="hidden px-3 py-2.5 text-right font-semibold uppercase tracking-wider text-zinc-500 sm:table-cell">
              NRR
            </th>
          </tr>
        </thead>
        <tbody>
          <AnimatePresence>
            {standings.map((entry, idx) => (
              <motion.tr
                key={entry.team}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.03 }}
                className={`border-b border-white/5 transition-colors ${
                  entry.isUser
                    ? "bg-accent-gold/5 hover:bg-accent-gold/10"
                    : "hover:bg-white/[0.02]"
                }`}
              >
                <td className="px-3 py-2.5 font-bold text-zinc-400">
                  {idx + 1}
                </td>
                <td className="px-3 py-2.5">
                  <span
                    className={`font-semibold ${
                      entry.isUser ? "text-accent-gold" : "text-white"
                    }`}
                  >
                    {entry.team}
                    {entry.isUser && (
                      <span className="ml-1.5 text-[9px] font-bold uppercase text-accent-gold/60">
                        YOU
                      </span>
                    )}
                  </span>
                </td>
                <td className="px-3 py-2.5 text-center text-zinc-400">
                  {entry.played}
                </td>
                <td className="px-3 py-2.5 text-center font-bold text-emerald-400">
                  {entry.won}
                </td>
                <td className="px-3 py-2.5 text-center font-bold text-red-400">
                  {entry.lost}
                </td>
                <td className="px-3 py-2.5 text-center font-black text-white">
                  {entry.points}
                </td>
                <td
                  className={`hidden px-3 py-2.5 text-right font-mono text-[11px] sm:table-cell ${
                    entry.nrr >= 0 ? "text-emerald-400" : "text-red-400"
                  }`}
                >
                  {entry.nrr >= 0 ? "+" : ""}
                  {entry.nrr.toFixed(3)}
                </td>
              </motion.tr>
            ))}
          </AnimatePresence>
        </tbody>
      </table>
    </div>
  );
}

// ─── SeasonDashboard Component ──────────────────────────────────────

interface SeasonDashboardProps {
  matches: LeagueMatch[];
  onBack?: () => void;
}

export default function SeasonDashboard({
  matches,
  onBack,
}: SeasonDashboardProps) {
  const completedMatches = matches.filter((m) => m.status === "completed");
  const wins = completedMatches.filter((m) => m.winner === "user").length;
  const losses = completedMatches.filter((m) => m.winner === "opponent").length;
  const ties = completedMatches.filter((m) => m.winner === "tie").length;
  const points = wins * 2 + ties;
  const isPerfect = wins === 14 && completedMatches.length === 14;

  const totalRuns = completedMatches.reduce((s, m) => s + m.user_score, 0);
  const totalWickets = completedMatches.reduce(
    (s, m) => s + m.user_wickets,
    0
  );
  const bestScore = completedMatches.length > 0
    ? Math.max(...completedMatches.map((m) => m.user_score))
    : 0;
  const highestChase = completedMatches
    .filter(
      (m) =>
        m.winner === "user" &&
        m.user_score > m.opponent_score
    )
    .reduce((max, m) => Math.max(max, m.user_score), 0);

  const standings = useMemo(() => computeStandings(matches), [matches]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-black text-white sm:text-2xl">
            Season Dashboard
          </h2>
          <p className="text-xs text-zinc-500">
            {completedMatches.length} of 14 matches completed
          </p>
        </div>
        {onBack && (
          <motion.button
            onClick={onBack}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="rounded-lg border border-white/8 bg-white/[0.03] px-3 py-1.5 text-xs text-zinc-400 hover:border-white/15 hover:text-white transition-all"
          >
            ← Back to Matches
          </motion.button>
        )}
      </div>

      {/* Perfect season celebration */}
      {isPerfect && <PerfectCelebration />}

      {/* Season stats grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard
          label="Record"
          value={`${wins}-${losses}`}
          sub={ties > 0 ? `${ties} ties` : undefined}
          color={
            wins > losses
              ? "text-emerald-400"
              : wins < losses
              ? "text-red-400"
              : "text-zinc-300"
          }
          delay={0}
        />
        <StatCard
          label="Points"
          value={points}
          sub={`of ${completedMatches.length * 2}`}
          color="text-accent-gold"
          delay={0.05}
        />
        <StatCard
          label="Total Runs"
          value={totalRuns}
          sub={`${completedMatches.length} innings`}
          color="text-blue-400"
          delay={0.1}
        />
        <StatCard
          label="Best Score"
          value={bestScore}
          sub={highestChase > 0 ? `Chase: ${highestChase}` : undefined}
          color="text-purple-400"
          delay={0.15}
        />
      </div>

      {/* Win/Loss visualizer */}
      <div className="rounded-xl border border-white/8 bg-white/[0.02] p-4">
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-500">
          Match Results
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {matches.map((m, i) => (
            <motion.div
              key={m.match_number}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.03 }}
              className={`flex h-8 w-8 items-center justify-center rounded-lg text-[10px] font-bold ${
                m.status !== "completed"
                  ? "border border-dashed border-zinc-700 text-zinc-600"
                  : m.winner === "user"
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : m.winner === "opponent"
                  ? "bg-red-500/20 text-red-400 border border-red-500/30"
                  : "bg-zinc-500/20 text-zinc-400 border border-zinc-500/30"
              }`}
              title={`Match ${m.match_number}: ${
                m.status !== "completed"
                  ? "Not played"
                  : m.winner === "user"
                  ? "Won"
                  : m.winner === "opponent"
                  ? "Lost"
                  : "Tied"
              }`}
            >
              {m.match_number}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Standings table */}
      <div>
        <h3 className="mb-3 text-sm font-bold text-white">
          League Standings
        </h3>
        <StandingsTable standings={standings} />
      </div>
    </motion.div>
  );
}
