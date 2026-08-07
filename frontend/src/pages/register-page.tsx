import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

import { getApiErrorMessage } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader } from "@/components/loader";
import { useAuth } from "@/hooks/use-auth";

const registerSchema = z.object({
  full_name: z.string().trim().min(1, "Enter your name.").max(255, "Name is too long."),
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(8, "Use at least 8 characters.").max(72, "Password is too long."),
});

type RegisterValues = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const { register: createAccount } = useAuth();
  const navigate = useNavigate();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    formState: { errors, isSubmitting },
    register,
    handleSubmit,
  } = useForm<RegisterValues>({ resolver: zodResolver(registerSchema) });

  const onSubmit = async (values: RegisterValues) => {
    setFormError(null);
    try {
      await createAccount(values);
      navigate("/dashboard", { replace: true });
    } catch (error) {
      setFormError(getApiErrorMessage(error));
    }
  };

  return (
    <div className="w-full">
      <h1 className="text-3xl font-bold tracking-tight text-slate-950">Create your account</h1>
      <p className="mt-2 text-slate-600">Start organizing your travel plans in one place.</p>
      <Card className="mt-8">
        <CardContent className="pt-6">
          <form className="space-y-5" noValidate onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-2">
              <Label htmlFor="full_name">Full name</Label>
              <Input autoComplete="name" id="full_name" placeholder="Avery Patel" {...register("full_name")} />
              {errors.full_name && <p className="text-sm text-rose-600">{errors.full_name.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input autoComplete="email" id="email" placeholder="you@example.com" type="email" {...register("email")} />
              {errors.email && <p className="text-sm text-rose-600">{errors.email.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input autoComplete="new-password" id="password" type="password" {...register("password")} />
              {errors.password && <p className="text-sm text-rose-600">{errors.password.message}</p>}
            </div>
            {formError && <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700" role="alert">{formError}</p>}
            <Button className="w-full" disabled={isSubmitting} type="submit">
              {isSubmitting && <Loader className="mr-2 size-4 border-teal-200 border-t-white" />}
              Create account
            </Button>
          </form>
        </CardContent>
      </Card>
      <p className="mt-6 text-center text-sm text-slate-600">
        Already have an account? <Link className="font-semibold text-teal-700 hover:text-teal-800" to="/login">Sign in</Link>.
      </p>
    </div>
  );
}
