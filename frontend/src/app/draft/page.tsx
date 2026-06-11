"use client";

import { useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "motion/react";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { useDraftStore } from "@/store/draftStore";
import { createDraftSession, triggerSpin, pickPlayer } from "@/lib/api";
import SpinWheel from "@/components/SpinWheel";
import DraftBoard from "@/components/DraftBoard";
import PlayerCard from "@/components/PlayerCard";
import LivePitchArt from "@/components/LivePitchArt";
import { SpinResult, Player, MAX_BUDGET } from "@/types/draft";

// ─── Draft Page ─────────────────────────────────────────────────────

export default function DraftPage() {
  const store = useDraftStore();
  const router = useRouter();

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

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const overseasCount = useMemo(() => store.getOverseasCount(), [store.roster]);

  // ── Render ─────────────────────────────────────────────────

  return (
    <div className="relative min-h-screen bg-background text-text-primary font-body">
      {/* Background pattern */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: "radial-gradient(var(--text-secondary) 1px, transparent 1px)",
            backgroundSize: "32px 32px",
          }}
        />
      </div>

      {/* Main content */}
      <div className="relative z-10 w-full h-screen flex flex-col px-4 py-4 sm:px-6 lg:px-8">
        {/* Top bar */}
        <header className="mb-8 flex items-center justify-between border-b-4 border-surface-border pb-4 bg-surface px-6">
          <div>
            <h1 className="text-4xl font-heading font-black tracking-widest text-accent-gold uppercase">
              14-0
            </h1>
          </div>
          {store.phase !== "IDLE" && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              onClick={() => store.reset()}
              className="btn-secondary text-sm"
            >
              RESET DRAFT
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
              className="mb-6 border-4 border-accent-red bg-background px-4 py-3 text-sm text-accent-red font-heading tracking-wide uppercase"
            >
              <div className="flex items-center justify-between">
                <span>{store.errorMessage}</span>
                <button
                  onClick={() => store.setError(null)}
                  className="ml-4 hover:text-white"
                >
                  [ X ]
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
            className="flex flex-col items-center justify-center py-20 border-4 border-surface-border bg-surface mt-10"
          >
            <motion.div
              className="mb-8 text-7xl"
              animate={{ rotate: [0, -10, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            >
              🏏
            </motion.div>
            <h2 className="mb-4 text-center text-5xl font-heading font-black text-white uppercase tracking-widest">
              BUILD YOUR DREAM XI
            </h2>
            <p className="mb-10 max-w-lg text-center text-lg text-text-secondary font-body uppercase tracking-wide leading-relaxed px-4">
              SPIN TO DISCOVER A RANDOM FRANCHISE AND ERA. DRAFT 11 PLAYERS
              WITHIN 100 CREDITS TO BUILD THE ULTIMATE SQUAD. GO{" "}
              <span className="font-black text-accent-gold">14-0</span>.
            </p>
            <motion.button
              id="start-draft-button"
              onClick={handleStartDraft}
              disabled={createSession.isPending}
              className="btn-primary text-2xl px-12 py-6"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <span className="relative z-10">
                {createSession.isPending ? "INITIALIZING..." : "START DRAFT"}
              </span>
            </motion.button>
          </motion.div>
        )}

        {/* ACTIVE DRAFT: Pitch + Console */}
        {store.phase !== "IDLE" && store.phase !== "COMPLETE" && (
          <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.5fr_1.8fr_320px] flex-1 min-h-0 pb-4">
            {/* Left: Live Pitch Art */}
            <div className="h-full overflow-hidden rounded-sm border-4 border-surface-border bg-accent-green shadow-sm">
              <LivePitchArt roster={store.roster} />
            </div>

            {/* Middle: Spin & Pool */}
            <div className="flex flex-col gap-6 h-full min-h-0 overflow-y-auto pr-2 custom-scrollbar">
              {/* Spin area */}
              {(store.phase === "READY" || store.phase === "SPINNING") && (
                <div className="rounded-sm border-4 border-surface-border bg-surface p-6 flex flex-col items-center justify-center min-h-[400px]">
                  <SpinWheel
                    onSpinStart={handleSpinStart}
                    onSpinComplete={handleSpinComplete}
                    isSpinning={store.phase === "SPINNING"}
                    disabled={store.phase !== "READY"}
                    spinResult={spinMutation.data || null}
                  />
                </div>
              )}

              {/* Player Pool */}
              {store.phase === "POOL" && store.currentSpin && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.3 }}
                  className="rounded-sm border-4 border-surface-border bg-surface p-6"
                >
                  {/* Pool header */}
                  <div className="mb-6 flex flex-col xl:flex-row xl:items-center justify-between border-b-4 border-surface-border pb-4 gap-4">
                    <div>
                      <h3 className="text-2xl font-heading font-bold text-white uppercase tracking-wider">
                        {store.currentSpin.franchise_name}
                        <span className="ml-2 text-accent-gold">
                          '{store.currentSpin.year.toString().slice(2)}
                        </span>
                      </h3>
                      <p className="text-sm text-text-secondary font-body mt-1">
                        SELECT A PLAYER TO DRAFT
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
                        className="btn-primary"
                      >
                        {pickMutation.isPending ? "DRAFTING..." : `DRAFT ${store.selectedPlayer.name.split(" ").pop()}`}
                      </motion.button>
                    )}
                  </div>

                  {/* Player grid */}
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
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

            {/* Right: Draft Board */}
            <div className="h-full min-h-0 overflow-y-auto pr-2 custom-scrollbar">
              <div className="rounded-sm border-4 border-surface-border bg-surface-bright p-4">
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
            className="flex-1 min-h-0 pb-4 grid grid-cols-1 gap-6 xl:grid-cols-[1.5fr_1fr]"
          >
            {/* Left: Live Pitch Art */}
            <div className="h-full overflow-hidden rounded-sm border-4 border-surface-border bg-accent-green shadow-sm">
              <LivePitchArt roster={store.roster} />
            </div>

            {/* Right: Board & Console */}
            <div className="flex flex-col gap-6 h-full overflow-y-auto custom-scrollbar pr-2 pb-4">
              {/* Victory Console */}
              <div className="border-4 border-surface-border bg-surface p-6 flex flex-col items-center">
                <motion.div
                  className="mb-4 text-6xl"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: 3 }}
                >
                  🏆
                </motion.div>
                <h2 className="mb-2 text-4xl font-heading font-black text-accent-gold uppercase tracking-widest text-center">
                  SQUAD COMPLETE!
                </h2>
                <p className="mb-6 text-lg font-body text-text-secondary uppercase text-center">
                  YOUR DREAM XI IS READY.<br/>BUDGET REMAINING:{" "}
                  <span className="font-black text-accent-gold">
                    {store.budgetRemaining} CR
                  </span>
                </p>

                <div className="flex gap-4 w-full">
                  <motion.button
                    onClick={() => router.push(`/league?session=${store.sessionId}`)}
                    className="btn-primary text-xl flex-1 py-4"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    🏏 SIMULATE
                  </motion.button>

                  <motion.button
                    onClick={() => store.reset()}
                    className="btn-secondary text-xl flex-1 py-4"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    DRAFT AGAIN
                  </motion.button>
                </div>
              </div>

              {/* Final roster display */}
              <div className="border-4 border-surface-border bg-background p-4 flex-1">
                <DraftBoard
                  roster={store.roster}
                  budgetRemaining={store.budgetRemaining}
                  overseasCount={overseasCount}
                  picksCount={store.picksCount}
                />
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
