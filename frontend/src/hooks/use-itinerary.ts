import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { itineraryService } from "@/services/itinerary-service";

export const itineraryQueryKeys = {
  all: ["itineraries"] as const,
  detail: (tripId: string) => [...itineraryQueryKeys.all, tripId] as const,
};

export function useTripItinerary(tripId: string) {
  return useQuery({
    queryKey: itineraryQueryKeys.detail(tripId),
    queryFn: () => itineraryService.getTripItinerary(tripId),
    enabled: Boolean(tripId),
  });
}

export function useItineraries() {
  return useQuery({ queryKey: itineraryQueryKeys.all, queryFn: () => itineraryService.listItineraries() });
}

export function useGenerateItinerary() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (tripId: string) => itineraryService.generateItinerary(tripId),
    onSuccess: (itinerary) => {
      queryClient.setQueryData(itineraryQueryKeys.detail(itinerary.trip_id), itinerary);
      void queryClient.invalidateQueries({ queryKey: itineraryQueryKeys.all });
    },
  });
}
