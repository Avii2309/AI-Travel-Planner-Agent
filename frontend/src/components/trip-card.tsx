import { CalendarDays, Pencil, Trash2, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { TripResponse } from "@/types/trip";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`));
}

function formatBudget(value: string): string {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(Number(value));
}

export function TripCard({ trip, onDelete }: { trip: TripResponse; onDelete: (trip: TripResponse) => void }) {
  return (
    <Card className="transition hover:border-teal-200 hover:shadow-md">
      <CardContent className="p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-lg font-bold text-slate-950">{trip.destination}</p>
            <p className="mt-1 text-sm text-slate-600">From {trip.source}</p>
          </div>
          <p className="rounded-full bg-teal-50 px-3 py-1 text-sm font-semibold text-teal-800">Budget {formatBudget(trip.budget)}</p>
        </div>
        <div className="mt-5 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
          <p className="flex items-center gap-2"><CalendarDays aria-hidden="true" className="size-4 text-teal-700" />{formatDate(trip.start_date)} – {formatDate(trip.end_date)}</p>
          <p className="flex items-center gap-2"><Users aria-hidden="true" className="size-4 text-teal-700" />{trip.travelers} traveler{trip.travelers === 1 ? "" : "s"}</p>
        </div>
        <div className="mt-5 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
          <Link className="inline-flex h-9 items-center rounded-lg bg-teal-700 px-3 text-xs font-semibold text-white transition hover:bg-teal-800" to={`/trips/${trip.id}`}>View details</Link>
          <Link className="inline-flex h-9 items-center rounded-lg border border-slate-300 bg-white px-3 text-xs font-semibold text-slate-800 transition hover:bg-slate-50" to={`/trips/${trip.id}/edit`}><Pencil aria-hidden="true" className="mr-1.5 size-3.5" />Edit</Link>
          <Button onClick={() => onDelete(trip)} size="sm" variant="ghost"><Trash2 aria-hidden="true" className="mr-1.5 size-3.5 text-rose-600" />Delete</Button>
        </div>
      </CardContent>
    </Card>
  );
}
