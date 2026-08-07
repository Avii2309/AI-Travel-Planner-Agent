import { ArrowRight, CalendarDays, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { Brand } from "@/components/brand";

export function LandingPage() {
  return (
    <main className="min-h-screen bg-slate-50">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5 sm:px-8">
        <Brand />
        <Link className="hidden h-10 items-center rounded-lg border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-800 transition hover:bg-slate-50 sm:inline-flex" to="/login">
          Sign in
        </Link>
      </header>
      <section className="mx-auto grid max-w-6xl gap-12 px-5 py-16 sm:px-8 lg:grid-cols-[1.1fr_0.9fr] lg:py-28">
        <div className="max-w-2xl">
          <p className="mb-5 inline-flex items-center gap-2 rounded-full bg-teal-100 px-3 py-1 text-sm font-semibold text-teal-800">
            <Sparkles aria-hidden="true" className="size-4" /> AI-assisted travel planning
          </p>
          <h1 className="text-4xl font-bold tracking-tight text-slate-950 sm:text-6xl">
            Plan the journey. Enjoy the destination.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">
            AI Travel Planner keeps your travel details in one calm workspace and turns them into useful day-by-day itineraries.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Link className="inline-flex h-12 items-center rounded-lg bg-teal-700 px-5 text-sm font-semibold text-white transition hover:bg-teal-800" to="/register">
              Create your account <ArrowRight aria-hidden="true" className="ml-2 size-4" />
            </Link>
            <Link className="inline-flex h-12 items-center rounded-lg border border-slate-300 bg-white px-5 text-sm font-semibold text-slate-800 transition hover:bg-slate-100" to="/login">
              Sign in
            </Link>
          </div>
        </div>
        <div className="rounded-3xl bg-gradient-to-br from-teal-700 to-cyan-800 p-7 text-white shadow-card sm:p-10">
          <CalendarDays aria-hidden="true" className="size-10 text-teal-100" />
          <p className="mt-16 text-sm font-semibold uppercase tracking-[0.2em] text-teal-100">One place for every trip</p>
          <p className="mt-3 text-3xl font-semibold leading-tight">Start with the details. Let AI help with the day-to-day.</p>
        </div>
      </section>
    </main>
  );
}
