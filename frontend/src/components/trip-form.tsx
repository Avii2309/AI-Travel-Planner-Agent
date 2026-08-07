import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Loader } from "@/components/loader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import type { TripCreate, TripResponse } from "@/types/trip";

const isPreferencesObject = (value: string) => {
  if (!value.trim()) {
    return true;
  }
  try {
    const parsed: unknown = JSON.parse(value);
    return typeof parsed === "object" && parsed !== null && !Array.isArray(parsed);
  } catch {
    return false;
  }
};

const tripFormSchema = z
  .object({
    source: z.string().trim().min(1, "Enter a departure location.").max(255, "Location is too long."),
    destination: z.string().trim().min(1, "Enter a destination.").max(255, "Location is too long."),
    start_date: z.string().min(1, "Select a start date."),
    end_date: z.string().min(1, "Select an end date."),
    budget: z.coerce.number().positive("Budget must be greater than zero.").max(9_999_999_999.99, "Budget is too large."),
    travelers: z.coerce.number().int("Use a whole number.").min(1, "At least one traveler is required.").max(100, "A maximum of 100 travelers is allowed."),
    preferences: z.string().refine(isPreferencesObject, "Preferences must be a valid JSON object."),
  })
  .refine((values) => values.end_date >= values.start_date, {
    message: "End date must be on or after the start date.",
    path: ["end_date"],
  });

type TripFormValues = z.infer<typeof tripFormSchema>;

interface TripFormProps {
  initialTrip?: TripResponse;
  isSubmitting: boolean;
  submitLabel: string;
  errorMessage?: string;
  onSubmit: (values: TripCreate) => Promise<void>;
}

const defaultValues: TripFormValues = {
  source: "",
  destination: "",
  start_date: "",
  end_date: "",
  budget: 0,
  travelers: 1,
  preferences: "{}",
};

function valuesFromTrip(trip: TripResponse): TripFormValues {
  return {
    source: trip.source,
    destination: trip.destination,
    start_date: trip.start_date,
    end_date: trip.end_date,
    budget: Number(trip.budget),
    travelers: trip.travelers,
    preferences: JSON.stringify(trip.preferences, null, 2),
  };
}

export function TripForm({ initialTrip, isSubmitting, submitLabel, errorMessage, onSubmit }: TripFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
    reset,
  } = useForm<TripFormValues>({
    defaultValues: initialTrip ? valuesFromTrip(initialTrip) : defaultValues,
    resolver: zodResolver(tripFormSchema),
  });

  useEffect(() => {
    reset(initialTrip ? valuesFromTrip(initialTrip) : defaultValues);
  }, [initialTrip, reset]);

  const submit = async (values: TripFormValues) => {
    const preferences = values.preferences.trim() ? JSON.parse(values.preferences) as Record<string, unknown> : {};
    await onSubmit({ ...values, preferences });
  };

  return (
    <form className="space-y-6" noValidate onSubmit={handleSubmit(submit)}>
      <div className="grid gap-5 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="source">Departure</Label>
          <Input autoComplete="off" id="source" placeholder="Mumbai" {...register("source")} />
          {errors.source && <p className="text-sm text-rose-600">{errors.source.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="destination">Destination</Label>
          <Input autoComplete="off" id="destination" placeholder="Goa" {...register("destination")} />
          {errors.destination && <p className="text-sm text-rose-600">{errors.destination.message}</p>}
        </div>
      </div>
      <div className="grid gap-5 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="start_date">Start date</Label>
          <Input id="start_date" type="date" {...register("start_date")} />
          {errors.start_date && <p className="text-sm text-rose-600">{errors.start_date.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="end_date">End date</Label>
          <Input id="end_date" type="date" {...register("end_date")} />
          {errors.end_date && <p className="text-sm text-rose-600">{errors.end_date.message}</p>}
        </div>
      </div>
      <div className="grid gap-5 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="budget">Total budget</Label>
          <Input id="budget" inputMode="decimal" min="0.01" step="0.01" type="number" {...register("budget")} />
          {errors.budget && <p className="text-sm text-rose-600">{errors.budget.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="travelers">Travelers</Label>
          <Input id="travelers" min="1" step="1" type="number" {...register("travelers")} />
          {errors.travelers && <p className="text-sm text-rose-600">{errors.travelers.message}</p>}
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="preferences">Preferences (optional JSON object)</Label>
        <Textarea id="preferences" placeholder={'{\n  "pace": "relaxed"\n}'} spellCheck="false" {...register("preferences")} />
        <p className="text-xs leading-5 text-slate-500">Use a JSON object to store flexible trip preferences. Leave it as {'{}'} when you have none.</p>
        {errors.preferences && <p className="text-sm text-rose-600">{errors.preferences.message}</p>}
      </div>
      {errorMessage && <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700" role="alert">{errorMessage}</p>}
      <Button disabled={isSubmitting} type="submit">
        {isSubmitting && <Loader className="mr-2 size-4 border-teal-200 border-t-white" />}
        {submitLabel}
      </Button>
    </form>
  );
}
