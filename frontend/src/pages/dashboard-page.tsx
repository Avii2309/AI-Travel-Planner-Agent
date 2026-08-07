import { ArrowRight, Map, Plus, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { getApiErrorMessage } from "@/api/client";
import { Loader } from "@/components/loader";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { useTrips } from "@/hooks/use-trips";

export function DashboardPage() {
  const { user } = useAuth();
  const tripsQuery = useTrips();

  return (
    <div className="mx-auto max-w-6xl space-y-7">
      <div>
        <p className="text-sm font-semibold text-teal-700">Workspace</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Welcome back, {user?.full_name.split(" ")[0]}.</h1>
        <p className="mt-2 text-slate-600">Your travel workspace is ready when you are.</p>
      </div>
      <div className="grid gap-5 md:grid-cols-2">
        <Card>
          <CardHeader>
            <p className="text-sm font-semibold text-slate-800">Your profile</p>
          </CardHeader>
          <CardContent className="space-y-1">
            <p className="font-semibold text-slate-900">{user?.full_name}</p>
            <p className="text-sm text-slate-600">{user?.email}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <p className="text-sm font-semibold text-slate-800">Your trips</p>
          </CardHeader>
          <CardContent>
            {tripsQuery.isPending && <Loader />}
            {tripsQuery.isError && <p className="text-sm leading-6 text-rose-700">{getApiErrorMessage(tripsQuery.error)}</p>}
            {tripsQuery.isSuccess && <><p className="text-3xl font-bold text-slate-950">{tripsQuery.data.length}</p><p className="mt-1 text-sm text-slate-600">trip{tripsQuery.data.length === 1 ? "" : "s"} in your workspace</p><Link className="mt-4 inline-flex items-center text-sm font-semibold text-teal-700 hover:text-teal-800" to="/trips">View all trips <ArrowRight aria-hidden="true" className="ml-1.5 size-4" /></Link></>}
          </CardContent>
        </Card>
      </div>
      <section>
        <h2 className="text-lg font-bold text-slate-900">What you’ll be able to do</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Link className="block" to="/trips/new">
          <Card className="border-teal-100 bg-teal-50 transition hover:border-teal-300 hover:shadow-md">
            <CardContent className="flex gap-4 pt-5">
              <Map aria-hidden="true" className="mt-0.5 size-5 text-teal-700" />
              <div><h3 className="font-semibold text-slate-900">Organize a trip <Plus aria-hidden="true" className="ml-1 inline size-4" /></h3><p className="mt-1 text-sm text-slate-600">Save destinations, dates, budgets, and preferences.</p></div>
            </CardContent>
          </Card>
          </Link>
          <Card className="border-cyan-100 bg-cyan-50">
            <CardContent className="flex gap-4 pt-5">
              <Sparkles aria-hidden="true" className="mt-0.5 size-5 text-cyan-700" />
              <div><h3 className="font-semibold text-slate-900">AI itineraries</h3><p className="mt-1 text-sm text-slate-600">Itinerary generation will be available in the next phase.</p></div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
