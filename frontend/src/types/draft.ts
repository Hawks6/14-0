// ─── Draft System Types ─────────────────────────────────────────────

export type PlayerRole = "BAT" | "BOWL" | "WK" | "AR";

export interface Player {
  player_season_id: string;
  player_id: string;
  name: string;
  country: string;
  role: PlayerRole;
  is_overseas: boolean;
  credit_cost: number;
  percentile_batting: number;
  percentile_bowling: number;
  prime_rating: number;
  season_rating: number;
}

export interface SpinResult {
  franchise_name: string;
  franchise_code: string;
  year: number;
  players: Player[];
}

export interface DraftPick {
  slot: number;
  player: Player;
}

export interface DraftSession {
  id: string;
  status: "DRAFTING" | "COMPLETE" | "SIMULATING";
  budget_remaining: number;
  picks: DraftPick[];
}

export interface RosterSlot {
  index: number;
  label: string;
  requiredRole?: PlayerRole;
  player?: Player;
}

// The 11 roster slots with role constraints
export const ROSTER_TEMPLATE: Omit<RosterSlot, "player">[] = [
  { index: 0, label: "Wicketkeeper", requiredRole: "WK" },
  { index: 1, label: "Batsman 1", requiredRole: "BAT" },
  { index: 2, label: "Batsman 2", requiredRole: "BAT" },
  { index: 3, label: "Batsman 3", requiredRole: "BAT" },
  { index: 4, label: "All-Rounder 1", requiredRole: "AR" },
  { index: 5, label: "All-Rounder 2", requiredRole: "AR" },
  { index: 6, label: "Bowler 1", requiredRole: "BOWL" },
  { index: 7, label: "Bowler 2", requiredRole: "BOWL" },
  { index: 8, label: "Bowler 3", requiredRole: "BOWL" },
  { index: 9, label: "Flex 1" },
  { index: 10, label: "Flex 2" },
];

export const MAX_BUDGET = 100;
export const MAX_OVERSEAS = 4;
export const ROSTER_SIZE = 11;

// IPL franchise colors for theming
export const FRANCHISE_COLORS: Record<string, { primary: string; secondary: string; glow: string }> = {
  CSK: { primary: "#FFC107", secondary: "#0D47A1", glow: "rgba(255,193,7,0.4)" },
  MI: { primary: "#004BA0", secondary: "#D4AF37", glow: "rgba(0,75,160,0.4)" },
  RCB: { primary: "#EC1C24", secondary: "#2B2A29", glow: "rgba(236,28,36,0.4)" },
  KKR: { primary: "#3A225D", secondary: "#D4AF37", glow: "rgba(58,34,93,0.4)" },
  DC: { primary: "#004C93", secondary: "#EF1B23", glow: "rgba(0,76,147,0.4)" },
  PBKS: { primary: "#ED1B24", secondary: "#A7A9AC", glow: "rgba(237,27,36,0.4)" },
  RR: { primary: "#EA1A85", secondary: "#254AA5", glow: "rgba(234,26,133,0.4)" },
  SRH: { primary: "#FF822A", secondary: "#000000", glow: "rgba(255,130,42,0.4)" },
  GT: { primary: "#1C1C1C", secondary: "#A0D2DB", glow: "rgba(160,210,219,0.4)" },
  LSG: { primary: "#A72056", secondary: "#FFCC00", glow: "rgba(167,32,86,0.4)" },
  DEC: { primary: "#1A3F66", secondary: "#D4AF37", glow: "rgba(26,63,102,0.4)" },
  DD: { primary: "#DD1F26", secondary: "#000080", glow: "rgba(221,31,38,0.4)" },
  KXIP: { primary: "#ED1B24", secondary: "#D4AF37", glow: "rgba(237,27,36,0.4)" },
  KTK: { primary: "#FF8000", secondary: "#9F000F", glow: "rgba(255,128,0,0.4)" },
  PWI: { primary: "#008080", secondary: "#C0C0C0", glow: "rgba(0,128,128,0.4)" },
  GL: { primary: "#FFA500", secondary: "#000080", glow: "rgba(255,165,0,0.4)" },
  RPS: { primary: "#D11D5B", secondary: "#3A225D", glow: "rgba(209,29,91,0.4)" },
  RPS2: { primary: "#D11D5B", secondary: "#3A225D", glow: "rgba(209,29,91,0.4)" },
  RCBB: { primary: "#EC1C24", secondary: "#2B2A29", glow: "rgba(236,28,36,0.4)" },
};
