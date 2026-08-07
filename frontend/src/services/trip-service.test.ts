import { AxiosHeaders, type AxiosResponse } from "axios";
import { afterEach, describe, expect, it, vi } from "vitest";

import { apiClient } from "@/api/client";
import { tripService } from "@/services/trip-service";
import type { TripCreate, TripResponse } from "@/types/trip";

const trip: TripResponse = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  user_id: "a50e8400-e29b-41d4-a716-446655440000",
  source: "Mumbai",
  destination: "Goa",
  start_date: "2026-09-10",
  end_date: "2026-09-12",
  budget: "25000.00",
  travelers: 2,
  preferences: { pace: "relaxed" },
  created_at: "2026-08-07T10:30:00Z",
};

const tripCreate: TripCreate = {
  source: "Mumbai",
  destination: "Goa",
  start_date: "2026-09-10",
  end_date: "2026-09-12",
  budget: 25000,
  travelers: 2,
  preferences: { pace: "relaxed" },
};

function response<T>(data: T): AxiosResponse<T> {
  return {
    data,
    status: 200,
    statusText: "OK",
    headers: {},
    config: { headers: new AxiosHeaders() },
  };
}

describe("tripService", () => {
  afterEach(() => vi.restoreAllMocks());

  it("maps each operation to the existing trip API", async () => {
    const post = vi.spyOn(apiClient, "post").mockResolvedValue(response(trip));
    const get = vi.spyOn(apiClient, "get")
      .mockResolvedValueOnce(response([trip]))
      .mockResolvedValueOnce(response(trip));
    const put = vi.spyOn(apiClient, "put").mockResolvedValue(response(trip));
    const remove = vi.spyOn(apiClient, "delete").mockResolvedValue(response(undefined));

    await tripService.createTrip(tripCreate);
    await tripService.listTrips();
    await tripService.getTrip(trip.id);
    await tripService.updateTrip(trip.id, { destination: "Panaji" });
    await tripService.deleteTrip(trip.id);

    expect(post).toHaveBeenCalledWith("/trips", tripCreate);
    expect(get).toHaveBeenNthCalledWith(1, "/trips", { params: { offset: 0, limit: 100 } });
    expect(get).toHaveBeenNthCalledWith(2, `/trips/${trip.id}`);
    expect(put).toHaveBeenCalledWith(`/trips/${trip.id}`, { destination: "Panaji" });
    expect(remove).toHaveBeenCalledWith(`/trips/${trip.id}`);
  });
});
