import { apiClient } from "@/api/client";
import type { VerifiedLocation } from "@/types/location";

export const locationService = {
  async verifyDestination(destination: string): Promise<VerifiedLocation> {
    const { data } = await apiClient.post<VerifiedLocation>("/locations/verify", { destination });
    return data;
  },
};
