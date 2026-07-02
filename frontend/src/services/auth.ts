import api from './api'
import type {
  AuthTokenResponse,
  AuthUser,
  LoginFormValues,
  RegisterFormValues,
} from '../types/auth'

export async function loginUser(
  values: LoginFormValues,
): Promise<AuthTokenResponse> {
  const response = await api.post<AuthTokenResponse>('/login', values)
  return response.data
}

export async function registerUser(
  values: RegisterFormValues,
): Promise<AuthUser> {
  const response = await api.post<AuthUser>('/register', values)
  return response.data
}

export async function getCurrentUser(): Promise<AuthUser> {
  const response = await api.get<AuthUser>('/me')
  return response.data
}