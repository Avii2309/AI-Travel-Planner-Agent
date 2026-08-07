import { apiClient } from "@/api/client";
import type { TripCreate, TripResponse, TripUpdate } from "@/types/trip";

export interface ListTripsOptions {
  offset?: number;
  limit?: number;
}

export const tripService = {
  async createTrip(values: TripCreate): Promise<TripResponse> {
    const { data } = await apiClient.post<TripResponse>("/trips", values);
    return data;
  },

  async listTrips({ offset = 0, limit = 100 }: ListTripsOptions = {}): Promise<TripResponse[]> {
    const { data } = await apiClient.get<TripResponse[]>("/trips", { params: { offset, limit } });
    return data;
  },

  async getTrip(tripId: string): Promise<TripResponse> {
    const { data } = await apiClient.get<TripResponse>(`/trips/${tripId}`);
    return data;
  },

  async updateTrip(tripId: string, values: TripUpdate): Promise<TripResponse> {
    const { data } = await apiClient.put<TripResponse>(`/trips/${tripId}`, values);
    return data;
  },

  async deleteTrip(tripId: string): Promise<void> {
    await apiClient.delete(`/trips/${tripId}`);
  },
};
