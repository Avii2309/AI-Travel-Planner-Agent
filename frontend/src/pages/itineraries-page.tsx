import { Link } from "react-router-dom";

import { getApiErrorMessage } from "@/api/client";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/error-state";
import { Loader } from "@/components/loader";
import { Card, CardContent } from "@/components/ui/card";
import { useItineraries } from "@/hooks/use-itinerary";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`));
}

export function ItinerariesPage() {
  const itinerariesQuery = useItineraries();

  return <div className="mx-auto max-w-4xl space-y-6"><div><p className="text-sm font-semibold text-teal-700">AI planning</p><h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">AI itineraries</h1><p className="mt-2 text-slate-600">Your saved, personalized day-by-day travel plans.</p></div>{itinerariesQuery.isPending && <div className="grid min-h-60 place-items-center"><Loader className="size-7" /></div>}{itinerariesQuery.isError && <ErrorState message={getApiErrorMessage(itinerariesQuery.error)} onRetry={() => void itinerariesQuery.refetch()} />}{itinerariesQuery.isSuccess && itinerariesQuery.data.length === 0 && <EmptyState action={<Link className="inline-flex h-10 items-center rounded-lg bg-teal-700 px-4 text-sm font-semibold text-white hover:bg-teal-800" to="/trips">View my trips</Link>} description="Generate an itinerary from one of your saved trips." title="No AI itineraries yet" />}{itinerariesQuery.isSuccess && itinerariesQuery.data.length > 0 && <div className="grid gap-4">{itinerariesQuery.data.map((itinerary) => <Card className="transition hover:border-teal-200 hover:shadow-md" key={itinerary.trip_id}><CardContent className="flex flex-wrap items-center justify-between gap-4 p-5"><div><h2 className="text-lg font-bold text-slate-950">{itinerary.destination}</h2><p className="mt-1 text-sm text-slate-600">{formatDate(itinerary.start_date)} – {formatDate(itinerary.end_date)}</p><p className="mt-2 text-xs font-medium text-slate-500">Generated {new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(itinerary.generated_at))}</p></div><Link className="inline-flex h-10 items-center rounded-lg bg-teal-700 px-4 text-sm font-semibold text-white hover:bg-teal-800" to={`/trips/${itinerary.trip_id}/itinerary`}>View itinerary</Link></CardContent></Card>)}</div>}</div>;
}
