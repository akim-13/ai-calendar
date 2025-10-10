import axios, { AxiosError, AxiosResponse } from "axios"

export interface ApiError {
  /** Human-readable summary */
  message: string
  /** HTTP status code if the server responded */
  status: number | null
  /** The request method and URL, if known */
  method?: string
  url?: string
  /** The error code from Axios (e.g. ERR_NETWORK, ECONNABORTED) */
  code?: string
  /** Backend-supplied payload (e.g. FastAPI detail) */
  details?: unknown
  /** The original unmodified error object, for debugging */
  raw: unknown
}

export function normaliseApiError(error: unknown): ApiError {
  // Case 1: It's an AxiosError (most common)
  if (axios.isAxiosError(error)) {
    const res: AxiosResponse | undefined = error.response
    const cfg = error.config

    return {
      message:
        res?.data?.detail ||
        res?.statusText ||
        error.message ||
        "Unknown error",
      status: res?.status ?? null,
      method: cfg?.method?.toUpperCase(),
      url: cfg?.url,
      code: error.code,
      details: res?.data,
      raw: error, // preserve everything
    }
  }

  // Case 2: It’s a normal JS error
  if (error instanceof Error) {
    return {
      message: error.message,
      status: null,
      raw: error,
    }
  }

  // Case 3: Unknown / non-Error value
  return {
    message: "Unknown error",
    status: null,
    raw: error,
  }
}
