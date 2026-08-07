import { Outlet } from "react-router-dom";

import { Brand } from "@/components/brand";

export function AuthLayout() {
  return (
    <main className="grid min-h-screen bg-slate-50 lg:grid-cols-2">
      <section className="flex flex-col p-6 sm:p-10">
        <Brand />
        <div className="mx-auto flex w-full max-w-md flex-1 items-center py-12">
          <Outlet />
        </div>
      </section>
      <aside className="hidden bg-teal-800 p-12 text-teal-50 lg:flex lg:flex-col lg:justify-end">
        <p className="mb-5 text-sm font-semibold uppercase tracking-[0.2em] text-teal-200">Travel, thoughtfully planned</p>
        <h1 className="max-w-lg text-5xl font-semibold tracking-tight">Turn a trip idea into an itinerary you can use.</h1>
        <p className="mt-6 max-w-md text-lg leading-8 text-teal-100">
          Keep your trips organized and generate practical day-by-day plans when you are ready.
        </p>
      </aside>
    </main>
  );
}
