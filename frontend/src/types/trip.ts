export type TripPreferences = Record<string, unknown>;

export interface TripCreate {
  source: string;
  destination: string;
  start_date: string;
  end_date: string;
  budget: number;
  travelers: number;
  preferences: TripPreferences;
}

export interface TripUpdate {
  source?: string;
  destination?: string;
  start_date?: string;
  end_date?: string;
  budget?: number;
  travelers?: number;
  preferences?: TripPreferences;
}

export interface TripResponse {
  id: string;
  user_id: string;
  source: string;
  destination: string;
  start_date: string;
  end_date: string;
  budget: string;
  travelers: number;
  preferences: TripPreferences;
  created_at: string;
}
