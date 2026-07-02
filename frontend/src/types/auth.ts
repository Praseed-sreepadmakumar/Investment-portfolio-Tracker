export interface AuthUser {
  id: number
  username: string
  email: string
  created_at: string
}

export interface AuthTokenResponse {
  access_token: string
  token_type: string
}

export interface LoginFormValues {
  username: string
  password: string
}

export interface RegisterFormValues {
  username: string
  email: string
  password: string
}

export interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (values: LoginFormValues) => Promise<void>
  register: (values: RegisterFormValues) => Promise<void>
  logout: () => void
}