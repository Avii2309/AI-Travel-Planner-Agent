import { ArrowLeft, CalendarDays, Pencil, Trash2, Users } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getApiErrorMessage } from "@/api/client";
import { ConfirmationDialog } from "@/components/confirmation-dialog";
import { Loader } from "@/components/loader";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useDeleteTrip, useTrip } from "@/hooks/use-trips";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "full" }).format(new Date(`${value}T00:00:00`));
}

export function TripDetailsPage() {
  const { tripId = "" } = useParams();
  const navigate = useNavigate();
  const tripQuery = useTrip(tripId);
  const deleteTrip = useDeleteTrip();
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const confirmDelete = async () => {
    setDeleteError(null);
    try {
      await deleteTrip.mutateAsync(tripId);
      navigate("/trips", { replace: true });
    } catch (error) {
      setDeleteError(getApiErrorMessage(error));
    }
  };

  if (tripQuery.isPending) {
    return <div className="grid min-h-60 place-items-center"><Loader className="size-7" /></div>;
  }

  if (tripQuery.isError || !tripQuery.data) {
    return (
      <div className="mx-auto max-w-3xl space-y-5">
        <Link className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-teal-700" to="/trips"><ArrowLeft aria-hidden="true" className="size-4" />Back to trips</Link>
        <Card><CardContent className="py-10 text-center"><h1 className="text-xl font-bold text-slate-950">Trip not available</h1><p className="mt-2 text-sm text-slate-600">{tripQuery.isError ? getApiErrorMessage(tripQuery.error) : "This trip could not be found."}</p><Button className="mt-6" onClick={() => void tripQuery.refetch()} variant="outline">Try again</Button></CardContent></Card>
      </div>
    );
  }

  const trip = tripQuery.data;
  const preferences = Object.keys(trip.preferences).length > 0 ? JSON.stringify(trip.preferences, null, 2) : "No preferences added.";

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-teal-700" to="/trips"><ArrowLeft aria-hidden="true" className="size-4" />Back to trips</Link>
        <div className="flex gap-2">
          <Link className="inline-flex h-10 items-center rounded-lg border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-800 transition hover:bg-slate-50" to={`/trips/${trip.id}/edit`}><Pencil aria-hidden="true" className="mr-2 size-4" />Edit</Link>
          <Button onClick={() => setIsDeleteOpen(true)} variant="danger"><Trash2 aria-hidden="true" className="mr-2 size-4" />Delete</Button>
        </div>
      </div>
      <Card>
        <CardHeader className="flex flex-wrap items-start justify-between gap-4">
          <div><p className="text-sm font-semibold text-teal-700">Trip details</p><h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">{trip.destination}</h1><p className="mt-2 text-slate-600">Departing from {trip.source}</p></div>
          <p className="rounded-full bg-teal-50 px-3 py-1 text-sm font-semibold text-teal-800">Budget {new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(Number(trip.budget))}</p>
        </CardHeader>
        <CardContent className="grid gap-6 py-6 sm:grid-cols-2">
          <div className="flex gap-3"><CalendarDays aria-hidden="true" className="mt-0.5 size-5 text-teal-700" /><div><p className="text-sm font-semibold text-slate-900">Travel dates</p><p className="mt-1 text-sm leading-6 text-slate-600">{formatDate(trip.start_date)} through {formatDate(trip.end_date)}</p></div></div>
          <div className="flex gap-3"><Users aria-hidden="true" className="mt-0.5 size-5 text-teal-700" /><div><p className="text-sm font-semibold text-slate-900">Travelers</p><p className="mt-1 text-sm leading-6 text-slate-600">{trip.travelers} traveler{trip.travelers === 1 ? "" : "s"}</p></div></div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><h2 className="font-bold text-slate-900">Preferences</h2></CardHeader>
        <CardContent><pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 text-sm leading-6 text-slate-100">{preferences}</pre></CardContent>
      </Card>
      {deleteError && <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700" role="alert">{deleteError}</p>}
      <ConfirmationDialog confirmLabel="Delete trip" description={`Delete your ${trip.destination} trip? This cannot be undone.`} isOpen={isDeleteOpen} isPending={deleteTrip.isPending} onConfirm={() => void confirmDelete()} onOpenChange={(open) => { if (!deleteTrip.isPending) setIsDeleteOpen(open); }} title="Delete this trip?" />
    </div>
  );
}
