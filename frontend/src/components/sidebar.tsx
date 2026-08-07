import { LayoutDashboard, Map, Sparkles } from "lucide-react";
import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

const navigation = [
  { label: "Overview", icon: LayoutDashboard, to: "/dashboard" },
  { label: "Trips", icon: Map, to: "/trips" },
  { label: "AI itineraries", icon: Sparkles, to: "/itineraries", disabled: true },
];

export function Sidebar() {
  return (
    <aside className="border-b border-slate-200 bg-white lg:min-h-[calc(100vh-4rem)] lg:w-60 lg:border-b-0 lg:border-r">
      <nav aria-label="Primary navigation" className="flex gap-2 overflow-x-auto p-3 lg:flex-col lg:p-4">
        {navigation.map(({ disabled, icon: Icon, label, to }) =>
          disabled ? (
            <span
              aria-disabled="true"
              className="inline-flex shrink-0 items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-400"
              key={label}
              title="Available in the next phase"
            >
              <Icon aria-hidden="true" className="size-4" />
              {label}
            </span>
          ) : (
            <NavLink
              className={({ isActive }) =>
                cn(
                  "inline-flex shrink-0 items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100",
                  isActive && "bg-teal-50 text-teal-800",
                )
              }
              key={label}
              to={to}
            >
              <Icon aria-hidden="true" className="size-4" />
              {label}
            </NavLink>
          ),
        )}
      </nav>
    </aside>
  );
}
