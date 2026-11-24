import { AxiosHeaders, type AxiosResponse } from "axios";
import { afterEach, describe, expect, it, vi } from "vitest";

import { apiClient } from "@/api/client";
import { locationService } from "@/services/location-service";
import type { VerifiedLocation } from "@/types/location";

const location: VerifiedLocation = {
  success: true,
  place_id: "google-place-id",
  name: "Jaipur",
  formatted_address: "Jaipur, Rajasthan, India",
  latitude: 26.9124,
  longitude: 75.7873,
  types: ["locality"],
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

describe("locationService", () => {
  afterEach(() => vi.restoreAllMocks());

  it("posts the entered destination to the authenticated verification route", async () => {
    const post = vi.spyOn(apiClient, "post").mockResolvedValue(response(location));

    await expect(locationService.verifyDestination("Jaipur, Rajasthan, India")).resolves.toEqual(location);

    expect(post).toHaveBeenCalledWith("/locations/verify", {
      destination: "Jaipur, Rajasthan, India",
    });
  });
});
