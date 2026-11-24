import { AxiosHeaders, type AxiosResponse } from "axios";
import { afterEach, describe, expect, it, vi } from "vitest";

import { apiClient } from "@/api/client";
import { itineraryService } from "@/services/itinerary-service";
import type { ItineraryListItem, ItineraryResponse } from "@/types/itinerary";

const itinerary: ItineraryResponse = {
  trip_id: "550e8400-e29b-41d4-a716-446655440000",
  generated_at: "2026-08-07T10:30:00Z",
  days: [],
  summary: "A relaxed trip.",
  estimated_total_cost: 25000,
  packing_tips: [],
  best_visiting_time: "Early morning",
};

function response<T>(data: T): AxiosResponse<T> {
  return { data, status: 200, statusText: "OK", headers: {}, config: { headers: new AxiosHeaders() } };
}

describe("itineraryService", () => {
  afterEach(() => vi.restoreAllMocks());

  it("uses the authenticated shared client and existing generate endpoint", async () => {
    const post = vi.spyOn(apiClient, "post").mockResolvedValue(response(itinerary));

    await expect(itineraryService.generateItinerary(itinerary.trip_id)).resolves.toEqual(itinerary);

    expect(post).toHaveBeenCalledWith(`/trips/${itinerary.trip_id}/generate-itinerary`);
  });

  it("retrieves an itinerary and its lightweight saved-itinerary list", async () => {
    const get = vi.spyOn(apiClient, "get")
      .mockResolvedValueOnce(response(itinerary))
      .mockResolvedValueOnce(response<ItineraryListItem[]>([{ trip_id: itinerary.trip_id, destination: "Goa", start_date: "2026-09-10", end_date: "2026-09-12", generated_at: itinerary.generated_at }]));

    await expect(itineraryService.getTripItinerary(itinerary.trip_id)).resolves.toEqual(itinerary);
    await expect(itineraryService.listItineraries()).resolves.toHaveLength(1);

    expect(get).toHaveBeenNthCalledWith(1, `/trips/${itinerary.trip_id}/itinerary`);
    expect(get).toHaveBeenNthCalledWith(2, "/itineraries");
  });
});
