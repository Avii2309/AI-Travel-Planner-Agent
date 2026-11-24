export interface ItineraryActivity {
  time: string;
  title: string;
  description: string;
  location: string;
  estimated_cost: number;
  place_id?: string | null;
}

export interface VerifiedPlace {
  place_id: string;
  name: string;
  formatted_address: string;
  latitude: number;
  longitude: number;
  types: string[];
}

export interface ItineraryDay {
  day: number;
  title: string;
  activities: ItineraryActivity[];
  sightseeing: string[];
  food: string[];
  transport: string;
  estimated_cost: number;
  travel_tips: string[];
  optional_activities: string[];
}

export interface ItineraryResponse {
  trip_id: string;
  generated_at: string;
  days: ItineraryDay[];
  summary: string;
  estimated_total_cost: number;
  packing_tips: string[];
  best_visiting_time: string;
  verified_places?: VerifiedPlace[];
}

export interface ItineraryListItem {
  trip_id: string;
  destination: string;
  start_date: string;
  end_date: string;
  generated_at: string;
}
