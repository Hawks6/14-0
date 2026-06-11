import { create } from "zustand";
import {
  Player,
  SpinResult,
  DraftPick,
  RosterSlot,
  ROSTER_TEMPLATE,
  MAX_BUDGET,
  MAX_OVERSEAS,
  ROSTER_SIZE,
  PlayerRole,
} from "@/types/draft";

// ─── Draft Phase Flow ───────────────────────────────────────────────

export type DraftPhase =
  | "IDLE"        // No session yet
  | "READY"       // Session created, ready to spin
  | "SPINNING"    // Spin animation playing
  | "POOL"        // Viewing available players from spin
  | "PICKING"     // Confirming a pick
  | "COMPLETE";   // All 11 slots filled

interface DraftState {
  // Session
  sessionId: string | null;
  phase: DraftPhase;
  budgetRemaining: number;

  // Roster
  roster: RosterSlot[];
  picksCount: number;

  // Current spin
  currentSpin: SpinResult | null;
  poolPlayers: Player[];

  // UI state
  selectedPlayer: Player | null;
  isAnimating: boolean;
  errorMessage: string | null;

  // Computed helpers (kept as getters via actions for Zustand)
  getOverseasCount: () => number;
  canPickPlayer: (player: Player) => boolean;
  getAvailableSlot: (role: PlayerRole) => number | null;

  // Actions
  initSession: (sessionId: string, budget: number) => void;
  startSpin: () => void;
  completeSpin: (spin: SpinResult) => void;
  selectPlayer: (player: Player | null) => void;
  confirmPick: (player: Player, updatedBudget: number) => void;
  setPhase: (phase: DraftPhase) => void;
  setAnimating: (v: boolean) => void;
  setError: (msg: string | null) => void;
  reset: () => void;
}

const buildEmptyRoster = (): RosterSlot[] =>
  ROSTER_TEMPLATE.map((t) => ({ ...t, player: undefined }));

export const useDraftStore = create<DraftState>((set, get) => ({
  sessionId: null,
  phase: "IDLE",
  budgetRemaining: MAX_BUDGET,

  roster: buildEmptyRoster(),
  picksCount: 0,

  currentSpin: null,
  poolPlayers: [],

  selectedPlayer: null,
  isAnimating: false,
  errorMessage: null,

  // ── Computed ────────────────────────────────────────────────

  getOverseasCount: () =>
    get().roster.filter((s) => s.player?.is_overseas).length,

  canPickPlayer: (player: Player) => {
    const state = get();
    if (player.credit_cost > state.budgetRemaining) return false;
    if (player.is_overseas && state.getOverseasCount() >= MAX_OVERSEAS)
      return false;
    if (state.getAvailableSlot(player.role) === null) return false;
    return true;
  },

  getAvailableSlot: (role: PlayerRole) => {
    const roster = get().roster;
    // First try to fill a role-specific slot
    const specific = roster.find(
      (s) => !s.player && s.requiredRole === role
    );
    if (specific) return specific.index;
    // Then try flex slots
    const flex = roster.find((s) => !s.player && !s.requiredRole);
    if (flex) return flex.index;
    return null;
  },

  // ── Actions ─────────────────────────────────────────────────

  initSession: (sessionId, budget) =>
    set({
      sessionId,
      phase: "READY",
      budgetRemaining: budget,
      roster: buildEmptyRoster(),
      picksCount: 0,
      currentSpin: null,
      poolPlayers: [],
      selectedPlayer: null,
      errorMessage: null,
    }),

  startSpin: () => set({ phase: "SPINNING", isAnimating: true, errorMessage: null }),

  completeSpin: (spin) =>
    set({
      currentSpin: spin,
      poolPlayers: spin.players,
      phase: "POOL",
      isAnimating: false,
    }),

  selectPlayer: (player) => set({ selectedPlayer: player }),

  confirmPick: (player, updatedBudget) => {
    const state = get();
    const slotIdx = state.getAvailableSlot(player.role);
    if (slotIdx === null) return;

    const newRoster = [...state.roster];
    newRoster[slotIdx] = { ...newRoster[slotIdx], player };
    const newCount = state.picksCount + 1;

    set({
      roster: newRoster,
      picksCount: newCount,
      budgetRemaining: updatedBudget,
      selectedPlayer: null,
      poolPlayers: [],
      currentSpin: null,
      phase: newCount >= ROSTER_SIZE ? "COMPLETE" : "READY",
    });
  },

  setPhase: (phase) => set({ phase }),
  setAnimating: (v) => set({ isAnimating: v }),
  setError: (msg) => set({ errorMessage: msg }),

  reset: () =>
    set({
      sessionId: null,
      phase: "IDLE",
      budgetRemaining: MAX_BUDGET,
      roster: buildEmptyRoster(),
      picksCount: 0,
      currentSpin: null,
      poolPlayers: [],
      selectedPlayer: null,
      isAnimating: false,
      errorMessage: null,
    }),
}));
