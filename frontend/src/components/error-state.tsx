import { AlertCircle } from "lucide-react";

import { Button } from "@/components/ui/button";

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="rounded-2xl border border-rose-200 bg-rose-50 px-6 py-10 text-center">
      <AlertCircle aria-hidden="true" className="mx-auto size-8 text-rose-600" />
      <h2 className="mt-4 text-lg font-bold text-rose-950">We couldn’t load your trips</h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-rose-800">{message}</p>
      {onRetry && <Button className="mt-6" onClick={onRetry} variant="outline">Try again</Button>}
    </div>
  );
}
