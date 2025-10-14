import type {
  UseMutationResult,
  UseQueryResult,
} from "@tanstack/react-query"
import { normaliseApiError } from "@/api/errors"

// App-facing interface returned by mutation factories
export interface MappedMutationHook<RequestBody, Model> {
  mutateMapped: (request: RequestBody) => Promise<Model>
  model: Model | null
  error: ReturnType<typeof normaliseApiError> | null
  isPending: boolean
  isSuccess: boolean
  isError: boolean
}

// App-facing interface returned by query factories
export interface MappedQueryHook<Model> {
  data: Model | null
  error: ReturnType<typeof normaliseApiError> | null
  isLoading: boolean
  isError: boolean
}

// Factory for wrapping Orval-generated mutation hooks
export function createMappedMutationHook<
  RequestBody,
  ResponseDto,
  Model
>(
  useGeneratedHook: () => UseMutationResult<ResponseDto, unknown, RequestBody, unknown>,
  mapper: (data: ResponseDto) => Model
): () => MappedMutationHook<RequestBody, Model> {
  return function useMappedMutation() {
    const {
      mutateAsync,
      data,
      error,
      isPending,
      isSuccess,
      isError: _ignoredIsError,
      ...rest
    } = useGeneratedHook()

    async function mutateMapped(request: RequestBody): Promise<Model> {
      try {
        const response = await mutateAsync(request)
        return mapper(response)
      } catch (err) {
        throw normaliseApiError(err)
      }
    }

    const model = data ? mapper(data) : null
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

// Factory for wrapping Orval-generated query hooks
export function createMappedQueryHook<ResponseDto, Model>(
  useGeneratedQuery: (...args: any[]) => UseQueryResult<ResponseDto, unknown>,
  mapper: (data: ResponseDto) => Model
): (...args: any[]) => MappedQueryHook<Model> {
  return function useMappedQuery(...args) {
    const { data, error, ...rest } = useGeneratedQuery(...args)

    const model = data ? mapper(data) : null
    const normalisedError = error ? normaliseApiError(error) : null

    return {
      data: model,
      error: normalisedError,
      ...rest,
    }
  }
}
