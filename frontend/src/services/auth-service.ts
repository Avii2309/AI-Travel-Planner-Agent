import { apiClient } from "@/api/client";
import type {
  AccessTokenResponse,
  LoginCredentials,
  RegisterCredentials,
  User,
} from "@/types/auth";

export const authService = {
  async login(credentials: LoginCredentials): Promise<AccessTokenResponse> {
    const { data } = await apiClient.post<AccessTokenResponse>("/auth/login", credentials);
    return data;
  },

  async register(credentials: RegisterCredentials): Promise<User> {
    const { data } = await apiClient.post<User>("/auth/register", credentials);
    return data;
  },

  async getCurrentUser(): Promise<User> {
    const { data } = await apiClient.get<User>("/auth/me");
    return data;
  },
};
