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
  source_place_id?: string | null;
  source_name?: string | null;
  source_address?: string | null;
  source_latitude?: number | null;
  source_longitude?: number | null;
  destination_place_id?: string | null;
  destination_name?: string | null;
  destination_address?: string | null;
  destination_latitude?: number | null;
  destination_longitude?: number | null;
}
