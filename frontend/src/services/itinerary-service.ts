import { apiClient } from "@/api/client";
import type { ItineraryListItem, ItineraryResponse } from "@/types/itinerary";

export const itineraryService = {
  async generateItinerary(tripId: string): Promise<ItineraryResponse> {
    const { data } = await apiClient.post<ItineraryResponse>(`/trips/${tripId}/generate-itinerary`);
    return data;
  },

  async getTripItinerary(tripId: string): Promise<ItineraryResponse> {
    const { data } = await apiClient.get<ItineraryResponse>(`/trips/${tripId}/itinerary`);
    return data;
  },

  async listItineraries(): Promise<ItineraryListItem[]> {
    const { data } = await apiClient.get<ItineraryListItem[]>("/itineraries");
    return data;
  },
};
