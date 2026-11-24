export interface VerifiedLocation {
  success: true;
  place_id: string;
  name: string;
  formatted_address: string;
  latitude: number;
  longitude: number;
  types: string[];
}
