import { ArrowLeft, CalendarDays, Clock3, MapPin, Sparkles, Users } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { getApiErrorMessage } from "@/api/client";
import { Loader } from "@/components/loader";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useTripItinerary } from "@/hooks/use-itinerary";
import { useTrip } from "@/hooks/use-trips";

function formatDate(value: string): string { return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`)); }
function formatCost(value: number): string { return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value); }

function ListSection({ items, title }: { items: string[]; title: string }) {
  if (items.length === 0) return null;
  return <div><h3 className="text-sm font-semibold text-slate-900">{title}</h3><ul className="mt-2 space-y-1 text-sm leading-6 text-slate-600">{items.map((item) => <li key={item}>{item}</li>)}</ul></div>;
}

export function ItineraryPage() {
  const { tripId = "" } = useParams();
  const itineraryQuery = useTripItinerary(tripId);
  const tripQuery = useTrip(tripId);
  const tripPath = `/trips/${tripId}`;

  if (itineraryQuery.isPending || tripQuery.isPending) {
    return <div className="grid min-h-60 place-items-center"><Loader className="size-7" /></div>;
  }

  if (itineraryQuery.isError || tripQuery.isError || !itineraryQuery.data || !tripQuery.data) {
    const message = itineraryQuery.isError ? getApiErrorMessage(itineraryQuery.error) : tripQuery.isError ? getApiErrorMessage(tripQuery.error) : "This itinerary could not be found.";
    return <div className="mx-auto max-w-3xl space-y-5"><Link className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-teal-700" to={tripPath}><ArrowLeft aria-hidden="true" className="size-4" />Back to trip</Link><Card><CardContent className="py-12 text-center"><Sparkles aria-hidden="true" className="mx-auto size-8 text-teal-700" /><h1 className="mt-4 text-xl font-bold text-slate-950">No itinerary to display</h1><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-600">{message}</p><Link className="mt-6 inline-flex h-10 items-center rounded-lg bg-teal-700 px-4 text-sm font-semibold text-white hover:bg-teal-800" to={tripPath}>View trip</Link></CardContent></Card></div>;
  }

  const itinerary = itineraryQuery.data;
  const trip = tripQuery.data;

  return <div className="mx-auto max-w-5xl space-y-6"><Link className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-teal-700" to={tripPath}><ArrowLeft aria-hidden="true" className="size-4" />Back to trip</Link><Card className="border-cyan-100 bg-gradient-to-br from-cyan-50 to-white"><CardHeader><p className="flex items-center gap-2 text-sm font-semibold text-teal-700"><Sparkles aria-hidden="true" className="size-4" />AI itinerary</p><h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">{trip.destination_name ?? trip.destination}</h1><p className="mt-2 max-w-3xl leading-6 text-slate-600">{itinerary.summary}</p>{trip.destination_address && <p className="text-sm text-slate-500">{trip.destination_address}</p>}</CardHeader><CardContent className="grid gap-4 border-t border-cyan-100 pt-5 text-sm text-slate-600 sm:grid-cols-3"><p className="flex items-start gap-2"><CalendarDays aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-teal-700" />{formatDate(trip.start_date)} – {formatDate(trip.end_date)}</p><p className="flex items-center gap-2"><Users aria-hidden="true" className="size-4 text-teal-700" />{trip.travelers} traveler{trip.travelers === 1 ? "" : "s"}</p><p>Budget {formatCost(Number(trip.budget))} · Estimated {formatCost(itinerary.estimated_total_cost)}</p></CardContent></Card><div className="space-y-5">{itinerary.days.map((day) => <Card key={day.day}><CardHeader><p className="text-sm font-semibold text-teal-700">Day {day.day}</p><h2 className="mt-1 text-xl font-bold text-slate-950">{day.title}</h2></CardHeader><CardContent className="space-y-5 border-t border-slate-100 pt-5">{day.activities.length > 0 && <div className="space-y-3">{day.activities.map((activity) => <article className="rounded-xl border border-slate-200 bg-slate-50 p-4" key={`${activity.time}-${activity.title}`}><div className="flex flex-wrap items-start justify-between gap-2"><div><p className="flex items-center gap-2 text-sm font-semibold text-teal-800"><Clock3 aria-hidden="true" className="size-4" />{activity.time}</p><h3 className="mt-2 font-semibold text-slate-950">{activity.title}</h3></div><p className="text-sm font-semibold text-slate-700">Estimated {formatCost(activity.estimated_cost)}</p></div><p className="mt-2 text-sm leading-6 text-slate-600">{activity.description}</p><p className="mt-3 flex items-center gap-2 text-sm text-slate-600"><MapPin aria-hidden="true" className="size-4 text-teal-700" />{activity.location}</p></article>)}</div>}<div className="grid gap-5 sm:grid-cols-2"><ListSection items={day.sightseeing} title="Sightseeing" /><ListSection items={day.food} title="Food" /><div><h3 className="text-sm font-semibold text-slate-900">Transport</h3><p className="mt-2 text-sm leading-6 text-slate-600">{day.transport}</p></div><ListSection items={day.travel_tips} title="Travel tips" /><ListSection items={day.optional_activities} title="Optional activities" /><div><h3 className="text-sm font-semibold text-slate-900">Estimated day cost</h3><p className="mt-2 text-sm text-slate-600">{formatCost(day.estimated_cost)}</p></div></div></CardContent></Card>)}</div><Card><CardHeader><h2 className="font-bold text-slate-900">Before you go</h2></CardHeader><CardContent className="grid gap-5 border-t border-slate-100 pt-5 sm:grid-cols-2"><ListSection items={itinerary.packing_tips} title="Packing tips" /><div><h3 className="text-sm font-semibold text-slate-900">Best visiting time</h3><p className="mt-2 text-sm leading-6 text-slate-600">{itinerary.best_visiting_time}</p></div></CardContent></Card></div>;
}
