import { normaliseApiError } from "@/api/errors"

// TODO: Yeah idk whats going on. Figure out and test.

/** Shape of an Orval-generated mutation hook (React Query mutation) */
export interface GeneratedMutationHook<RequestBody, ResponseData> {
  mutateAsync: (args: { data: RequestBody }) => Promise<{ data: ResponseData }>
  data?: { data: ResponseData }
  error?: unknown
  isPending: boolean
  isSuccess: boolean
}

/** Shape of an Orval-generated query hook (React Query query) */
export interface GeneratedQueryHook<ResponseData> {
  data?: { data: ResponseData }
  error?: unknown
  isLoading: boolean
  isError: boolean
}


/**
 * Factory that creates a mapped, normalised mutation hook
 * from an Orval-generated mutation hook.
 */
export function createMappedMutationHook<
  RequestBody,
  ResponseData,
  Model
>(
  useGeneratedHook: () => GeneratedMutationHook<RequestBody, ResponseData>,
  mapper: (data: ResponseData) => Model
) {
  return function useMappedMutation() {
    const { mutateAsync, data, error, isPending, isSuccess, ...rest } =
      useGeneratedHook()

    async function mutateMapped(request: RequestBody): Promise<Model> {
      try {
        const response = await mutateAsync({ data: request })
        return mapper(response.data)
      } catch (err) {
        throw normaliseApiError(err)
      }
    }

    const model = data ? mapper(data.data) : null
    const normalisedError = error ? normaliseApiError(error) : null

    return {
      mutateMapped,
      model,
      error: normalisedError,
      isPending,
      isSuccess,
      isError: !!error,
      ...rest,
    }
  }
}


/**
 * Factory that creates a mapped, normalised query hook
 * from an Orval-generated query hook.
 */
export function createMappedQueryHook<ResponseData, Model>(
  useGeneratedQuery: (...args: any[]) => GeneratedQueryHook<ResponseData>,
  mapper: (data: ResponseData) => Model
) {
  return function useMappedQuery(...args: any[]) {
    const { data, error, ...rest } = useGeneratedQuery(...args)

    const model = data ? mapper(data.data) : null
    const normalisedError = error ? normaliseApiError(error) : null

    return {
      data: model,
      error: normalisedError,
      ...rest,
    }
  }
}
