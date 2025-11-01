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
        const response = error.response
        const cfg = error.config

        return {
            message:
            response?.data?.detail ||
            response?.statusText ||
            error.message ||
            "Unknown error",
            status: response?.status ?? null,
            raw: error,
            // Return right hand side only if it exists, otherwise spread `undefined` to omit the field.
            ...(error?.code && { code: error.code }),
            ...(cfg?.method && { method: cfg.method.toUpperCase() }),
            ...(cfg?.url && { url: cfg.url }),
            ...(response?.data && { details: response.data }),
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
