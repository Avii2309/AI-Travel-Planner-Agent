import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getApiErrorMessage } from "@/api/client";
import { Loader } from "@/components/loader";
import { TripForm } from "@/components/trip-form";
import { Card, CardContent } from "@/components/ui/card";
import { useTrip, useUpdateTrip } from "@/hooks/use-trips";
import type { TripCreate } from "@/types/trip";

export function EditTripPage() {
  const { tripId = "" } = useParams();
  const navigate = useNavigate();
  const tripQuery = useTrip(tripId);
  const updateTrip = useUpdateTrip();
  const [submitError, setSubmitError] = useState<string | undefined>();

  const submit = async (values: TripCreate) => {
    setSubmitError(undefined);
    try {
      const trip = await updateTrip.mutateAsync({ tripId, values });
      navigate(`/trips/${trip.id}`, { replace: true });
    } catch (error) {
      setSubmitError(getApiErrorMessage(error));
    }
  };

  if (tripQuery.isPending) {
    return <div className="grid min-h-60 place-items-center"><Loader className="size-7" /></div>;
  }

  if (tripQuery.isError || !tripQuery.data) {
    return <div className="mx-auto max-w-3xl"><Link className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-teal-700" to="/trips"><ArrowLeft aria-hidden="true" className="size-4" />Back to trips</Link><Card className="mt-6"><CardContent className="py-10 text-center"><h1 className="text-xl font-bold text-slate-950">Trip not available</h1><p className="mt-2 text-sm text-slate-600">{tripQuery.isError ? getApiErrorMessage(tripQuery.error) : "This trip could not be found."}</p></CardContent></Card></div>;
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-teal-700" to={`/trips/${tripId}`}><ArrowLeft aria-hidden="true" className="size-4" />Back to trip</Link>
      <div><p className="text-sm font-semibold text-teal-700">Trip management</p><h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Edit trip</h1><p className="mt-2 text-slate-600">Update your trip details and preferences.</p></div>
      <Card><CardContent className="pt-6"><TripForm errorMessage={submitError} initialTrip={tripQuery.data} isSubmitting={updateTrip.isPending} onSubmit={submit} submitLabel="Save changes" /></CardContent></Card>
    </div>
  );
}
