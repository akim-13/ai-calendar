export interface MutationMapper<
    FrontendRequest,
    BackendRequest,
    BackendResponse,
    FrontendResponse,
> {
    toRequest(input: FrontendRequest): BackendRequest
    fromResponse(dto: BackendResponse): FrontendResponse
}

export interface QueryMapper<
    BackendResponse,
    FrontendResponse
> {
    fromResponse(dto: BackendResponse): FrontendResponse
}
