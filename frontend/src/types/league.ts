/** Ball-by-ball event from the simulation engine */
export interface BallEvent {
  ball_number: number;
  over_number: number;
  runs_scored: number;
  extras: number;
  wicket_type: string | null;
  event_meta: Record<string, unknown>;
}

/** Single match in the 14-match league */
export interface LeagueMatch {
  id: string;
  match_number: number;
  status: "pending" | "in_progress" | "completed";
  user_team: string;
  opponent_team: string;
  user_score: number;
  user_wickets: number;
  user_overs?: number;
  opponent_score: number;
  opponent_wickets: number;
  opponent_overs?: number;
  winner: "user" | "opponent" | "tie" | null;
  events?: BallEvent[];
}

/** League season state */
export interface LeagueSeason {
  draft_session_id: string;
  matches: LeagueMatch[];
}

/** Computed season standings entry */
export interface StandingsEntry {
  team: string;
  played: number;
  won: number;
  lost: number;
  tied: number;
  points: number;
  nrr: number;
  isUser: boolean;
}

/** Share card data */
export interface ShareCardData {
  teamName: string;
  wins: number;
  losses: number;
  ties: number;
  totalRuns: number;
  totalWickets: number;
  bestScore: string;
  isPerfect: boolean;
}
