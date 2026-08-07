import { cn } from "@/lib/utils";

export function Loader({ className }: { className?: string }) {
  return (
    <span
      aria-label="Loading"
      className={cn("inline-block size-5 animate-spin rounded-full border-2 border-slate-200 border-t-teal-700", className)}
      role="status"
    />
  );
}
