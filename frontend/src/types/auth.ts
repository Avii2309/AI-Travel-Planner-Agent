export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  full_name: string;
}

export interface AccessTokenResponse {
  access_token: string;
  token_type: "bearer";
}
