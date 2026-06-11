"use client";

import { useCallback, useMemo, useEffect, Suspense } from "react";
import { motion, AnimatePresence } from "motion/react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";

import { useLeagueStore } from "@/store/leagueStore";
import { startLeague, getLeagueMatches, getMatchDetails } from "@/lib/api";
import type { LeagueMatch, ShareCardData } from "@/types/league";

import Scorecard from "@/components/Scorecard";
import BallTicker from "@/components/BallTicker";
import MatchCard from "@/components/MatchCard";
import SeasonDashboard from "@/components/SeasonDashboard";
import ShareCard from "@/components/ShareCard";

// ─── Progress bar for season ────────────────────────────────────────

function SeasonProgressBar({
  matches,
}: {
  matches: LeagueMatch[];
}) {
  const completed = matches.filter((m) => m.status === "completed").length;
  const wins = matches.filter((m) => m.winner === "user").length;
  const losses = matches.filter((m) => m.winner === "opponent").length;
  const pct = (completed / 14) * 100;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs">
        <span className="text-zinc-500">Season Progress</span>
        <div className="flex items-center gap-3">
          <span className="font-bold text-emerald-400">{wins}W</span>
          <span className="font-bold text-red-400">{losses}L</span>
          <span className="text-zinc-500">{completed}/14</span>
        </div>
      </div>
      <div className="relative h-1.5 overflow-hidden rounded-full bg-white/5">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-accent-gold to-amber-500"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

// ─── Tab Navigation ─────────────────────────────────────────────────

function ViewTabs({
  view,
  onViewChange,
  seasonComplete,
}: {
  view: string;
  onViewChange: (v: "matches" | "scorecard" | "dashboard") => void;
  seasonComplete: boolean;
}) {
  const tabs = [
    { key: "matches" as const, label: "Matches", icon: "🏏" },
    ...(seasonComplete
      ? [{ key: "dashboard" as const, label: "Dashboard", icon: "📊" }]
      : []),
  ];

  return (
    <div className="flex items-center gap-1 rounded-xl border border-white/8 bg-white/[0.02] p-1">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onViewChange(tab.key)}
          className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
            view === tab.key
              ? "bg-white/10 text-white shadow-sm"
              : "text-zinc-500 hover:text-zinc-300"
          }`}
        >
          <span>{tab.icon}</span>
          {tab.label}
        </button>
      ))}
    </div>
  );
}

// ─── Loading skeleton ───────────────────────────────────────────────

function MatchGridSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="h-24 animate-pulse rounded-xl border border-white/5 bg-white/[0.02]"
        />
      ))}
    </div>
  );
}

// ─── Empty state ────────────────────────────────────────────────────

function EmptyState({
  onStart,
  isPending,
}: {
  onStart: () => void;
  isPending: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      className="flex flex-col items-center justify-center py-20"
    >
      <motion.div
        className="mb-6 text-7xl"
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 3, repeat: Infinity }}
      >
        🏟️
      </motion.div>
      <h2 className="mb-3 text-center text-3xl font-black text-white">
        Start Your Season
      </h2>
      <p className="mb-8 max-w-md text-center text-sm text-zinc-400">
        Your Dream XI is ready. Simulate a 14-match league season and aim for
        the legendary{" "}
        <span className="font-bold text-accent-gold">14-0</span> record.
      </p>
      <motion.button
        id="start-league-button"
        onClick={onStart}
        disabled={isPending}
        className="btn-primary"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <motion.div
          className="absolute inset-0 -translate-x-full rounded-full bg-gradient-to-r from-transparent via-white/20 to-transparent"
          animate={{ translateX: ["-100%", "200%"] }}
          transition={{ duration: 2.5, repeat: Infinity, repeatDelay: 2 }}
        />
        <span className="relative z-10">
          {isPending ? "Simulating…" : "🏏 Simulate Season"}
        </span>
      </motion.button>
    </motion.div>
  );
}

// ─── League Page ────────────────────────────────────────────────────

function LeaguePageContent() {
  const store = useLeagueStore();
  const searchParams = useSearchParams();

  // Get draft session ID from URL params or store
  const draftSessionId =
    store.draftSessionId || searchParams.get("session") || null;

  // Sync URL param to store
  useEffect(() => {
    const urlSession = searchParams.get("session");
    if (urlSession && !store.draftSessionId) {
      store.setDraftSessionId(urlSession);
    }
  }, [searchParams, store]);

  // ── Data fetching ──────────────────────────────────────────

  const leagueQuery = useQuery({
    queryKey: ["league", draftSessionId],
    queryFn: () => getLeagueMatches(draftSessionId!),
    enabled: !!draftSessionId,
    refetchOnWindowFocus: false,
  });

  // Start league mutation
  const startMutation = useMutation({
    mutationFn: () => startLeague(draftSessionId!),
    onSuccess: (season) => {
      store.setSeason(season);
    },
    onError: (err) => {
      store.setError(`Failed to start league: ${err.message}`);
    },
  });

  // Update store when league data is fetched
  useEffect(() => {
    if (leagueQuery.data) {
      store.setSeason(leagueQuery.data);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [leagueQuery.data]);

  // ── Match detail fetch ─────────────────────────────────────

  const matchDetailQuery = useQuery({
    queryKey: ["match-detail", store.selectedMatch?.id],
    queryFn: () => getMatchDetails(store.selectedMatch!.id),
    enabled: !!store.selectedMatch?.id,
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    if (matchDetailQuery.data?.events) {
      store.setMatchEvents(matchDetailQuery.data.events);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [matchDetailQuery.data]);

  // ── Handlers ───────────────────────────────────────────────

  const handleStartLeague = useCallback(() => {
    if (!draftSessionId) {
      store.setError("No draft session found. Complete a draft first.");
      return;
    }
    startMutation.mutate();
  }, [draftSessionId, startMutation, store]);

  const handleSelectMatch = useCallback(
    (match: LeagueMatch) => {
      store.selectMatch(match);
    },
    [store]
  );

  const handleCloseScorecard = useCallback(() => {
    store.clearSelection();
  }, [store]);

  const handleViewDashboard = useCallback(() => {
    store.setView("dashboard");
  }, [store]);

  // ── Computed values ────────────────────────────────────────

  const seasonComplete = store.getSeasonComplete();
  const isPerfect = store.isPerfectSeason();

  const shareData: ShareCardData | null = useMemo(() => {
    if (!seasonComplete || store.matches.length === 0) return null;
    const completedMatches = store.matches.filter(
      (m) => m.status === "completed"
    );
    return {
      teamName: store.matches[0]?.user_team || "Dream XI",
      wins: store.getWins(),
      losses: store.getLosses(),
      ties: store.getTies(),
      totalRuns: completedMatches.reduce((s, m) => s + m.user_score, 0),
      totalWickets: completedMatches.reduce((s, m) => s + m.user_wickets, 0),
      bestScore: `${Math.max(...completedMatches.map((m) => m.user_score))}`,
      isPerfect,
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seasonComplete, isPerfect]);

  // ── Render ─────────────────────────────────────────────────

  const hasMatches = store.matches.length > 0;

  return (
    <div className="relative min-h-screen bg-background text-white">
      {/* Background effects */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute left-1/4 top-0 h-[600px] w-[600px] rounded-full bg-accent-blue/[0.03] blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 h-[500px] w-[500px] rounded-full bg-accent-purple/[0.03] blur-[120px]" />
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-[400px] w-[400px] rounded-full bg-accent-gold/[0.02] blur-[100px]" />
        <div
          className="absolute inset-0 opacity-[0.012]"
          style={{
            backgroundImage:
              "radial-gradient(rgba(255,255,255,0.3) 1px, transparent 1px)",
            backgroundSize: "32px 32px",
          }}
        />
      </div>

      {/* Main content */}
      <div className="relative z-10 mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-400 bg-clip-text text-2xl font-black tracking-tight text-transparent sm:text-3xl">
                14-0
              </h1>
              <span className="rounded-full border border-accent-blue/30 bg-accent-blue/10 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-accent-blue">
                Season
              </span>
            </div>
            <p className="mt-1 text-xs text-zinc-500">
              {hasMatches
                ? `${store.matches.filter((m) => m.status === "completed").length} matches played`
                : "Simulate your 14-match league season"}
            </p>
          </div>

          <div className="flex items-center gap-2">
            {hasMatches && (
              <ViewTabs
                view={store.view}
                onViewChange={store.setView}
                seasonComplete={seasonComplete}
              />
            )}
            {seasonComplete && store.view !== "dashboard" && (
              <motion.button
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                onClick={handleViewDashboard}
                className="flex items-center gap-1.5 rounded-xl border border-accent-gold/30 bg-accent-gold/10 px-3 py-1.5 text-xs font-bold text-accent-gold transition-all hover:bg-accent-gold/20"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                📊 Season Summary
              </motion.button>
            )}
          </div>
        </header>

        {/* Error toast */}
        <AnimatePresence>
          {store.error && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300"
            >
              <div className="flex items-center justify-between">
                <span>{store.error}</span>
                <button
                  onClick={() => store.setError(null)}
                  className="ml-4 text-red-400 hover:text-red-200"
                >
                  ✕
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Season progress */}
        {hasMatches && store.view !== "dashboard" && (
          <div className="mb-6">
            <SeasonProgressBar matches={store.matches} />
          </div>
        )}

        {/* Loading state */}
        {(leagueQuery.isLoading || startMutation.isPending) && (
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-sm text-zinc-400">
              <motion.div
                className="h-4 w-4 rounded-full border-2 border-accent-gold border-t-transparent"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
              {startMutation.isPending
                ? "Simulating your 14-match season…"
                : "Loading league data…"}
            </div>
            <MatchGridSkeleton />
          </div>
        )}

        {/* Empty state — no matches yet */}
        {!hasMatches &&
          !leagueQuery.isLoading &&
          !startMutation.isPending && (
            <EmptyState
              onStart={handleStartLeague}
              isPending={startMutation.isPending}
            />
          )}

        {/* ── MATCHES VIEW ───────────────────────────────────── */}
        {hasMatches && store.view === "matches" && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              <AnimatePresence>
                {store.matches.map((match, idx) => (
                  <MatchCard
                    key={match.id || match.match_number}
                    match={match}
                    onSelect={handleSelectMatch}
                    index={idx}
                  />
                ))}
              </AnimatePresence>
            </div>
          </motion.div>
        )}

        {/* ── SCORECARD VIEW ─────────────────────────────────── */}
        <AnimatePresence>
          {store.view === "scorecard" && store.selectedMatch && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              {/* Back button */}
              <button
                onClick={handleCloseScorecard}
                className="flex items-center gap-1.5 text-xs text-zinc-500 transition-colors hover:text-white"
              >
                ← Back to Matches
              </button>

              {/* Scorecard */}
              <Scorecard
                match={store.selectedMatch}
                onClose={handleCloseScorecard}
              />

              {/* Ball-by-ball ticker */}
              <div>
                {matchDetailQuery.isLoading ? (
                  <div className="flex items-center gap-2 rounded-xl border border-white/8 bg-white/[0.02] p-6 text-sm text-zinc-500">
                    <motion.div
                      className="h-4 w-4 rounded-full border-2 border-accent-gold border-t-transparent"
                      animate={{ rotate: 360 }}
                      transition={{
                        duration: 1,
                        repeat: Infinity,
                        ease: "linear",
                      }}
                    />
                    Loading ball-by-ball data…
                  </div>
                ) : (
                  <BallTicker events={store.selectedMatchEvents} />
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── DASHBOARD VIEW ─────────────────────────────────── */}
        {store.view === "dashboard" && hasMatches && (
          <div className="space-y-8">
            <SeasonDashboard
              matches={store.matches}
              onBack={() => store.setView("matches")}
            />

            {/* Share card */}
            {shareData && (
              <div className="border-t border-white/5 pt-8">
                <ShareCard data={shareData} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function LeaguePage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center text-white">Loading...</div>}>
      <LeaguePageContent />
    </Suspense>
  );
}
