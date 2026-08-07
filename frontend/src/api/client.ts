import axios, { AxiosError } from "axios";

const TOKEN_STORAGE_KEY = "ai-travel-planner.access-token";

interface ApiErrorPayload {
  detail?: string;
  error?: {
    message?: string;
  };
}

export const tokenStorage = {
  get: (): string | null => sessionStorage.getItem(TOKEN_STORAGE_KEY),
  set: (token: string): void => sessionStorage.setItem(TOKEN_STORAGE_KEY, token),
  clear: (): void => sessionStorage.removeItem(TOKEN_STORAGE_KEY),
};

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || undefined,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const accessToken = tokenStorage.get();
  if (accessToken) {
    config.headers.set("Authorization", `Bearer ${accessToken}`);
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorPayload>) => {
    if (error.response?.status === 401) {
      tokenStorage.clear();
      window.dispatchEvent(new Event("auth:unauthorized"));
    }
    return Promise.reject(error);
  },
);

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError<ApiErrorPayload>(error)) {
    return "Something went wrong. Please try again.";
  }

  if (!error.response) {
    return "Unable to reach the service. Check your connection and try again.";
  }

  const payload = error.response.data;
  if (typeof payload?.error?.message === "string") {
    return payload.error.message;
  }
  if (typeof payload?.detail === "string") {
    return payload.detail;
  }

  const messages: Record<number, string> = {
    401: "Your session has expired. Please sign in again.",
    403: "You do not have permission to perform this action.",
    404: "The requested resource could not be found.",
    429: "Too many requests. Please wait a moment and try again.",
    500: "The service encountered an error. Please try again later.",
  };
  return messages[error.response.status] ?? "The request could not be completed.";
}
