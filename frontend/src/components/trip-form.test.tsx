import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { TripForm } from "@/components/trip-form";

describe("TripForm destination and date validation", () => {
  beforeEach(() => vi.clearAllMocks());

  it("sets date minimums and submits without a separate location verification step", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <TripForm
        isSubmitting={false}
        onSubmit={onSubmit}
        submitLabel="Create trip"
      />,
    );

    const timezone = import.meta.env.VITE_APP_TIMEZONE || "Asia/Kolkata";
    const parts = new Intl.DateTimeFormat("en-CA", {
      timeZone: timezone,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).formatToParts(new Date());
    const today = `${parts.find((part) => part.type === "year")?.value}-${parts.find((part) => part.type === "month")?.value}-${parts.find((part) => part.type === "day")?.value}`;

    expect(screen.getByLabelText("Start date")).toHaveAttribute("min", today);
    expect(screen.getByLabelText("End date")).toHaveAttribute("min", today);
    expect(screen.queryByRole("button", { name: /verify destination/i })).not.toBeInTheDocument();

    const startDate = new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    fireEvent.change(screen.getByLabelText("Departure"), { target: { value: "Jaipur, Rajasthan" } });
    fireEvent.change(screen.getByLabelText("Destination"), { target: { value: "Delhi, India" } });
    fireEvent.change(screen.getByLabelText("Start date"), { target: { value: startDate } });
    fireEvent.change(screen.getByLabelText("End date"), { target: { value: startDate } });
    fireEvent.change(screen.getByLabelText("Total budget"), { target: { value: "1000" } });
    fireEvent.click(screen.getByRole("button", { name: "Create trip" }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          source: "Jaipur, Rajasthan",
          destination: "Delhi, India",
          start_date: startDate,
          end_date: startDate,
        }),
      );
    });
  });

  it("shows a backend location error on the corresponding form field", async () => {
    const onSubmit = vi.fn().mockRejectedValue({
      response: {
        data: {
          error_code: "INVALID_START_LOCATION",
          field: "start_location",
          message: "Please enter a valid starting location.",
        },
      },
    });
    render(
      <TripForm
        isSubmitting={false}
        onSubmit={onSubmit}
        submitLabel="Create trip"
      />,
    );

    fireEvent.change(screen.getByLabelText("Departure"), { target: { value: "InvalidXYZ123" } });
    fireEvent.change(screen.getByLabelText("Destination"), { target: { value: "Jaipur, Rajasthan" } });
    const startDate = new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    fireEvent.change(screen.getByLabelText("Start date"), { target: { value: startDate } });
    fireEvent.change(screen.getByLabelText("End date"), { target: { value: startDate } });
    fireEvent.change(screen.getByLabelText("Total budget"), { target: { value: "1000" } });
    fireEvent.click(screen.getByRole("button", { name: "Create trip" }));

    await waitFor(() => {
      expect(screen.getByText("Please enter a valid starting location.")).toBeInTheDocument();
    });
  });

  it("shows the validation status and disables submission while processing", () => {
    render(
      <TripForm
        isSubmitting
        onSubmit={vi.fn()}
        submitLabel="Create trip"
      />,
    );

    expect(screen.getByText("Validating trip details...")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Validating/ })).toBeDisabled();
  });
});
