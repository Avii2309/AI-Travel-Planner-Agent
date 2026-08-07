import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { tripService } from "@/services/trip-service";
import type { TripCreate, TripUpdate } from "@/types/trip";

export const tripQueryKeys = {
  all: ["trips"] as const,
  detail: (tripId: string) => [...tripQueryKeys.all, tripId] as const,
};

export function useTrips() {
  return useQuery({
    queryKey: tripQueryKeys.all,
    queryFn: () => tripService.listTrips(),
  });
}

export function useTrip(tripId: string) {
  return useQuery({
    queryKey: tripQueryKeys.detail(tripId),
    queryFn: () => tripService.getTrip(tripId),
    enabled: Boolean(tripId),
  });
}

export function useCreateTrip() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (values: TripCreate) => tripService.createTrip(values),
    onSuccess: (trip) => {
      queryClient.setQueryData(tripQueryKeys.detail(trip.id), trip);
      void queryClient.invalidateQueries({ queryKey: tripQueryKeys.all });
    },
  });
}

export function useUpdateTrip() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ tripId, values }: { tripId: string; values: TripUpdate }) => tripService.updateTrip(tripId, values),
    onSuccess: (trip) => {
      queryClient.setQueryData(tripQueryKeys.detail(trip.id), trip);
      void queryClient.invalidateQueries({ queryKey: tripQueryKeys.all });
    },
  });
}

export function useDeleteTrip() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (tripId: string) => tripService.deleteTrip(tripId),
    onSuccess: (_, tripId) => {
      queryClient.removeQueries({ queryKey: tripQueryKeys.detail(tripId) });
      void queryClient.invalidateQueries({ queryKey: tripQueryKeys.all });
    },
  });
}
