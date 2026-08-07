import { MapPinned } from "lucide-react";
import { Link } from "react-router-dom";

export function Brand() {
  return (
    <Link aria-label="AI Travel Planner home" className="inline-flex items-center gap-2 text-slate-950" to="/">
      <span className="grid size-9 place-items-center rounded-xl bg-teal-700 text-white shadow-sm">
        <MapPinned aria-hidden="true" className="size-5" />
      </span>
      <span className="text-base font-bold tracking-tight">AI Travel Planner</span>
    </Link>
  );
}
