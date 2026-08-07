import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";

import { getApiErrorMessage } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader } from "@/components/loader";
import { useAuth } from "@/hooks/use-auth";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password."),
});

type LoginValues = z.infer<typeof loginSchema>;

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    formState: { errors, isSubmitting },
    register,
    handleSubmit,
  } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (values: LoginValues) => {
    setFormError(null);
    try {
      await login(values);
      const destination = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? "/dashboard";
      navigate(destination, { replace: true });
    } catch (error) {
      setFormError(getApiErrorMessage(error));
    }
  };

  return (
    <div className="w-full">
      <h1 className="text-3xl font-bold tracking-tight text-slate-950">Welcome back</h1>
      <p className="mt-2 text-slate-600">Sign in to continue planning your next trip.</p>
      <Card className="mt-8">
        <CardContent className="pt-6">
          <form className="space-y-5" noValidate onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input autoComplete="email" id="email" placeholder="you@example.com" type="email" {...register("email")} />
              {errors.email && <p className="text-sm text-rose-600">{errors.email.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input autoComplete="current-password" id="password" type="password" {...register("password")} />
              {errors.password && <p className="text-sm text-rose-600">{errors.password.message}</p>}
            </div>
            {formError && <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700" role="alert">{formError}</p>}
            <Button className="w-full" disabled={isSubmitting} type="submit">
              {isSubmitting && <Loader className="mr-2 size-4 border-teal-200 border-t-white" />}
              Sign in
            </Button>
          </form>
        </CardContent>
      </Card>
      <p className="mt-6 text-center text-sm text-slate-600">
        New to AI Travel Planner? <Link className="font-semibold text-teal-700 hover:text-teal-800" to="/register">Create an account</Link>.
      </p>
    </div>
  );
}
