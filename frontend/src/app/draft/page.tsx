"use client";

import { useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "motion/react";
import { useMutation } from "@tanstack/react-query";

import { useDraftStore } from "@/store/draftStore";
import { createDraftSession, triggerSpin, pickPlayer } from "@/lib/api";
import SpinWheel from "@/components/SpinWheel";
import DraftBoard from "@/components/DraftBoard";
import PlayerCard from "@/components/PlayerCard";
import { SpinResult, Player, MAX_BUDGET } from "@/types/draft";

// ─── Draft Page ─────────────────────────────────────────────────────

export default function DraftPage() {
  const store = useDraftStore();

  // ── Mutations ──────────────────────────────────────────────

  const createSession = useMutation({
    mutationFn: createDraftSession,
    onSuccess: (session) => {
      store.initSession(session.id, session.budget_remaining);
    },
    onError: (err) => {
      store.setError(`Failed to create session: ${err.message}`);
    },
  });

  const spinMutation = useMutation({
    mutationFn: () => triggerSpin(store.sessionId!),
    onError: (err) => {
      store.setError(`Spin failed: ${err.message}`);
      store.setPhase("READY");
      store.setAnimating(false);
    },
  });

  const pickMutation = useMutation({
    mutationFn: (playerSeasonId: string) =>
      pickPlayer(store.sessionId!, playerSeasonId),
    onSuccess: (session) => {
      const player = store.selectedPlayer!;
      store.confirmPick(player, session.budget_remaining);
    },
    onError: (err) => {
      store.setError(`Pick failed: ${err.message}`);
    },
  });

  // ── Handlers ───────────────────────────────────────────────

  const handleStartDraft = useCallback(() => {
    createSession.mutate();
  }, [createSession]);

  const handleSpinStart = useCallback(() => {
    store.startSpin();
    spinMutation.mutate();
  }, [store, spinMutation]);

  const handleSpinComplete = useCallback(
    (result: SpinResult) => {
      store.completeSpin(result);
    },
    [store]
  );

  const handleSelectPlayer = useCallback(
    (player: Player) => {
      store.selectPlayer(
        store.selectedPlayer?.player_season_id === player.player_season_id
          ? null
          : player
      );
    },
    [store]
  );

  const handleConfirmPick = useCallback(() => {
    if (!store.selectedPlayer) return;
    pickMutation.mutate(store.selectedPlayer.player_season_id);
  }, [store.selectedPlayer, pickMutation]);

  const overseasCount = useMemo(() => store.getOverseasCount(), [store.roster]);

  // ── Render ─────────────────────────────────────────────────

  return (
    <div className="relative min-h-screen bg-[#0a0a12] text-white">
      {/* Background effects */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute left-1/4 top-0 h-[600px] w-[600px] rounded-full bg-amber-500/[0.03] blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 h-[500px] w-[500px] rounded-full bg-purple-500/[0.03] blur-[120px]" />
        <div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage:
              "radial-gradient(rgba(255,255,255,0.3) 1px, transparent 1px)",
            backgroundSize: "32px 32px",
          }}
        />
      </div>

      {/* Main content */}
      <div className="relative z-10 mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Top bar */}
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="bg-gradient-to-r from-amber-300 via-yellow-200 to-amber-400 bg-clip-text text-2xl font-black tracking-tight text-transparent sm:text-3xl">
              14-0
            </h1>
            <p className="text-xs text-zinc-500">IPL Draft Simulator</p>
          </div>
          {store.phase !== "IDLE" && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              onClick={() => store.reset()}
              className="rounded-lg border border-white/8 bg-white/[0.03] px-3 py-1.5 text-xs text-zinc-400 hover:border-white/15 hover:bg-white/[0.06] hover:text-white transition-all"
            >
              Reset Draft
            </motion.button>
          )}
        </header>

        {/* Error toast */}
        <AnimatePresence>
          {store.errorMessage && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-6 rounded-xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-300"
            >
              <div className="flex items-center justify-between">
                <span>{store.errorMessage}</span>
                <button
                  onClick={() => store.setError(null)}
                  className="ml-4 text-rose-400 hover:text-rose-200"
                >
                  ✕
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* IDLE: Start screen */}
        {store.phase === "IDLE" && (
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
            className="flex flex-col items-center justify-center py-20"
          >
            <motion.div
              className="mb-8 text-7xl"
              animate={{ rotate: [0, -10, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            >
              🏏
            </motion.div>
            <h2 className="mb-3 text-center text-3xl font-black text-white sm:text-4xl">
              Build Your Dream XI
            </h2>
            <p className="mb-8 max-w-md text-center text-sm text-zinc-400">
              Spin to discover a random IPL franchise and era. Draft 11 players
              within 100 credits to build the ultimate squad. Go{" "}
              <span className="font-bold text-amber-400">14-0</span>.
            </p>
            <motion.button
              id="start-draft-button"
              onClick={handleStartDraft}
              disabled={createSession.isPending}
              className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-500 px-8 py-4 text-sm font-bold uppercase tracking-widest text-black shadow-[0_0_30px_rgba(245,158,11,0.2)] transition-all hover:shadow-[0_0_50px_rgba(245,158,11,0.3)] disabled:opacity-50"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <motion.div
                className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent"
                animate={{ translateX: ["-100%", "200%"] }}
                transition={{ duration: 2.5, repeat: Infinity, repeatDelay: 2 }}
              />
              <span className="relative z-10">
                {createSession.isPending ? "Creating Session…" : "Start Draft"}
              </span>
            </motion.button>
          </motion.div>
        )}

        {/* ACTIVE DRAFT: Spin + Board + Pool */}
        {store.phase !== "IDLE" && store.phase !== "COMPLETE" && (
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_340px]">
            {/* Left: Spin + Pool */}
            <div className="flex flex-col gap-8">
              {/* Spin area — show when READY or SPINNING */}
              {(store.phase === "READY" || store.phase === "SPINNING") && (
                <SpinWheel
                  onSpinStart={handleSpinStart}
                  onSpinComplete={handleSpinComplete}
                  isSpinning={store.phase === "SPINNING"}
                  disabled={store.phase !== "READY"}
                  spinResult={spinMutation.data || null}
                />
              )}

              {/* Player Pool — show when POOL */}
              {store.phase === "POOL" && store.currentSpin && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.3 }}
                >
                  {/* Pool header */}
                  <div className="mb-4 flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-white">
                        {store.currentSpin.franchise_name}
                        <span className="ml-2 text-sm font-normal text-zinc-500">
                          {store.currentSpin.year}
                        </span>
                      </h3>
                      <p className="text-xs text-zinc-500">
                        Select a player to draft
                      </p>
                    </div>
                    {store.selectedPlayer && (
                      <motion.button
                        id="confirm-pick-button"
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={handleConfirmPick}
                        disabled={pickMutation.isPending}
                        className="rounded-xl bg-gradient-to-r from-emerald-500 to-green-500 px-5 py-2.5 text-sm font-bold text-white shadow-[0_0_20px_rgba(16,185,129,0.2)] transition-all hover:shadow-[0_0_30px_rgba(16,185,129,0.3)] disabled:opacity-50"
                      >
                        {pickMutation.isPending ? (
                          <span className="flex items-center gap-2">
                            <motion.span
                              animate={{ rotate: 360 }}
                              transition={{
                                duration: 1,
                                repeat: Infinity,
                                ease: "linear",
                              }}
                            >
                              ⏳
                            </motion.span>
                            Drafting…
                          </span>
                        ) : (
                          `Draft ${store.selectedPlayer.name}`
                        )}
                      </motion.button>
                    )}
                  </div>

                  {/* Player grid */}
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
                    <AnimatePresence>
                      {store.poolPlayers.map((player, idx) => (
                        <PlayerCard
                          key={player.player_season_id}
                          player={player}
                          onSelect={handleSelectPlayer}
                          isSelected={
                            store.selectedPlayer?.player_season_id ===
                            player.player_season_id
                          }
                          canPick={store.canPickPlayer(player)}
                          index={idx}
                        />
                      ))}
                    </AnimatePresence>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Right sidebar: Draft Board */}
            <div className="lg:sticky lg:top-6 lg:self-start">
              <div className="rounded-2xl border border-white/8 bg-white/[0.02] p-4 backdrop-blur-sm">
                <DraftBoard
                  roster={store.roster}
                  budgetRemaining={store.budgetRemaining}
                  overseasCount={overseasCount}
                  picksCount={store.picksCount}
                />
              </div>
            </div>
          </div>
        )}

        {/* COMPLETE */}
        {store.phase === "COMPLETE" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
            className="flex flex-col items-center py-12"
          >
            <motion.div
              className="mb-6 text-6xl"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.6, repeat: 3 }}
            >
              🏆
            </motion.div>
            <h2 className="mb-2 text-3xl font-black text-amber-400">
              Squad Complete!
            </h2>
            <p className="mb-8 text-sm text-zinc-400">
              Your Dream XI is ready. Budget remaining:{" "}
              <span className="font-bold text-amber-300">
                {store.budgetRemaining} credits
              </span>
            </p>

            {/* Final roster display */}
            <div className="w-full max-w-lg">
              <div className="rounded-2xl border border-white/8 bg-white/[0.02] p-4 backdrop-blur-sm">
                <DraftBoard
                  roster={store.roster}
                  budgetRemaining={store.budgetRemaining}
                  overseasCount={overseasCount}
                  picksCount={store.picksCount}
                />
              </div>
            </div>

            <motion.button
              onClick={() => store.reset()}
              className="mt-8 rounded-xl border border-amber-500/30 bg-amber-500/10 px-6 py-3 text-sm font-bold text-amber-400 transition-all hover:bg-amber-500/20"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Draft Again
            </motion.button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
