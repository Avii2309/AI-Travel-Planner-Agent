import { Plus } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { ConfirmationDialog } from "@/components/confirmation-dialog";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/error-state";
import { Loader } from "@/components/loader";
import { TripCard } from "@/components/trip-card";
import { Button } from "@/components/ui/button";
import { getApiErrorMessage } from "@/api/client";
import { useDeleteTrip, useTrips } from "@/hooks/use-trips";
import type { TripResponse } from "@/types/trip";

export function TripsPage() {
  const tripsQuery = useTrips();
  const deleteTrip = useDeleteTrip();
  const [selectedTrip, setSelectedTrip] = useState<TripResponse | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const confirmDelete = async () => {
    if (!selectedTrip) {
      return;
    }
    setDeleteError(null);
    try {
      await deleteTrip.mutateAsync(selectedTrip.id);
      setSelectedTrip(null);
    } catch (error) {
      setDeleteError(getApiErrorMessage(error));
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-7">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-teal-700">Trip management</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Your trips</h1>
          <p className="mt-2 text-slate-600">Keep every destination, date, and budget together.</p>
        </div>
        <Link className="inline-flex h-10 items-center rounded-lg bg-teal-700 px-4 text-sm font-semibold text-white transition hover:bg-teal-800" to="/trips/new"><Plus aria-hidden="true" className="mr-2 size-4" />Create trip</Link>
      </div>

      {tripsQuery.isPending && <div className="grid min-h-60 place-items-center"><Loader className="size-7" /></div>}
      {tripsQuery.isError && <ErrorState message={getApiErrorMessage(tripsQuery.error)} onRetry={() => void tripsQuery.refetch()} />}
      {tripsQuery.isSuccess && tripsQuery.data.length === 0 && (
        <EmptyState
          action={<Link className="inline-flex h-10 items-center rounded-lg bg-teal-700 px-4 text-sm font-semibold text-white transition hover:bg-teal-800" to="/trips/new">Create your first trip</Link>}
          description="Add your dates, destination, budget, and preferences to begin planning."
          title="No trips yet"
        />
      )}
      {tripsQuery.isSuccess && tripsQuery.data.length > 0 && (
        <div className="grid gap-5 lg:grid-cols-2">
          {tripsQuery.data.map((trip) => <TripCard key={trip.id} onDelete={setSelectedTrip} trip={trip} />)}
        </div>
      )}
      {deleteError && <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700" role="alert">{deleteError}</p>}
      <ConfirmationDialog
        confirmLabel="Delete trip"
        description={selectedTrip ? `Delete your ${selectedTrip.destination} trip? This cannot be undone.` : ""}
        isOpen={selectedTrip !== null}
        isPending={deleteTrip.isPending}
        onConfirm={() => void confirmDelete()}
        onOpenChange={(open) => { if (!open && !deleteTrip.isPending) setSelectedTrip(null); }}
        title="Delete this trip?"
      />
    </div>
  );
}
