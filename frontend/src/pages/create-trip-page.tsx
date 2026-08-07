import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { getApiErrorMessage } from "@/api/client";
import { TripForm } from "@/components/trip-form";
import { Card, CardContent } from "@/components/ui/card";
import { useCreateTrip } from "@/hooks/use-trips";
import type { TripCreate } from "@/types/trip";

export function CreateTripPage() {
  const navigate = useNavigate();
  const createTrip = useCreateTrip();
  const [submitError, setSubmitError] = useState<string | undefined>();

  const submit = async (values: TripCreate) => {
    setSubmitError(undefined);
    try {
      const trip = await createTrip.mutateAsync(values);
      navigate(`/trips/${trip.id}`, { replace: true });
    } catch (error) {
      setSubmitError(getApiErrorMessage(error));
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-teal-700" to="/trips"><ArrowLeft aria-hidden="true" className="size-4" />Back to trips</Link>
      <div><p className="text-sm font-semibold text-teal-700">Trip management</p><h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Create a trip</h1><p className="mt-2 text-slate-600">Start with the essentials and add flexible preferences if you need them.</p></div>
      <Card><CardContent className="pt-6"><TripForm errorMessage={submitError} isSubmitting={createTrip.isPending} onSubmit={submit} submitLabel="Create trip" /></CardContent></Card>
    </div>
  );
}
