import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

import { getStoredToken } from '../lib/storage'

const MAX_RETRIES = 3
const RETRY_DELAY_MS = 500

interface RetryConfig extends InternalAxiosRequestConfig {
  _retryCount?: number
}

const isRetryable = (error: AxiosError): boolean => {
  // Retry on network errors or 5xx server errors, but not on 4xx client errors.
  if (!error.response) return true
  return error.response.status >= 500
}

const delay = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms))

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000',
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  // Attach JWT token for all authenticated API calls.
  const token = getStoredToken()

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as RetryConfig | undefined

    if (!config || !isRetryable(error)) {
      return Promise.reject(error)
    }

    config._retryCount = (config._retryCount ?? 0) + 1

    if (config._retryCount > MAX_RETRIES) {
      return Promise.reject(error)
    }

    // Exponential backoff: 500ms, 1000ms, 2000ms
    const backoff = RETRY_DELAY_MS * 2 ** (config._retryCount - 1)
    await delay(backoff)

    return api(config)
  },
)

export default api