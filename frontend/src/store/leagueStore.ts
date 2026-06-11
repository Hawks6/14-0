import { create } from "zustand";
import type { LeagueMatch, LeagueSeason, BallEvent } from "@/types/league";

export type LeagueView = "matches" | "scorecard" | "dashboard";

interface LeagueState {
  // Session
  draftSessionId: string | null;
  season: LeagueSeason | null;
  matches: LeagueMatch[];

  // Current match detail
  selectedMatch: LeagueMatch | null;
  selectedMatchEvents: BallEvent[];

  // UI state
  view: LeagueView;
  isLoading: boolean;
  error: string | null;
  simulationProgress: number; // 0-14 for animation

  // Actions
  setSeason: (season: LeagueSeason) => void;
  setMatches: (matches: LeagueMatch[]) => void;
  selectMatch: (match: LeagueMatch, events?: BallEvent[]) => void;
  setMatchEvents: (events: BallEvent[]) => void;
  setView: (view: LeagueView) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSimulationProgress: (progress: number) => void;
  setDraftSessionId: (id: string) => void;
  clearSelection: () => void;
  reset: () => void;

  // Computed
  getWins: () => number;
  getLosses: () => number;
  getTies: () => number;
  isPerfectSeason: () => boolean;
  getSeasonComplete: () => boolean;
}

export const useLeagueStore = create<LeagueState>((set, get) => ({
  draftSessionId: null,
  season: null,
  matches: [],
  selectedMatch: null,
  selectedMatchEvents: [],
  view: "matches",
  isLoading: false,
  error: null,
  simulationProgress: 0,

  // ── Actions ─────────────────────────────────────────────────

  setSeason: (season) => set({ season, matches: season.matches }),

  setMatches: (matches) => set({ matches }),

  selectMatch: (match, events) =>
    set({
      selectedMatch: match,
      selectedMatchEvents: events ?? [],
      view: "scorecard",
    }),

  setMatchEvents: (events) => set({ selectedMatchEvents: events }),

  setView: (view) => set({ view }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  setSimulationProgress: (progress) => set({ simulationProgress: progress }),

  setDraftSessionId: (id) => set({ draftSessionId: id }),

  clearSelection: () =>
    set({
      selectedMatch: null,
      selectedMatchEvents: [],
      view: "matches",
    }),

  reset: () =>
    set({
      draftSessionId: null,
      season: null,
      matches: [],
      selectedMatch: null,
      selectedMatchEvents: [],
      view: "matches",
      isLoading: false,
      error: null,
      simulationProgress: 0,
    }),

  // ── Computed ────────────────────────────────────────────────

  getWins: () =>
    get().matches.filter((m) => m.winner === "user").length,

  getLosses: () =>
    get().matches.filter((m) => m.winner === "opponent").length,

  getTies: () =>
    get().matches.filter((m) => m.winner === "tie").length,

  isPerfectSeason: () =>
    get().matches.length === 14 &&
    get().matches.every((m) => m.winner === "user"),

  getSeasonComplete: () =>
    get().matches.length === 14 &&
    get().matches.every((m) => m.status === "completed"),
}));
